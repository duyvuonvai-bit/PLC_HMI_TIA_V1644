# Báo cáo đánh giá V1688 — 25/10/2026

Đối tượng đánh giá: [PLC_HMI_TIA_V1688](https://github.com/duyvuonvai-bit/PLC_HMI_TIA_V1688/tree/aae862c01ddf4d1225ce9127cda915b7a7da8b55), commit `aae862c01ddf4d1225ce9127cda915b7a7da8b55`. Báo cáo được lưu trên nhánh tài liệu review đã dùng trước; không thay đổi chương trình trong repo V1688.

- **[PDF báo cáo đầy đủ](Bao_cao_danh_gia_PLC_HMI_V1688.pdf)**: cấu trúc, đánh giá 18 Network, lỗi/nguy cơ, rút gọn, đối chiếu biến, HMI, ưu tiên xử lý và chấm điểm.
- [Bản Word để ghi chú/chỉnh thuyết minh](Bao_cao_danh_gia_PLC_HMI_V1688.docx).
- **[PDF 40 tình huống kiểm thử](Bo_40_tinh_huong_PLCSIM_V1688.pdf)**.
- [CSV 40 tình huống để điền kết quả](Bo_tinh_huong_PLCSIM.csv).
- [Báo cáo đọc trực tiếp trên GitHub](DANH_GIA_V1688.md).
- [Bảng đối chiếu PLC/DB/HMI](BANG_DOI_CHIEU_BIEN.md).
- [Nguồn ảnh theo từng Network](NGUON_ANH.md).
- [Kiểm chứng logic độc lập và giới hạn](kiem_tra/README.md).

## Những kết luận chính

- Chưa thấy lỗi điều khiển xác định ở lịch, bảng năm bước van, thứ tự timer/chốt bước hoặc ưu tiên RESET của bản đã đọc.
- Toàn bộ 29 trường DB có dùng. Chưa khuyên xóa ngay trường DB nào.
- Sáu input I0.0–I0.5 chưa được đọc trong LAD; điều khiển/bảo vệ đang nhận từ HMI. HMI_DUNUOC vẫn trỏ I0.1, khác HMI_DU_NUOC đọc DB.
- Cần làm rõ đèn AUTO đang đọc trạng thái trong ca; bước0 có thể hiện còn10s nếu STOP đã1 trước AUTO; lỗi tổng có thể còn lưu khi nguyên nhân đã hết.
- Có thể rút hai tiếp điểm /HỦY ở NW8 và năm tiếp điểm TỰ ĐỘNG CHẠY ở các rung Q→MOVE NW10–14; giữ đúng thứ tự và các điều kiện reset timer. Có thể gộp điều kiện reset hai biến bước tại NW15.
- Hiện nên giữ ĐÃ GẠT TẮT và /hmi_stop riêng rung bơm. Việc rút chúng chỉ được chứng minh khi đầu vào HMI nhất quán theo scan; không suy rộng kết quả mô hình sang mọi ghi DB bất đồng bộ.
- Điểm phần thiết kế có đủ căn cứ: **76/90**; **10 điểm kiểm thử/vận hành chưa chấm**, chưa kết luận tổng trên100.

Chấp nhận xác nhận của người dùng: FirstScan thay OB100; Events HMI đúng; ảnh Network đã đủ. Không sửa PLC, HMI hoặc các tag của project.

40 tình huống đều để **Chưa chạy PLCSIM**. Kiểm chứng Python là kiểm chứng biểu thức/trạng thái độc lập, không phải thử TIA/PLCSIM, không chứng nhận thời gian IEC timer hoặc bảo vệ bơm thật.
