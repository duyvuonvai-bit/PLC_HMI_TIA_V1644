# Kiểm chứng logic rút gọn V1688

Nguồn: biểu thức chép từ ảnh của commit `aae862c01ddf4d1225ce9127cda915b7a7da8b55`. Chỉ tạo mô hình đối chiếu, **không sửa PLC/HMI và không chạy TIA Portal hoặc PLCSIM**.

Chạy lại:

```bash
python kiem_chung_logic.py
```

Kết quả máy đọc: [ket_qua_logic.json](ket_qua_logic.json).

## Kết quả đã thực hiện

| Phép kiểm tra | Số trường hợp đã xét | Kết quả trong mô hình |
|---|---:|---|
| Khởi tạo FirstScan với mọi tổ hợp trạng thái cũ G/Q/bộ nhớ cạnh/nhớ lỗi và mọi đầu vào Boolean | 16 × 32 = **512** | Không khác quan sát giữa phương án gốc và phương án bỏ G cùng hai tiếp điểm /HỦY ở NW8 |
| Duyệt đến điểm bất động toàn bộ đồ thị trạng thái có thể đạt tới sau FirstScan | **7 trạng thái, 224 chuyển trạng thái** | Không có chuyển trạng thái nào khác ở các biến quan sát |
| Hai tiếp điểm /HỦY của NW8, với SR ưu tiên R1 | **32** | Hai biểu thức tương đương |
| Tiếp điểm TỰ ĐỘNG CHẠY ở rung Q→MOVE của NW10–14 | **160** | Tương đương khi Q được đọc sau lời gọi timer có R ưu tiên |
| Tiếp điểm /hmi_stop ở rung bơm NW16 | **64** | Tương đương Boolean khi cùng giá trị STOP được dùng cho các rung van và bơm |
| Gom cùng điều kiện reset cho hai MOVE0 ở NW15 | **256** | Hai biến bước cho cùng kết quả |

Không gọi những kết quả trên là “PLCSIM Đạt”. Đây là duyệt trạng thái/biểu thức hữu hạn của một mô hình độc lập.

## Chứng minh bỏ ĐÃ GẠT TẮT có điều kiện

G là `ĐÃ GẠT TẮT`; Q là `CHO PHÉP AUTO`; A là `chon_auto_hmi`.

1. FirstScan xóa G/Q và có trong `HỦY PHÉP CHẠY`; SR.R1 giữ Q=0 dù tiếp điểm P phát xung.
2. Tiếp điểm P đứng đầu rung, cập nhật bộ nhớ cạnh ở mọi vòng quét.
3. Sau FirstScan, P(A)=1 đòi hỏi A của lần gọi P trước bằng0.
4. Khi A=0, NW7 đặt G=1 và HỦY=1; SR xóa Q, nên cuộn Q→R G phía sau không xóa G.
5. Vì thế, ở mọi cạnh lên hợp lệ sau FirstScan, G đã bằng1. Bỏ điều kiện G cùng ba cuộn ghi G không làm đổi các trạng thái quan sát trong mô hình này.

Đây là **logic có dùng nhưng có thể được bao phủ bởi cơ chế khác**, không phải biến không có tham chiếu. Không áp dụng kết luận bằng cách xóa riêng biến mà để lại toán hạng còn trỏ vào nó.

## Tình huống hiển thị được tái hiện

Trong ca, không có lỗi, giữ `hmi_stop=1` rồi đổi AUTO 0→1:

- `CHO PHÉP AUTO=1`, `TỰ ĐỘNG CHẠY=1`.
- NW9 đề nghị bước1 nhưng NW15 bị STOP chặn, nên bước hiện tại vẫn0.
- Timer đều reset, ET=0; bơm và bốn van OFF.
- NW18 cho `thoigianconlai=10`, vì chỉ ghi0 khi `TỰ ĐỘNG CHẠY=0`.

Trace hai vòng được lưu trong JSON. Kết quả này chứng minh khả năng hiển thị bước0/còn10giây từ biểu thức, không chứng minh người dùng đã gặp nó trên PLCSIM.

## Các giả định bắt buộc

- FirstScan thực sự hoạt động đúng và nằm trong HỦY; P luôn được xử lý, bộ nhớ cạnh không bị tác vụ khác sửa.
- Chương trình giữ thứ tự: tính HỦY → SR → TỰ ĐỘNG CHẠY; gọi timer → đọc Q; tính bốn Q van → bơm.
- Không có khối khác, HMI hoặc Force ghi đè bit quyền AUTO, timer hay Q van giữa các phép tính.
- **Mô hình giữ giá trị đầu vào HMI nhất quán trong một vòng quét.** Nó không mô phỏng thay đổi dữ liệu DB giữa các rung do truyền thông hoặc tác vụ khác.

Giả định cuối đặc biệt quan trọng với việc bỏ `/hmi_stop` ở rung bơm: nếu các rung van đã được tính với STOP=0 nhưng trước rung bơm STOP đổi thành1, tiếp điểm hiện có có thể tắt bơm ngay trong lượt đó. Bỏ nó và chỉ OR bốn Q cũ có thể chờ lượt sau. Do đó, khi chưa có snapshot đầu vào hoặc chưa bảo đảm tính nhất quán, **nên giữ tiếp điểm này**; lợi ích giảm một tiếp điểm rất nhỏ. Việc bỏ G cũng chỉ được chứng minh với các lần đọc A nhất quán như trên.

## Ngoài phạm vi

Không kiểm chứng thời gian thực của IEC TONR, sai số chu kỳ quét, cấu hình đồng hồ/FirstScan, Events và chất lượng kết nối HMI, dội nút, thời gian relay hoặc dây điện. Bài kiểm không cho phép kết luận hệ thống đã đủ điều kiện đưa bơm thật vào vận hành.
