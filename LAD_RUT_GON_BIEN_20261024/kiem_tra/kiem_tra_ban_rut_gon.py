"""Mô hình LAD rút gọn 24/10/2026 và đối chiếu theo từng vòng quét.

Chỉ dùng Python chuẩn; không giao tiếp thiết bị. Đây KHÔNG phải TIA/PLCSIM.
Bốn edge được tính độc lập, rồi mới OR: không mô phỏng bằng OR short-circuit
các hàm có thay đổi bộ nhớ. s.xung chỉ là dấu vết kiểm tra để dùng lại các
phép thử cũ, không phải bốn biến cần khai báo trong DB của bản LAD mới.
"""
from dataclasses import asdict
from pathlib import Path
import json
import random
import traceback
import mo_hinh_tham_chieu_20261022 as goc

MoHinhGoc = goc.MoHinh


class MoHinhRutGon(MoHinhGoc):
    def scan(self, **changes):
        for key, val in changes.items():
            if not hasattr(self.i, key):
                raise KeyError(key)
            setattr(self.i, key, val)
        i, s = self.i, self.s
        first = not s.da_qua_vong_dau

        # NW1–2: giữ chuẩn hóa STOP và lọc ổn định cả nhấn/nhả.
        stop_nhan = (i.stop_nc and not i.stop_day) or (not i.stop_nc and i.stop_day)
        for raw, on, release, name in (
            (i.start_that, s.loc_auto, s.loc_auto_nha, 'auto_on_dinh'),
            (stop_nhan, s.loc_stop, s.loc_stop_nha, 'stop_on_dinh'),
            (i.reset_that, s.loc_reset, s.loc_reset_nha, 'reset_on_dinh'),
        ):
            q_nhan = on.scan(raw and not first, self.dt)
            q_nha = release.scan(not raw and not first, self.dt)
            setattr(s, name, (getattr(s, name) or q_nhan) and not (q_nha or first))

        # NW3: chuỗi tiếp điểm cấp trực tiếp IN, đọc trực tiếp Q của TON.
        s.cho_nha.scan(not (i.start_that or stop_nhan or i.reset_that or
                           i.auto_hmi or i.stop_hmi or i.reset_hmi or i.tat_hmi or first), self.dt)
        s.da_nha_lenh = (s.da_nha_lenh or s.cho_nha.q) and not first

        # NW4: P ở đầu mỗi nhánh, bộ nhớ riêng; điều kiện cho phép ở sau OR.
        levels = (s.auto_on_dinh, i.auto_hmi, s.stop_on_dinh, i.stop_hmi)
        edges = tuple(level and not s.nho_canh[k] for k, level in enumerate(levels))
        s.nho_canh = list(levels)
        s.lenh_auto = (edges[0] or edges[1]) and s.da_nha_lenh
        s.lenh_stop = (edges[2] or edges[3]) and s.da_nha_lenh
        s.xung = [edge and s.da_nha_lenh for edge in edges]  # Chỉ trace kiểm tra.

        # NW5: RESET hợp mức; giữ RESET tiếp tục khóa quyền chạy.
        s.reset_chuong_trinh = (s.reset_on_dinh or i.reset_hmi) and not first

        # NW6–8: RTC, lịch, lỗi hiện tại giữ nguyên.
        s.rtc_ok = i.ma_rtc in (0, 1)
        t = i.giay_trong_ngay
        s.trong_gio = s.rtc_ok and ((21600 <= t < 28800) or (61200 <= t < 73800))
        s.an_toan = not i.dung_khan and i.du_nuoc and not i.qua_tai
        s.loi_hien_tai = not s.an_toan or ((s.cho_phep_auto or s.lenh_auto) and not s.rtc_ok)

        # NW9: bỏ tiếp điểm /LỖI HIỆN TẠI do AN TOÀN & RTC OK đã bao phủ.
        s.xac_nhan_loi = s.reset_chuong_trinh and s.an_toan and s.rtc_ok
        s.nho_loi = (s.nho_loi or s.loi_hien_tai) and not s.xac_nhan_loi
        s.den_loi = s.nho_loi

        # NW11: SR ưu tiên R1; bỏ hai tiếp điểm /HỦY lặp ở chân S và rung TU.
        s.huy_phep_chay = (first or i.tat_hmi or s.reset_chuong_trinh or
                          not s.an_toan or not s.rtc_ok or s.nho_loi)
        set_auto = s.lenh_auto and not s.lenh_stop
        s.cho_phep_auto = (s.cho_phep_auto or set_auto) and not s.huy_phep_chay
        s.tu_dong_chay = s.cho_phep_auto and s.trong_gio

        # NW12–13: một phép ghi pause và một bản sao bước dự kiến.
        s.tam_dung = s.cho_phep_auto and (s.tam_dung != s.lenh_stop)
        s.buoc_tiep_theo = s.buoc_hien_tai
        if s.tu_dong_chay and s.buoc_hien_tai == 0:
            s.buoc_tiep_theo = 1

        # NW14–18: gọi timer trước khi đọc Q; R giữ nguyên.
        for k in range(5):
            n = k + 1
            reset_timer = s.buoc_hien_tai != n or not s.tu_dong_chay
            inp = s.tu_dong_chay and s.buoc_hien_tai == n and not s.tam_dung
            if reset_timer:
                s.et[k] = 0
            elif inp:
                s.et[k] = min(10000, s.et[k] + self.dt)
            s.timer_q[k] = s.et[k] >= 10000
            if s.timer_q[k] and not s.tam_dung:
                s.buoc_tiep_theo = n % 5 + 1

        # NW19: commit trước các ngõ ra và hiển thị, xóa bước khi TU=0.
        if s.tu_dong_chay and not s.tam_dung:
            s.buoc_hien_tai = s.buoc_tiep_theo
        if not s.tu_dong_chay:
            s.buoc_hien_tai = s.buoc_tiep_theo = 0

        # NW20: bốn van giữ đủ điều kiện; bơm đọc bốn Q vừa được tính.
        enable = s.tu_dong_chay and not s.tam_dung
        n = s.buoc_hien_tai
        s.van = tuple(enable and lo <= n <= hi for lo, hi in ((1, 4), (2, 5), (3, 4), (4, 5)))
        s.bom = any(s.van)

        # NW21–22: chỉ cần bước hợp lệ sau NW19, không lặp TU.
        valid = 1 <= n <= 5
        elapsed = s.et[n - 1] if valid else 0
        s.thoigianconlai = 10 - elapsed // 1000 if valid else 0
        s.da_qua_vong_dau = True
        self.so_vong += 1
        return s


