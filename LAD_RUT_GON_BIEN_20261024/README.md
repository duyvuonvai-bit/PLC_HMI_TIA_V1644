# LAD rút gọn biến — HMI và ba nút thật

Bản **24/10/2026**, gồm **22 Network trên 43 trang**, tiếp tục phương án của ngày 22/10. Bản này gộp các nhánh và đọc trực tiếp đầu ra timer để bỏ sáu biến đệm, giữ chức năng điều khiển chung HMI và START / STOP / RESET thật.

- **[Mở/tải PDF mới](LAD_Rut_gon_bien_HMI_3_nut_that_V1644.pdf)**.
- [Bản HTML có thể tải về, mở bằng trình duyệt](Xem_LAD_rut_gon.html).
- [Ảnh PNG và SVG từng trang](hinh/).
- [DB daiphunnuoc: 46 biến](Bang_DB_daiphunnuoc_46_bien.csv).
- [PLC tag: 10 tên cần dùng trong phương án](Bang_PLC_tag_10_bien.csv).
- [HMI tag: 22 liên kết trong phương án](Bang_HMI_tag_22_bien.csv).
- [Danh sách biến bỏ và cách chuyển đổi](Danh_sach_bien_bo_va_doi.csv).
- [12 instance timer](Bang_instance_timer.csv).

Các CSV là bảng đối chiếu để nhập/kiểm tra; **không phải định dạng import tag của TIA**.

## Số biến giảm như thế nào

DB V1644 gốc có 36 trường nhìn thấy trong ảnh. Thiết kế HMI + nút thật ngày 22/10 bỏ 3 trường cũ, thêm 19 Bool, nên có **52 trường DB**. Bản này giữ 13 Bool mới, đưa DB về **46 trường: giảm 6 so với bản thiết kế trước**, không phải giảm từ 36 xuống 46. Các con số không tính 12 instance timer hoặc bảng tag HMI.

Sáu biến đệm trước đây có dùng, nay được thay bằng cách nối trực tiếp:

| Biến bỏ khỏi bản ngày 22/10 | Cách thay trong bản mới |
|---|---|
| `tat_ca_lenh_da_nha` | NW3 nối các tiếp điểm nhả lệnh trực tiếp tới IN của TON. |
| `nha_lenh_on_dinh` | NW3 dùng trực tiếp `"cho_nha_lenh".Q`. |
| `xung_auto_that`, `xung_auto_hmi` | NW4 hợp hai tiếp điểm P, rồi qua `da_nha_lenh` để ghi `lenh_auto`. |
| `xung_stop_that`, `xung_stop_hmi` | NW4 hợp hai tiếp điểm P, rồi qua `da_nha_lenh` để ghi `lenh_stop`. |

**Giữ riêng bốn bộ nhớ cạnh**: `nho_auto_that`, `XUNG AUTO`, `nho_stop_that`, `nho_stop_hmi`. Không gộp chúng và không đưa cổng `da_nha_lenh` lên trước các tiếp điểm P.

Ba trường cũ `CÓ VAN MỞ`, `KHỞI TẠO CHỜ`, `ĐÃ GẠT TẮT` không nằm trong bản mới. Chỉ xóa khỏi project thực tế sau khi đã thay toàn bộ logic liên quan và kiểm tra không còn tham chiếu. `giaydachay3` chỉ **đổi tên** thành `giay_con_lai_tinh`, vẫn DInt; không tạo cả hai biến cùng lúc.

Giữ năm biến `etbuoc1`…`etbuoc5`, `etdangchay`, hai biến bước và năm TONR. Chúng còn công dụng trong thứ tự quét này.

## Hành vi vận hành giữ nguyên

- START thật hoặc AUTO HMI chốt quyền AUTO. Nhả nút vẫn giữ chế độ; ngoài ca thì chờ lịch.
- STOP lần 1 tạm dừng, lần 2 tiếp tục. Trong ca, giữ bước và thời gian khi dừng; có thể dùng xen kẽ hai nguồn lệnh.
- RESET đang nhấn khóa chạy và đưa chu trình về 0. Nhả RESET rồi nhấn START mới để xin chạy lại.
- TẮT hoặc lỗi hủy AUTO/tạm dừng, xóa bước và timer. Lỗi đã hết vẫn cần RESET để xóa nhớ lỗi.
- Hết ca xóa bước và timer, giữ AUTO và trạng thái tạm dừng. Ca sau bắt đầu từ bước 1 khi đủ điều kiện.
- Lịch chạy: 06:00–08:00 và 17:00–20:30, không gồm thời điểm kết thúc.
- Mỗi bước 10 giây; bốn van lần lượt `1000 → 1100 → 1110 → 1111 → 0101` rồi lặp lại.

