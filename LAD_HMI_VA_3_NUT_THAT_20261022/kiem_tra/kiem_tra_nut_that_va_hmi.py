"""Mô hình vòng quét độc lập cho bản LAD nhận lệnh nút thật + HMI.

Chạy: python kiem_tra_nut_that_va_hmi.py
Chỉ dùng thư viện chuẩn Python; không kết nối PLC.
Đây là mô hình logic rời rạc, KHÔNG phải PLCSIM/TIA hoặc mô hình thời gian
thực chính xác của IEC TON/TONR Siemens. Mỗi scan tích lũy dt_ms giả định.
"""

from dataclasses import dataclass, field
from pathlib import Path
import json
import random
import traceback


@dataclass
class DauVao:
    start_that: bool = False       # %I0.0, giả định tiếp điểm NO
    stop_day: bool = False         # %I0.5, giá trị điện đầu vào
    reset_that: bool = False       # %I0.2, giả định tiếp điểm NO
    stop_nc: bool = False          # True nếu tiếp điểm STOP thực là NC
    auto_hmi: bool = False         # DB chon_auto_hmi: lệnh nhấn
    stop_hmi: bool = False         # DB hmi_stop: lệnh nhấn, không phải pause
    reset_hmi: bool = False        # DB hmi_reset: lệnh theo mức
    tat_hmi: bool = False          # DB lenh_tat_hmi: lệnh theo mức
    du_nuoc: bool = True
    qua_tai: bool = False
    dung_khan: bool = False
    ma_rtc: int = 0
    giay_trong_ngay: int = 6 * 3600


@dataclass
class TON:
    et: int = 0
    q: bool = False

    def scan(self, inp, dt_ms, pt_ms=30):
        self.et = min(pt_ms, self.et + dt_ms) if inp else 0
        self.q = self.et >= pt_ms
        return self.q


@dataclass
class TrangThai:
    da_qua_vong_dau: bool = False
    da_nha_lenh: bool = False
    cho_phep_auto: bool = False
    tam_dung: bool = False
    nho_loi: bool = False
    loi_hien_tai: bool = False
    an_toan: bool = True
    rtc_ok: bool = True
    trong_gio: bool = True
    huy_phep_chay: bool = False
    tu_dong_chay: bool = False
    reset_chuong_trinh: bool = False
    xac_nhan_loi: bool = False
    lenh_auto: bool = False
    lenh_stop: bool = False
    buoc_hien_tai: int = 0
    buoc_tiep_theo: int = 0
    thoigianconlai: int = 0
    et: list = field(default_factory=lambda: [0] * 5)
    timer_q: list = field(default_factory=lambda: [False] * 5)
    van: tuple = (False, False, False, False)
    bom: bool = False
    den_loi: bool = False
    nho_canh: list = field(default_factory=lambda: [False] * 4)
    xung: list = field(default_factory=lambda: [False] * 4)
    loc_auto: TON = field(default_factory=TON)
    loc_auto_nha: TON = field(default_factory=TON)
    loc_stop: TON = field(default_factory=TON)
    loc_stop_nha: TON = field(default_factory=TON)
    loc_reset: TON = field(default_factory=TON)
    loc_reset_nha: TON = field(default_factory=TON)
    auto_on_dinh: bool = False
    stop_on_dinh: bool = False
    reset_on_dinh: bool = False
    cho_nha: TON = field(default_factory=TON)


