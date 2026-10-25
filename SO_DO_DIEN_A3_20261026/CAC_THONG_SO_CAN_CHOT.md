# Thông số phải chốt trước bản phát hành chính thức

Ngày lập: **26/10/2026**. Tình trạng hiện tại: **bản dự thảo nguyên lý**. Các thông số chưa có không cản việc dựng CAD, nhưng không được coi là đã lựa chọn hoặc kiểm tra an toàn.

| Mục | Nội dung bắt buộc xác nhận | Tác động tới bản vẽ |
|---|---|---|
| CPU | Tem đúng 6ES7214-1BG40-0XB0; sơ đồ đấu dây chính hãng đúng phiên bản; điện áp nguồn, khả năng tiếp điểm relay theo loại tải | Chốt tên chân, các nhóm common, tải relay, cầu chì và đầu nối |
| Nguồn cấp tủ | Có đủ L1/L2/L3/N/PE hay không; điện áp đo; sơ đồ tiếp địa; thiết bị cách ly/bảo vệ đầu nguồn | CPU/PSU phải lấy điện áp phù hợp L–N; nếu không có N phải thiết kế nguồn khác |
| Bơm | Tem motor CMA 0.75T thực tế: kW, điện áp Δ/Y, In, tần số và điều kiện tải | Xác nhận Y400 V hay phương án khác; cài OL1 và chọn dây/CB |
| KM1 | Đúng LC1D09BD cuộn 24 VDC; công suất hút/giữ; các tiếp điểm phụ sử dụng; khả năng phản hồi trạng thái, chống xung tích hợp | Xác nhận tải nguồn, liên động, cực tính và thời gian nhả |
| OL1 | Đúng LRD07 1,6–2,5 A; giá trị chỉnh theo tem; chế độ reset; chân 95–96 và 97–98 | Chốt ngưỡng và cách phục hồi sau quá tải; không mặc định chỉnh 1,8 A |
| YV1–YV4 | Hãng/model 2W160-15 thực tế; đúng bản 24 VDC; dòng/công suất từng cuộn, dòng hút/giữ; áp suất, môi chất, độ kín và chế độ làm việc | Chọn relay, cầu chì, nguồn, dây; xác nhận van thường đóng phù hợp thủy lực |
| KA0–KA4 | Model 24 VDC, ít nhất số tiếp điểm cần dùng; dòng tiếp điểm với tải DC cảm, công suất cuộn, chân đế | Hoàn thiện sơ đồ chân thật và khả năng đóng cắt; không chỉ so sánh dòng tải thuần trở |
| LS1/KSL | LS1 tiếp điểm khô hay cảm biến điện tử; đủ nước tương ứng trạng thái nào; model KSL, hai NO theo phương án; dòng cuộn | Sửa kiểu đấu đầu vào và điều kiện phần cứng chống chạy khô |
| Dừng khẩn/KSR | Model SB0 hai NC, KSR, điện áp, sơ đồ 2 kênh, reset giám sát, EDM, số tiếp điểm, dòng tải, yêu cầu đánh giá rủi ro | Thay cổng chức năng bằng terminal thật; xác định có cần thêm contactor và thay đổi kiến trúc hay không |
| Phục hồi sau lỗi | Hành vi khi nhả dừng khẩn, reset KSR, reset OL1, nước trở lại, mất/cấp lại điện, lệnh Q còn ON | Kiểm tra chống chạy lại ngoài ý muốn; có START mới; không coi reset là lệnh chạy |
| Bộ nguồn | Đúng NDR-120-24; nhiệt độ/điều kiện lắp; tổng tải lớn nhất và xung hút | Xác nhận 24 V/5 A đủ dùng, dây và phân nhánh; chưa kết luận khi thiếu dòng van |
| CB/cầu chì | Icc tại tủ; dòng khởi động; khả năng cắt và bảng phối hợp; đặc tuyến; định mức cầu chì các nhánh | Chốt A9F74306/A9F74110 hoặc cập nhật sau tính chọn; không tự thay model trong bản dự thảo |
| Dây/cầu đấu | Chiều dài, cách đi dây, nhiệt độ, mật độ dây, sụt áp, đầu cos, loại cầu đấu, tiết diện PE | Chốt tiết diện và dòng bảo vệ tương ứng; cập nhật bảng đấu nối |
| Chống xung/EMC | Module trên contactor/relay/van có sẵn hay không; chọn phần tử phù hợp; đường đi cáp, PE và 0 V | Tránh đấu sai cực hoặc kéo dài thời gian nhả; hoàn thiện bố trí tủ |
| Nút vận hành | SB_AUTO/SB_RESET/SB_STOP thực là NO hay NC, nhấn nhả hay duy trì | Thống nhất mức điện và bắt cạnh trong PLC; STOP không thay thế dừng khẩn |
| PLC/HMI | Tích hợp I0.0–I0.5 với DB/HMI; ưu tiên lỗi, STOP, reset; trạng thái nguồn/PLC; kiểm tra kết nối thật | Bản V1688 đang dùng HMI, chưa đủ để kết luận đầu vào thật sẽ điều khiển đúng |
| Kiểm thử | Đo cách điện/PE theo quy trình phù hợp; thử từng I/O với tải kiểm tra; thử mất tín hiệu, lỗi, phục hồi, lịch chạy, thứ tự van | Ghi kết quả đo và thử; rà soát trước khi thay tải đèn bằng bơm/van thật |

**Không ghi “đã kiểm tra an toàn”, không gán PL/SIL, không phát hành để thi công chỉ từ bộ bản vẽ này.** Sau khi có thông số, cần cập nhật đồng thời sơ đồ, bảng thiết bị, bảng đấu nối và các ghi chú của hai trang để không còn mâu thuẫn.
