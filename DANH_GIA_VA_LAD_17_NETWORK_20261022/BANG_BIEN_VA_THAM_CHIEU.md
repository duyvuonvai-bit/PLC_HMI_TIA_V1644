# Rà soát biến bản PLC_HMI_TIA_V1644

Nguồn: commit bắt đầu `dffa0dd`, 28 ảnh trong kho, 18 Network. Bảng PLC: `020357.png`; DB: `020404.png`, `020411.png`; HMI: `020425.png`, `020430.png`. Tên đầy đủ các ảnh bắt đầu bằng `Screenshot 2026-10-22`.

Đã đọc lại toàn bộ ảnh của bản này, không lấy kết luận Network từ bản 1611. Đây là rà soát ảnh; chưa có project TIA để chạy Cross-references đối tượng HMI, script và toàn bộ chương trình.

## Kết luận

- **CÓ VAN MỞ** trong DB: không thấy được đọc/ghi ở bất kỳ Network 1–18 hoặc bảng ánh xạ HMI nào. Đây là ứng viên xóa rõ nhất sau khi Cross-references toàn project xác nhận không dùng.
- **HMI_DUNUOC** vẫn liên kết `%I0.1` qua PLC tag `ĐỦ NƯỚC`; **HMI_DU_NUOC** liên kết DB `hmi_du_nuoc`, là tín hiệu LAD sử dụng. Hai tag không phải alias cùng địa chỉ. Cần thống nhất các đối tượng mức nước dùng nguồn phù hợp chế độ giả lập trước khi xóa tag cũ.
- **HMI_STOP_NHAN** là Bool Internal tag. Chưa thấy nơi dùng, nhưng cần kiểm tra Events/Scripts/Animations HMI. `<Undefined>` trong cột PLC tag không phải lỗi đối với Internal tag.
- Sáu PLC input tags `%I0.0…%I0.5` không được dùng trong 18 Network; `%I0.1` còn được một HMI tag liên kết. Có thể giữ để triển khai nút/cảm biến thật. Gỡ tên khai báo không làm biến mất vùng đầu vào vật lý và không tạo ra cải thiện đáng kể về thời gian quét.
- **HMI_TRONG_GIO** là tag mới đúng mục đích, liên kết DB `TRONG GIỜ`; không có tag tên HMI_LICH trong bảng đã chụp.
- Toàn bộ biến thời gian ET và đổi kiểu vẫn có tham chiếu thật. **giaydachay3** thực chất là giây còn lại; nên đổi tên có nghĩa, không gọi là biến không dùng.
- **XUNG AUTO** là bộ nhớ bắt cạnh tại NW8, phải giữ. **BƯỚC TIẾP THEO** còn cần cho cách cập nhật bước hiện tại ở cuối chuỗi. **KHỞI TẠO CHỜ** được đọc ở NW5/NW7, không phải biến thừa.

Có 17 hàng PLC tags, 36 trường DB và 22 HMI tag nhìn thấy qua các ảnh. Không dùng các số trong dấu ngoặc vuông của tiêu đề bảng làm số lượng biến.

## 1. PLC tag table

