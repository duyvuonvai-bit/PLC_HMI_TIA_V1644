# Kiểm tra mô hình logic V1644 và bản 17 Network

Kết quả: **17 nhóm đạt, 0 nhóm lỗi**. Nguồn đối chiếu: commit `dffa0dd`.

Đây là mô hình vòng quét rời rạc bằng Python, không phải chạy TIA Portal, PLCSIM hoặc CPU Siemens. Timer tích lũy theo dt giả định; chưa xác nhận thời gian thực, độ trễ phần cứng hoặc Events HMI.

Phần điều khiển của hai bản được so sánh giữ cùng kết quả. Hiển thị giây còn lại được sửa có chủ ý: khi chưa có bước 1–5, bản mới hiện 0 thay vì 10; STOP tại bước hợp lệ vẫn giữ thời gian.

| Nhóm kiểm tra | Kết quả |
|---|---|
| Hai ca và toàn bộ mốc giây trong ngày | Đạt |
| Giải mã van và bơm, kể cả bước ngoài 1–5 | Đạt |
| Chu trình năm bước, bơm không mất lệnh khi chuyển bước | Đạt |
| STOP giữ bước/ET/giây rồi tiếp tục | Đạt |
| STOP sát thời điểm timer hoàn thành | Đạt |
| TẮT trong lúc STOP | Đạt |
| Hiển thị bước 0 khi bật AUTO lúc STOP đang giữ | Đạt |
| Thiếu nước | Đạt |
| Quá tải | Đạt |
| Dừng khẩn | Đạt |
| Lỗi đọc RTC | Đạt |
| RESET giữa lúc đang chạy và giữ nút RESET | Đạt |
| Hết ca và vào ca tiếp theo | Đạt |
| STOP kéo dài qua thời điểm hết ca | Đạt |
| Khóa khởi động khi AUTO đang bật | Đạt |
| Ngõ ra khi bước bị ghi giá trị bất thường | Đạt |
| So sánh V1644 và bản 17 qua chuỗi tín hiệu thay đổi | Đạt |

Đã kiểm tra 86.400 mốc giây trong ngày; 88 tổ hợp giải mã bước/ngõ ra; 30.000 vòng quét đối chiếu với tín hiệu thay đổi và các tình huống vận hành đặt trước.

[Mã kiểm tra](kiem_tra/validate_v1644.py) · [Kết quả chi tiết](kiem_tra/ket_qua_mo_hinh.json)

Chạy lại bằng Python 3: `python kiem_tra/validate_v1644.py`. Script chỉ mô phỏng và ghi kết quả JSON, không kết nối hay điều khiển PLC.

Trước khi nạp chương trình thật vẫn cần Compile cả PLC/HMI, kiểm tra Cross-references, chạy thử các biên thời gian và sự kiện nút trong môi trường Siemens.
