# Rà soát HMI — PLC_HMI_TIA_V1644

Nguồn: commit `dffa0dd`; đọc trực tiếp ảnh `020453` (Tổng quan), `020457` (Điều khiển và giả lập đầu vào), `020503` (Cảnh báo), `020425`/`020430` (bảng biến HMI), đối chiếu NW5–6 trong `020554`/`020557`. Ảnh mang ngày 22/10/2026. Kho không có Events, Animation, Connections hoặc bản project nên không kết luận hành vi động chưa quan sát.

## Kết luận

Cấu trúc ba màn hình vẫn phù hợp mô hình sáu đèn. Bản mới đã gọn hơn ở phần đồng hồ, nhưng cần xác minh trạng thái kết nối và liên kết các đèn cảnh báo. Không cần dựng lại toàn bộ giao diện.

## Những gì đã sửa và còn tồn tại so với V1611

| Nội dung | Kết quả ở V1644 |
|---|---|
| Hai đồng hồ lặp tại hai ca | Đã gộp thành một đồng hồ ở đầu trang Tổng quan. |
| Biến lịch chung | Có thêm `HMI_TRONG_GIO` liên kết DB `TRONG GIỜ`; phù hợp hiển thị trạng thái trong/ngoài ca. |
| Giờ 24 h | Chưa thể hiện: đang dùng `12:00:00 AM`, tức 00:00:00. |
| Hai biến nguồn nước | Vẫn có `HMI_DU_NUOC` đọc DB `hmi_du_nuoc` và `HMI_DUNUOC` đọc PLC tag vật lý `ĐỦ NƯỚC`. |
| Nút STOP/tiếp tục | Ảnh vẫn chỉ thấy nhãn STOP. Chưa có ảnh lúc tạm dừng để xác nhận nhãn động. |
| Biến `HMI_STOP_NHAN` | Vẫn là Internal tag; không có bằng chứng đủ để kết luận không dùng. |
| Trạng thái PLC ONLINE | Vẫn có khung xanh nhưng chưa thấy nguồn trạng thái hoặc Events/Animation. |
| Hiển thị chờ xác nhận lỗi | Chưa thấy dòng giải thích “lỗi đã hết — chờ RESET”. |

## 1. Cần kiểm tra sự nhất quán trạng thái trước

Các ảnh chụp Runtime gần nhau thể hiện:

- Tổng quan `020453`: `PLC ONLINE` xanh; giờ `12:00:00 AM`; đèn đủ nước xám; `KHÔNG LỖI` xanh; bước 0, toàn bộ tải OFF.
- Cài đặt `020457`: công tắc đang `THIẾU NƯỚC`.
- Cảnh báo `020503`: `THIẾU NƯỚC` đỏ và `LỖI RTC` đỏ.

Đây là **tổ hợp hiển thị cần đối chiếu**, chưa đủ khẳng định LAD lỗi. Có thể Runtime đang chưa kết nối/giá trị khởi tạo, PLC chưa RUN, giá trị bị giữ cũ, ảnh ở các thời điểm khác nhau hoặc liên kết đối tượng khác nguồn. Chỉ riêng banner xanh không chứng minh PLC đang trao đổi dữ liệu.

NW6 trong `020557` đưa đầu Q của khối SR nhớ lỗi ra `Q0.5 ĐÈN BÁO LỖI`; `HMI_LOI` trong `020425` đang liên kết đúng tag Q đó. Do đó nên xem cùng lúc tại PLC: `AN TOÀN`, `RTC OK`, `LỖI HIỆN TẠI`, `NHỚ LỖI`, `Q0.5` và `HMI_LOI`. Nếu PLC thật sự RUN và lỗi đã được đặt, màn tổng quan phải phản ánh cùng trạng thái với trang Cảnh báo.

Bổ sung phép thử ngắt kết nối. Khi mất dữ liệu, banner phải báo mất kết nối/không cập nhật; không tiếp tục để mọi ô trông như thông tin bình thường. Nếu dùng heartbeat, timeout chỉ xác nhận mất cập nhật và có thể do PLC STOP hoặc mất liên lạc, không khẳng định riêng đứt cáp.

## 2. Nguồn nước phải thống nhất

Hai tag vẫn tồn tại:

- `HMI_DU_NUOC` → DB `daiphunnuoc.hmi_du_nuoc`.
- `HMI_DUNUOC` → PLC tag `ĐỦ NƯỚC`.

Với mô hình đầu vào giả lập, công tắc, đèn Tổng quan, dòng Cảnh báo và LAD phải cùng dùng tín hiệu giả lập được chọn. Ảnh chưa cho biết các đối tượng đang liên kết tag nào, nên chưa xác nhận đã mắc lỗi này. Khi chuyển sang thiết bị thật, cũng phải chọn rõ nguồn đầu vào; không đọc một nguồn để quyết định chạy nhưng hiển thị nguồn kia.

