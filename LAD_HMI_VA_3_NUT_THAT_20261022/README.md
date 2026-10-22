# LAD dùng chung HMI và ba nút START / STOP / RESET thật

Bản ngày **22/10/2026**, đối chiếu chương trình `PLC_HMI_TIA_V1644` tại commit `dffa0dd8752a838d4b986bcf3dc6072befdaf487`. Tài liệu gồm **22 Network trên 36 trang**, vẽ tiếp điểm, cuộn dây, bộ nhớ cạnh, khối so sánh, SR, TON, TONR và các khối xử lý dữ liệu để nhập lại trong TIA Portal V16.

- **[Mở/tải PDF đầy đủ](LAD_HMI_va_3_nut_that_V1644.pdf)**.
- [Bản HTML phóng to từng Network](Xem_LAD_HMI_va_nut_that.html): tải về rồi mở bằng trình duyệt.
- [Ảnh PNG và SVG của từng trang](hinh/) · [Mục lục và số trang](muc_luc.json).
- [Bảng biến CSV tham khảo](Bang_bien_tham_khao.csv): bảng đối chiếu, **không phải định dạng import tag của TIA**.
- [Mã và kết quả kiểm tra mô hình](kiem_tra/README.md).

Đây là **bản thay thế phần điều khiển cũ**, không nối thêm toàn bộ bản này phía sau chương trình cũ. Phải tránh để hai đoạn cùng ghi `CHO PHÉP AUTO`, trạng thái tạm dừng hoặc bước chạy. Các Network dài được chia thành nhiều trang nhưng vẫn giữ chung số Network.

## Hành vi sau khi sửa

| Thao tác / điều kiện | AUTO và tạm dừng | Bước / thời gian | Bơm và van |
|---|---|---|---|
| START thật hoặc AUTO HMI | Chốt AUTO; nhả nút vẫn giữ | Trong ca: bắt đầu bước 1; ngoài ca: chờ lịch | Chạy khi đủ điều kiện |
| STOP lần thứ nhất | Giữ AUTO, bật `tam_dung` | Giữ bước và thời gian trong ca | Tắt |
| STOP lần thứ hai, từ bất kỳ nguồn nào | Giữ AUTO, bỏ `tam_dung` | Tiếp tục bước cũ nếu vẫn trong ca | Chạy lại |
| START khi đang tạm dừng | Vẫn tạm dừng | Không đổi | Vẫn tắt; dùng STOP để tiếp tục |
| RESET đang nhấn | Xóa AUTO và tạm dừng; khóa START | Về bước 0, thời gian 0 | Tắt |
| Nhả RESET rồi nhấn START mới | Có thể chọn lại AUTO | Bắt đầu lại khi đủ điều kiện | Theo lịch và bảo vệ |
| TẮT trên HMI | Xóa AUTO và tạm dừng | Về bước 0, thời gian 0 | Tắt |
| Hết ca | **Giữ AUTO và trạng thái tạm dừng** | Xóa bước và timer | Tắt |
| Bắt đầu ca kế tiếp | Nếu AUTO còn và không tạm dừng thì chạy; nếu đang tạm dừng thì chờ STOP tiếp tục | Bắt đầu từ bước 1 | Theo trạng thái tạm dừng |
| Thiếu nước, quá tải, dừng khẩn giả lập hoặc lỗi RTC khi xin/chạy AUTO | Hủy AUTO, xóa tạm dừng, nhớ lỗi | Về bước 0, thời gian 0 | Tắt; đèn lỗi sáng |

Lịch chạy: **06:00 ≤ giờ < 08:00** và **17:00 ≤ giờ < 20:30**. Mỗi bước 10 giây; trạng thái bốn van lần lượt `1000 → 1100 → 1110 → 1111 → 0101`, rồi lặp lại.

Sau lỗi: phục hồi điều kiện, RESET, nhả RESET rồi nhấn START mới. Giữ chính sách RESET theo mức của chương trình cũ: nếu nguyên nhân lỗi hết trong khi còn giữ RESET thì nhớ lỗi được xóa, nhưng hệ thống vẫn bị khóa chạy đến khi nhả RESET và có lệnh START mới.

## Cách phối hợp hai nguồn lệnh

Mỗi nguồn START/STOP có bộ nhớ cạnh riêng; sau đó mới hợp xung bằng hai nhánh song song. Nhờ vậy, một nút đang giữ không che lần nhấn từ nguồn còn lại. HMI và nút thật cùng điều khiển **một AUTO và một trạng thái tạm dừng chung do PLC giữ**.

