# Hồ sơ kiểm chứng Snaplock

Các bản sao trong thư mục này giữ số đo, hash source và kết quả của các checkpoint ngày 12–13/10/2026. Đường dẫn máy local đã được lược bỏ trong bản công khai. File log gốc và lịch sử thao tác được bảo quản trong bản sao local riêng.

| Bằng chứng | Phạm vi |
|---|---|
| [Ma trận 65 cấu hình](latch-size-matrix.json), [CSV](latch-size-matrix.csv) và [ảnh lắp](latch-size-assemblies.png) | 54 cấu hình đạt tiêu chí latch, 10 cấu hình đổi chiều cao nắp cấn latch, một thân 25 mm mặc định bị SCAD từ chối; tiếp xúc thân–nắp/bản lề ghi riêng |
| [Lắp latch minimum](latch-minimum-fit.json) và [mặt cắt](latch-minimum-fit-sections.png) | Đúng STL bộ minimum đã in; nắp 11,7 mm hạ ổ cầu/răng 3,3 mm; đối chứng nắp 15 mm giữ Body/Latch và giảm giao latch–thân từ 34,684 xuống 0,000173 mm³ |
| [Gân Fusion offline](fusion-reinforcement-offline.json) | 24 phép CSG từ biểu thức native so SCAD, ba kích thước × tám tổ hợp công tắc; lần Run Fusion xác nhận solver/kernel và cập nhật Pattern |
| [Gân trong SCAD](scad-reinforcement.json) | Ba công tắc, đủ tám tổ hợp bật/tắt và 27 cấu hình; baseline và bản gân cao/chân lớn; khoảng hở nắp đóng và năm góc mở lấy mẫu; preset 240 × 220 × 100 mm cho khổ sử dụng 250 mm |
| [Sweep Parallel native](slot-sweep-native.json) | Cung khe dịch chuyển, 2 plane/2 sketch/0 Loft, 10 timeline item healthy, fully constrained và chiều dày 6 → 5 → 6,5 → 6 mm; residual lấy mẫu lớn nhất 0,0008 mm |
| [SCAD mặc định](scad-audit-default.json) và [biến thể](scad-audit-variant.json) | Mesh kín, bounds và sai khác thể tích của SCAD |
| [Răng SCAD tròn/elip](scad-catch-csg.json) và [ảnh mặt cắt](scad-catch-csg-sections.png) | So sánh snapshot, STL và ba chiều dày; khoảng cách lấy mẫu hai chiều và timing tham khảo |
| [Khe hybrid](scad-slot-hybrid.json), [bộ thử tiết diện](scad-slot-section-probes.json) và [ảnh đối chiếu](scad-slot-hybrid.png) | Đuôi Extrude, tám tiết diện trước; ngưỡng 0,03 mm và ba chiều dày |
| [Số đo tham chiếu](reference-measurements.json) | Kích thước và hệ tọa độ đo từ mẫu |
| [Log native thành công](fusion-native-success.log) | Source `4cad327e…`, bốn body, sketch/feature và hai biến thể recompute |
| [Thể tích mesh streaming](fusion-native-export-metrics.json) | Số tam giác, hash, bounds và thể tích có dấu của STL Fusion |
| [Lỗi sketch đầu tiên](fusion-latch-constraint-failure.log) | Trạng thái lần chạy lỗi của source ghi trong log |
| [Chẩn đoán cạnh tự do](fusion-free-lines-failure.log) | Điểm đủ ràng buộc, bốn cạnh tự do của `Latch plate` |

Source native thành công có SHA256 `4cad327eab71f336bfe42e6dca9e688672e2635e3ba56e83fd2be63386d688f3`. Source Python bản sửa thứ tự profile có SHA256 `e09a82813f0831d98fec28d0dcf609ff71ad05832a74064c11d83f16cc5cf2f2`. Mỗi hash xác định phạm vi bằng chứng của phiên bản tương ứng.

Bản sửa thứ tự profile đang ở mốc kiểm chứng offline với 28 test. Lần chạy native tiếp theo xác nhận tác dụng trong Fusion. Sai khác đối xứng của STL Fusion, khoảng cách bề mặt và thử lắp/in là các mốc kiểm chứng tiếp theo.
