# Mẫu giao việc dựng SCAD rồi chuyển sang Fusion Python.

Mẫu này dùng cho đầu vào `[file hoặc thư mục dự án]` và mục tiêu `[tái dựng theo mẫu hoặc thiết kế mới]`. Các giá trị trong ngoặc vuông được điền theo nhiệm vụ. Phạm vi bàn giao gồm `[part, nguồn, mức bám mẫu, biến thể và hình thức kiểm chứng]`.

[Quy trình STL → SCAD](stl-to-scad.md) cung cấp bước chuẩn bị hình học từ mesh và mẫu giao việc để tạo baseline cho quy trình này.

## Agent đọc nguồn và chốt ý đồ hình học.

Agent đọc source, README, preview, manifest, dependency, test và checkpoint hiện có. Agent ghi bảng part, kích thước sử dụng, lòng chứa, đáy, bo/vát, lỗ, ren, khớp, khe hở và đường lắp. Agent lưu hash đầu vào, quy ước đơn vị, hệ tọa độ và snapshot của phần tham chiếu.

Agent xác định các đặc trưng được giữ theo yêu cầu: hình dáng nhận diện, tỷ lệ, kích thước sử dụng, các part, quan hệ giữa part và chức năng. Mức bám mẫu được ghi thành tiêu chí đo hoặc tiêu chí chức năng của từng vùng.

## Agent dựng và kiểm chứng bản SCAD.

Agent tổ chức module theo chức năng, tham số đầu vào và công thức derived. Miền hợp lệ được diễn đạt bằng assert. Agent render cấu hình mặc định và các biến thể trong phạm vi `[bộ tham số]`.

Agent kiểm tra solid, tính kín, winding, bounds, thể tích, số lỗ và kích thước cơ cấu. Agent đối chiếu mẫu bằng boolean thừa/thiếu, mặt cắt và khoảng cách bề mặt theo `[ngưỡng và mục tiêu đo]`. Vùng xấp xỉ được ghi cùng vị trí, kích thước và ảnh hưởng.

Agent chốt source SCAD, hash, tham số, output và báo cáo làm baseline chuyển đổi.

Agent áp dụng [quy trình test toàn bộ khi đổi tham số](parameter-change-validation.md): thử từ kích thước nhỏ nhất của miền cơ cấu đến giới hạn `[khổ hữu dụng, mặc định kiểm tra 250 mm mỗi trục]`, thử từng trục và tổ hợp biên, mọi topology liên quan, toàn bộ cặp lắp và miền chuyển động. Agent đo envelope thật gồm tai/chốt/gân cùng phần chừa in. Miền source, tiêu chí latch, tiếp xúc thân–nắp, Fusion native và lắp vật lý có trạng thái riêng trong báo cáo.

## Agent dựng script Python native trong Fusion.

Agent áp dụng [quy trình kiểm chứng qua MCP Fusion](fusion-mcp-testing.md) sau khi script đã qua regression offline. Wrapper gọi hàm dựng/kiểm tra của source chính, tạo document test riêng, giữ exception và log stage, thử biến thể tham số, đo giao temporary BRep rồi audit STL độc lập. Hồ sơ bàn giao gắn source/wrapper hash với ma trận, phiên bản Fusion, log và bộ xuất.

Agent ưu tiên hình học giải tích và feature diễn đạt trực tiếp quy luật: sketch đường thẳng/cung tròn/elip, Extrude/Cut, Revolve, Sweep, Fillet, Chamfer, Combine, Mirror và Pattern. Profile dịch chuyển giữ nguyên hướng được đánh giá bằng Sweep Parallel; profile thay đổi được đánh giá bằng guide rail, guide surface và ghép mặt theo quy luật của từng vùng. Loft ít tiết diện phục vụ đoạn chuyển tiếp phù hợp. Loft nhiều tiết diện có mức ưu tiên cuối cùng, được chọn sau khi các phương pháp trực tiếp đã được đánh giá bằng công thức, khả năng cập nhật và sai lệch hình học. Cây feature có tên thể hiện chức năng. Component/body được tổ chức theo `[bố trí part hoặc assembly]`, với ownership và tool được theo dõi rõ.