Ba nút thật được lọc cả nhấn và nhả bằng TON 30 ms. Sau khi CPU vào RUN, phải nhả cả ba nút và bốn lệnh HMI ổn định 30 ms để mở quyền nhận START/STOP. Việc này tránh nhận nhầm một nút đang bị giữ từ trước khi khởi động.

Hai xung STOP xuất hiện **trong cùng một vòng quét** chỉ đảo trạng thái một lần. Hai xung ở hai vòng quét khác nhau vẫn là hai lệnh; bản này không gộp các thao tác gần đồng thời của hai người thành một thao tác.

## Biến, timer và cấu hình PLC

Các biến mới được liệt kê tại bảng A1–A2 trong PDF và trong CSV. Tất cả trạng thái mới không Retain, giá trị khởi tạo FALSE; riêng `stop_thuong_dong` phải đặt **Start value** theo tiếp điểm thực:

- STOP dùng NO: `stop_thuong_dong = FALSE`.
- STOP dùng NC: `stop_thuong_dong = TRUE`.

Không chỉ Modify online tham số này rồi coi đó là cấu hình khởi động. START và RESET trong bản vẽ giả định dùng tiếp điểm NO.

Giữ `XUNG AUTO` làm bộ nhớ cạnh cho lệnh AUTO HMI; không dùng nó làm cuộn xung khác. Giữ các biến RTC, bước hiện tại/bước tiếp theo, năm biến ET, `etdangchay`, các biến tính thời gian và ngõ ra hiện có. Đổi tên `giaydachay3` thành `giay_con_lai_tinh`, vẫn kiểu **DInt**; không tạo cả hai biến rồi để khối tính đọc biến cũ.

| Instance timer | Loại | PT | Cách xử lý |
|---|---|---|---|
| `loc_auto_nhan`, `loc_auto_nha` | TON | T#30ms | Tạo mới, lọc START |
| `loc_stop_nhan`, `loc_stop_nha` | TON | T#30ms | Tạo mới, lọc STOP |
| `loc_reset_nhan`, `loc_reset_nha` | TON | T#30ms | Tạo mới, lọc RESET |
| `cho_nha_lenh` | TON | T#30ms | Tạo mới, chờ nhả lệnh khi vào RUN |
| `buoc1`…`buoc5` | TONR | T#10s | Giữ năm instance DB2…DB6 cũ |

Để TIA cấp số DB chưa dùng cho bảy TON mới. Các timer không Retain và mỗi instance chỉ được gọi một lần mỗi vòng quét.

`FirstScan` trong bản vẽ là **%M1.0**. Kiểm tra trong **CPU Properties → System and clock memory**: đã bật system memory byte và chọn **MB1**, không trùng vùng nhớ đang dùng. Chỉ đặt tên tag `FirstScan` chưa đủ để nó tự thành xung vòng quét đầu.

`ĐÃ GẠT TẮT`, `KHỞI TẠO CHỜ` và `CÓ VAN MỞ` không được dùng trong bản mới. Chỉ xóa sau khi thay xong chương trình và kiểm tra cross-reference cả PLC/HMI. Với `HMI_STOP_NHAN` hoặc `HMI_DUNUOC`, phải kiểm tra thêm Events, Animations, Scripts và nguồn mức nước; không kết luận thừa chỉ vì không xuất hiện trong LAD.

## Phải sửa Events và phản hồi HMI

| Nút | HMI tag | Biến PLC | Press | Release |
|---|---|---|---|---|
| AUTO | `chon_auto_hmi` | `daiphunnuoc.chon_auto_hmi` | SetBit | ResetBit |
| TẮT | `HMI_TAT_NHAN` mới | `daiphunnuoc.lenh_tat_hmi` | SetBit | ResetBit |
| STOP / TIẾP TỤC | `HMI_STOP` | `daiphunnuoc.hmi_stop` | SetBit | ResetBit |
| RESET | `HMI_RESET_NHAN` | `daiphunnuoc.hmi_reset` | SetBit | ResetBit |

Không dùng InvertBit cho `hmi_stop`. Nút TẮT không còn chỉ ResetBit `chon_auto_hmi`; nó gửi lệnh riêng. PLC đọc bốn bit lệnh này, không ghi trả vào chúng.

