# Bài thử Sweep Parallel cho cung khe đàn hồi

Add-in tạo một document Fusion mới và một mảnh mặt cong từ cung đo tại ba điểm. Bài thử tập trung vào cung có tọa độ X dịch chuyển theo chiều cao. Khe hoàn chỉnh được ghép từ các vùng có quy luật hình học riêng.

## Chạy và lấy bằng chứng

1. Trong Fusion, mở Utilities → Scripts and Add-Ins → Add-Ins và thêm thư mục `fusion/tests/SlotSweepTest` của checkout này.
2. Chọn `SlotSweepTest` và nhấn Run. Thư mục `fusion/SnaplockStorageBox` cung cấp helper đi kèm trong cùng checkout.
3. Hộp thoại báo trạng thái và đường dẫn `results/last-run.json`. Document giữ hình học tại bước xảy ra lỗi để quan sát.
4. Log ghi stage, hash hai source, phiên bản Fusion, hướng sketch, constraint, feature health, timeline, tham số và phép đo bề mặt.
5. Khi trạng thái là `passed`, document đã trải qua chiều dày 6 → 5 → 6,5 → 6 mm. Change Parameters tiếp tục điều khiển `latch_thickness` trong miền thử 5–6,5 mm.

## Hình học và cập nhật tham số

Cung đo đi qua `(-0.383,15.751)`, `(-0.4699,16.2434)`, `(0,16.5724)` mm trước khi cộng độ dịch X. Đường tròn qua ba điểm có bán kính xấp xỉ 0,499953593 mm. Độ dịch của cung tuân theo `c(z)=1.359+0.2976*sqrt(25-(z-t/2)^2)` mm với `t=latch_thickness`.

Đường đi của đầu cung nằm trên elip có bán trục X=1,488 mm, Z=5 mm và tâm X=0,976 mm. Sweep Parallel giữ cung song song mặt XY. Hai sketch chứa hình học đo cố định; người chỉnh chiều dày thao tác qua User Parameter, Move và mặt phẳng cắt trên.

Patch ban đầu phủ khoảng Z=0–8 mm. Move đặt tâm tại `t/2`, hai Split Body cắt tại Z=0 và Z=t, hai Remove giữ mảnh giữa. Timeline dự kiến gồm 2 plane, 2 sketch, 1 Sweep, 1 Move, 2 Split và 2 Remove, tổng cộng 10 item và 0 Loft. Hình học đo trong sketch dùng Fix; việc thay đổi bán trục hoặc điểm đo thuộc bước chỉnh hình học của bài thử.

Log kiểm tra 231 điểm tham chiếu mỗi biến thể và lưới UV 21×21 trên từng face theo chiều ngược lại. Mẫu UV được lọc theo biên face. Residual chiều ngược đo đến cung tham chiếu tại cùng Z và cung biên khi Z vượt miền. Ngưỡng 0,001 mm phục vụ xác nhận công thức của patch. Ngưỡng sản xuất 0,03 mm của model được giữ theo baseline riêng.

Phiên bản 0.1.1 Fix các curve và các SketchPoint riêng của hai sketch hằng, gồm tâm và đầu cung. Log `constraints_before_fix`, `constraints_after_fix` và `sketch_constraints` ghi trạng thái từng đối tượng. Các feature Move và Split tiếp tục điều khiển chiều dày qua expression.

## Mốc xác nhận

Source có kiểm tra công thức offline cho đường elip, ba điểm đo, dịch chuyển cứng và khả năng phát hiện điểm lệch. Chạy native cung cấp bằng chứng cho solver, Sweep và cập nhật timeline. Tích hợp vào khe hoàn chỉnh tiếp nối mốc native đạt, ghép mặt kín và so sánh toàn bộ latch với SCAD/STL.

Lần chạy native của 0.1.0 đã tạo một surface body với 10 timeline item healthy tại chiều dày 6 mm và dừng ở contract fully constrained của hai sketch. [Log native 0.1.1 đã đối chiếu hash](../../../docs/validation/slot-sweep-native.json) xác nhận cả hai sketch fully constrained, một face và 10 timeline item healthy qua chiều dày 6 → 5 → 6,5 → 6 mm trên Fusion 2705.1.30. Mỗi cấu hình đo 231 điểm theo chiều thuận và 441 điểm theo chiều ngược; residual lớn nhất là 0,0008 mm so với ngưỡng 0,001 mm.

Log trước Fix điểm xác nhận cả hai curve đã fixed/fully constrained trong khi hai đầu cung của mỗi curve vẫn tự do. Fix bổ sung các điểm đưa cả hai sketch về fully constrained. Bài học áp dụng cho sketch hằng đo từ mẫu: curve và SketchPoint có trạng thái ràng buộc riêng; agent kiểm tra từng đối tượng và contract toàn sketch.

Độ dịch X khởi tạo profile trong 0.1.1 là 2,251 mm; công thức elip tại đầu patch cho 2,2518 mm. Chênh 0,0008 mm này khớp residual quan sát. Mốc native giữ nguyên source đã đo; bước tích hợp dùng công thức chung cho điểm đầu profile và đường dẫn, đồng thời đối chiếu lại toàn bộ khe.

## Quyết định sử dụng trong model

Khe Snaplock hiện tại tiếp tục dùng Loft tám tiết diện liên kết với `latch_thickness`. Phần trước khe có 7 plane mới, 8 sketch và 1 Loft, tổng 16 bước theo source, tạo toàn bộ khối dụng cụ phía trước. Bài thử Sweep có 10 bước native cho một mặt cung. Mỗi số đếm đi cùng phạm vi đầu ra tương ứng.

Agent đánh giá ứng viên thay thế toàn khe bằng tổng bước hoàn thiện cùng hình học, số đầu vào sửa độc lập, công thức, sai lệch và thời gian. Chiều dày của cả hai cách cập nhật qua tham số; hình dạng cung/đường elip của bài thử dùng sketch hằng với Fix. Phép dựng trực tiếp được ưu tiên khi tạo mô hình gọn và dễ chỉnh. Loft nhiều tiết diện liên kết công thức được giữ khi đáp ứng các tiêu chí tốt hơn phương án thay thế.

## Nguồn Autodesk

- [Sweep Parallel và các chế độ hướng profile](https://help.autodesk.com/cloudhelp/ENU/Fusion-Patch/files/SFC-SWEEP.htm).
- [SweepFeatureInput.orientation](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/fusion_SweepFeatureInput_orientation.htm).
- [Cung elip từ tâm, bán trục và góc](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/fusion_SketchEllipticalArcs_addByAngle.htm).
- [Open profile từ một cung](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/fusion_Component_createOpenProfile.htm).
- [Split Body hỗ trợ open body và construction plane](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/fusion_SplitBodyFeatures_createInput.htm).
- [Tham số bề mặt tại điểm](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/core_SurfaceEvaluator_getParameterAtPoint.htm) và [kiểm tra biên face](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/core_SurfaceEvaluator_isParameterOnFace.htm).