| Tên | Kiểu | Địa chỉ | Sử dụng nhìn thấy / khuyến nghị |
|---|---|---|---|
| CHỌN AUTO | Bool | %I0.0 | Không dùng LAD; thay bằng DB chon_auto_hmi trong bản giả lập. Giữ nếu chuẩn bị đấu thật hoặc xóa tên nếu toàn project không tham chiếu. |
| ĐỦ NƯỚC | Bool | %I0.1 | LAD không dùng; HMI_DUNUOC vẫn liên kết. Không xóa trước khi xử lý HMI. |
| NÚT RESET | Bool | %I0.2 | Không dùng LAD; bản hiện tại dùng hmi_reset. |
| DỪNG KHẨN CẤP | Bool | %I0.3 | Không dùng LAD; bản hiện tại dùng hmi_dung_khan. |
| QUÁ TẢI | Bool | %I0.4 | Không dùng LAD; bản hiện tại dùng hmi_qua_tai. |
| NÚT DỪNG | Bool | %I0.5 | Không dùng LAD; bản hiện tại dùng hmi_stop. |
| BƠM P1 | Bool | %Q0.0 | NW16 ghi; HMI_BOM liên kết. |
| VAN 1 | Bool | %Q0.1 | NW16 ghi và đọc cho bơm; HMI_VAN1. |
| VAN 2 | Bool | %Q0.2 | NW16 ghi và đọc cho bơm; HMI_VAN2. |
| VAN 3 | Bool | %Q0.3 | NW16 ghi và đọc cho bơm; HMI_VAN3. |
| VAN 4 | Bool | %Q0.4 | NW16 ghi và đọc cho bơm; HMI_VAN4. |
| ĐÈN BÁO LỖI | Bool | %Q0.5 | NW6 ghi từ Q của latch NHỚ LỖI; HMI_LOI. |
| System_Byte | Byte | %MB1 | Không thấy đọc cả byte; giữ vùng byte hệ thống khi CPU đã cấu hình. Xóa alias không giải phóng byte khỏi chức năng hệ thống. |
| FirstScan | Bool | %M1.0 | NW1 đọc. Cần giữ và cấu hình đúng system memory byte. |
| DiagStatusUpdate | Bool | %M1.1 | Không thấy LAD/HMI dùng. Có thể gỡ tên nếu Cross-references = 0, nhưng không dùng lại bit làm bộ nhớ thường. |
| AlwaysTRUE | Bool | %M1.2 | Không thấy LAD/HMI dùng; cùng lưu ý byte hệ thống. |
| AlwaysFALSE | Bool | %M1.3 | Không thấy LAD/HMI dùng; cùng lưu ý byte hệ thống. |

## 2. DB daiphunnuoc

Địa chỉ byte tuyệt đối không hiện trong ảnh nên không suy đoán offset. Các trường Retain nhìn thấy đều bỏ chọn.

| Biến | Kiểu | Network / liên kết sử dụng |
|---|---|---|
| GIỜ PLC | DTL | NW2 RD_LOC_T ghi; NW3 đọc HOUR/MINUTE; HMI_GIO_PLC |
| TRẠNG THÁI RTC | Int | NW2 RET_VAL ghi, so sánh 0/1 |
| RTC OK | Bool | NW2 ghi; NW3,4,5,7 đọc; HMI_RTC_OK |
| CA SÁNG | Bool | NW3 ghi và đọc để tính TRONG GIỜ; HMI_CA_SANG |
| CA TỐI | Bool | NW3 ghi và đọc để tính TRONG GIỜ; HMI_CA_TOI |
| TRONG GIỜ | Bool | NW3 ghi; NW8 đọc; HMI_TRONG_GIO |
| AN TOÀN | Bool | NW4 ghi và đọc; NW5,7,16 đọc |
| LỖI HIỆN TẠI | Bool | NW4 ghi; NW5,6 đọc |
| NHỚ LỖI | Bool | NW6 latch SR; NW7 đọc |
| XUNG AUTO | Bool | Bộ nhớ tiếp điểm cạnh lên P ở NW8; không xóa |
| XÁC NHẬN LỖI | Bool | NW5 ghi; NW6 đọc vào R1 của latch |
| ĐÃ GẠT TẮT | Bool | NW1 R; NW7 S; NW8 đọc rồi R khi cấp phép |
| HỦY PHÉP CHẠY | Bool | NW7 ghi; NW8 đọc |
| CHO PHÉP AUTO | Bool | NW1 R; NW8 latch và đọc |
| TỰ ĐỘNG CHẠY | Bool | NW8 ghi; NW9–18 đọc theo chức năng; HMI_AUTO |
| BƯỚC HIỆN TẠI | Int | NW1/NW15 ghi; NW9–14,16,17 đọc; HMI_BUOC |
| BƯỚC TIẾP THEO | Int | NW1/NW9–15 xử lý; giữ khi còn kiến trúc current/next |
| CÓ VAN MỞ | Bool | Không thấy sử dụng trong 18 Network và ánh xạ HMI |
| etbuoc1 | Time | NW10 ghi ET; NW17 đọc |
| etbuoc2 | Time | NW11 ghi ET; NW17 đọc |
| etbuoc3 | Time | NW12 ghi ET; NW17 đọc |
| etbuoc4 | Time | NW13 ghi ET; NW17 đọc |
| etbuoc5 | Time | NW14 ghi ET; NW17 đọc |
| etdangchay | Time | NW17 đặt mặc định và chọn ET theo bước; NW18 đọc |
| etms | DInt | NW18 T_CONV ghi rồi DIV đọc |
| giaydachay | DInt | NW18 DIV ghi rồi SUB đọc |
| giaydachay3 | DInt | NW18 SUB ghi rồi CONV đọc; chứa giây còn lại |
| thoigianconlai | Int | NW18 CONV ghi và MOVE 0 khi không chạy; HMI_CONLAI |
| KHỞI TẠO CHỜ | Bool | NW1 **coil thường** nhận FirstScan; NW5/NW7 đọc; cuối NW16 R vô điều kiện |
| chon_auto_hmi | Bool | NW4,7,8 đọc; HMI tag cùng tên |
| hmi_du_nuoc | Bool | NW4 đọc; HMI_DU_NUOC |
| hmi_qua_tai | Bool | NW4 đọc; HMI_QUA_TAI |
| hmi_dung_khan | Bool | NW4 đọc; HMI_DUNG_KHAN |
| hmi_reset | Bool | NW5 đọc; HMI_RESET_NHAN |
| hmi_stop | Bool | NW10–16 đọc; HMI_STOP |
| reset_chuong_trinh | Bool | NW5 ghi/đọc; NW7,10–15 đọc |

