# Nguồn internet cho agent học OpenSCAD và kiểm chứng hình học

Mốc tham khảo: **13/10/2026**. Bộ nguồn gồm tài liệu của OpenSCAD, BOSL2, Trimesh và CloudCompare. Mỗi mục gắn kiến thức với bài thực hành và bằng chứng cần lưu. Các bài thực hành dưới đây là đề xuất tổng hợp từ nguồn; kết quả áp dụng được ghi sau mỗi lần chạy thực tế.

## 1. OpenSCAD: dựng bằng quy luật và phép dựng có sẵn

Nguồn: [Documentation](https://openscad.org/documentation.html) và [Cheat Sheet](https://openscad.org/cheatsheet/).

Trang Documentation dẫn tới hướng dẫn tham số, module, vòng lặp, extrusion, nhập/xuất và dòng lệnh. Cheat Sheet giúp chọn primitive, phép boolean, `offset`, `hull`, `minkowski`, `linear_extrude` và `rotate_extrude`. Agent dùng `$fa`, `$fs`, `$fn` để quản lý độ mịn và dùng modifier xem riêng vùng đang phân tích. Cheat Sheet mang nhãn phiên bản 2021.01; agent đối chiếu tính năng với phiên bản OpenSCAD đang chạy.

Bài thực hành: dựng hộp từ tiết diện 2D và extrusion; biểu diễn thành, đáy, bo góc bằng tham số; tạo tai lặp bằng module và vòng lặp. Agent kiểm tra cấu hình mặc định cùng hai biến thể kích thước, rồi ghi miền tham số hợp lệ bằng `assert`. Các vị trí tai được suy ra từ kích thước vỏ và khoảng lùi.

Bằng chứng: hash source, phiên bản OpenSCAD, bộ tham số, lệnh render, số solid kín, kích thước bao và ảnh cùng góc nhìn. Agent chọn phép dựng dựa trên hình học đầu ra, khả năng cập nhật tham số và chi phí render đo được.

## 2. BOSL2: quan hệ lắp ghép và chuyển tiếp tiết diện

Nguồn: [Attachment Overview](https://github.com/BelfrySCAD/BOSL2/wiki/Tutorial-Attachment-Overview), [attachments.scad](https://github.com/BelfrySCAD/BOSL2/wiki/attachments.scad), [rounding.scad](https://github.com/BelfrySCAD/BOSL2/wiki/rounding.scad) và [skin.scad](https://github.com/BelfrySCAD/BOSL2/wiki/skin.scad).

BOSL2 cung cấp anchor, orientation và quan hệ cha–con để đặt chi tiết theo hình học của chi tiết chứa nó. Nhóm rounding cung cấp công cụ xử lý bo và chuyển tiếp. Nhóm skin/sweep hỗ trợ nối tiết diện và quét tiết diện theo đường dẫn. Agent chọn tiết diện, đường dẫn và cách ghép phù hợp để tạo solid hợp lệ.

Bài thực hành: chọn một gân hoặc tai có nhiều mặt cắt trong STL, dựng một bản bằng OpenSCAD cơ bản và một bản thử bằng BOSL2. Agent so sánh mặt cắt, khoảng cách bề mặt, số dòng mô tả hình học và thời gian render. Quyết định thêm thư viện gắn với lợi ích cụ thể đo được trên chi tiết đó.

Bằng chứng: phiên bản hoặc commit BOSL2, hàm và tham số sử dụng, hệ trục anchor, ảnh chồng, mặt cắt, trạng thái mesh kín và thời gian render. Việc thêm dependency vào dự án là một bước triển khai riêng sau bài thử.

## 3. Trimesh: đọc STL bằng mặt cắt

Nguồn: [Section example](https://trimesh.org/section.html) và [Trimesh API](https://trimesh.org/trimesh.html).

Trimesh hỗ trợ cắt mesh bằng mặt phẳng và chuyển đường cắt sang biểu diễn 2D. Agent dùng các mặt cắt để nhận diện thành, đáy, gân, mặt vát, ổ cầu và vùng đàn hồi. Mỗi mặt phẳng được xác định bằng origin và normal; phép chuyển giữa hệ 3D và hệ mặt cắt 2D được lưu cùng kết quả.

Bài thực hành: lấy nhiều mặt cắt tại vùng đầu, giữa và cuối của một tai hoặc khóa. Agent đặt STL và SCAD trong cùng đơn vị, hệ trục và mặt phẳng cắt, rồi chồng đường bao theo cùng tỷ lệ. Các đoạn thẳng, cung tròn và tiết diện thay đổi được mô tả bằng tham số phù hợp với số đo.

Bằng chứng: hash hai mesh, bảng mặt phẳng cắt, phép biến đổi tọa độ, ảnh có tỷ lệ và kích thước đặc trưng. Khi khớp đường thẳng hoặc cung tròn, agent lưu phần dư của phép khớp và phạm vi mặt cắt đã khảo sát.

## 4. Đo sai khác bằng khoảng cách tới bề mặt

Nguồn: [Trimesh sampling](https://trimesh.org/trimesh.sample.html), [Trimesh proximity](https://trimesh.org/trimesh.proximity.html) và [CloudCompare Distances Computation](https://www.cloudcompare.org/doc/wiki/index.php/Distances_Computation).

`sample_surface` tạo điểm mẫu trên bề mặt và hỗ trợ seed để tái lập kết quả. `closest_point` tìm điểm gần nhất trên các tam giác của mesh, trả về khoảng cách và chỉ số tam giác. CloudCompare giải thích phép đo cloud-to-mesh và ảnh hưởng của mật độ điểm lấy mẫu. Khoảng cách tới đỉnh gần nhất là một đại lượng riêng; khoảng cách tới bề mặt dùng điểm gần nhất trên tam giác.

Bài thực hành đề xuất: lấy mẫu theo diện tích bề mặt và đo hai chiều **STL → SCAD** cùng **SCAD → STL**. Agent báo median, P95, P99 và cực đại quan sát được của từng chiều, rồi tăng số điểm để đánh giá độ ổn định. Vùng khóa, ổ cầu và thành mỏng có bộ mẫu cục bộ riêng. Các phép đo khoảng cách bổ sung cho kích thước bao, sai khác thể tích và mặt cắt.

Bằng chứng: seed, số điểm mỗi chiều, đơn vị, phép căn chỉnh, độ mịn mesh, thống kê từng bộ phận và bản đồ màu sai lệch. Giá trị lớn nhất trong mẫu mang tên **cực đại quan sát được**. Kết luận về khoảng cách Hausdorff đầy đủ cần phép tính hoặc cận sai số tương ứng. Ngưỡng chấp nhận gắn với yêu cầu của từng đặc trưng, như độ dày thành, khe lắp hoặc hình dáng ngoài.

Trimesh quy ước signed distance dương ở phía trong mesh và âm ở phía ngoài; các điểm sát bề mặt trong `tol.merge` cũng nhận dấu dương. Agent ghi rõ quy ước dấu, kiểm tra độ kín, winding và hướng normal trước khi diễn giải kết quả signed distance.

## 5. Biến tài liệu thành tri thức tái sử dụng

Mỗi bài học theo cấu trúc **vấn đề → nguồn → giả thuyết → bài thử nhỏ → kết quả đo → phạm vi áp dụng → bước tiếp theo**. Agent ghi phiên bản công cụ và tạo ví dụ tối thiểu để xác nhận API trên môi trường thực tế. Bài thử đã xác minh được liên kết vào [sổ lỗi](error-cookbook.md) hoặc [cẩm nang agent](agent-learning.md), kèm source và bằng chứng. Bài thử đang khảo sát mang trạng thái và tiêu chí hoàn tất cụ thể.

Thứ tự học đề xuất là **OpenSCAD cơ bản → mặt cắt STL → đo sai khác bề mặt → BOSL2 theo nhu cầu hình học → Fusion native theo bản SCAD đã đối chiếu**. Cách học này ưu tiên công cụ có sẵn, module tái sử dụng, vị trí theo công thức và phép đo tái lập. Agent cập nhật tài liệu sau mỗi bài thực hành để phiên tiếp theo tiếp tục từ bằng chứng đã lưu.

## Checkpoint nghiên cứu

Ngày 13/10/2026: các nguồn liên kết đã được tham khảo và tổng hợp thành lộ trình đọc, bài thực hành cùng yêu cầu bằng chứng. Phạm vi thay đổi của lượt này là tài liệu. Bài thử BOSL2 và phép đo lấy mẫu hai chiều mang trạng thái đề xuất; kết quả chạy trên Snaplock thuộc checkpoint thực hành tiếp theo. Source CAD và dependency giữ phiên bản hiện tại.