class MoHinh:
    def __init__(self, dt_ms=10, **inputs):
        self.i = DauVao(**inputs)
        self.s = TrangThai()
        self.dt = dt_ms
        self.so_vong = 0

    def scan(self, **changes):
        for key, val in changes.items():
            if not hasattr(self.i, key):
                raise KeyError(key)
            setattr(self.i, key, val)
        i, s = self.i, self.s
        first = not s.da_qua_vong_dau

        # NW1: chuẩn hóa STOP; nhấn luôn có nghĩa True.
        stop_nhan = (i.stop_nc and not i.stop_day) or (not i.stop_nc and i.stop_day)

        # NW2: lọc cả cạnh nhấn và nhả, mỗi phía TON 30 ms.
        # SR mức ổn định ưu tiên nhả hoặc FirstScan; glitch ngắn không đổi bit.
        for raw, on, release, name in (
            (i.start_that, s.loc_auto, s.loc_auto_nha, 'auto_on_dinh'),
            (stop_nhan, s.loc_stop, s.loc_stop_nha, 'stop_on_dinh'),
            (i.reset_that, s.loc_reset, s.loc_reset_nha, 'reset_on_dinh'),
        ):
            pressed_q = on.scan(raw and not first, self.dt)
            released_q = release.scan(not raw and not first, self.dt)
            setattr(s, name, (getattr(s, name) or pressed_q) and not (released_q or first))
        auto_loc = s.auto_on_dinh
        stop_loc = s.stop_on_dinh
        reset_loc = s.reset_on_dinh

        # NW3: chỉ mở quyền nhận lệnh sau lần nhả tất cả lệnh ổn định.
        # Cờ này giữ cho tới FirstScan tiếp theo, không reset mỗi khi nhấn.
        da_nha = not any((i.start_that, stop_nhan, i.reset_that,
                         i.auto_hmi, i.stop_hmi, i.reset_hmi, i.tat_hmi))
        nha_on_dinh = s.cho_nha.scan(da_nha and not first, self.dt)
        s.da_nha_lenh = (s.da_nha_lenh or nha_on_dinh) and not first

        # NW4: bốn bộ nhớ cạnh riêng. Luôn cập nhật bộ nhớ TRƯỚC khi chặn xung.
        levels = (auto_loc, i.auto_hmi, stop_loc, i.stop_hmi)
        raw_edges = [level and not prev for level, prev in zip(levels, s.nho_canh)]
        s.nho_canh = list(levels)
        s.xung = [edge and s.da_nha_lenh for edge in raw_edges]

        # NW5: hợp lệnh; RESET/TẮT theo mức để giữ quyền ưu tiên khi còn nhấn.
        s.lenh_auto = s.xung[0] or s.xung[1]
        s.lenh_stop = s.xung[2] or s.xung[3]
        s.reset_chuong_trinh = (reset_loc or i.reset_hmi) and not first

        # NW6–8: giờ địa phương, lịch vận hành, bảo vệ.
        s.rtc_ok = i.ma_rtc in (0, 1)
        t = i.giay_trong_ngay
        s.trong_gio = s.rtc_ok and ((21600 <= t < 28800) or (61200 <= t < 73800))
        s.an_toan = not i.dung_khan and i.du_nuoc and not i.qua_tai
        s.loi_hien_tai = (not s.an_toan or
                         ((s.cho_phep_auto or s.lenh_auto) and not s.rtc_ok))

        # NW9–10: giữ chính sách RESET theo mức như V1644.
        s.xac_nhan_loi = (s.reset_chuong_trinh and s.an_toan and
                         s.rtc_ok and not s.loi_hien_tai)
        s.nho_loi = (s.nho_loi or s.loi_hien_tai) and not s.xac_nhan_loi
        s.den_loi = s.nho_loi

        # NW11: SR ưu tiên reset; CHO PHÉP AUTO là trạng thái chung duy nhất.
        s.huy_phep_chay = (first or i.tat_hmi or s.reset_chuong_trinh or
                          not s.an_toan or not s.rtc_ok or s.nho_loi)
        set_auto = s.lenh_auto and not s.lenh_stop and not s.huy_phep_chay
        s.cho_phep_auto = (s.cho_phep_auto or set_auto) and not s.huy_phep_chay
        s.tu_dong_chay = s.cho_phep_auto and s.trong_gio and not s.huy_phep_chay

        # NW12: một phép ghi pause. Đọc trạng thái cũ hai nhánh XOR rồi chốt.
        old_pause = s.tam_dung
        s.tam_dung = s.cho_phep_auto and (old_pause != s.lenh_stop)

        # NW13: chuẩn bị, chưa cập nhật bước hiện tại giữa các timer.
        s.buoc_tiep_theo = s.buoc_hien_tai
        if s.tu_dong_chay and s.buoc_hien_tai == 0:
            s.buoc_tiep_theo = 1

        # NW14–18: năm TONR riêng, reset ưu tiên hơn IN.
        for k in range(5):
            n = k + 1
            reset_timer = s.buoc_hien_tai != n or not s.tu_dong_chay
            inp = s.tu_dong_chay and s.buoc_hien_tai == n and not s.tam_dung
            if reset_timer:
                s.et[k] = 0
            elif inp:
                s.et[k] = min(10000, s.et[k] + self.dt)
            s.timer_q[k] = s.et[k] >= 10000
            if s.timer_q[k] and not s.tam_dung and s.tu_dong_chay:
                s.buoc_tiep_theo = n % 5 + 1

        # NW19: commit chỉ một lần, rồi ưu tiên xóa khi mất quyền theo lịch.
        if s.tu_dong_chay and not s.tam_dung:
            s.buoc_hien_tai = s.buoc_tiep_theo
        if not s.tu_dong_chay:
            s.buoc_hien_tai = 0
            s.buoc_tiep_theo = 0

        # NW20: van trước, bơm sau.
        enable = s.tu_dong_chay and not s.tam_dung
        n = s.buoc_hien_tai
        s.van = tuple(enable and lo <= n <= hi for lo, hi in ((1, 4), (2, 5), (3, 4), (4, 5)))
        s.bom = any(s.van) and enable and s.an_toan

        # NW21–22: lấy ET theo bước đã commit, ghi 0 khi không có bước hợp lệ.
        valid = 1 <= n <= 5
        elapsed = s.et[n - 1] if valid and s.tu_dong_chay else 0
        s.thoigianconlai = 10 - elapsed // 1000 if valid and s.tu_dong_chay else 0
        s.da_qua_vong_dau = True
        self.so_vong += 1
        return s

    def nhieu_vong(self, count=5, **changes):
        for _ in range(count):
            self.scan(**changes)
        return self.s

    def san_sang(self):
        self.nhieu_vong(6)
        assert self.s.da_nha_lenh
        assert not self.s.cho_phep_auto
        return self

    def nhan_nha(self, source, count=5):
        press = False if source == 'stop_day' and self.i.stop_nc else True
        release = not press
        self.nhieu_vong(count, **{source: press})
        self.nhieu_vong(count, **{source: release})
        return self.s


