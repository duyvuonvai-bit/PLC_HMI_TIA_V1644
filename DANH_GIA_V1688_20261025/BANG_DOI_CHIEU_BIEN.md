# Bảng đối chiếu biến V1688

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
