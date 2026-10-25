# Đánh giá chương trình đài phun nước V1688

Ngày đánh giá: **25/10/2026**. Nguồn: [PLC_HMI_TIA_V1688](https://github.com/duyvuonvai-bit/PLC_HMI_TIA_V1688/tree/aae862c01ddf4d1225ce9127cda915b7a7da8b55), commit `aae862c01ddf4d1225ce9127cda915b7a7da8b55`.

## 1. Kết luận và phạm vi

**Bản này có cấu trúc điều khiển hợp lý cho mô hình PLC/HMI điều khiển sáu đèn. Chưa tìm thấy lỗi xác định làm sai lịch chạy, sai bảng van, nhảy nhiều bước trong một vòng quét hoặc làm RESET vượt qua điều kiện bảo vệ.** Không cần viết lại toàn bộ chương trình.

Các điểm cần xử lý chủ yếu là: phân biệt AUTO được chọn với đang trong ca, hiển thị thời gian khi bước còn 0, giải thích trạng thái lỗi đã hết nhưng chưa RESET, và làm rõ rằng sáu đầu vào vật lý hiện chưa tham gia chương trình. Có thể rút bảy tiếp điểm lặp và gộp hai nhánh reset mà vẫn giữ thứ tự quét. Việc bỏ cơ chế nhớ ĐÃ GẠT TẮT chỉ được chứng minh khi đầu vào HMI nhất quán theo scan, nên chưa khuyến nghị bỏ ngay trong bản hiện tại.

Đã đọc đủ 18 Network, 13 PLC tags, 29 trường DB, 21 HMI tags và ba màn Runtime trong 27 ảnh. Đã đối chiếu lịch và bảng van với phiếu giao đề tài. Chấp nhận các xác nhận của người dùng: **không dùng OB100, khởi tạo trực tiếp bằng FirstScan; Events HMI đã cấu hình đúng; ảnh các Network đã đủ**. Không coi các xác nhận này là lỗi hoặc yêu cầu gửi lại.

Đây là đánh giá từ ảnh và kiểm chứng logic độc lập, không phải kết quả Compile/Cross-references trực tiếp trong TIA hoặc nghiệm thu trên PLC thật. Người dùng đã chạy được các tình huống của mình; điều đó được ghi nhận, nhưng không dùng để gán kết quả “Đạt” cho những tình huống chưa cung cấp kết quả. **Không thay đổi code, tag, Events hoặc project PLC/HMI.**

## 2. Cấu trúc và hành vi thực tế

| Nhóm | Network | Nhiệm vụ |
|---|---|---|
| Khởi tạo, thời gian | 1–3 | Khởi tạo khi vào RUN; đọc giờ địa phương; xác định hai ca |
| Bảo vệ và lỗi | 4–6 | Tính an toàn; xử lý RESET; ghi nhớ lỗi và xuất đèn lỗi |
| Quyền AUTO | 7–8 | Nhận cạnh bật AUTO, hủy quyền chạy khi không đủ điều kiện |
| Chu trình | 9–15 | Chuẩn bị bước; gọi năm TONR; chốt bước sau các timer |
| Ngõ ra | 16 | Tính bốn van rồi tính bơm từ các lệnh van |
| Hiển thị thời gian | 17–18 | Chọn ET theo bước; tính số giây còn lại |

Lịch đúng theo đề: **06:00 ≤ giờ < 08:00** hoặc **17:00 ≤ giờ < 20:30**. Riêng 20:00–20:29 được xét bằng HOUR = 20 và MINUTE < 30. Giờ 20:00 vẫn thuộc ca; 20:30 không còn thuộc ca.

| Bước | Thời gian đặt | Van 1 | Van 2 | Van 3 | Van 4 | Lệnh bơm |
|---|---|---|---|---|---|---|
| 1 | 10 s | Mở | Đóng | Đóng | Đóng | ON |
| 2 | 10 s | Mở | Mở | Đóng | Đóng | ON |
| 3 | 10 s | Mở | Mở | Mở | Đóng | ON |
| 4 | 10 s | Mở | Mở | Mở | Mở | ON |
| 5 | 10 s | Đóng | Mở | Đóng | Mở | ON |

Hết bước 5 quay lại bước 1. Năm timer là **TONR**, không phải TON thường. TONR có công dụng giữ thời gian khi tạm dừng.

### 2.1. AUTO, STOP và RESET của chính V1688

| Thao tác/trạng thái | Kết quả theo code hiện tại |
|---|---|
| AUTO 0→1, an toàn, RTC tốt, không còn nhớ lỗi | Cấp CHO PHÉP AUTO; trong ca thì chạy, ngoài ca thì chờ |
| AUTO = 0 | Hủy AUTO; bước và timer về 0; bơm/van OFF |
| hmi_stop = 1 khi đang chạy trong ca | Bơm/van OFF; giữ bước và ET của bước hiện tại |
| hmi_stop trở về 0 | Tiếp tục phần thời gian còn lại nếu vẫn đủ điều kiện |
| Hết ca | Bước và timer về 0; giữ quyền AUTO để chờ ca sau; không tự xóa hmi_stop |
| RESET | Hủy AUTO, xóa bước/timer; chỉ xóa nhớ lỗi nếu an toàn và RTC hợp lệ |
| Giữ RESET | Tiếp tục khóa quyền chạy; không khởi động được bằng AUTO trong lúc giữ |
| Lỗi đã hết, RESET hợp lệ rồi nhả RESET | Chưa tự chạy; phải đưa AUTO về TẮT rồi bật lại để tạo cạnh mới |
| STOP đang 1, sau đó RESET hoặc TẮT | hmi_stop vẫn theo giá trị HMI; nếu vẫn 1 thì lần AUTO tiếp theo vẫn bị tạm dừng |

**Trong PLC không có bộ đảo trạng thái STOP.** Nó chỉ đọc mức `hmi_stop`. Nếu HMI cho thao tác nhấn lần một dừng/lần hai tiếp tục, việc đổi bit đó do Events HMI thực hiện. Không áp cách hoạt động của bản 22 Network trước vào bản này.

`chon_auto_hmi` là lựa chọn duy trì: nó phải còn 1 để AUTO tiếp tục được phép. `CHO PHÉP AUTO` là quyền đã được chấp nhận; `TỰ ĐỘNG CHẠY` còn phụ thuộc lịch. Khi STOP = 1, `TỰ ĐỘNG CHẠY` có thể vẫn 1, trong khi ngõ ra đã OFF. Ba ý nghĩa này không nên gộp thành một đèn “đang chạy”.

Với Start value trong ảnh, `hmi_du_nuoc=false`. Nếu PLC khởi tạo theo giá trị này và HMI chưa ghi đủ nước, NW4/NW6 sẽ bật nhớ lỗi và đèn Q0.5; bơm và bốn van vẫn OFF. Đây là báo thiếu nước ban đầu, không phải lỗi FirstScan. Sau khi đặt các điều kiện giả lập bình thường, cần RESET hợp lệ rồi mới xin AUTO.

### 2.2. Thứ tự quét và thời gian

NW9 chỉ chuẩn bị BƯỚC TIẾP THEO. NW10–14 vẫn cùng xét BƯỚC HIỆN TẠI trước khi NW15 chốt bước. Vì vậy một timer chuyển bước không làm timer kế tiếp chạy ngay theo bước mới trong cùng scan. Đây là cấu trúc nên giữ.

Timer của bước mới bắt đầu nhận IN = 1 ở lần gọi trong vòng quét tiếp theo. Thời gian lệnh van có lượng tử theo chu kỳ quét và cách cập nhật timer; không nên cam kết đúng tuyệt đối 10.000 ms chỉ từ ảnh. Không thấy cơ chế gây mất hoặc cộng sai hàng giây trong chu trình bình thường. NW15 chốt bước mới trước NW17–18 nên giá trị đếm có thể chuyển thẳng sang10 giây của bước mới, không bắt buộc xuất hiện0 ở ranh giới bước. Chu kỳ làm tươi HMI còn có thể bỏ qua các trạng thái ngắn; nên dùng Trace/ghi mẫu khi kiểm thử.

## 3. Đánh giá từng Network

“Không phát hiện lỗi” dưới đây nghĩa là chưa thấy lỗi từ tài liệu đã đọc; không phải chứng nhận đã thử mọi trường hợp.

| NW | Chức năng | Kết quả kiểm tra | Lỗi hoặc nguy cơ | Mức độ | Hướng xử lý |
|---|---|---|---|---|---|
| 1 | Khởi tạo bằng FirstScan | Reset quyền AUTO, cờ đã tắt và hai biến bước; NW7–16 tiếp tục đưa timer/ngõ ra về trạng thái dừng | Chưa thấy lỗi; không cần thêm OB100 | Không phát hiện lỗi | Giữ FirstScan và hiện giữ cờ ĐÃ GẠT TẮT; kiểm tra STOP→RUN/mất điện; chỉ cân nhắc rút cờ theo điều kiện mục 5 |
| 2 | Đọc RD_LOC_T | Gọi mỗi scan; RTC OK nhận RET_VAL = 0 hoặc 1 | RTC OK không xác nhận giờ/múi giờ đã được cài chính xác | Không phát hiện lỗi; giới hạn chức năng | Giữ; thử mã lỗi và đối chiếu giờ CPU |
| 3 | Tính ca sáng, ca tối, trong giờ | Đúng hai khoảng; không hở tại 20:00 | Chưa thấy lỗi điều kiện biên | Không phát hiện lỗi | Giữ và thử các mốc 06:00, 08:00, 17:00, 20:00, 20:30 |
| 4 | An toàn và lỗi hiện tại | Đủ nước, không quá tải, không dừng khẩn; lỗi RTC gắn với lựa chọn AUTO | Chỉ đọc DB HMI, không đọc cảm biến vật lý | Phù hợp sáu đèn; nghiêm trọng nếu dùng làm bảo vệ bơm thật mà không tích hợp I/O | Giữ cho giả lập; tích hợp nguồn tín hiệu thật khi chuyển mục tiêu |
| 5 | RESET, xác nhận xóa lỗi | RESET giữ mức; xóa lỗi chỉ khi an toàn và RTC OK | RESET vẫn dừng chương trình dù lỗi chưa được xóa; đây là chủ đích hợp lý | Không phát hiện lỗi | Giữ; hướng dẫn rõ RESET không đồng nghĩa tự khởi động lại |
| 6 | SR nhớ lỗi, Q0.5 | SR có chân R1 ưu tiên reset; lỗi được giữ sau khi nguyên nhân hết | Một bit tổng không lưu được nguyên nhân cũ | Không phát hiện lỗi điều khiển; hạn chế chẩn đoán | Giữ SR; HMI nên báo “cần RESET” sau khi nguyên nhân hết |
| 7 | Cờ đã tắt, điều kiện hủy | Hủy khi AUTO OFF, mất an toàn, RTC lỗi, nhớ lỗi, RESET hoặc FirstScan | ĐÃ GẠT TẮT có thể được bao phủ khi các lần đọc AUTO nhất quán | Nhẹ: tối ưu có điều kiện | Giữ HỦY PHÉP CHẠY; hiện nên giữ cờ vì lợi ích bỏ một Bool nhỏ |
| 8 | Cấp AUTO, tính quyền chạy trong ca | Cạnh lên nằm đầu rung; SR reset ưu tiên; không tự tái cấp khi AUTO giữ 1 sau lỗi/RESET | Hai tiếp điểm /HỦY PHÉP CHẠY bị lặp; không được xóa bộ nhớ P | Nhẹ: tối ưu | Xem mục 5; đèn AUTO nên phân biệt quyền AUTO với chạy trong ca |
| 9 | Chuẩn bị bước tiếp theo | Sao chép bước trước, đề nghị bước 1 khi bước 0 | Không tự sửa bước ngoài 0–5; chỉ là tình huống ghi trạng thái bất thường | Trung bình khi xảy ra trạng thái ngoài miền | Giữ hai biến bước; cân nhắc nhánh chặn/báo bước không hợp lệ |
| 10 | Timer bước 1; đề nghị bước 2 | TONR 10 s; R khi khác bước hoặc không được chạy | Tiếp điểm TỰ ĐỘNG CHẠY ở rung Q→MOVE có thể rút | Không phát hiện lỗi; tối ưu nhẹ | Giữ IN/R và thứ tự gọi timer trước đọc Q |
| 11 | Timer bước 2; đề nghị bước 3 | Như NW10, đúng bước đích | Cùng phần lặp trên rung Q→MOVE | Không phát hiện lỗi; tối ưu nhẹ | Như NW10 |
| 12 | Timer bước 3; đề nghị bước 4 | Như NW10, đúng bước đích | Cùng phần lặp trên rung Q→MOVE | Không phát hiện lỗi; tối ưu nhẹ | Như NW10 |
| 13 | Timer bước 4; đề nghị bước 5 | Như NW10, đúng bước đích | Cùng phần lặp trên rung Q→MOVE | Không phát hiện lỗi; tối ưu nhẹ | Như NW10 |
| 14 | Timer bước 5; quay bước 1 | Vòng lặp đúng, không đề nghị bước 6 | Cùng phần lặp trên rung Q→MOVE | Không phát hiện lỗi; tối ưu nhẹ | Như NW10 |
| 15 | Chốt hoặc xóa bước | Commit sau cả năm timer; hai điều kiện ghi bước loại trừ nhau | Hai rung reset dùng cùng điều kiện /TỰ ĐỘNG CHẠY | Nhẹ: tổ chức | Có thể dùng chung điều kiện cho hai MOVE, vẫn reset cả hai biến |
| 16 | Bốn van và bơm | Đúng bảng van; tính các Q van trước bơm | /hmi_stop riêng rung bơm chỉ lặp nếu STOP không đổi giữa các rung; Q không chứng minh van thực đã mở | Giới hạn phần cứng; tối ưu có điều kiện | Nên giữ tiếp điểm STOP riêng của bơm trong bản hiện tại |
| 17 | Chọn ET của bước | Mặc định 0 rồi chọn một ET theo bước; không giữ ET cũ khi bước 0 | Không có lỗi xác định | Không phát hiện lỗi | Giữ MOVE mặc định và đọc ET trực tiếp |
| 18 | Tính giây còn lại | Chia nguyên phù hợp hiển thị; không tràn Int trong ET hợp lệ | TỰ ĐỘNG CHẠY=1, bước=0 vì STOP giữ thì hiển thị 10 s; tương tự bước ngoài miền | Nhẹ: hiển thị | Chỉ hiển thị đếm bước khi 1≤bước≤5; ngoài miền hiển thị 0 hoặc trạng thái rõ; đặt tên Network |

## 4. Vấn đề có căn cứ và điều kiện xuất hiện

### V01 — Đèn AUTO đang biểu diễn điều kiện chạy trong ca

Trong bảng HMI, `HMI_AUTO` trỏ tới `TỰ ĐỘNG CHẠY`. Tại 12:00, bật AUTO hợp lệ: `CHO PHÉP AUTO=1` nhưng `TỰ ĐỘNG CHẠY=0`; đèn dùng HMI_AUTO sẽ tắt. Đó là khác biệt ý nghĩa, không phải PLC làm mất chế độ AUTO.

Hướng chỉnh: nếu nhãn vẫn là AUTO thì liên kết tới `CHO PHÉP AUTO`; nếu muốn hiện lựa chọn công tắc thì dùng `chon_auto_hmi` và ghi rõ lựa chọn chưa chắc được chấp nhận. Nên có trạng thái riêng CHỜ LỊCH / ĐANG CHẠY / TẠM DỪNG / LỖI. Không cần sửa chu trình van để sửa hiển thị này.

### V02 — Bước 0 nhưng còn 10 giây

Trong ca, để `hmi_stop=1` trước khi bật AUTO. Quyền AUTO và TỰ ĐỘNG CHẠY lên 1, nhưng NW15 chưa cho chốt bước 1, nên bước vẫn 0. NW17 cho ET=0; NW18 tính 10−0=10 và không MOVE0 vì TỰ ĐỘNG CHẠY vẫn 1. Bơm và van đều OFF. Đây là vấn đề hiển thị mức nhẹ, không phải tự chạy hoặc timer đếm sai.

Chỉnh đúng chỗ: điều kiện giá trị hiển thị tại cuối NW18. Khi bước không nằm 1–5, đưa `thoigianconlai` về 0, hoặc dùng nhãn “chưa bắt đầu”. Không bỏ điều kiện STOP ở NW15 để làm màn hình đẹp hơn.

### V03 — Các nguyên nhân đã bình thường nhưng lỗi tổng còn giữ

Gây thiếu nước lúc đang chạy, sau đó trả đủ nước nhưng chưa RESET. NW6 vẫn giữ NHỚ LỖI, đúng thiết kế. Các dòng cảnh báo đọc tình trạng hiện tại có thể đã xanh hết; người vận hành chưa được giải thích vì sao lỗi tổng còn bật.

Đề xuất tối thiểu: thông báo “Điều kiện đã bình thường — nhấn RESET xác nhận” khi còn NHỚ LỖI và các điều kiện hiện tại đã hợp lệ. Nếu yêu cầu tìm nguyên nhân quá khứ thì cần alarm history hoặc lưu riêng nguyên nhân. Một bit NHỚ LỖI không chứa đủ thông tin để khôi phục lịch sử. Không coi thiếu lịch sử là lỗi bảng van.

### V04 — Nút/cảm biến vật lý chưa tác động vào chương trình

Đã xác định từ toàn bộ 18 NW: không có lệnh đọc `%I0.0–%I0.5`; các lệnh và điều kiện bảo vệ dùng các trường `hmi_*` trong DB. Do đó chỉ đấu dây ba nút START/STOP/RESET vào I0.0/I0.5/I0.2 chưa tạo ra điều khiển song song HMI.

Với PLC thật và sáu đèn giả lập, đây là phạm vi phù hợp. Với bơm thật, thiếu nước/quá tải ở chân vật lý sẽ không được NW4 xử lý nếu chưa tích hợp: đó là rủi ro nghiêm trọng khi đổi phạm vi triển khai. Dừng khẩn bằng bit HMI/PLC tiêu chuẩn không thay mạch dừng khẩn phần cứng. Không đề xuất OR “đủ nước giả” để vượt qua cảm biến thật khi vận hành bơm.

### V05 — Mất HMI không tự làm PLC dừng

Không có watchdog kết nối trong 18 NW. Nếu đang AUTO trong ca, `hmi_stop=0`, các bit an toàn vẫn giữ giá trị cuối, việc ngắt Runtime/cáp không tự biến các bit đó thành lỗi. PLC có thể tiếp tục chạy theo lịch. Đây là hành vi xác định của chương trình, nhưng chỉ thành lỗi yêu cầu nếu mất HMI bắt buộc phải dừng.

Mô hình sáu đèn có thể chấp nhận hành vi này. Nếu cần dừng khi mất liên lạc, phải bổ sung giám sát liên lạc theo thời gian và trạng thái mất chất lượng phù hợp, không suy ra kết nối chỉ từ đèn màu xanh. Nhãn PLC ONLINE hiện đúng hay sai chưa thể kết luận từ một ảnh; cần thử ngắt kết nối. Khi kết nối lại, cần kiểm tra HMI có ghi lại lựa chọn AUTO từ giá trị cũ hay không; không khẳng định hiện tại nó chắc chắn làm vậy.

### V06 — Chưa xử lý bước bị ghi ngoài miền

Trong PLCSIM, đang được chạy, dùng Modify một lần đưa BƯỚC HIỆN TẠI = 6 hoặc −1. NW9 giữ giá trị đó; cả năm timer reset vì không trùng bước; không có Q đề nghị bước mới. Bơm và van OFF, bước bị giữ và NW18 có thể hiện 10 s. Không thấy đường chuyển bước bình thường nào tự tạo giá trị này; không được gọi đây là lỗi tự phát.

Nếu cần tăng khả năng chẩn đoán, thêm kiểm tra miền bước và đưa về trạng thái lỗi/dừng để người vận hành xác nhận. Không tự cho phép phục hồi rồi bật bơm mà chưa thống nhất hành vi. Chưa áp dụng thay đổi này.

### Những điều không được coi là lỗi

- Không có OB100: hợp lệ vì đã dùng FirstScan trong OB1.
- Cùng biến được ghi nhiều lần ở NW1/8, NW9–15, NW17–18: có thứ tự và mục đích, không tự động là xung đột.
- RESET không chạy lại ngay: đúng cơ chế cạnh AUTO hiện tại.
- STOP còn giữ sau RESET/TẮT: đây là đầu vào HMI duy trì; code không tự xóa nó. Cần mô tả vận hành rõ, không áp đặt phải đổi.
- Không thấy số 0 giây giữa các bước trên HMI: thường do bước mới/ET mới đã được cập nhật và chu kỳ làm tươi HMI.
- RTC OK=1 nhưng đồng hồ lệch múi giờ: mã đọc thành công không kiểm chứng được thời gian bên ngoài. Cần cài CPU đúng, không tự thêm một “lỗi RTC” không có chuẩn thời gian so sánh.

## 5. Rút gọn có căn cứ — chỉ đề xuất, chưa áp dụng

| Mã | Vị trí | Có thể rút | Lý do và giới hạn |
|---|---|---|---|
| O01 | NW8, nhánh S của SR AUTO | Một tiếp điểm thường đóng HỦY PHÉP CHẠY | R1 của cùng SR đã ưu tiên reset khi HỦY=1; giữ nguyên SR và thứ tự |
| O02 | NW8, rung TỰ ĐỘNG CHẠY | Một tiếp điểm thường đóng HỦY PHÉP CHẠY | CHO PHÉP AUTO vừa qua SR đã bằng0 nếu HỦY=1; không có writer khác ở giữa |
| O03 | NW10–14, các rung Q→MOVE | Năm tiếp điểm TỰ ĐỘNG CHẠY | Khi không được chạy, timer vừa gọi có R=1 nên Q=0; phải giữ gọi timer trước đọc Q và đủ nhánh reset |
| O04 | NW16, chỉ rung bơm | Một tiếp điểm thường đóng hmi_stop, nhưng hiện nên giữ | Tương đương Boolean nếu các rung đọc cùng STOP. Nếu DB HMI đổi giữa rung van và bơm, tiếp điểm hiện tại có thể tắt bơm sớm hơn một scan. Chưa có lấy mẫu đầu vào nhất quán thì không khuyên bỏ |
| O05 | NW15 | Dùng chung /TỰ ĐỘNG CHẠY cho hai MOVE0 | Chỉ gọn nhánh, vẫn ghi cả BƯỚC HIỆN TẠI và BƯỚC TIẾP THEO về0 |
| O06 | NW1, NW7, NW8 | Cơ chế ĐÃ GẠT TẮT và một biến Bool, nhưng hiện nên giữ | Tương đương trên trạng thái đạt tới khi các lần đọc AUTO nhất quán. P luôn cập nhật đầu rung; FirstScan nằm trong HỦY. Không khẳng định tương đương dưới mọi ghi DB bất đồng bộ |

**Khuyến nghị cho bản hiện tại: O01–O03 rút bảy tiếp điểm; O05 gộp điều kiện reset lặp ở hai nhánh.** Giữ O04/O06 trừ khi đã bảo đảm dữ liệu đầu vào không đổi giữa các lần đọc hoặc đã tổ chức lấy mẫu đầu vào mỗi scan. Nếu sau này áp dụng O06 đầy đủ, DB có thể từ 29 xuống 28; hiện không có biến DB nào được khuyên xóa ngay. Đây là số lượng theo 18 NW đã đọc, không phải tuyên bố đã sửa project.

### Vì sao ĐÃ GẠT TẮT có dùng nhưng vẫn có thể rút?

`ĐÃ GẠT TẮT` không phải biến bỏ quên: nó được reset ở NW1, set khi AUTO=0 ở NW7, đọc trước SR và reset sau SR ở NW8. Tuy nhiên, với cấu trúc hiện tại:

1. Ở FirstScan, HỦY=1 nên SR AUTO reset, dù tiếp điểm P có phát cạnh.
2. Ngoài FirstScan, P chỉ có xung khi AUTO trước đó là0, hiện tại là1.
3. Ở vòng quét AUTO=0, NW7 đã set ĐÃ GẠT TẮT=1 và đồng thời HỦY=1; SR AUTO reset nên nhánh reset cờ ở NW8 không thực hiện.
4. Vì vậy khi có cạnh AUTO có thể được nhận ở vòng kế tiếp, cờ này đã là1; nó không thêm ràng buộc vào cạnh đó. Sau lỗi/RESET mà AUTO vẫn1, P không phát cạnh mới, kể cả bỏ cờ.

Chứng minh phụ thuộc P đứng đầu rung và được cập nhật mỗi scan, FirstScan hoạt động đúng, SR có R1 ưu tiên reset, không có đoạn khác ghi các trạng thái ở giữa, và **các lần đọc chon_auto_hmi nhất quán trong cùng scan**. Không dùng kết luận này nếu chuyển cổng điều kiện lên trước P, tự Force trạng thái nội bộ hoặc giả định mọi cập nhật DB HMI đều luôn nằm đúng đầu scan. **Không bỏ XUNG AUTO:** đó là bộ nhớ cạnh của P. Với lợi ích chỉ một Bool, giữ cơ chế hiện tại là lựa chọn hợp lý; không cần thêm biến lấy mẫu chỉ để rồi bỏ một biến khác.

### Các phần nên giữ

- Giữ năm TONR, PT10s, điều kiện IN và hai nhánh reset hiện tại; không bỏ nhánh /TỰ ĐỘNG CHẠY ở chân R vì bước chỉ được xóa sau các timer.
- Giữ hai biến bước và commit ở NW15, không gộp thành một biến cập nhật ngay trong từng timer.
- Giữ MOVE ET mặc định0 ở NW17 và thứ tự NW15→NW16→NW17→NW18.
- Giữ SR nhớ lỗi và xác nhận xóa lỗi có điều kiện. Giữ HỦY PHÉP CHẠY là biến tập trung điều kiện, dù một số tiếp điểm đọc nó lặp.
- Giữ CA SÁNG/CA TỐI/TRONG GIỜ vì phục vụ cả lịch và HMI; giữ các biến hiển thị chỉ được HMI đọc.
- Không thay toàn bộ bằng một timer chỉ để giảm số Network; đó là thiết kế khác và cần kiểm chứng lại.

Có thể gộp **NW7 và NW8** thành một Network “Quản lý quyền AUTO”, giữ nguyên thứ tự các rung. NW10–14 vẫn nên tách theo từng bước. NW17–18 có thể giữ riêng vì một mạng chọn ET, một mạng tính/chuẩn hóa hiển thị. Đặt tên NW18 là “TÍNH THỜI GIAN CÒN LẠI CHO HMI”. Số Network ít hơn không tự chứng minh chương trình tối ưu hơn.

## 6. Biến thừa và bảng tag

**Cả 29 trường DB hiện đều có công dụng hoặc tham chiếu. Không có trường nào đủ căn cứ để xóa ngay vì “không dùng”.** Riêng ĐÃ GẠT TẮT có thể loại sau khi thay đồng bộ cơ chế như O06, không xóa tên trước rồi để các rung cũ lỗi toán hạng.

| Nhóm | Kết luận |
|---|---|
| PLC tags I0.0, I0.2, I0.3, I0.4, I0.5 | Không được đọc trong 18 NW và không thấy HMI tag liên kết trong bảng đã gửi. Có thể bỏ tên nếu chỉ làm HMI/sáu đèn và Cross-references xác nhận không dùng ngoài; giữ nếu chuẩn bị đấu nút/cảm biến thật |
| PLC tag ĐỦ NƯỚC, I0.1 | Không tham gia LAD nhưng HMI_DUNUOC còn trỏ tới; chưa xóa riêng khi chưa kiểm đối tượng HMI |
| HMI_DUNUOC | Ứng viên kiểm tra xóa: đọc I0.1, khác HMI_DU_NUOC đọc DB hmi_du_nuoc. Chuyển hết hiển thị giả lập về đúng nguồn đang dùng trước khi xóa tag cũ |
| Q0.0–Q0.5 và FirstScan | Đều được dùng; giữ |
| XUNG AUTO | Bộ nhớ của P, không phải bit xung bỏ quên; giữ |
| thoigianconlai, GIỜ PLC, các bit lịch | HMI có đọc; không coi là dư chỉ vì ít hoặc không có tiếp điểm LAD đọc |
| etms, giaydachay, giay_con_lai_tinh | Có dùng theo chuỗi tính; không xóa riêng. Có thể tái dùng một DInt trung gian khi thiết kế lại nhưng sẽ khó theo dõi hơn, chưa cần làm |
| buoc1…buoc5 | Năm instance đều được gọi, đọc Q và ET; không dư |

Xóa tên tag chỉ làm gọn danh mục, không làm mất địa chỉ vật lý và không tự giảm đáng kể thời gian quét. Bảng đối chiếu đầy đủ từng trường kèm theo là đọc từ ảnh, không phải bản xuất Cross-references của TIA.

## 7. HMI và khả năng triển khai

Ba màn tổng quan, điều khiển/giả lập và cảnh báo đã phân chia chức năng rõ. Bơm, bốn van, bước, giây còn lại và lịch có thông tin phục vụ thử bài. Các chỉnh sửa nên ưu tiên:

1. Hiển thị AUTO đúng ý nghĩa, thêm trạng thái CHỜ LỊCH/TẠM DỪNG. Khi STOP=1 nhưng TỰ ĐỘNG CHẠY=1 không ghi hệ thống đang bơm.
2. Hiển thị nguyên nhân hiện tại và lời nhắc RESET khi nguyên nhân đã hết nhưng lỗi tổng còn lưu.
3. Cho người vận hành thấy STOP đang giữ; nếu đặt nút ở trang phụ, tổng quan vẫn nên có trạng thái dừng. Nhãn TẠM DỪNG/TIẾP TỤC rõ hơn một chữ STOP không đổi.
4. Ô lịch nên giữ rõ hai dòng “Ca sáng 06:00–08:00”, “Ca tối 17:00–20:30” và một dòng trạng thái ca. Hiện ảnh đang lặp NGOÀI CA hai lần; có thể tận dụng chỗ đó. Một đồng hồ PLC chung theo HH:mm:ss là đủ.
5. Đổi tên nút CÀI ĐẶT thành ĐIỀU KHIỂN/GIẢ LẬP nếu màn đích chỉ gồm các công tắc giả lập và STOP/RESET. Định dạng 24 giờ thuận tiện đối chiếu lịch; định dạng AM/PM hiện tại không tự nó là lỗi thời gian.
6. Thử nhãn PLC ONLINE khi rút cáp hoặc dừng Runtime; không suy đoán rằng đèn này đã hoặc chưa được liên kết đúng từ ảnh tĩnh.

Với mô hình sáu đèn, có thể dùng WinCC trên máy tính kết nối PLC thật, nạp chương trình và xuất sáu Q tương ứng. PLCSIM không trực tiếp tạo điện ở các cọc ngõ ra PLC thật. Nút/cảm biến vật lý muốn dùng phải được tích hợp vào logic; hiện tại đấu dây đơn thuần chưa đủ.

Với bơm/van thật, lệnh Q không chứng minh có nước, contactor đã đóng hoặc van đã mở. Cần bảo vệ quá tải và dừng khẩn phần cứng phù hợp, lựa chọn tín hiệu đứt dây/mất nguồn theo trạng thái an toàn, và nguồn cảm biến thật tham gia điều kiện chạy. Không lấy kết quả mô phỏng sáu đèn làm chứng nhận cho bộ bơm công suất.

## 8. Thứ tự xử lý đề nghị

| Ưu tiên | Việc làm | Tác động |
|---|---|---|
| 1 | Chốt phạm vi HMI + sáu đèn; ghi rõ nút thật chưa tích hợp; thử STOP/RESET/lỗi và mất liên lạc | Tránh hiểu nhầm công dụng thực của các chân I |
| 2 | Sửa nguồn đèn AUTO hoặc đổi nhãn; thống nhất HMI_DU_NUOC/HMI_DUNUOC; hiện trạng thái cần RESET | Chủ yếu HMI; không đổi chu trình |
| 3 | Chỉnh điều kiện hiển thị ở cuối NW18 cho bước0/ngoài miền; đặt tên NW18 | Không thay timer hoặc bảng van |
| 4 | Nếu muốn gọn hơn: ưu tiên O01–O03 và O05, từng nhóm một; giữ O04/O06 khi chưa bảo đảm giả định | Bỏ logic lặp có chứng minh, không viết lại toàn bộ |
| 5 | Nếu cần độ bền vận hành cao hơn: bổ sung xử lý bước bất hợp lệ, mất liên lạc, nguồn đầu vào thật | Đây là bổ sung chức năng, cần xác định hành vi mong muốn; chưa tự áp dụng |

Khi thực sự chỉnh, giữ một bản gốc để đối chiếu; Compile PLC/HMI và kiểm tra Cross-references sau từng nhóm. Không làm đồng thời tối ưu và đổi chức năng STOP, vì sẽ khó phân biệt nguyên nhân nếu kết quả khác.

## 9. Bộ kiểm thử và cách ghi kết quả

Bộ tình huống chi tiết đi kèm có mục đích, điều kiện ban đầu, thao tác, kết quả mong đợi của bản hiện tại, biến cần theo dõi và dấu hiệu sai. Tất cả ô kết quả PLCSIM để **Chưa chạy PLCSIM**; không dùng kết quả mô hình độc lập để điền thay.

Tối thiểu phải thử: năm bước và vòng lặp; các biên giờ; AUTO giữ sẵn lúc vàoRUN; STOP giữa bước và sát chuyển bước; RESET khi lỗi còn và khi hết lỗi; AUTO/RESET đồng thời; hết ca lúc tạm dừng; lỗi đồng thời; mất/kết nối lại HMI; các I vật lý chưa tích hợp; bước ngoài miền; trạng thái hiển thị AUTO và lỗi lưu.

Theo dõi đồng thời: chon_auto_hmi, hmi_stop, hmi_reset, ba bit giả lập an toàn, RTC OK, TRONG GIỜ, NHỚ LỖI, HỦY PHÉP CHẠY, CHO PHÉP AUTO, TỰ ĐỘNG CHẠY, hai biến bước, Q/ET của năm TONR, thoigianconlai và Q0.0…Q0.5. Các ranh giới scan nên dùng Trace nếu CPU/công cụ hỗ trợ; màn Runtime không phản ánh được mọi trạng thái ngắn.

Đã thực hiện riêng kiểm chứng logic: 512 tổ hợp FirstScan; duyệt 7 trạng thái đạt tới và 224 chuyển trạng thái của phần cấp quyền; các phép đối chiếu cục bộ 32/160/64/256 trường hợp. Không có khác biệt dưới giả định của mô hình. Cũng tái hiện được trạng thái bước 0/còn 10 s khi STOP đã 1 trước AUTO. Các con số này là duyệt mô hình Python, **không phải số ca PLCSIM đã đạt** và không xác nhận định thời IEC thực. Giới hạn đầu vào HMI nhất quán theo scan là lý do giữ O04/O06 trong khuyến nghị cuối.

## 10. Chấm điểm theo mức chứng cứ

Đây là **điểm thiết kế qua tài liệu cho mô hình sáu đèn**, không phải điểm nghiệm thu bơm thật. Không trừ điểm vì không dùng OB100; chấp nhận xác nhận Events HMI đúng và ảnh đủ.

| Tiêu chí | Tối đa | Điểm có căn cứ | Giải thích |
|---|---:|---:|---|
| Đúng yêu cầu công nghệ | 20 | 18 | Lịch, năm mẫu van, PT10s và điều kiện dừng phù hợp; trạng thái hiển thị AUTO/thời gian cần làm rõ |
| Logic và trình tự thực thi | 25 | 23 | Hai biến bước, thứ tự timer/commit/ngõ ra và SR hợp lý; chưa xử lý bước ngoài miền |
| STOP, RESET, điều kiện an toàn | 20 | 17 | Pause giữ ET, RESET có điều kiện, lỗi có nhớ; phải phân biệt nguồn bảo vệ giả lập và phần cứng, hướng dẫn rõ STOP giữ sau RESET |
| Ổn định và tình huống bất thường | 15 | 10 | Có khóa khởi động và lỗi; chưa có giám sát mất HMI hoặc xử lý trạng thái bước bất thường, cần thử kết nối lại |
| Tối ưu, dễ hiểu, bảo trì | 10 | 8 | Nhóm Network tương đối rõ, mọi DB có dùng; còn logic lặp, NW18 chưa đặt tên, UI trạng thái cần thống nhất |
| Khả năng kiểm thử và vận hành thực tế | 10 | Chưa chấm | Chưa có kết quả riêng của bộ tình huống biên/thiết bị thật; không tự quy đổi một lần chạy thành đạt toàn bộ |

**Phần đã chấm: 76/90 điểm. Còn 10 điểm chưa chấm; chưa kết luận tổng điểm trên 100.** Có thể chốt phần còn lại sau khi có kết quả kiểm thử tương ứng. Các điểm là nhận định kỹ thuật có giải thích, không phải chứng nhận an toàn hoặc kết quả tự động.

## 11. Kết luận sử dụng trong đồ án

Bản V1688 đủ cơ sở để tiếp tục dùng làm bản đồ án/mô hình sáu đèn: lõi lịch, chu trình và dừng/RESET không cần viết lại. Nên sửa các điểm hiển thị nhỏ, ghi đúng phạm vi đầu vào HMI và hoàn thành bộ tình huống biên trước khi chốt. Tối ưu có thể làm sau, vì các tiếp điểm lặp hiện không phải nguyên nhân làm hệ thống sai.

Chưa đủ căn cứ nghiệm thu hệ thống bơm thật hoặc nói “không còn lỗi trong mọi tình huống”. Nếu bổ sung ba nút thật, cảm biến thật hay chính sách dừng khi mất HMI, đó là phần chức năng còn phải tích hợp và kiểm thử, không phải chỉ nối thêm dây.


# Phụ lục — Bảng đối chiếu biến V1688

Đọc từ ảnh commit aae862c01ddf4d1225ce9127cda915b7a7da8b55; không phải xuất Cross-references trực tiếp từ TIA.

### Đối chiếu 29 trường DB

| Trường DB | Nơi ghi/cập nhật | Nơi đọc trong LAD | HMI / kết luận |
|---|---|---|---|
| GIỜ PLC | NW2: OUT của RD_LOC_T | NW3: HOUR, MINUTE | HMI_GIO_PLC; giữ |
| TRẠNG THÁI RTC | NW2: RET_VAL | NW2: so sánh 0/1 | Giữ để kiểm tra RTC |
| RTC OK | NW2 | NW3, NW4, NW5, NW7 | HMI_RTC_OK; giữ |
| CA SÁNG | NW3 | NW3: hợp TRONG GIỜ | HMI_CA_SANG; giữ |
| CA TỐI | NW3 | NW3: hợp TRONG GIỜ | HMI_CA_TOI; giữ |
| TRONG GIỜ | NW3 | NW8 | HMI_TRONG_GIO; giữ |
| AN TOÀN | NW4 | NW4, NW5, NW7 | Giữ |
| LỖI HIỆN TẠI | NW4 | NW6: S của SR | Giữ hoặc nối biểu thức trực tiếp khi thiết kế lại; không phải không dùng |
| NHỚ LỖI | NW6: SR có nhớ | NW6 qua đầu ra Q và trạng thái SR; NW7 | HMI_LOI đọc đèn lỗi là giá trị tương ứng; giữ |
| XUNG AUTO | NW8: bộ nhớ tiếp điểm P | NW8: giá trị trước để phát hiện cạnh | Không phải bit xung thừa; không được xóa nếu vẫn dùng P |
| XÁC NHẬN LỖI | NW5 | NW6: R1 | Có dùng; tách tên giúp đọc và kiểm thử |
| ĐÃ GẠT TẮT | NW1 R; NW7 S; NW8 R | NW8, trước SR AUTO | Có tham chiếu; hiện nên giữ. Chỉ chứng minh rút được khi AUTO nhất quán theo scan, xem báo cáo tổng hợp |
| HỦY PHÉP CHẠY | NW7 | NW8: S/R1 SR và rung TỰ ĐỘNG CHẠY | Giữ biến; một số tiếp điểm có thể rút, khác với xóa biến |
| CHO PHÉP AUTO | NW1 R; NW8 SR | NW8: xóa ĐÃ GẠT TẮT và tính TỰ ĐỘNG CHẠY | Khác TỰ ĐỘNG CHẠY khi ngoài ca; không gộp hai biến |
| TỰ ĐỘNG CHẠY | NW8 | NW9, NW10–14, NW15, NW16, NW18 | HMI_AUTO đang trỏ vào biến này; giữ |
| BƯỚC HIỆN TẠI | NW1 và NW15 | NW9, NW10–14, NW16, NW17 | HMI_BUOC; giữ |
| BƯỚC TIẾP THEO | NW1, NW9, NW10–14, NW15 | NW15 | Biến đệm có công dụng giữ việc commit bước ở cuối chuỗi timer; giữ |
| etdangchay | NW17: đặt 0 rồi chọn ET theo bước | NW18: T_CONV | Giữ |
| etms | NW18: T_CONV | NW18: DIV | Có dùng, không xóa riêng |
| thoigianconlai | NW18: CONV; MOVE 0 khi không chạy | Không thấy LAD đọc tiếp | HMI_CONLAI đọc; giữ dù LAD không đọc |
| giaydachay | NW18: DIV | NW18: SUB | Có dùng, không xóa riêng |
| giay_con_lai_tinh | NW18: SUB | NW18: CONV | Có dùng, không xóa riêng |
| chon_auto_hmi | HMI theo cấu hình người dùng xác nhận | NW4, NW7, NW8 | Tag HMI chon_auto_hmi; giữ |
| hmi_du_nuoc | HMI | NW4 | HMI_DU_NUOC; giữ |
| hmi_qua_tai | HMI | NW4 | HMI_QUA_TAI; giữ |
| hmi_dung_khan | HMI | NW4 | HMI_DUNG_KHAN; giữ |
| hmi_reset | HMI | NW5 | HMI_RESET_NHAN; giữ |
| hmi_stop | HMI | NW10–14: IN/chuyển bước; NW15 commit; NW16 van/bơm | HMI_STOP; giữ |
| reset_chuong_trinh | NW5 | NW5: xác nhận lỗi; NW7: hủy chạy | Giữ |

Việc `BƯỚC TIẾP THEO`, `BƯỚC HIỆN TẠI`, `etdangchay`, `thoigianconlai` được ghi nhiều lần trong vòng quét là có chủ đích theo thứ tự; không được chỉ nhìn số vị trí ghi rồi kết luận xung đột. Đánh giá điều kiện ghi ở phần phân tích logic.

### 13 PLC tags

| Tag | Địa chỉ | Dấu vết trong V1688 | Kết luận về xóa |
|---|---|---|---|
| CHỌN AUTO | I0.0 | Không có tiếp điểm trong NW1–18; không thấy HMI tag trỏ vào | Không dùng trong LAD bản ảnh; có thể bỏ tên nếu không chuẩn bị đấu START thật |
| ĐỦ NƯỚC | I0.1 | Không đọc trong LAD; HMI_DUNUOC vẫn trỏ vào | Chưa xóa ngay: kiểm đối tượng HMI đang dùng HMI_DUNUOC trước |
| NÚT RESET | I0.2 | Không đọc trong LAD; không thấy HMI tag trỏ vào | Không dùng trong LAD bản ảnh; giữ nếu sắp đấu RESET thật |
| DỪNG KHẨN CẤP | I0.3 | Không đọc trong LAD; không thấy HMI tag trỏ vào | Không dùng trong LAD bản ảnh; giữ nếu chuẩn bị input thật |
| QUÁ TẢI | I0.4 | Không đọc trong LAD; không thấy HMI tag trỏ vào | Không dùng trong LAD bản ảnh; giữ nếu chuẩn bị input thật |
| NÚT DỪNG | I0.5 | Không đọc trong LAD; không thấy HMI tag trỏ vào | Không dùng trong LAD bản ảnh; giữ nếu sắp đấu STOP thật |
| BƠM P1 | Q0.0 | NW16 ghi; HMI_BOM đọc | Giữ |
| VAN 1–4 | Q0.1–Q0.4 | NW16 ghi, cùng NW16 đọc hợp OR cho bơm; HMI_VAN1–4 | Giữ cả bốn |
| ĐÈN BÁO LỖI | Q0.5 | NW6 ghi; HMI_LOI đọc | Giữ |
| FirstScan | M1.0 | NW1, NW5, NW7 | Giữ; không cần thêm OB100 chỉ vì không có OB100 |

Xóa tên tag input chỉ làm gọn bảng, không làm mất địa chỉ vật lý. Không tự động làm chương trình nhanh hơn một cách đáng kể. Nếu dự định tích hợp ba nút thật thì giữ `CHỌN AUTO`, `NÚT DỪNG`, `NÚT RESET` để dùng khi sửa đúng chức năng.

### 21 HMI tags

Nhóm cần giữ theo chức năng rõ trong ba màn: `chon_auto_hmi`, `HMI_AUTO`, `HMI_BOM`, `HMI_BUOC`, `HMI_CA_SANG`, `HMI_CA_TOI`, `HMI_CONLAI`, `HMI_DU_NUOC`, `HMI_DUNG_KHAN`, `HMI_GIO_PLC`, `HMI_LOI`, `HMI_QUA_TAI`, `HMI_RESET_NHAN`, `HMI_RTC_OK`, `HMI_STOP`, `HMI_TRONG_GIO`, `HMI_VAN1`, `HMI_VAN2`, `HMI_VAN3`, `HMI_VAN4`.

**Ứng viên kiểm tra bỏ là `HMI_DUNUOC`**: nó đọc input vật lý `ĐỦ NƯỚC` I0.1, trong khi NW4 quyết định an toàn bằng `hmi_du_nuoc` và tag HMI `HMI_DU_NUOC`. Hai tag tên gần nhau nhưng không cùng nguồn dữ liệu. Chưa thể khẳng định `HMI_DUNUOC` không có đối tượng tham chiếu chỉ từ bảng tag. Nếu còn đèn/trạng thái trỏ vào tag này, nên thống nhất hiển thị về đúng tín hiệu chương trình đang dùng trước khi xóa tag cũ. Đây là điểm đối chiếu cụ thể, không phủ nhận xác nhận Events đúng của người dùng.