TESTS = []


def test(name):
    def deco(fn):
        TESTS.append((name, fn))
        return fn
    return deco


def off(s):
    assert not s.bom and not any(s.van)


@test('Khởi động giữ START thật: không nhận cạnh muộn do TON lọc nút')
def startup_held_physical():
    m = MoHinh(start_that=True)
    m.nhieu_vong(150)
    assert not m.s.da_nha_lenh and not m.s.cho_phep_auto
    off(m.s)
    m.nhieu_vong(10, start_that=False)
    assert m.s.da_nha_lenh
    m.nhan_nha('start_that')
    assert m.s.cho_phep_auto and m.s.bom


@test('Khởi động giữ AUTO HMI: phải nhả rồi nhấn mới được chạy')
def startup_held_hmi():
    m = MoHinh(auto_hmi=True)
    m.nhieu_vong(80)
    assert not m.s.da_nha_lenh and not m.s.cho_phep_auto
    m.nhieu_vong(10, auto_hmi=False)
    m.nhan_nha('auto_hmi')
    assert m.s.bom


@test('Khởi động giữ STOP/RESET/TẮT: chỉ mở nhận lệnh sau nhả đủ 30 ms')
def startup_other_commands():
    for source in ('stop_day', 'reset_that', 'stop_hmi', 'reset_hmi', 'tat_hmi'):
        m = MoHinh(**{source: True})
        m.nhieu_vong(20)
        assert not m.s.da_nha_lenh
        m.scan(**{source: False})
        m.scan()
        assert not m.s.da_nha_lenh
        m.scan()
        assert m.s.da_nha_lenh
        off(m.s)


@test('START thật chốt AUTO; nhả START không làm mất quyền chạy')
def start_latch():
    m = MoHinh().san_sang()
    m.nhan_nha('start_that')
    m.nhieu_vong(300)
    assert m.s.cho_phep_auto and m.s.bom
    assert m.s.buoc_hien_tai == 1