Không xóa `HMI_DUNUOC` hoặc `HMI_STOP_NHAN` chỉ vì LAD không có tên đó. Dùng Cross-references HMI kiểm tra cả đối tượng, Animation và Events trước.

## 3. Ô lịch đang lặp nội dung và thiếu mốc giờ dễ đọc

Ảnh Tổng quan hiện có hai dòng `NGOÀI CA` trong cùng khung. Nên phân công mỗi dòng một ý:

- `LỊCH: 06:00–08:00 / 17:00–20:30` là dòng cố định.
- `TRẠNG THÁI: CA SÁNG / CA TỐI / NGOÀI CA` là dòng động.

Giữ một đồng hồ trên đầu trang, đổi sang `HH:mm:ss`, có nhãn `GIỜ PLC`. Khi `RTC OK = 0` hoặc mất cập nhật, hiển thị `--:--:--`/`CHƯA ĐỌC ĐƯỢC GIỜ` và trạng thái lịch `CHƯA XÁC ĐỊNH`; đừng dùng 00:00 hoặc NGOÀI CA để thay cho dữ liệu chưa hợp lệ.

`HMI_GIO_PLC` đã có nguồn DTL là DB `GIỜ PLC`, nhưng vẫn phải xác nhận đối tượng thời gian dùng đúng tag này, không phải giờ máy tính hoặc giá trị mặc định. `RTC OK` nghĩa là lệnh đọc giờ thành công theo mã trạng thái; không tự phát hiện đồng hồ đặt sai giờ hoặc sai múi giờ.

## 4. STOP và RESET

Màn `020457` gọn, công tắc và nút có chữ nên dễ thao tác. Nếu STOP đảo trạng thái để tạm dừng/tiếp tục, hãy đổi chữ theo bit PLC: `TẠM DỪNG` khi chưa dừng; `TIẾP TỤC` khi đã dừng. Có thể thêm `ĐANG TẠM DỪNG` trên Tổng quan. Ảnh một thời điểm không cho biết nút hiện tại đã có Animation hay chưa.

Không giữ nhận xét RESET của V1611: NW5 mới trong `020554` không còn các tiếp điểm STOP/AUTO như bản cũ. Cần bám điều kiện mới: yêu cầu reset, trạng thái chốt reset, AN TOÀN, RTC OK và không còn LỖI HIỆN TẠI. Nếu cần, HMI hiển thị “Khắc phục nguyên nhân rồi RESET”; PLC vẫn quyết định việc chấp nhận, không chỉ khóa nút trên giao diện.

Ảnh không đủ xác nhận kiểu Press/Release, InvertBit hoặc cách nhả bit reset. Cần kiểm tra Events để tránh đảo bit ở cả Press và Release hoặc giữ reset mãi bằng 1.

## 5. Cảnh báo hiện tại và lỗi còn nhớ

Trang `020503` phân màu và nhãn rõ: thiếu nước và RTC đỏ, quá tải và dừng khẩn bình thường xanh. Đây là bảng nguyên nhân hiện thời, chưa phải nhật ký cảnh báo.

Vì PLC có nhớ lỗi, cần thể hiện thêm trường hợp các nguyên nhân đã bình thường nhưng `NHỚ LỖI` vẫn còn: `LỖI ĐÃ HẾT — CHỜ RESET`. Có thể dùng một dòng trạng thái chung thay vì thêm nhiều đèn.

Trên Tổng quan, chữ `KHÔNG LỖI` cố định với đèn đổi màu dễ gây lúng túng khi đèn đỏ; dùng text list `KHÔNG LỖI / CÓ LỖI / CHỜ RESET` rõ hơn. Nếu tag đang không cập nhật thì báo `MẤT DỮ LIỆU` trước, tránh báo bình thường từ giá trị 0 mặc định.

## Thử nhanh để chốt HMI

1. Chạy PLC và đưa đủ nước, không quá tải, không dừng khẩn: đối chiếu tất cả đèn/trạng thái với watch table.
2. Chuyển thiếu nước: Cảnh báo đỏ, `Q0.5`/`HMI_LOI` đúng, Tổng quan phản ánh cùng lỗi; bơm/van OFF.
3. Khôi phục nước: xác nhận trạng thái chờ RESET nếu nhớ lỗi vẫn còn; RESET phải được nhận theo điều kiện mới.
4. Thử STOP lần một và lần hai; chữ trạng thái phải diễn đạt đúng dừng/tiếp tục.
5. Đặt các mốc 07:00, 08:00, 17:00, 20:30; đối chiếu lịch và giờ PLC.
6. Ngắt kết nối: không giữ banner PLC ONLINE xanh và không coi 00:00 là giờ thực.