EQUIV_TESTS = []
COMPARE_COUNT = 0


def equivalence(name):
    def decorate(fn):
        EQUIV_TESTS.append((name, fn))
        return fn
    return decorate


class Pair:
    def __init__(self, **inputs):
        self.a = MoHinhGoc(**inputs)
        self.b = MoHinhRutGon(**inputs)

    def scan(self, **changes):
        global COMPARE_COUNT
        a = self.a.scan(**changes)
        b = self.b.scan(**changes)
        COMPARE_COUNT += 1
        da, db = asdict(a), asdict(b)
        differences = {key: (da[key], db[key]) for key in da if da[key] != db[key]}
        assert not differences, {'scan': self.a.so_vong, 'input': changes, 'different': differences}
        return b

    def many(self, count, **changes):
        for _ in range(count):
            self.scan(**changes)
        return self.b.s

    def press(self, name):
        high = not (name == 'stop_day' and self.a.i.stop_nc)
        self.many(5, **{name: high})
        self.many(5, **{name: not high})


@equivalence('Hai chu trình đầy đủ, bốn mẫu thao tác chéo và giữ một nguồn')
def normal_sequence():
    p = Pair(); p.many(6); p.press('start_that'); p.many(10500)
    p.press('stop_hmi'); p.many(1100); p.press('stop_day'); p.many(1500)
    p.many(10, auto_hmi=True); p.press('reset_that'); p.press('start_that')
    p.many(10, stop_hmi=True); p.press('stop_day'); p.many(500)
    p.many(5, auto_hmi=False, stop_hmi=False); p.press('tat_hmi')