@test('Điều khiển chéo: START thật, STOP HMI, tiếp tục bằng STOP thật')
def cross_control():
    m = MoHinh().san_sang()
    m.nhan_nha('start_that')
    m.nhieu_vong(230)
    m.nhan_nha('stop_hmi')
    paused = (m.s.buoc_hien_tai, m.s.et[:], m.s.thoigianconlai)
    assert m.s.tam_dung and m.s.cho_phep_auto and m.s.tu_dong_chay
    off(m.s)
    m.nhieu_vong(2000)
    assert paused == (m.s.buoc_hien_tai, m.s.et[:], m.s.thoigianconlai)
    m.nhan_nha('stop_day')
    assert not m.s.tam_dung and m.s.bom
    assert m.s.buoc_hien_tai == paused[0]
    assert m.s.et[paused[0]-1] > paused[1][paused[0]-1]


@test('AUTO HMI, STOP thật, tiếp tục HMI; giữ nút không đảo pause nhiều lần')
def reversed_cross_control():
    m = MoHinh().san_sang()
    m.nhan_nha('auto_hmi')
    m.nhieu_vong(100, stop_day=True)
    assert m.s.tam_dung
    m.nhieu_vong(100)
    assert m.s.tam_dung
    m.nhieu_vong(10, stop_day=False)
    m.nhieu_vong(100, stop_hmi=True)
    assert not m.s.tam_dung


@test('Một nguồn giữ mức 1 không che cạnh nhấn từ nguồn còn lại')
def independent_sources():
    m = MoHinh().san_sang()
    m.nhieu_vong(5, auto_hmi=True)
    assert m.s.cho_phep_auto
    # HMI AUTO vẫn giữ, RESET thật hủy quyền; START thật phải được nhận riêng.
    m.nhan_nha('reset_that')
    assert not m.s.cho_phep_auto
    m.nhan_nha('start_that')
    assert m.s.cho_phep_auto
    # HMI STOP giữ 1; STOP thật vẫn có thể tiếp tục.
    m.nhieu_vong(10, stop_hmi=True)
    assert m.s.tam_dung
    m.nhan_nha('stop_day')
    assert not m.s.tam_dung


@test('Xung dội nút thật ngắn hơn 30 ms không tạo lệnh; lần nhấn ổn định chỉ một xung')
def bounce_filter():
    m = MoHinh().san_sang()
    for _ in range(15):
        m.nhieu_vong(2, start_that=True)
        m.scan(start_that=False)
    assert not m.s.cho_phep_auto
    m.nhan_nha('start_that')
    for _ in range(15):
        m.nhieu_vong(2, stop_day=True)
        m.scan(stop_day=False)
    assert not m.s.tam_dung
    m.nhieu_vong(20, stop_day=True)
    assert m.s.tam_dung
    for _ in range(12):
        m.scan(stop_day=False)
        m.scan(stop_day=True)
    assert m.s.tam_dung
    m.nhieu_vong(5, stop_day=False)
    m.nhan_nha('stop_day')
    assert not m.s.tam_dung


@test('Đang giữ STOP: glitch nhả ngắn hơn 30 ms không tạo lần nhấn mới')
def brief_release_glitches():
    m = MoHinh().san_sang()
    m.nhan_nha('start_that')
    m.nhieu_vong(5, stop_day=True)
    assert m.s.tam_dung and m.s.stop_on_dinh
    for _ in range(10):
        m.nhieu_vong(2, stop_day=False)
        assert m.s.stop_on_dinh
        m.nhieu_vong(5, stop_day=True)
        assert m.s.stop_on_dinh and m.s.tam_dung
    m.nhieu_vong(4, stop_day=False)
    assert not m.s.stop_on_dinh and m.s.tam_dung
    m.nhieu_vong(4, stop_day=True)
    assert m.s.stop_on_dinh and not m.s.tam_dung


