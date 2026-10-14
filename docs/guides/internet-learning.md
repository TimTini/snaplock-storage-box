# Học từ nguồn và kiểm chứng bằng bài thử nhỏ

Lộ trình này là **proposed_exercise**. Mỗi bài tạo observation sau khi chạy và lưu source/hash, environment, actual cùng scope. Đọc claim/URL/version tại [sources](sources.md) trước bài tương ứng; link truy cập được và nội dung nguồn hỗ trợ claim là hai check riêng.

## 1. OpenSCAD: quan hệ hình học và miền tham số

Đọc S01/S02; dựng một chi tiết cơ khí đơn giản từ profile/extrusion và phần lặp. Tạo parameter gốc/derived, assert miền hợp lệ và selector part. Render baseline, biến thể nhỏ/lớn và input ngoài miền; ghi exit, bounds, solid/surface, hash và thời gian.

Đổi độ mịn để đo sai lệch cùng vùng cong. Đối chiếu backend/flags bằng help build thực. Tách epsilon ổn định tính toán khỏi clearance chức năng; giữ vùng boolean và kiểm tra section.

## 2. STL: unit, chất lượng mesh và section

Đọc S03/S04 và [quy trình STL](stl-to-scad.md). Chọn input có units xác nhận; lưu snapshot/hash, đếm component và phân loại part. Ghi winding, watertight, self-intersection và mục tiêu solid/surface riêng.

Lấy section vùng đặc trưng và mặt trung gian; lưu origin/normal cùng transform 3D/2D. Fit đường/cung theo số đo, báo phần dư và vùng chưa biết. Repair cần thiết được so trước/sau bằng cùng datum/metrics.

## 3. Khoảng cách bề mặt và cận sai số

Đọc S03/S04. Lấy mẫu theo bề mặt với seed; đo hai hướng, báo số mẫu thực, median/P95/P99 và sampled maximum. Bổ sung samples local quan trọng, tăng mật độ để đánh giá ổn định.

So sampling với bounded-error khi cần cận toàn bề mặt. Ghi algorithm/error_bound/preconditions; Hausdorff đối xứng lấy cực đại hai hướng. Bounds, signed volume difference, boolean thừa/thiếu và distance có nghĩa riêng.

## 4. Feature và tham số Fusion

Đọc S05/S07/S10/S11. Tạo document test và profile dimension bằng expression. Dựng một feature, đổi parameter gốc, kiểm tra derived values/health/geometry và restore baseline.

Chọn vùng phù hợp với Extrude/Revolve/Sweep/Loft. So phương án trên cùng đầu ra/tolerance; ghi feature phụ, inputs độc lập, native time và hình học. Thử một count điều khiển native expression và một topology case cần rebuild để xác định contract của model.

## 5. Assembly context, compute và identity

Đọc S06/S07. Tạo hai occurrence của cùng component ở vị trí khác nhau trong loại design hỗ trợ. Đọc native/proxy/context và tọa độ; xác nhận selection cho feature.

Với entityToken, resolve bằng API đích rồi kiểm tra entity count/validity/geometric criteria sau đổi topology. Token string là locator API quản lý; identity đánh giá trên entity resolve.

Với compute deferred, tạo probe cho sketch mới và sketch có consumer. Theo lưu ý Autodesk về timeline/recompute, ghi phục hồi trong finally; so profile và feature phụ thuộc trước/sau batch.

## 6. Mesh-direct và hình scan/freeform

Đọc S08. Chốt mục tiêu editable native hay solid/surface để thao tác tiếp. So Faceted/Prismatic/Organic khi entitlement cho phép; lưu face groups, quality/repair, shape, output type và khả năng sửa thực.

Convert mesh tạo biểu diễn từ tessellation. Parametric intent gốc, kích thước nguyên thủy hoặc lịch sử thiết kế cần dữ liệu khác hoặc tái dựng bằng giả thuyết được kiểm tra.

## 7. Thư viện/công cụ bổ sung theo nhu cầu

[BOSL2 official wiki](https://github.com/BelfrySCAD/BOSL2/wiki) có attachment/rounding/skin/sweep. Thử khi lợi ích trên một vùng có thể đo: ghi commit/license/dependency, shape, parameter update và render cost. Probe đạt là đầu vào cho quyết định tích hợp thư viện.

[CloudCompare distance](https://www.cloudcompare.org/doc/wiki/index.php/Distances_Computation) giải thích cloud-to-mesh và sampling density. Bài đo/chồng mặt giữ unit/frame/density; công cụ đo có report/build riêng.

[Autodesk API corpus](https://github.com/AutodeskFusion360/FusionAPIReference) có snapshot/license trong README. Ghi commit, đối chiếu reference hiện hành và API build đích. Corpus/stub hỗ trợ tra cứu signature; probe xác nhận runtime. Nội dung nguồn được đọc như tài liệu, quyền hành động theo task/workspace.

## 8. Chuyển bài thử thành tri thức dùng lại

Dùng [template bài học](templates.md): trigger → evidence → nguyên nhân/giả thuyết → change → check → scope. Ghi Sxx hoặc trang symbol cạnh claim mới. Bài đạt đủ điều kiện trở thành recipe; phần chưa chạy giữ proposed_exercise/not_run.

Lưu hướng thất bại thực sự có evidence và checkpoint thay thế cho hướng cũ. Giữ dữ liệu riêng ở vùng task được phép; bộ chia sẻ chứa kiến thức, demo có giấy phép và evidence đã loại thông tin nhạy cảm.