@equivalence('Các lệnh giữ lúc khởi động và FirstScan có trạng thái cũ')
def startup_held():
    for name in ('start_that', 'stop_day', 'reset_that', 'auto_hmi', 'stop_hmi', 'reset_hmi', 'tat_hmi'):
        p = Pair(**{name: True})
        for m in (p.a, p.b):
            m.s.cho_phep_auto = m.s.da_nha_lenh = m.s.tam_dung = True
            m.s.buoc_hien_tai = m.s.buoc_tiep_theo = 4
            m.s.et = [9000] * 5
        p.many(200); p.many(5, **{name: False}); p.press('start_that'); p.many(200)


@equivalence('Lọc dội, nhả chớp khi giữ nút, tiếp điểm STOP NO và NC')
def bounce_and_nc():
    for nc in (False, True):
        p = Pair(stop_nc=nc, stop_day=nc); p.many(6); p.press('start_that')
        press, release = not nc, nc
        for _ in range(20):
            p.many(2, stop_day=press); p.many(1, stop_day=release)
        p.many(10, stop_day=press)
        for _ in range(20):
            p.many(2, stop_day=release); p.many(4, stop_day=press)
        p.many(5, stop_day=release); p.press('stop_day'); p.many(300)


@equivalence('Giữ RESET, START/STOP/TẮT đồng thời và xóa lỗi theo mức')
def priorities():
    for nc in (False, True):
        for reset in ('reset_that', 'reset_hmi'):
            p = Pair(stop_nc=nc, stop_day=nc); p.many(6); p.press('start_that')
            p.press('stop_hmi'); p.many(5, **{reset: True}); p.press('start_that')
            p.many(5, **{reset: False}); p.press('start_that')
            for fault, bad, normal in [('du_nuoc', False, True), ('qua_tai', True, False), ('dung_khan', True, False), ('ma_rtc', 0x8080, 0)]:
                p.scan(**{fault: bad}); p.many(5, **{reset: True}); p.scan(**{fault: normal})
                p.many(5, **{reset: False}); p.press('start_that')
            p.scan(auto_hmi=True, stop_hmi=True, tat_hmi=True)
            p.many(5, auto_hmi=False, stop_hmi=False, tat_hmi=False)
            p.scan(auto_hmi=True, stop_hmi=True, reset_hmi=True)


@equivalence('Các biên giờ chạy, chọn AUTO ngoài ca và hết ca khi tạm dừng')
def schedules():
    p = Pair(giay_trong_ngay=21599); p.many(6); p.press('start_that')
    for t in (21600, 28799, 28800, 61199, 61200, 73799, 73800):
        p.many(40, giay_trong_ngay=t)
    p.scan(giay_trong_ngay=28799); p.press('stop_hmi'); p.many(5, giay_trong_ngay=28800)
    p.many(5, giay_trong_ngay=61200); p.press('stop_day'); p.many(500)


@equivalence('STOP ngay trước/vừa đạt 10 s, và bước bất hợp lệ được hiển thị 0')
def timer_boundary():
    p = Pair(); p.many(6); p.press('auto_hmi')
    while p.b.s.et[0] < 9990:
        p.scan()
    p.scan(stop_hmi=True); p.many(20, stop_hmi=False); p.scan(stop_hmi=True)
    p.many(5, stop_hmi=False)
    for n in (-2, 0, 6, 32767):
        for m in (p.a, p.b):
            m.s.buoc_hien_tai = n
        p.scan()
    p.press('reset_hmi')