@test('RESET đang giữ chặn START; nhả RESET rồi nhấn START mới chạy lại')
def reset_hold_restart():
    for source in ('reset_that', 'reset_hmi'):
        m = MoHinh().san_sang()
        m.nhan_nha('auto_hmi')
        m.nhan_nha('stop_hmi')
        m.nhieu_vong(10, **{source: True})
        assert not m.s.cho_phep_auto and not m.s.tam_dung
        assert m.s.buoc_hien_tai == 0 and m.s.thoigianconlai == 0
        m.nhan_nha('start_that')
        assert not m.s.cho_phep_auto
        m.nhieu_vong(10, **{source: False})
        off(m.s)
        m.nhan_nha('start_that')
        assert m.s.bom and m.s.buoc_hien_tai == 1


@test('Thiếu nước/quá tải/dừng khẩn: dừng và nhớ lỗi; RESET sau hết lỗi rồi START')
def fault_reset_restart():
    for changes, normal in [({'du_nuoc':False},{'du_nuoc':True}),
                            ({'qua_tai':True},{'qua_tai':False}),
                            ({'dung_khan':True},{'dung_khan':False})]:
        m = MoHinh().san_sang()
        m.nhan_nha('start_that')
        m.scan(**changes)
        assert m.s.den_loi and not m.s.cho_phep_auto and m.s.buoc_hien_tai == 0
        off(m.s)
        m.nhan_nha('reset_hmi')
        assert m.s.den_loi
        m.scan(**normal)
        assert m.s.den_loi
        m.nhan_nha('start_that')
        assert not m.s.cho_phep_auto
        m.nhan_nha('reset_hmi')
        assert not m.s.den_loi and not m.s.cho_phep_auto
        m.nhan_nha('start_that')
        assert m.s.bom


@test('Giữ RESET khi nguyên nhân hết: xóa nhớ lỗi theo mức, vẫn không tự khởi động')
def level_reset_policy():
    m = MoHinh().san_sang()
    m.nhan_nha('start_that')
    m.scan(qua_tai=True)
    m.nhieu_vong(5, reset_hmi=True)
    assert m.s.den_loi
    m.scan(qua_tai=False)
    assert not m.s.den_loi and not m.s.cho_phep_auto
    m.scan(reset_hmi=False)
    off(m.s)


@test('Lỗi RTC khi yêu cầu START chưa được cấp AUTO vẫn chốt cảnh báo')
def rtc_request_fault():
    m = MoHinh(ma_rtc=0x8080).san_sang()
    assert not m.s.den_loi
    m.nhan_nha('start_that')
    assert m.s.den_loi and not m.s.cho_phep_auto
    m.scan(ma_rtc=0)
    m.nhan_nha('reset_that')
    m.nhan_nha('start_that')
    assert m.s.bom
    m.scan(ma_rtc=1)
    assert m.s.rtc_ok and m.s.bom


@test('FirstScan xóa quyền AUTO/pause/bước kể cả khi gieo trạng thái cũ')
def first_scan_old_states():
    m = MoHinh(start_that=True, auto_hmi=True)
    m.s.cho_phep_auto = True
    m.s.tam_dung = True
    m.s.da_nha_lenh = True
    m.s.buoc_hien_tai = 4
    m.s.buoc_tiep_theo = 4
    m.s.et = [9000]*5
    m.scan()
    assert not m.s.da_nha_lenh and not m.s.cho_phep_auto and not m.s.tam_dung
    assert m.s.buoc_hien_tai == 0 and m.s.buoc_tiep_theo == 0
    assert m.s.et == [0]*5
    off(m.s)
    m.nhieu_vong(100)
    assert not m.s.cho_phep_auto


@test('STOP loại NC: nhả đọc 1, nhấn đọc 0, vẫn pause/tiếp tục đúng')
def stop_nc():
    m = MoHinh(stop_nc=True, stop_day=True).san_sang()
    m.nhan_nha('start_that')
    m.nhan_nha('stop_day')
    assert m.s.tam_dung
    m.nhan_nha('stop_day')
    assert not m.s.tam_dung and m.s.bom


