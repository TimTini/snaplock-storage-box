# LoftSketchTest — nhiều Plane → Sketch, một Loft

Loft tạo hình bằng cách nối các tiết diện theo thứ tự. Bài thử tạo năm vòng tròn ở năm cao độ, với đường kính thay đổi 20 → 30 → 18 → 28 → 16 mm. Một Loft nối cả năm vòng tròn thành một khối đặc có thân phình, eo và miệng thu nhỏ. Extrude kéo một biên dạng theo hướng; Loft cho phép biên dạng thay đổi giữa các tiết diện.

## Chạy trong Fusion

1. Mở **Utilities → Add-Ins → Scripts and Add-Ins → Add-Ins**.
2. Bấm **+**, chọn thư mục `LoftSketchTest` chứa Python và manifest.
3. Chọn **LoftSketchTest → Run**. Bài thử tạo một document mới tên `LoftSketchTest_5_sections`.
4. Xem timeline: **Plane 01 → Section 01 → Plane 02 → Section 02 → Plane 03 → Section 03 → Plane 04 → Section 04 → Plane 05 → Section 05 → Loft**.
5. Bật từng `Section` trong Browser để thấy năm vòng tròn bên trong khối. Bật các `Plane` để thấy năm mức cao độ.
6. Dùng marker timeline kéo về ngay trước Loft để quan sát trạng thái có đủ năm sketch. Kéo marker về cuối để xem khối tạo ra từ chúng.
7. Mở **Modify → Change Parameters**, chỉnh `loft_height` và `diameter_scale` để quan sát các plane, sketch và khối cùng cập nhật.
8. Dùng **Stop → Run** để tạo một document thử mới.

Năm plane được tính từ Origin XY theo `5 mm + loft_height * i / 4`, với `i` từ 0 đến 4. Mỗi vòng tròn có tâm cố định tại X=15 mm, Y=0 trong sketch; đường kính dùng biểu thức liên kết `diameter_scale`. Ở cấu hình đầu, các cao độ là 5, 15, 25, 35, 45 mm. Khi chiều cao đổi từ 40 lên 60 mm, các cao độ trở thành 5, 20, 35, 50, 65 mm.

## Chuỗi bước và log

Script dựng đủ năm cặp Plane → Sketch trước, sau đó đưa năm profile vào cùng một Loft. Timeline dự kiến gồm 11 mục: 5 plane, 5 sketch và 1 Loft. Mỗi sketch là một đầu vào của Loft cuối chuỗi.

`results/last-run.json` được cập nhật sau từng checkpoint và giữ local qua `.gitignore`. Log gồm hash source, thời gian UTC, tên plane/sketch, công thức, số timeline tại từng bước và danh sách profile của Loft. Ba checkpoint `initial`, `variant`, `restored` ghi số plane/sketch/loft/body, timeline health, cao độ thực tế của plane/sketch, đường kính thực tế, trạng thái fully constrained, bounds Z và thể tích khối.

Biến thể tự động dùng `loft_height = 60 mm`, `diameter_scale = 1.2`, rồi phục hồi `40 mm` và `1`. Kiểm tra runtime đối chiếu từng tiết diện với công thức, khối solid có thể tích dương và chiều cao đúng. Giá trị `status: passed` ghi nhận lần chạy native hoàn tất; `status: failed` kèm traceback và log tới checkpoint gần nhất hỗ trợ kiểm tra document đang mở.

Checkpoint bàn giao gồm kiểm tra cú pháp, manifest, source và tài liệu API. Lần chạy trong Fusion cung cấp bằng chứng native về timeline và hình học trên máy sử dụng.

## Nguồn

[Loft Feature API Sample của Autodesk](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/LoftFeatureSample_Sample.htm) minh họa việc tạo nhiều sketch trước, thêm từng profile vào `loftSections`, rồi gọi tạo một Loft. Bài thử này sử dụng năm tiết diện và cấu hình solid.