- Đèn/trạng thái `HMI_AUTO` đọc **CHO PHÉP AUTO**.
- Thêm `HMI_TAM_DUNG` đọc **tam_dung** để hiển thị trạng thái dừng và chữ TẠM DỪNG / TIẾP TỤC.
- Giữ `HMI_BUOC`, `HMI_CONLAI` và hiển thị bơm/van/đèn lỗi theo biến bước, thời gian và Q hiện có.
- Các công tắc giả lập đủ nước, quá tải và dừng khẩn vẫn giữ trạng thái; không đổi chúng thành nút nhấn nhả.

HMI tag phải là External tag liên kết đúng PLC. Khi thử, giữ nút vài trăm ms để PLC nhận mức 1 qua truyền thông. Nếu mất kết nối trong lúc giữ TẮT/RESET, lệnh có thể còn bằng 1: kiểm tra và đưa lệnh về 0 sau khi kết nối lại.

## Đối chiếu Network cũ và bản mới

| Chức năng trong V1644 | Vị trí bản mới |
|---|---|
| Nhận nút thật, lọc, chờ nhả, bắt cạnh và hợp lệnh | NW1–5 mới |
| NW1 cũ: cờ khởi tạo | Dùng trực tiếp FirstScan tại NW2, 3, 5, 11; bỏ cờ trung gian sau kiểm tra tham chiếu |
| NW2 cũ: đọc RTC | NW6 |
| NW3 cũ: lịch chạy | NW7 |
| NW4 cũ: bảo vệ | NW8 |
| NW5 cũ: RESET / xác nhận lỗi | Tách về NW5 và NW9 |
| NW6 cũ: nhớ lỗi | NW10 |
| NW7–8 cũ: hủy / cấp quyền chạy | NW11; tạm dừng chung ở NW12 |
| NW9 cũ: chuẩn bị bước | NW13 |
| NW10–14 cũ: năm timer | NW14–18 |
| NW15 cũ: cập nhật bước | NW19 |
| NW16 cũ: ngõ ra | NW20, van trước bơm sau |
| NW17 cũ: chọn ET | NW21 |
| NW18 cũ: số giây còn lại | NW22 |

## Đấu nối và trình tự thử

| Nút thật | PLC tag | Địa chỉ |
|---|---|---|
| START | CHỌN AUTO | %I0.0 |
| STOP | NÚT DỪNG | %I0.5 |
| RESET | NÚT RESET | %I0.2 |

Với tiếp điểm khô và DI 24 VDC phù hợp: **+24 VDC → tiếp điểm nút → DI tương ứng**, common DI về 0 V theo sơ đồ phần cứng. Ngắt nguồn, đo thông mạch để xác định đúng cặp cọc và NO/NC trước khi đấu. Không đưa 220 VAC vào DI; kiểm tra các công tắc có sẵn trên bộ thực hành không giữ ép tín hiệu vào bằng 1.

Sáu ngõ ra %Q0.0…%Q0.5 lần lượt là bơm, van 1–4 và đèn lỗi. Phần này giữ cách đấu sáu đèn đã có; ảnh chưa đủ để xác nhận điện áp đèn hoặc số chân common relay. WinCC Runtime trên PC phải kết nối IP **PLC thật**, không dùng PLCSIM để xuất trực tiếp ra đèn thật.

Lưu bản sao project → tạo biến/timer → nhập đủ Network → sửa HMI → Compile PLC/HMI → thử trong PLCSIM → thử trên bộ sáu đèn. Kiểm tra thao tác chéo START thật → STOP HMI → tiếp tục bằng STOP thật; sau đó thử RESET, giữ nút, lỗi bảo vệ và hai mốc kết thúc ca.

## Kết quả kiểm tra và giới hạn

Mô hình Python đạt **25 nhóm, 0 lỗi**, gồm kiểm tra 86.400 mốc giây lịch chạy và 30.000 vòng quét ngẫu nhiên. [Xem mô tả](kiem_tra/README.md) và [kết quả JSON](kiem_tra/ket_qua_kiem_tra.json).

Đây là bản vẽ hướng dẫn dựng lại LAD, **không phải project TIA đã biên dịch hay file nhập trực tiếp**. Chưa Compile TIA, chạy PLCSIM hoặc CPU Siemens cho bản sửa này. Mô hình giả định mỗi vòng quét 10 ms, không chứng minh thời gian thực, chất lượng truyền thông, cấu hình HMI hoặc đấu dây thực tế.

Thiết kế dùng cho **mô hình sáu đèn**; STOP dạng nhấn lần hai để tiếp tục là lệnh vận hành, không thay cho dừng khẩn phần cứng.