@test('Hết ca khi pause: giữ AUTO/pause, xóa bước/ET; ca sau tiếp tục từ bước 1')
def schedule_pause():
    m = MoHinh(giay_trong_ngay=28799).san_sang()
    m.nhan_nha('start_that')
    m.nhieu_vong(200)
    m.nhan_nha('stop_hmi')
    m.scan(giay_trong_ngay=28800)
    assert m.s.cho_phep_auto and m.s.tam_dung and not m.s.tu_dong_chay
    assert m.s.buoc_hien_tai == 0 and m.s.et == [0]*5 and m.s.thoigianconlai == 0
    m.scan(giay_trong_ngay=61200)
    assert m.s.tu_dong_chay and m.s.tam_dung and m.s.buoc_hien_tai == 0
    assert m.s.thoigianconlai == 0
    off(m.s)
    m.nhan_nha('stop_day')
    assert m.s.buoc_hien_tai == 1 and m.s.bom


@test('Chọn AUTO ngoài ca: giữ quyền, chờ đúng giờ rồi bắt đầu bước 1')
def auto_outside_schedule():
    m = MoHinh(giay_trong_ngay=12*3600).san_sang()
    m.nhan_nha('start_that')
    assert m.s.cho_phep_auto and not m.s.tu_dong_chay
    assert m.s.buoc_hien_tai == 0 and m.s.thoigianconlai == 0
    off(m.s)
    m.scan(giay_trong_ngay=17*3600)
    assert m.s.tu_dong_chay and m.s.buoc_hien_tai == 1 and m.s.bom
    m.scan(giay_trong_ngay=20*3600+30*60)
    assert m.s.cho_phep_auto and not m.s.tu_dong_chay
    assert m.s.buoc_hien_tai == 0 and m.s.et == [0]*5
    off(m.s)


@test('Lịch ngày đủ 86.400 mốc giây: sáng 06–08, tối 17–20:30')
def schedule_all_seconds():
    for t in range(86400):
        m = MoHinh(giay_trong_ngay=t)
        m.scan()
        expected = (6*3600 <= t < 8*3600) or (17*3600 <= t < 20*3600+30*60)
        assert m.s.trong_gio == expected


@test('STOP và START được nhận cùng scan: STOP chặn việc cấp AUTO mới')
def simultaneous_start_stop():
    m = MoHinh().san_sang()
    m.scan(auto_hmi=True, stop_hmi=True)
    assert m.s.lenh_auto and m.s.lenh_stop and not m.s.cho_phep_auto
    off(m.s)
    # Hai nút thật có cùng bộ lọc và được nhấn đồng thời.
    m = MoHinh().san_sang()
    m.nhieu_vong(3, start_that=True, stop_day=True)
    assert m.s.lenh_auto and m.s.lenh_stop and not m.s.cho_phep_auto


@test('TẮT/RESET cùng START hoặc STOP: quyền hủy thắng, trạng thái về 0')
def cancel_priority():
    for cmd in ('tat_hmi', 'reset_hmi'):
        for active in (False, True):
            m = MoHinh().san_sang()
            if active:m.nhan_nha('start_that')
            m.scan(auto_hmi=True, stop_hmi=True, **{cmd:True})
            assert not m.s.cho_phep_auto and not m.s.tam_dung
            assert m.s.buoc_hien_tai == 0
            off(m.s)


@test('Hai nguồn STOP cùng scan chỉ đảo pause một lần')
def simultaneous_two_stops():
    m = MoHinh().san_sang()
    m.nhan_nha('start_that')
    m.nhieu_vong(2, stop_day=True)
    m.scan(stop_hmi=True)
    assert m.s.xung[2] and m.s.xung[3] and m.s.tam_dung
    m.nhieu_vong(50)
    assert m.s.tam_dung


@test('START khi đang pause không tự tiếp tục; phải nhấn STOP lần nữa')
def start_does_not_resume():
    m = MoHinh().san_sang()
    m.nhan_nha('start_that')
    m.nhan_nha('stop_hmi')
    m.nhan_nha('start_that')
    assert m.s.tam_dung
    off(m.s)
    m.nhan_nha('stop_hmi')
    assert not m.s.tam_dung and m.s.bom


