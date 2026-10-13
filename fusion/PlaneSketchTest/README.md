# PlaneSketchTest — thử mặt phẳng và sketch trong Fusion

Add-in tạo ba document mới, mỗi document có ba trụ cùng hình học. Mỗi lần Run thực hiện bài thử trực tiếp. Document đang mở được kích hoạt lại khi bài thử kết thúc; ba document thử vẫn nằm trong các tab của Fusion.

| Document | Cách dựng | Plane tạo thêm | Sketch | Extrude | Timeline dự kiến |
|---|---|---:|---:|---:|---:|
| A_separate_planes | Mỗi sketch có một offset plane riêng ở cùng Z | 3 | 3 | 3 | 9 |
| B_shared_plane | Ba sketch dùng chung một offset plane | 1 | 3 | 3 | 7 |
| C_extrude_offset | Ba sketch trên XY; Extrude dùng Start Offset | 0 | 3 | 3 | 6 |

Các số trong bảng là kỳ vọng để đối chiếu với số đếm thực tế. Mặt phẳng XY có sẵn thuộc Origin; cột Plane đếm construction plane do bài thử tạo thêm. Mỗi timeline giữ riêng sketch và feature để việc so sánh tập trung vào cách đặt cao độ.

## Chạy

1. Mở Fusion, vào **Utilities → Add-Ins → Scripts and Add-Ins**.
2. Chọn tab **Add-Ins**, bấm **+**, chọn thư mục `PlaneSketchTest` chứa file Python và manifest.
3. Chọn **PlaneSketchTest → Run**. Add-in tạo ba document và hiện kết quả.
4. Chuyển qua các tab `PlaneSketchTest_A_…`, `PlaneSketchTest_B_…`, `PlaneSketchTest_C_…` để xem timeline. Bật sketch/plane trong Browser để quan sát vị trí của chúng.
5. Mở **Modify → Change Parameters**, chỉnh `demo_z`, `demo_diameter`, `demo_height`. Khoảng cách tâm cố định 25 mm; dùng đường kính nhỏ hơn 25 mm để giữ ba trụ tách nhau.
6. Dùng **Stop → Run** trong tab Add-Ins để thực hiện lại bài thử và tạo bộ document mới.

## Kiểm chứng lúc chạy

Bài thử kiểm tra ba trạng thái: Z 10 mm / đường kính 10 mm / cao 4 mm; Z 18 mm / đường kính 12 mm / cao 6 mm; rồi phục hồi trạng thái đầu. Mỗi trạng thái kiểm tra số body, số feature, timeline health, sketch fully constrained, bounds và thể tích từng trụ theo công thức. Mỗi thiết kế được đối chiếu với cùng một bộ kỳ vọng hình học.

`results/last-run.json` ghi hash source, số đếm thực tế và kết quả từng trạng thái. Giá trị `status: passed` ghi nhận một lần chạy native hoàn tất. `status: failed` kèm traceback hỗ trợ chẩn đoán; document thử được giữ để xem feature. Báo cáo này được giữ local qua `.gitignore`.

Checkpoint bàn giao gồm kiểm tra cú pháp Python, manifest JSON và đối chiếu API chính thức. Lần chạy trong Fusion cung cấp bằng chứng native cho máy đang sử dụng.

## Plane và sketch có vai trò riêng

Plane xác định vị trí và hướng của mặt phẳng vẽ trong không gian. Sketch chứa đường, cung và kích thước trên mặt phẳng đó. Extrude hoặc Loft sử dụng profile của sketch để tạo hình khối. Vì vậy timeline có thể ghi ba bước riêng: **Plane → Sketch → Feature**.

Sketch có thể đặt trực tiếp trên mặt phẳng Origin, trên một construction plane đã có hoặc trên mặt phẳng phẳng của body. Nhiều sketch có thể dùng chung một plane. Với phép Extrude thẳng, Start Offset đặt vị trí bắt đầu của khối ngay trong feature; trường hợp C minh họa cách này. Với sketch tham số, vị trí sketch được điều khiển bởi hình học tham chiếu của nó.

Trong script Snaplock, `Native.profile()` gọi `Native.plane()` trước mỗi sketch. `Native.plane()` dùng lại base khi offset là chuỗi `0 mm`; các offset khác tạo construction plane riêng. `build_latch()` tạo 25 tiết diện răng khóa và 25 tiết diện khe đàn hồi theo cùng 25 mức chiều dày. Tại mỗi mức, hai sketch có thể chia sẻ một plane; hai sketch phục vụ hai loft riêng. Số lượng 25 tiết diện là lựa chọn lấy mẫu biên dạng của bản dựng hiện tại. Thay đổi số tiết diện cần đối chiếu lại hình học của răng và khe.

Plane dùng chung biểu diễn một datum chung. Hai plane độc lập biểu diễn hai vị trí có thể điều khiển độc lập về sau. Khi chia sẻ plane trong model tham số, nhóm các sketch theo cùng datum và cùng biểu thức offset; giữ liên kết biểu thức khi giá trị hiện tại bằng zero.

## Nguồn API

- [Sketches.add — construction plane hoặc planar face](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/fusion_Sketches_add.htm).
- [ConstructionPlaneInput.setByOffset](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/fusion_ConstructionPlaneInput_setByOffset.htm).
- [ExtrudeFeatureInput.startExtent](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/fusion_ExtrudeFeatureInput_startExtent.htm).
- [OffsetStartDefinition.create](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/fusion_OffsetStartDefinition_create.htm).
- [Sketch.transform — vị trí sketch tham số theo hình học tham chiếu](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/fusion_Sketch_transform.htm).
