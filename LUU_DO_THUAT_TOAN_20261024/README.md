# Lưu đồ thuật toán điều khiển đài phun nước

Lưu đồ theo yêu cầu công nghệ trong phiếu giao đề tài và phương án [LAD rút gọn, HMI + ba nút thật](../LAD_RUT_GON_BIEN_20261024/README.md).

- **[Tải PDF: ba trang A3, phóng to không vỡ nét](Luu_do_thuat_toan_dai_phun_nuoc.pdf)**.
- **[Tải Word: mục 2.2 và ba hình lưu đồ](Muc_2_2_Luu_do_thuat_toan.docx)**.
- [Hình 1 — điều khiển tổng thể](hinh/01_luu_do_tong_the.png).
- [Hình 2 — xử lý lệnh và bảo vệ](hinh/02_lenh_va_bao_ve.png).
- [Hình 3 — chu trình năm bước](hinh/03_chu_trinh_5_buoc.png).
- [Mã nguồn Graphviz để chỉnh hình](nguon/).

## Nội dung

1. **Lưu đồ tổng thể:** đọc lệnh và RTC, xác định lịch, gọi xử lý bảo vệ, xét AUTO/tạm dừng, thực hiện chu trình và cập nhật ngõ ra/HMI.
2. **Lệnh và bảo vệ:** thiếu nước, quá tải, dừng khẩn, lỗi đọc RTC; ghi nhớ lỗi; RESET; cấp/hủy AUTO; STOP tạm dừng/tiếp tục.
3. **Chu trình:** năm bước, mỗi bước 10 giây; bốn van lần lượt `1000 → 1100 → 1110 → 1111 → 0101`, rồi lặp lại.

Lịch vận hành: **06:00 ≤ t < 08:00** hoặc **17:00 ≤ t < 20:30**. Bơm có lệnh ON liên tục khi chu trình hoạt động bình thường. Hết ca đưa bước và timer về 0, giữ AUTO để chờ ca sau.

## Phân biệt yêu cầu đề và cách triển khai

Phiếu giao đề tài yêu cầu dừng khi hết giờ, nhấn dừng, bơm quá tải hoặc nước thấp. Phương án PLC đã thống nhất bổ sung: STOP giữ bước/thời gian và nhấn lần hai để tiếp tục; RESET; nhớ lỗi; dừng khẩn giả lập; phối hợp HMI với START/STOP/RESET thật. Những chức năng bổ sung này được thể hiện trong lưu đồ.

- STOP trong ca: giữ bước và thời gian; bơm/van OFF.
- STOP lần hai: tiếp tục nếu còn đủ điều kiện chạy.
- Hết ca khi đang tạm dừng: bước và timer về 0, AUTO và trạng thái tạm dừng vẫn giữ; ca sau cần nhấn STOP để tiếp tục từ bước 1.
- RESET/TẮT/lỗi: hủy AUTO, xóa tạm dừng, bước và timer về 0. Lỗi hết vẫn phải RESET hợp lệ rồi nhả RESET và nhấn START mới.
- Timer được gọi mỗi vòng quét. Khi tạm dừng, chỉ timer bước hiện tại giữ ET với IN=0, R=0; timer các bước khác được reset. Không bỏ qua việc gọi timer khi dừng.
- RTC đọc hợp lệ không chứng minh đồng hồ đã được cài đúng giờ/múi giờ.

Bản Word là tài liệu riêng để chèn vào mục 2.2; không thay đổi bản đồ án gốc. Đây là tài liệu thuật toán, không phải project nhập trực tiếp vào TIA Portal. Không công bố phiếu giao đề tài gốc hoặc thông tin cá nhân trong đó.
