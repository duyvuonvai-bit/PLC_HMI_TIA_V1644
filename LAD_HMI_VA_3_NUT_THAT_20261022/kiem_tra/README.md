# Kiểm tra mô hình nhận lệnh nút thật và HMI

Chạy bằng Python 3:

```text
python kiem_tra_nut_that_va_hmi.py
```

Script chỉ dùng thư viện chuẩn, mô phỏng vòng quét và ghi lại `ket_qua_kiem_tra.json` cạnh file mã. **Không kết nối PLC và không ghi dữ liệu ra thiết bị.**

Kết quả hiện tại: **25 nhóm đạt, 0 nhóm lỗi**. Ngoài các tình huống xác định, bộ kiểm tra duyệt 86.400 mốc giây của lịch ngày và 30.000 vòng quét với đầu vào thay đổi ngẫu nhiên có hạt giống cố định.

Các nhóm tình huống bao gồm:

- Giữ sẵn START, STOP hoặc lệnh HMI khi CPU khởi động; chỉ nhận lệnh sau khi đã nhả các lệnh ổn định 30 ms.
- Lọc cả cạnh nhấn và nhả của ba nút thật bằng hai TON 30 ms và một SR cho mỗi nút; glitch nhả dưới 30 ms không tạo thêm lần STOP.
- START thật và AUTO HMI đều giữ quyền AUTO sau khi nhả nút.
- Điều khiển chéo giữa HMI và nút thật; một nguồn giữ mức 1 không che cạnh nhấn từ nguồn còn lại.
- STOP tạm dừng, giữ bước/ET/giây, rồi tiếp tục; STOP sát thời điểm timer hoàn thành; hai nguồn STOP cùng một vòng quét chỉ đảo trạng thái một lần.
- RESET/TẮT ưu tiên hơn START; RESET xóa AUTO và pause để nhả RESET rồi nhấn START mới có thể chạy lại.
- Thiếu nước, quá tải, dừng khẩn, lỗi RTC, nhớ lỗi và xác nhận xóa lỗi.
- STOP loại NC, chọn AUTO ngoài ca, kết thúc ca trong khi pause và bắt đầu ca kế tiếp.
- Năm bước van, vòng lặp và bơm luôn có lệnh trong chu trình đang chạy.

## Hành vi thiết kế được kiểm tra

- `CHO PHÉP AUTO` là trạng thái AUTO chung do PLC giữ. HMI gửi lệnh nhấn, không ghi trực tiếp trạng thái này.
- START không phải nút tiếp tục khi đang pause; nhấn STOP lần nữa mới tiếp tục.
- Hết ca xóa bước và timer nhưng giữ AUTO; nếu đang pause thì pause cũng giữ cho đến khi bỏ pause hoặc bị RESET/TẮT/lỗi hủy AUTO.
- RESET giữ chính sách theo mức của V1644: nếu nguyên nhân lỗi hết trong lúc vẫn giữ RESET thì nhớ lỗi được xóa; AUTO vẫn bị khóa trong thời gian RESET còn hiệu lực.
- Tham số `stop_nc` phải tương ứng tiếp điểm thực và được đặt ở giá trị khởi tạo/cấu hình. Không xem một lần Modify online là cấu hình chắc chắn còn đúng sau khi PLC khởi động lại.

## Giới hạn

Đây là **mô hình logic rời rạc bằng Python**, chưa Compile trong TIA Portal, chưa chạy PLCSIM hoặc CPU Siemens. TON/TONR tích lũy theo bước giả định 10 ms; kết quả không chứng minh thời gian thực hay sai số một vòng quét của IEC timer trên CPU.

Các phép thử không xác nhận được dây điện, NO/NC thực tế, cấu hình bộ lọc DI, Events của HMI hoặc chất lượng truyền thông. Cần đối chiếu bản vẽ đã dựng, Compile PLC/HMI và thử lại trên PLCSIM/thiết bị trước khi dùng.

Sáu đèn là tải mô phỏng. STOP dạng nhấn lần hai để tiếp tục là lệnh vận hành, không phải chức năng dừng khẩn phần cứng.