## Cấu hình cần áp dụng cùng bản vẽ

1. **Thay phần điều khiển cũ** theo thứ tự 22 Network; không chạy hai bản cùng ghi AUTO, tạm dừng và bước.
2. Các trạng thái/instance timer không Retain. Bật System memory byte **MB1** để có `FirstScan %M1.0`; không ghi các bit hệ thống như bộ nhớ thường.
3. Đặt Start value `stop_thuong_dong = FALSE` nếu STOP dùng NO, hoặc TRUE nếu dùng NC. Đo kiểm tiếp điểm thực trước khi chọn; START/RESET giả định NO.
4. AUTO, TẮT, STOP và RESET trên HMI dùng **Press → SetBit, Release → ResetBit**. Không dùng InvertBit cho lệnh STOP. HMI ghi các lệnh, PLC giữ trạng thái.
5. `HMI_AUTO` đọc `CHO PHÉP AUTO`; `HMI_TAM_DUNG` đọc `tam_dung`. Các công tắc giả lập nước/quá tải/dừng khẩn vẫn duy trì trạng thái.
6. `HMI_DUNUOC` cũ đọc `%I0.1`; chuyển các đối tượng giả lập cần thiết sang `HMI_DU_NUOC` đọc DB trước khi xóa. `HMI_STOP_NHAN` chỉ xóa khi Events, Animations và Scripts không dùng.

Ba tag đầu vào `ĐỦ NƯỚC`, `DỪNG KHẨN CẤP`, `QUÁ TẢI` tại I0.1/I0.3/I0.4 không nằm trong danh sách tối thiểu cho mô hình giả lập này. Có thể giữ nếu chuẩn bị đấu cảm biến thật. Xóa tên tag chỉ làm gọn bảng, không làm mất vùng đầu vào vật lý.

Các alias hệ thống `System_Byte`, `DiagStatusUpdate`, `AlwaysTRUE`, `AlwaysFALSE` có thể giữ nguyên. Nếu xóa tên không dùng, vẫn giữ cấu hình MB1 và `FirstScan`.

## Tra nhanh trong PDF

| Trang | Nội dung |
|---|---|
| 2–28 | 22 Network LAD, vẽ đầy đủ các nhánh sau khi rút gọn |
| 29 | 10 PLC tag cần cho mô hình |
| 30–33 | Toàn bộ 46 trường DB daiphunnuoc |
| 34 | Các instance timer |
| 35–36 | Biến đã bỏ và các tag chỉ xóa sau khi kiểm tra |
| 37 | Các tiếp điểm lặp đã rút |
| 38–41 | Sự kiện nút và 22 HMI tag |
| 42–43 | Đấu nối và chạy thử |

## Phạm vi kiểm chứng

[Kiểm tra mô hình](kiem_tra/README.md): **25 nhóm tình huống cũ và 7 nhóm đối chiếu đều đạt**; so sánh 100.138 vòng quét giữa hai mô hình, không phát hiện sai khác. [Kết quả JSON](kiem_tra/ket_qua_rut_gon.json).

Kiểm tra danh mục trên bản vẽ: cả 46 biến DB đều có tham chiếu; không còn 9 biến đã loại (3 cũ + 6 đệm) làm toán hạng trên LAD. Đây không phải Cross-references trực tiếp từ project TIA.

Đây là bản vẽ để dựng lại trong TIA Portal V16, **không phải project đã Compile hoặc file nhập LAD trực tiếp**. Kiểm tra mô hình logic không xác nhận dây điện, cấu hình HMI hoặc thời gian thực của IEC timer trên CPU.

Sau khi nhập: kiểm tra Cross-references PLC/HMI, Compile cả hai, thử lại khởi động, thao tác chéo HMI/nút thật, giữ nút, STOP/tiếp tục, RESET, lỗi và hết ca. Bản rút gọn phụ thuộc đúng thứ tự network và không có đoạn khác ghi đè các trạng thái/ngõ ra.

Thiết kế dành cho mô hình sáu đèn. STOP nhấn lần hai để tiếp tục là nút vận hành, không thay chức năng dừng khẩn phần cứng. Khi dùng PLC thật, WinCC trên máy tính kết nối PLC thật; PLCSIM không trực tiếp xuất điện ra các đèn.