[Bài thử Sweep Parallel cho cung khe](../../fusion/tests/SlotSweepTest/README.md) cung cấp source, bộ biến thể chiều dày và log native để xác nhận một vùng dịch chuyển cứng trước khi ghép vào model hoàn chỉnh.

Agent so sánh các phương pháp trên cùng phần hình học và cùng tiêu chí đầu ra. Tổng bước bao gồm plane, sketch, tạo mặt/khối, Move, Split, Remove, Stitch, Combine và các feature phụ thực tế của phương pháp. Khả năng chỉnh sửa được đánh giá bằng số đầu vào độc lập, User Parameters và công thức dùng chung. Phương án được chọn có cây feature gọn, quan hệ dễ hiểu và sai lệch đạt mục tiêu. Loft nhiều tiết diện liên kết công thức được giữ khi phương án đó đáp ứng các tiêu chí tốt hơn ứng viên thay thế. Khe Snaplock hiện tại giữ Loft tám tiết diện; bài thử Sweep cung cấp bằng chứng cho một mặt cung với phạm vi riêng.

Agent tạo User Parameters và expression cho kích thước, vị trí và các quan hệ phụ thuộc. Đơn vị API và đơn vị báo cáo được chuyển đổi rõ. Các lựa chọn topology và nội dung tạo lúc Run được ghi trong hướng dẫn.

Agent giữ các đặc trưng thiết kế đã chốt, đồng thời dùng cấu trúc native gọn theo chức năng. Mỗi thay đổi đơn giản hóa có mô tả và phép đối chiếu. Agent tích hợp chỉnh sửa CAD theo trục, pivot và công thức hình học liên kết.

## Agent kiểm chứng theo từng lớp bằng chứng.

Agent chạy syntax, test công thức và regression cho ca lỗi có thể tái hiện offline. Agent chạy Fusion để kiểm tra solver, profile, feature health, BRep, số body và recompute của `[bộ biến thể]`. Log ghi stage, hash source, tham số và kết quả; expression gốc được phục hồi và kiểm tra lại.

Agent xuất từng body cùng manifest chứa đơn vị, hash và độ mịn. Agent so sánh đầu ra Fusion với mẫu và baseline SCAD theo tiêu chí đã chốt. Agent kiểm tra vị trí assembly, đường lắp và miền chuyển động theo phạm vi nhiệm vụ.

Agent ghi kết quả source, offline, native, slicer và vật lý thành các checkpoint riêng. Mẫu coupon và phép thử `[khe hở, lực thao tác, tải hoặc độ bền]` cung cấp bằng chứng vật lý tương ứng.

## Agent bàn giao bộ có thể sửa và tiếp tục.

Bộ bàn giao gồm SCAD, Python, manifest, hướng dẫn chạy, bảng tham số, test, báo cáo và checkpoint. Nhật ký lỗi ghi hiện tượng, bằng chứng, nguyên nhân hoặc giả thuyết, thay đổi và mức xác nhận. Hướng dẫn chỉ rõ các tham số cập nhật qua Change Parameters và các lựa chọn được tạo lại bằng Run.

Tài liệu công khai dùng dữ liệu demo, đường dẫn tương đối, nguồn và giấy phép phù hợp. Bản tham chiếu riêng, transcript và log nguyên bản được lưu trong vùng local. Agent bàn giao commit cùng kết quả kiểm chứng và trạng thái remote theo quyền của nhiệm vụ.

Nguồn quy trình là [cẩm nang agent](agent-learning.md), [sổ lỗi](error-cookbook.md) và [tài liệu kỹ thuật](fusion-python-tu-hoc.md).