@test('Năm bước và vòng lặp 50 giây: mẫu van đúng, bơm không mất lệnh khi chuyển')
def sequence_valves():
    m = MoHinh().san_sang()
    m.scan(auto_hmi=True)
    m.scan(auto_hmi=False)
    expected = {1:(1,0,0,0),2:(1,1,0,0),3:(1,1,1,0),4:(1,1,1,1),5:(0,1,0,1)}
    transitions=[];old=0
    for _ in range(5100):
        s=m.scan()
        assert tuple(map(int,s.van)) == expected[s.buoc_hien_tai]
        assert s.bom
        if s.buoc_hien_tai != old:
            transitions.append(s.buoc_hien_tai);old=s.buoc_hien_tai
    assert transitions[:6] == [1,2,3,4,5,1]


@test('STOP sát 10 s giữ bước, bỏ pause chỉ chuyển sang một bước kế tiếp')
def stop_near_boundary():
    m = MoHinh().san_sang()
    m.nhan_nha('auto_hmi')
    while m.s.et[0] < 9990:m.scan()
    m.scan(stop_hmi=True)
    assert m.s.buoc_hien_tai == 1 and m.s.et[0] == 9990 and m.s.tam_dung
    m.nhieu_vong(20, stop_hmi=False)
    m.scan(stop_hmi=True)
    assert m.s.buoc_hien_tai == 2 and not m.s.tam_dung
    assert m.s.thoigianconlai == 10


@test('30.000 scan ngẫu nhiên: ngõ ra, liên động và ưu tiên hủy luôn nhất quán')
def random_invariants():
    rng=random.Random(20261022)
    m=MoHinh().san_sang()
    for _ in range(30000):
        changes={}
        for name in ('start_that','stop_day','reset_that','auto_hmi','stop_hmi','reset_hmi','tat_hmi'):
            if rng.random()<.015:changes[name]=not getattr(m.i,name)
        if rng.random()<.005:changes['du_nuoc']=not m.i.du_nuoc
        if rng.random()<.005:changes['qua_tai']=not m.i.qua_tai
        if rng.random()<.005:changes['ma_rtc']=rng.choice((0,1,0x8080))
        if rng.random()<.005:changes['giay_trong_ngay']=rng.randrange(86400)
        s=m.scan(**changes)
        assert not s.cho_phep_auto or (s.an_toan and s.rtc_ok and not s.nho_loi and not s.reset_chuong_trinh and not m.i.tat_hmi)
        assert not s.tam_dung or s.cho_phep_auto
        assert s.bom == any(s.van)
        if s.tam_dung or not s.tu_dong_chay:off(s)
        if not s.tu_dong_chay:
            assert s.buoc_hien_tai == 0 and s.buoc_tiep_theo == 0 and s.et == [0]*5
        assert 0 <= s.thoigianconlai <= 10


def main():
    rows=[]
    for name,fn in TESTS:
        try:
            fn();rows.append({'ten':name,'ket_qua':'Đạt'})
        except Exception:
            rows.append({'ten':name,'ket_qua':'Lỗi','chi_tiet':traceback.format_exc()})
    passed=sum(r['ket_qua']=='Đạt' for r in rows)
    result={
        'mo_ta':'Mô hình Python rời rạc; chưa Compile, PLCSIM hoặc chạy PLC Siemens.',
        'dt_ms':10,
        'so_nhom_dat':passed,
        'so_nhom_loi':len(rows)-passed,
        'ket_qua':rows,
        'gioi_han':[
            'TON/TONR tích lũy theo dt giả định; không chứng minh thời gian thực hoặc sai số một vòng quét của CPU.',
            'Không kiểm tra dây điện, loại tiếp điểm thực, sự kiện HMI hay chất lượng truyền thông.',
            'Lọc cả cạnh nhấn/nhả 30 ms chỉ là giả định thiết kế cần đối chiếu tín hiệu thực và cấu hình bộ thực hành.',
            'RESET theo mức giữ chính sách V1644: lỗi hết trong khi RESET còn giữ sẽ xóa nhớ lỗi, nhưng AUTO vẫn bị khóa.',
        ],
    }
    target=Path(__file__).with_name('ket_qua_kiem_tra.json')
    target.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'dat':passed,'loi':len(rows)-passed,'tep':str(target)},ensure_ascii=False))
    for row in rows:
        if row['ket_qua']=='Lỗi':print(row['ten'],row['chi_tiet'])
    raise SystemExit(0 if passed==len(rows) else 1)


if __name__=='__main__':main()
