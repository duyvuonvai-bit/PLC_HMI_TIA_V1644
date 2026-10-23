# Kiểm tra bản LAD rút gọn ngày 24/10/2026

Chạy bằng Python 3, không cần thư viện bổ sung:

```text
python kiem_tra_ban_rut_gon.py
```

Hai file `.py` cần nằm cùng thư mục. Script chỉ mô phỏng logic trong bộ nhớ và ghi `ket_qua_rut_gon.json`; không kết nối hoặc ghi ra PLC.

Kết quả đã chạy:

- **25/25 nhóm tình huống cũ đạt** khi thay mô hình bằng bản rút gọn.
- **7/7 nhóm đối chiếu đạt**, so sánh toàn bộ trạng thái sau từng vòng quét giữa bản ngày 22/10 và bản rút gọn.
- **100.138 vòng quét đối chiếu, không phát hiện sai khác**, gồm 80.000 vòng quét ngẫu nhiên với hạt giống cố định cho cả STOP NO và STOP NC.

Các nhóm tình huống cũ có kiểm tra lịch tại 86.400 mốc giây trong ngày và 30.000 vòng quét ngẫu nhiên kiểm tra các điều kiện bất biến. Những con số này nằm trong 25 nhóm tình huống; không cộng chúng vào số vòng quét đối chiếu hai phiên bản.

## Nội dung rút gọn được mô hình hóa

1. NW3 cấp trực tiếp chuỗi điều kiện nhả lệnh vào TON `cho_nha_lenh`, và đọc trực tiếp `cho_nha_lenh.Q` vào SR `da_nha_lenh`. Không cần hai biến trung gian `tat_ca_lenh_da_nha`, `nha_lenh_on_dinh`.
2. NW4 bắt cạnh riêng từng nguồn bằng bốn bộ nhớ P, ghép hai nhánh rồi mới qua `da_nha_lenh` để ghi `lenh_auto` hoặc `lenh_stop`. Không cần bốn biến xung trung gian trong DB.
3. NW9 bỏ `/LỖI HIỆN TẠI` khi đã có `AN TOÀN` và `RTC OK`.
4. NW11 bỏ `/HỦY PHÉP CHẠY` lặp ở chân S và nhánh `TỰ ĐỘNG CHẠY`; SR vẫn ưu tiên reset và R1 vẫn nhận đầy đủ điều kiện hủy.
5. NW14–18 bỏ `TỰ ĐỘNG CHẠY` ở nhánh Q→MOVE; chân R timer giữ nguyên và timer được gọi trước khi đọc Q.
6. NW20 tính bốn van trước rồi OR bốn ngõ ra để điều khiển bơm; bỏ các tiếp điểm liên động lặp ở nhánh bơm.
7. NW21 và nhánh ghi 0 NW22 không lặp `TỰ ĐỘNG CHẠY`, vì NW19 đã xóa bước khi mất quyền chạy.

Năm bản sao ET và năm TONR được giữ nguyên. Mô hình không đề xuất đổi thuật toán thời gian hoặc tự gộp các thao tác STOP ở hai vòng quét khác nhau.

## Điều kiện của phép tương đương

- Giữ đúng thứ tự network như tài liệu, chỉ một nơi quản lý từng trạng thái chung, không có OB khác hoặc thao tác force ghi đè các biến giữa chừng.
- P trong hình là **tiếp điểm bắt cạnh toán hạng**, mỗi nguồn có bộ nhớ riêng và đặt ở đầu nhánh. Cả bốn bộ nhớ được cập nhật mỗi scan; điều kiện `da_nha_lenh` nằm sau điểm ghép nhánh.
- Không thay bốn P bằng một P sau khi OR hai tín hiệu thô. Làm vậy sẽ che cạnh của nguồn thứ hai khi nguồn thứ nhất đang giữ.
- Không thay tùy ý bằng các khối bắt cạnh bị gọi có điều kiện. Trong Python, phải tính mọi edge trước khi OR, tránh toán tử OR ngắn mạch bỏ qua cập nhật bộ nhớ của nhánh thứ hai.

Trường `s.xung` trong mô hình chỉ lưu dấu vết để tái sử dụng phép thử cũ và đối chiếu kết quả. Nó **không có nghĩa phải khai báo lại bốn biến xung đã bỏ trong DB PLC**.

## Giới hạn

Đây là kiểm tra **mô hình logic rời rạc**, không phải Compile TIA, PLCSIM hoặc chạy CPU Siemens. TON/TONR tích lũy theo bước giả định 10 ms; phép đối chiếu không xác nhận sai số thực tế, chi tiết cập nhật IEC timer trên CPU, việc gọi lệnh LAD do trình biên dịch tạo ra, Events HMI hoặc đấu dây.

Cần nhập LAD theo hình, Compile cả PLC/HMI và thử các thao tác chéo, giữ nút, RESET, lỗi bảo vệ và mốc kết thúc ca trên PLCSIM/bộ thực hành. STOP nhấn lần hai để tiếp tục là lệnh vận hành của mô hình sáu đèn, không thay dừng khẩn phần cứng.