Các timer instance DB2…DB6 (`buoc1…buoc5`) dùng tại NW10–14, không được xem là DB dư chỉ vì không nằm trong bảng daiphunnuoc.

## 3. HMI tag table

Các tên ở cột PLC tag dài có dấu ba chấm đã được đối chiếu với DB và LAD. Bảng ánh xạ chưa chứng minh việc sử dụng bởi từng đối tượng màn hình; cần Cross-references HMI để kết luận xóa.

| HMI tag | Kiểu | PLC tag liên kết |
|---|---|---|
| chon_auto_hmi | Bool | daiphunnuoc.chon_auto_hmi |
| HMI_AUTO | Bool | daiphunnuoc."TỰ ĐỘNG CHẠY" |
| HMI_BOM | Bool | "BƠM P1" |
| HMI_BUOC | Int | daiphunnuoc."BƯỚC HIỆN TẠI" |
| HMI_CA_SANG | Bool | daiphunnuoc."CA SÁNG" |
| HMI_CA_TOI | Bool | daiphunnuoc."CA TỐI" |
| HMI_CONLAI | Int | daiphunnuoc.thoigianconlai |
| HMI_DU_NUOC | Bool | daiphunnuoc.hmi_du_nuoc |
| HMI_DUNG_KHAN | Bool | daiphunnuoc.hmi_dung_khan |
| HMI_DUNUOC | Bool | "ĐỦ NƯỚC" = %I0.1 |
| HMI_GIO_PLC | DTL | daiphunnuoc."GIỜ PLC" |
| HMI_LOI | Bool | "ĐÈN BÁO LỖI" |
| HMI_QUA_TAI | Bool | daiphunnuoc.hmi_qua_tai |
| HMI_RESET_NHAN | Bool | daiphunnuoc.hmi_reset |
| HMI_RTC_OK | Bool | daiphunnuoc."RTC OK" |
| HMI_STOP | Bool | daiphunnuoc.hmi_stop |
| HMI_STOP_NHAN | Bool | Internal tag, không ánh xạ PLC |
| HMI_TRONG_GIO | Bool | daiphunnuoc."TRONG GIỜ" |
| HMI_VAN1 | Bool | "VAN 1" |
| HMI_VAN2 | Bool | "VAN 2" |
| HMI_VAN3 | Bool | "VAN 3" |
| HMI_VAN4 | Bool | "VAN 4" |

