# Bắt đầu một nhiệm vụ hoặc tiếp nhận trên máy mới

## 1. Đọc phần nền bắt buộc

Agent đọc [README](README.md), [cẩm nang](agent-learning.md), [môi trường](environment.md), [template](templates.md) và quy ước nhãn trong [sources](sources.md). Agent đọc chỉ dẫn workspace đang có trước khi thao tác. Nội dung bộ hướng dẫn cung cấp kiến thức và quy trình; quyền ghi, chạy CAD, công bố và điều khiển ứng dụng theo nhiệm vụ của người dùng.

Agent tiếp nhận đọc checkpoint hiện có, Git status/diff và source/hash hiện tại. Hồ sơ bàn giao và runbook cũ được đối chiếu với phiên bản thực trước khi sử dụng.

## 2. Chọn phần đọc theo đầu vào và đầu ra

- STL: đọc [phân tích STL và chọn route](stl-to-scad.md), gồm unit/mesh hỏng, chỉ đo, chuyển mesh trực tiếp hoặc tái dựng SCAD theo mục tiêu.
- SCAD hoặc thiết kế mới: đọc phần dựng tham số trong [cẩm nang](agent-learning.md) và [kiểm tra tham số](parameter-change-validation.md).
- Fusion native: đọc [Fusion Python](fusion-python-tu-hoc.md) và [mẫu nhiệm vụ](scad-to-fusion-task.md).
- Fusion qua công cụ agent: đọc thêm [MCP](fusion-mcp-testing.md), kiểm tra capabilities trước khi chọn transport.
- Lỗi hoặc dữ liệu lạ: đọc recipe tương ứng trong [sổ lỗi](error-cookbook.md); recipe có điều kiện riêng.
- API, thư viện hoặc thao tác chưa rõ: mở nguồn Sxx tương ứng trong [registry](sources.md); ghi phiên bản đích và kết quả đối chiếu.

## 3. Lập bản xác nhận tiếp nhận

Trước chỉnh sửa, agent ghi vào runbook:

1. Mục tiêu và đầu ra: báo cáo, mesh, SCAD editable, Fusion native, assembly hoặc mẫu chế tạo.
2. Đầu vào và thẩm quyền: đường dẫn tương đối, SHA256, giấy phép, quy ước đơn vị và căn cứ số đo.
3. Route đã chọn và lý do; các feature hoặc vùng xấp xỉ cần xử lý riêng.
4. Miền tham số, topology, part/cặp tiếp xúc và dung sai theo từng đặc trưng.
5. Môi trường thực có: OS, Python audit, OpenSCAD/backend, Fusion/build, font/library, MCP nếu dùng.
6. Lệnh/check sẽ chạy và đầu ra chứng minh; phần source/offline/native/slicer/physical theo đúng yêu cầu.
7. Dữ liệu hoặc capability còn thiếu, việc vẫn thực hiện được và điều kiện để tiếp tục phần phụ thuộc.

Đơn vị chưa có căn cứ giữ trạng thái blocked cho phép đo kích thước và dung sai. Thiếu Fusion giữ native ở not_run; các bước đọc source, logic và chuẩn bị có thể tiếp tục với phạm vi offline rõ ràng.

## 4. Kiểm tra tiếp nhận bằng một trường hợp ngoài dự án cũ

Chọn tình huống tương ứng trong [readiness scenarios](examples/readiness-scenarios.md). Agent lập intake và kế hoạch kiểm chứng từ chính task mới. Người kiểm tra đối chiếu các quyết định với đầu vào, thay vì đếm số file agent đã mở.

Mức hoàn tất chỉ được ghi khi có evidence gắn source/hash và phép kiểm tra. Ngưỡng đo, khổ chế tạo, số part và cơ cấu được lấy từ job specification. Các thông số trong ví dụ giữ phạm vi của ví dụ đó.

## 5. Bàn giao

Dùng [template handoff](templates.md). Ghi file đã đổi, lệnh đã chạy, kết quả theo từng lớp, nguồn xác nhận và phần còn thiếu. Lưu tiến trình vào tài liệu/version control được nhiệm vụ cho phép. Máy tiếp nhận dựng lại môi trường và thực hiện preflight; mọi claim runtime cũ giữ ngày/build/source của lần chạy đó.