@equivalence('80.000 vòng quét ngẫu nhiên có hạt giống cố định, cả STOP NO và NC')
def random_comparison():
    rng = random.Random(20261024)
    for nc in (False, True):
        p = Pair(stop_nc=nc, stop_day=nc); p.many(6)
        for _ in range(40000):
            changes = {}
            for name in ('start_that','stop_day','reset_that','auto_hmi','stop_hmi','reset_hmi','tat_hmi'):
                if rng.random() < .012:
                    changes[name] = not getattr(p.a.i, name)
            for name in ('du_nuoc','qua_tai','dung_khan'):
                if rng.random() < .001:
                    changes[name] = not getattr(p.a.i, name)
            if rng.random() < .002:
                changes['ma_rtc'] = rng.choice((0, 1, 0x8080))
            if rng.random() < .002:
                changes['giay_trong_ngay'] = rng.choice((21599,21600,28799,28800,61199,61200,73799,73800,43200))
            p.scan(**changes)


def main():
    rows = []
    # Chạy nguyên 25 nhóm tình huống cũ trên mô hình rút gọn.
    goc.MoHinh = MoHinhRutGon
    for name, fn in goc.TESTS:
        try:
            fn(); rows.append({'ten': name, 'ket_qua': 'Đạt'})
        except Exception:
            rows.append({'ten': name, 'ket_qua': 'Lỗi', 'chi_tiet': traceback.format_exc()})
    goc.MoHinh = MoHinhGoc
    equiv_rows = []
    for name, fn in EQUIV_TESTS:
        before = COMPARE_COUNT
        try:
            fn(); equiv_rows.append({'ten': name, 'ket_qua': 'Đạt', 'so_vong_doi_chieu': COMPARE_COUNT-before})
        except Exception:
            equiv_rows.append({'ten': name, 'ket_qua': 'Lỗi', 'chi_tiet': traceback.format_exc()})
    passed = sum(r['ket_qua'] == 'Đạt' for r in rows)
    equiv_passed = sum(r['ket_qua'] == 'Đạt' for r in equiv_rows)
    result = {
        'mo_ta': 'Mô hình Python rời rạc và đối chiếu từng vòng quét; chưa Compile hoặc chạy trên Siemens.',
        'dt_ms': 10,
        'nhom_tinh_huong_dat': passed,
        'nhom_tinh_huong_loi': len(rows)-passed,
        'nhom_doi_chieu_dat': equiv_passed,
        'nhom_doi_chieu_loi': len(equiv_rows)-equiv_passed,
        'tong_so_vong_doi_chieu': COMPARE_COUNT,
        'tinh_huong': rows,
        'doi_chieu': equiv_rows,
        'gioi_han': [
            'Không thay cho Compile TIA, PLCSIM hoặc thử CPU thực.',
            'TON/TONR dùng dt giả định 10 ms, không chứng minh thời gian thực và chi tiết cập nhật timer Siemens.',
            'Chỉ tương đương với thứ tự network và nơi ghi biến như thiết kế; không xét force hoặc OB khác ghi đè giữa chừng.',
            'P là tiếp điểm bắt cạnh toán hạng, bộ nhớ riêng, mỗi nhánh được đánh giá mỗi scan; không dùng một P sau OR.',
            'Bốn phần tử s.xung là trace của bộ kiểm tra, không phải bốn biến trong bảng DB rút gọn.',
        ],
    }
    out = Path(__file__).with_name('ket_qua_rut_gon.json')
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({k: result[k] for k in ('nhom_tinh_huong_dat','nhom_tinh_huong_loi','nhom_doi_chieu_dat','nhom_doi_chieu_loi','tong_so_vong_doi_chieu')}, ensure_ascii=False))
    for row in rows + equiv_rows:
        if row['ket_qua'] == 'Lỗi':
            print(row['ten'], row['chi_tiet'])
    raise SystemExit(0 if passed == len(rows) and equiv_passed == len(equiv_rows) else 1)


if __name__ == '__main__':
    main()