## 4. Tối ưu có căn cứ

1. `KHỞI TẠO CHỜ` không thừa, nhưng **rung R vô điều kiện cuối NW16 có thể bỏ** trong cấu trúc hiện tại: NW1 đã dùng coil thường `KHỞI TẠO CHỜ := FirstScan` ở mỗi vòng quét. Ở vòng kế tiếp FirstScan=0 sẽ tự cập nhật bit về 0 trước khi NW5/NW7 dùng. Nếu giữ R chỉ để hiển thị bit cuối scan thì không mang chức năng bảo vệ thêm. Không đổi coil thường NW1 thành S nếu không giữ reset phù hợp.
2. Có thể bỏ các nhánh reset timer riêng bằng reset_chuong_trinh ở NW10–14 và các nhánh reset bước riêng cùng biến ở NW15 **chỉ sau khi chứng minh thứ tự hiện tại không đổi**: reset_chuong_trinh đã nằm trong HỦY PHÉP CHẠY NW7, làm TỰ ĐỘNG CHẠY=false ở NW8; các điều kiện NOT TỰ ĐỘNG CHẠY vì thế đã bao phủ. Đây là dư biểu thức, không phải reset_chuong_trinh không dùng.
3. `giaydachay3` nên đổi tên thành `giay_con_lai_dint` (hoặc tên tiếng Việt thống nhất). Muốn xóa thật cần viết kết quả SUB vào một biến DInt đích và thống nhất HMI_CONLAI; không xóa biến khỏi DB khi CONV vẫn đọc.
4. Năm biến bản sao ET có thể thay bằng truy cập ET trực tiếp từ instance timer nếu người thiết kế thấy dễ đọc, nhưng không cần đổi cấu trúc đang ổn chỉ để giảm vài trường DB.
5. Các tag dùng làm hiển thị trạng thái không dư chỉ vì LAD không ghi từ HMI. Ví dụ HMI_TRONG_GIO, HMI_CA_SANG, HMI_CA_TOI phục vụ trình bày lịch ca; HMI_GIO_PLC phục vụ đồng hồ.

## 5. Giới hạn kiểm chứng HMI

Ảnh runtime cho thấy "PLC ONLINE" xanh, đồng hồ 12:00:00 AM, mức nước thiếu, RTC báo lỗi, trong khi ô tổng quan KHÔNG LỖI vẫn xanh. Có thể đây là giá trị khởi tạo/chưa có dữ liệu khi CPU chưa chạy hoặc HMI chưa nhận đủ tag; từ ảnh riêng không kết luận PLC đã xử lý và bỏ sót lỗi. Nên kiểm tra liên kết và quality/connection status của các đối tượng, thay vì suy luận chỉ từ màu.

Không thấy một tag heartbeat/kết nối được khai báo trong các bảng đã chụp, nhưng trạng thái kết nối có thể lấy từ sự kiện/system tag của HMI; không được kết luận chắc nhãn PLC ONLINE là tĩnh nếu chưa xem cấu hình đối tượng.

## 6. Trình tự dọn biến

Chạy Cross-references cho ứng viên → kiểm tra PLC và HMI Events/Animations/Scripts → đổi các binding nguồn nước nếu cần → xóa chỉ các khai báo không còn tham chiếu → compile PLC/HMI → thử các tình huống AUTO, TẮT, STOP tiếp tục, RESET, lỗi và hết ca. Không có project gốc nên báo cáo này chưa thực hiện các bước đó trong TIA.

## Đối chiếu với bản 17 Network kèm theo

Bảng trên mô tả V1644 gốc. Bản 17 thay hai chỗ đọc KHỞI TẠO CHỜ bằng FirstScan rồi bỏ các nhánh ghi cờ; chỉ sau khi sửa đầy đủ và kiểm tra tham chiếu mới có thể xóa trường này. Các biến thời gian vẫn giữ nguyên.
