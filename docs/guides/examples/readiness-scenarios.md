# Tình huống kiểm tra tiếp nhận và độ bao phủ

Đây là bài kiểm tra đọc hiểu/quyết định của bộ tài liệu, không phải kết quả CAD native. Các tình huống dùng dữ liệu giả định được khai báo rõ để đánh giá agent trước khi đưa input thực. Dùng [START-HERE](../START-HERE.md) và [job template](../templates.md).

## A. Một part cơ khí, cần SCAD editable

Task giả định: STL của một giá đỡ đơn, đơn vị mm đã có số đo kiểm chứng; mục tiêu thay chiều rộng và bề dày, bàn giao SCAD/STL. Khổ máy và Fusion không thuộc yêu cầu.

Acceptance tiếp nhận: agent chọn inspection → reconstruction SCAD → variants/mesh audit; lập tham số/bề dày/datum/tolerance từ task. Fusion native và assembly nhiều part mang not_applicable. Agent ghi metrics/reference hash, không lấy part count/cơ cấu/khổ của ví dụ khác làm mặc định.

## B. Mesh scan hở, chưa xác định đơn vị

Task giả định: mesh một bề mặt hữu cơ có lỗ, mục tiêu đo kích thước và chuyển sang Fusion.

Acceptance: agent ghi blocked cho absolute dimensions/tolerances tới khi có căn cứ units; vẫn phân tích component/holes/topology không phụ thuộc scale. Agent phân biệt surface với solid và route mesh/Organic theo capability. Volume boolean giữ blocked khi chưa có solid đáng tin. Repair dùng copy và nêu ảnh hưởng; input gốc giữ hash.

## C. SCAD đã có, cần Fusion native nhưng máy chưa có Fusion

Task giả định: source tham số và baseline mesh đủ; native là deliverable, host hiện chỉ có Python/OpenSCAD.

Acceptance: agent chuẩn bị contract/feature mapping/source/offline evidence; native blocked/not_run cùng yêu cầu runtime cụ thể. Handoff có commands, source/input hashes, versions và next native probe. Task vẫn chưa hoàn tất acceptance native.

## D. Assembly có tiếp xúc và thay đổi count

Task giả định: ba part có một khớp quay, count các lỗ có miền biến thiên; một count được native Pattern expression điều khiển, count khác được Python loop tạo lúc Run.

Acceptance: agent lập contact pairs/transforms, phân biệt hai loại count, thử recompute cho Pattern và rebuild cho loop khi cần. Pose sampled_motion và toàn hành trình có phạm vi chứng cứ riêng. Các tiếp xúc thiết kế có threshold/rule, không dùng giao bằng 0 làm điều kiện duy nhất cho mọi cặp.

## E. Chỉ cần sửa mesh trực tiếp

Task giả định: model hữu cơ có units/quality đủ, chỉ cần một chỉnh sửa cục bộ và output solid/surface để dùng tiếp.

Acceptance: agent đánh giá Mesh tools/Convert Mesh trước khi chốt route; ghi output type, method/entitlement, approximation và khả năng chỉnh thực. SCAD là lựa chọn theo mục tiêu, không là giai đoạn bắt buộc.

## F. Chuyển bộ sang đường dẫn mới và làm việc offline

Task giả định: chép toàn guides tới thư mục có khoảng trắng; Internet tạm vắng; có Python chuẩn.

Acceptance: validator/tests chạy từ cwd khác; core links vẫn nằm trong bundle; agent đọc workflow và registry offline, ghi trạng thái nguồn đã đối chiếu theo ngày lưu. Runtime/native hoặc việc làm mới nguồn giữ scope thiếu tương ứng.

## G. Nguồn mâu thuẫn với runtime

Task giả định: symbol có trong corpus cũ nhưng build đích thiếu hoặc signature khác.

Acceptance: agent ghi source snapshot/build và lỗi probe thật, đọc reference đúng version, giữ unresolved/blocked cho phần phụ thuộc. Chỉ chọn phương án thay thế sau khi đã hiểu contract; bài học lưu điều kiện thất bại thực, không che lỗi bằng retry.

## Cách chấm và ghi kết quả

Mỗi scenario ghi intake, route, dữ liệu còn thiếu, commands/checks, trạng thái các lớp và lý do. Đạt khi quyết định phù hợp facts đã khai báo và được dẫn từ workflow; sai khi tự giả định units, biến part/cơ cấu/khổ ví dụ thành mặc định, hoặc dùng offline làm bằng chứng native/physical.

Thay facts giả định bằng input thực và chạy đúng check để xác nhận một model mới. Báo cáo bản phát hành ghi riêng review scenario ở mức tài liệu với runtime model đã chạy.
