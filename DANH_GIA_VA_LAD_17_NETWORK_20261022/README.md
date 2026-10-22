# Đánh giá và sắp xếp LAD — PLC_HMI_TIA_V1644

Bản rà soát ngày **22/10/2026**. Nguồn: [commit dffa0dd](https://github.com/duyvuonvai-bit/PLC_HMI_TIA_V1644/tree/dffa0dd8752a838d4b986bcf3dc6072befdaf487), gồm 28 ảnh thể hiện 18 Network, bảng biến và ba màn HMI.

## Kết luận

**Bản V1644 đã có cấu trúc hợp lý và đã sửa các vấn đề chính của bản trước.** Qua các nhánh nhìn thấy, lịch vận hành, năm mẫu van, STOP giữ bước/thời gian và RESET dừng hệ thống có quan hệ nhất quán. Chưa thấy lỗi logic nghiêm trọng trong chu trình bình thường. Phần cần ưu tiên là liên kết và phản hồi trạng thái HMI, dọn các biến không còn tham chiếu và bỏ một số nhánh lặp.

Bản ghép kèm theo có **17 Network**. Mục tiêu là mỗi Network có nhiệm vụ rõ và giữ thứ tự quét; đồng thời sửa trường hợp bước 0 hiển thị còn 10 giây. Không xem số Network nhỏ nhất là tối ưu nhất. Việc ghép Network chủ yếu giúp đọc, bảo trì và theo dõi online, không tự chứng minh CPU chạy nhanh hơn.

Kho chỉ có ảnh, không có project `.ap16`/`.zap16` hoặc bản xuất khối đầy đủ. Vì vậy đây là **đánh giá từ ảnh và sơ đồ LAD để dựng lại**, chưa phải chương trình đã Compile hoặc chạy trong Siemens. Các sự kiện nút, Animation, kết nối HMI và tham chiếu ngoài ảnh còn phải đối chiếu trong project.

## Tệp để xem và sử dụng

- [Sơ đồ LAD 17 Network — PDF](LAD_17_NETWORK_V1644.pdf).
- [Xem sơ đồ trong trình duyệt sau khi tải tệp HTML](LAD_17_NETWORK_V1644.html).
- [Bảng biến và nơi đang dùng](BANG_BIEN_VA_THAM_CHIEU.md).
- [Rà soát ba màn HMI](DANH_GIA_HMI.md).
- [Kết quả kiểm tra mô hình vòng quét](KIEM_TRA_MO_HINH.md).

## 1. Những phần đã đúng và nên giữ

| Nội dung | Nhận xét trên V1644 |
|---|---|
| Lịch chạy — NW3 | Đúng 06:00 ≤ giờ < 08:00 và 17:00 ≤ giờ < 20:30. Hai ca không bao gồm thời điểm kết thúc. |
| Năm bước — NW10–14, NW16 | Mỗi bước đặt 10 s; trạng thái V1–V4 là 1000 → 1100 → 1110 → 1111 → 0101 → lặp. |
| Bơm — NW16 | Đã chuyển phép tính bơm xuống sau các cuộn van. Không còn lỗi đọc trạng thái van của vòng trước như V1611. |
| Giới hạn bước — NW16 | Các van đã có cả giới hạn dưới và trên; không mở theo giá trị bước ngoài phạm vi dự kiến. |
| Chuyển bước — NW10–14 | Có TỰ ĐỘNG CHẠY và không STOP ở nhánh MOVE khi timer xong; không tự chuyển lúc đã mất quyền chạy. |
| STOP trong ca | TONR ngừng tích lũy nhưng không bị reset; bước và số giây được giữ, ngõ ra OFF. Bỏ STOP sẽ tiếp tục. |
| Hết ca, TẮT, lỗi, RESET | TỰ ĐỘNG CHẠY về 0; timer reset và hai biến bước về 0. Ca sau bắt đầu lại từ bước 1 nếu quyền AUTO vẫn còn. |
| Bước hiện tại/bước tiếp theo | Tách riêng hai biến và cập nhật bước sau khi xử lý cả năm timer là hợp lý; không xóa BƯỚC TIẾP THEO để giảm biến. |

Nếu STOP kéo dài qua thời điểm hết ca thì điều kiện hết ca có ưu tiên: bước/thời gian bị xóa. STOP chỉ giữ trạng thái khi các điều kiện vận hành khác vẫn còn hợp lệ.

## 2. Biến nào có thể bỏ, biến nào phải giữ?

| Biến hoặc nhóm | Tình trạng thấy trong ảnh | Xử lý đề nghị |
|---|---|---|
| DB `CÓ VAN MỞ` | Không thấy được dùng trong 18 Network hoặc ánh xạ HMI. | Ứng viên xóa rõ nhất. Xác nhận Cross-references toàn project bằng 0 rồi xóa. |
| HMI `HMI_STOP_NHAN` | Là Internal tag, không thấy vai trò trong các ảnh. | Kiểm tra Events, Scripts và Animation. Chưa đủ căn cứ xóa ngay; `<Undefined>` tại cột PLC tag là bình thường với biến nội bộ. |
| HMI `HMI_DUNUOC` | Đọc PLC tag `ĐỦ NƯỚC` tại %I0.1. | Kiểm tra các đối tượng đang dùng. Với bản demo hiện tại, đổi chúng sang nguồn DB phù hợp trước khi gỡ biến cũ. |
| HMI `HMI_DU_NUOC` | Đọc DB `hmi_du_nuoc`, đúng nguồn LAD giả lập. | Giữ và dùng thống nhất cho công tắc, đèn đủ nước, trang cảnh báo của bản demo. |
| `%I0.0…%I0.5` | Không được LAD đã chụp sử dụng; riêng %I0.1 vẫn được HMI_DUNUOC tham chiếu. | Có thể giữ để đấu nút/cảm biến thật. Xóa tên khai báo không mang lại cải thiện đáng kể về thời gian quét. |
| `System_Byte`, `DiagStatusUpdate`, `AlwaysTRUE`, `AlwaysFALSE` | Không thấy được logic ứng dụng dùng trực tiếp. | Có thể dọn alias không dùng sau kiểm tra, nhưng không tái sử dụng %MB1 làm bộ nhớ thường nếu đã cấu hình làm byte hệ thống. |
| `FirstScan` | Dùng cho khởi tạo. | Giữ. Phải bật System memory byte đúng địa chỉ; đặt tên FirstScan cho %M1.0 chưa đủ tạo chức năng này. |
| `KHỞI TẠO CHỜ` | Đang dùng tại NW5/NW7; được gán bằng FirstScan ở NW1 và reset cuối NW16. | Không phải biến bỏ quên. Bản 17 Network thay hai nơi đọc bằng FirstScan rồi bỏ các nhánh ghi; sau đó mới có thể xóa trường này nếu không có tham chiếu khác. |
| `XUNG AUTO`, `ĐÃ GẠT TẮT`, `BƯỚC TIẾP THEO`, `NHỚ LỖI` | Có nhiệm vụ thật trong bắt cạnh, cấp lại quyền AUTO, chuyển bước và nhớ lỗi. | Giữ. XUNG AUTO là ô nhớ cạnh của tiếp điểm P, không cần có cuộn dây thường mới được coi là sử dụng. |
| `etbuoc1…etbuoc5`, `etdangchay`, `etms`, `giaydachay`, `giaydachay3`, `thoigianconlai` | Đều được NW10–14/NW17/NW18 dùng. | Không xóa riêng lẻ. `giaydachay3` thực chất chứa giây còn lại; có thể đổi tên thành `giay_con_lai_tinh` bằng chức năng rename và cập nhật tham chiếu. Bản kèm theo giữ tên hiện tại để dễ đối chiếu. |

Bảng ảnh có 17 PLC tags, 36 trường trong DB và 22 HMI tags. Đây không phải kết luận toàn project chỉ có từng ấy biến; các instance timer còn nằm ở DB riêng.

## 3. Những nhánh dư và cách rút gọn

### 3.1. Gộp NW7 và NW8

Hai Network đều mang tên “Quản lý chế độ AUTO”, cùng xử lý một quyền vận hành. Gộp thành NW7 mới theo đúng thứ tự:

1. AUTO đang TẮT → ghi nhận ĐÃ GẠT TẮT.
2. Tính HỦY PHÉP CHẠY từ AUTO, điều kiện bảo vệ, RTC, nhớ lỗi, yêu cầu RESET và vòng khởi tạo.
3. Cạnh lên AUTO, đã qua TẮT và không hủy → Set quyền AUTO; điều kiện hủy có ưu tiên Reset.
4. Khi CHO PHÉP AUTO đã được cấp → Reset dấu ĐÃ GẠT TẮT.
5. Quyền AUTO hợp lệ và đang trong ca → TỰ ĐỘNG CHẠY.

Không đưa STOP vào HỦY PHÉP CHẠY hoặc TỰ ĐỘNG CHẠY: làm vậy sẽ kích hoạt reset timer/bước và mất chức năng tạm dừng.

### 3.2. Bỏ cờ trung gian KHỞI TẠO CHỜ

Trong V1644, NW1 dùng **cuộn thường** để gán `KHỞI TẠO CHỜ = FirstScan`. Hai nơi đọc cờ đều nằm trước nhánh reset cuối NW16. Vì vậy tại các nơi sử dụng, hai giá trị luôn giống nhau.

Bản đề xuất đổi tiếp điểm NC của cờ ở NW5 thành NC FirstScan; đổi tiếp điểm NO của cờ trong hủy chạy thành NO FirstScan; bỏ cuộn thường ở NW1 và cuộn R cuối NW16. Như vậy Network ngõ ra không còn lẫn công việc khởi tạo.

Điều kiện áp dụng: các Network chạy liên tục theo thứ tự trong cùng OB1, %M1.0 là bit FirstScan đã cấu hình đúng và không có nơi khác đọc/ghi cờ ngoài phần đã thấy. Nếu chưa kiểm tra hết tham chiếu, có thể giữ trường DB tạm thời; trường không còn dùng không làm sai chương trình.

### 3.3. Bỏ nhánh RESET bị lặp ở timer và xóa bước

NW7–8 đã bảo đảm: **reset_chuong_trinh = 1 → HỦY PHÉP CHẠY = 1 → TỰ ĐỘNG CHẠY = 0**, ngay trong vòng quét hiện tại.

Do đó, ở năm timer, điều kiện R có thể rút từ:

`BƯỚC HIỆN TẠI khác n HOẶC không TỰ ĐỘNG CHẠY HOẶC reset_chuong_trinh`

thành:

`BƯỚC HIỆN TẠI khác n HOẶC không TỰ ĐỘNG CHẠY`.

Tương tự, hai nhánh MOVE 0 ở NW15 cũ chỉ cần `không TỰ ĐỘNG CHẠY`; bỏ nhánh song song reset_chuong_trinh. Bản đề xuất bỏ bảy nhánh RESET bị lặp này. **Vẫn giữ biến reset_chuong_trinh và tiếp điểm của nó trong HỦY PHÉP CHẠY.**

Cách rút gọn chỉ tương đương khi phần cấp/hủy quyền chạy được xử lý trước timer và cập nhật bước. Đừng di chuyển các nhóm chức năng khỏi thứ tự trong sơ đồ kèm theo.

Một số tiếp điểm AN TOÀN, RTC hoặc HỦY còn có thể chứng minh là dư dưới thứ tự hiện tại. Bản đề xuất giữ các liên động dễ đọc đó; lợi ích bỏ thêm vài tiếp điểm nhỏ hơn nguy cơ khó theo dõi khi sửa chương trình.

### 3.4. Sửa hiển thị bước 0 nhưng còn 10 giây

Có một tình huống biên ở bản gốc: khi STOP đang giữ, bật AUTO trong ca có thể làm TỰ ĐỘNG CHẠY = 1 nhưng BƯỚC HIỆN TẠI vẫn = 0. NW17 chọn ET mặc định bằng 0; NW18 tính 10 − 0 = 10, nên HMI có thể hiện **bước 0, còn 10 giây**, dù chưa có bước nào được thực hiện.

Bản 17 Network bổ sung hai nhánh song song ở MOVE 0 cuối NW17: `BƯỚC HIỆN TẠI < 1` hoặc `BƯỚC HIỆN TẠI > 5`. Vì vậy chưa có bước hợp lệ sẽ hiện 0 giây. Khi STOP tại bước 1–5, số giây vẫn được giữ. Đây là chỉnh hiển thị có chủ ý, không đổi trình tự van hoặc cách TONR giữ thời gian.

## 4. Bố cục 17 Network đề xuất

| Network mới | Nhiệm vụ riêng | Lấy từ V1644 |
|---|---|---|
| 1 | Khởi tạo trạng thái khi CPU vào RUN | NW1, bỏ cờ trung gian |
| 2 | Đọc giờ địa phương và xác nhận trạng thái RTC | NW2 |
| 3 | Xác định ca sáng, ca tối và đang trong giờ | NW3 |
| 4 | Kiểm tra điều kiện bảo vệ, lập lỗi hiện tại | NW4 |
| 5 | Nhận RESET và xác nhận xóa nhớ lỗi khi đã đủ điều kiện | NW5 |
| 6 | Chốt nhớ lỗi và điều khiển đèn báo lỗi | NW6 |
| 7 | Nhận, giữ, hủy quyền AUTO và cho phép chu trình theo lịch | NW7 + NW8 |
| 8 | Chuẩn bị bước tiếp theo, vào bước 1 từ trạng thái 0 | NW9 |
| 9 | Định thời bước 1, hết 10 s đề nghị bước 2 | NW10 |
| 10 | Định thời bước 2, hết 10 s đề nghị bước 3 | NW11 |
| 11 | Định thời bước 3, hết 10 s đề nghị bước 4 | NW12 |
| 12 | Định thời bước 4, hết 10 s đề nghị bước 5 | NW13 |
| 13 | Định thời bước 5, hết 10 s đề nghị quay về bước 1 | NW14 |
| 14 | Chốt bước hiện tại; xóa hai biến bước khi không còn chạy | NW15 |
| 15 | Xuất bốn van theo bước, sau đó xuất bơm | NW16, bỏ reset cờ khởi tạo |
| 16 | Chọn thời gian tích lũy của bước đang hoạt động | NW17 |
| 17 | Đổi thời gian sang giây còn lại; bước không hợp lệ thì hiển thị 0 | NW18, bổ sung tiêu đề và điều kiện ghi 0 |

Năm timer tiếp tục tách theo bước để dễ theo dõi online. Mỗi Network timer có cả TONR và MOVE sang bước kế tiếp vì hai nhánh cùng phục vụ một bước. Không đổi sang một timer duy nhất trong lần chỉnh này: cần thêm cơ chế reset/tái kích hoạt ở mỗi chuyển bước, thử lại STOP và thời điểm biên; giảm instance chưa chắc làm chương trình dễ hiểu hơn.

## 5. HMI hợp lý ở đâu, nên chỉnh gì?

Ba trang Tổng quan — Giả lập đầu vào — Cảnh báo là cách chia phù hợp. Biểu tượng bơm/van, bước và giây còn lại đã giúp theo dõi chu trình. Chỉ cần chỉnh các điểm sau:

1. **Thống nhất nguồn mức nước.** Đèn Tổng quan, công tắc giả lập, cảnh báo và LAD phải đọc cùng DB `hmi_du_nuoc` trong chế độ demo. Kiểm tra cả hai tag gần giống tên trước khi xóa.
2. **Kiểm tra trạng thái kết nối thật.** Ảnh Tổng quan hiện PLC ONLINE và KHÔNG LỖI màu xanh, trong khi ảnh Cảnh báo có THIẾU NƯỚC và LỖI RTC. Điều này cần đối chiếu khi PLC RUN và có kết nối; có thể là dữ liệu mặc định/cũ hoặc ảnh ở thời điểm khác nhau, chưa đủ chứng minh LAD sai. Cùng lúc theo dõi AN TOÀN, RTC OK, LỖI HIỆN TẠI, NHỚ LỖI, Q0.5 và HMI_LOI.
3. **Lịch chạy có mốc giờ cố định và một dòng trạng thái.** Khung hiện lặp NGOÀI CA hai lần. Đổi thành `06:00–08:00 / 17:00–20:30` và dòng động `CA SÁNG / CA TỐI / NGOÀI CA`. Khi RTC chưa hợp lệ thì báo CHƯA XÁC ĐỊNH, không suy ra đang ngoài ca.
4. **Đồng hồ ghi rõ GIỜ PLC, dùng 24 giờ.** Bản mới đã gộp thành một đồng hồ nhưng đang hiển thị AM/PM. Khi chưa đọc được giờ hoặc mất cập nhật, dùng `--:--:--`. RTC OK chỉ nói lệnh đọc giờ hợp lệ, không tự kiểm tra giờ/múi giờ đã đặt đúng.
5. **STOP đổi chữ theo trạng thái.** Chưa dừng: TẠM DỪNG. Đang dừng: TIẾP TỤC. Thêm dòng ĐANG TẠM DỪNG tại Tổng quan; không dùng đèn AUTO như bằng chứng ngõ ra đang chạy vì TỰ ĐỘNG CHẠY vẫn có thể bằng 1 khi STOP.
6. **Phản hồi RESET và lỗi còn nhớ.** Nếu nguyên nhân hết nhưng NHỚ LỖI vẫn 1, hiển thị CHỜ RESET. RESET mới không yêu cầu AUTO tắt hoặc STOP bật. Nhấn RESET làm hủy quyền chạy; sau nhả cần TẮT → AUTO và bỏ STOP nếu đang giữ. Giao diện nên nhắc thao tác này.

Nút RESET cần được kiểm tra Events để không bị giữ mức 1 ngoài ý muốn. Ảnh chưa cho biết đang dùng Press/Release hay loại sự kiện nào. Nếu muốn bắt buộc mỗi lần xóa lỗi là một lần nhấn mới, có thể bổ sung bắt cạnh RESET, nhưng đó là thay đổi chức năng riêng chứ không đưa lẫn vào lần ghép Network này.

## 6. Cách áp dụng trong TIA Portal V16

1. Lưu một bản sao project đang chạy tốt. Giữ bản V1644 để đối chiếu.
2. Tạo hoặc sắp lại các Network theo PDF; giữ nguyên tên biến, địa chỉ Q và năm instance TONR `buoc1…buoc5`. Không tạo nhiều lời gọi cho cùng một timer trong vòng quét.
3. Thay cờ khởi tạo và rút các nhánh lặp đúng vị trí nêu trên. Nếu giữ nguyên biến chưa dọn, chương trình vẫn có thể hoạt động; ưu tiên đúng tham chiếu.
4. Kiểm tra Cross-references của từng biến định xóa trên PLC và HMI, kể cả Events/Animations/Scripts. Chỉ xóa sau khi đã sửa mọi liên kết cần giữ.
5. Compile PLC và HMI. Chạy lại các tình huống bên dưới trên PLCSIM rồi mới đối chiếu phần cứng.

| Phép thử | Kết quả cần thấy |
|---|---|
| Khởi động CPU với AUTO đã bật | Không tự nhận quyền chạy cho đến khi TẮT → AUTO. |
| AUTO trong ca, đầu vào bình thường | Bước 1→2→3→4→5→1; mỗi timer đặt 10 s; mẫu van đúng bảng; bơm chạy suốt chu trình. |
| STOP giữa bước, giữ 20 s | Bước và ET giữ; bơm/van OFF; tiếp tục chạy từ thời gian cũ sau khi bỏ STOP. |
| STOP khi gần hết 10 s | Không nhảy nhiều bước khi tiếp tục; kiểm tra Q/ET của timer và bước kế tiếp. |
| TẮT khi đang STOP | Bước và giây về 0; các ngõ ra OFF. |
| Thiếu nước, quá tải, dừng khẩn | Mỗi lỗi làm dừng, reset timer/bước và chốt đèn lỗi; khôi phục tín hiệu không tự xóa nhớ lỗi. |
| RESET khi nguyên nhân còn tồn tại | Dừng/reset chu trình nhưng không xóa nhớ lỗi khi điều kiện chưa hợp lệ. |
| RESET khi đã hết lỗi | Xóa nhớ lỗi; không tự chạy. Nhả RESET, TẮT → AUTO; bỏ STOP nếu còn. |
| 07:59:59→08:00;20:29:59→20:30 | Dừng, xóa bước và timer. Ca sau nếu quyền AUTO còn thì bắt đầu bước 1. |
| Mất kết nối HMI–PLC | HMI không tiếp tục trình bày dữ liệu cũ như trạng thái hiện tại hợp lệ. |

Mô hình Python đi kèm đã đạt 17 nhóm kiểm tra, gồm so sánh 30.000 vòng quét với tín hiệu thay đổi, toàn bộ 86.400 mốc giây của lịch ngày và tình huống STOP/RESET/lỗi. Phần điều khiển giữ kết quả tương đương; phần hiển thị khác có chủ ý khi chưa có bước hợp lệ. Kiểm tra này chỉ đối chiếu logic và thứ tự vòng quét. Nó không thay thế thời gian thực TONR, Runtime HMI hoặc kiểm thử PLC Siemens.
