# Bộ hướng dẫn chung STL, OpenSCAD và Fusion

Phiên bản tài liệu: **1.0.2 — 15/10/2026**. Bắt đầu tại [START-HERE](START-HERE.md). Bộ này hướng dẫn phân tích STL, dựng OpenSCAD tham số và dựng/kiểm chứng Fusion native theo mục tiêu của từng nhiệm vụ.

## Phạm vi và cách chọn lộ trình

- STL cần đo hoặc kiểm tra: dùng [quy trình STL](stl-to-scad.md), kết thúc ở báo cáo khi nhiệm vụ chỉ yêu cầu khảo sát.
- Model cơ khí cần dựng lại bằng quy luật: STL → OpenSCAD → kiểm chứng; tiếp tục Fusion khi cần cây feature native.
- SCAD đã có: đọc source và tham số, chốt baseline rồi dùng [quy trình Fusion](fusion-python-tu-hoc.md).
- Chỉnh mesh hoặc hình scan/organic: đánh giá Mesh tools/Convert Mesh trong Fusion và yêu cầu solid/surface; ghi rõ mức giữ tham số và giới hạn thay vì ép mọi hình qua primitive.
- Thiết kế mới: dùng bảng yêu cầu và số đo được duyệt làm căn cứ; tạo baseline SCAD hoặc Fusion theo đầu ra yêu cầu.

Các route và điểm dừng được chốt trước khi sửa. Model scan/freeform, dữ liệu lỗi, công nghệ chế tạo và topology đặc biệt có bước đánh giá riêng; mức hỗ trợ được ghi theo nhiệm vụ.

## Mục lục theo công việc

1. [Điểm vào cho agent](START-HERE.md): phần bắt buộc đọc, intake và điều kiện chuyển máy.
2. [Cẩm nang làm việc](agent-learning.md): chọn route, ownership và mức bằng chứng.
3. [STL → OpenSCAD](stl-to-scad.md): đơn vị, mesh, dựng tham số và so sánh.
4. [Fusion Python](fusion-python-tu-hoc.md): feature, hệ trục, tham số và native.
5. [Mẫu giao việc SCAD → Fusion](scad-to-fusion-task.md): phạm vi và acceptance.
6. [Kiểm tra thay đổi tham số](parameter-change-validation.md): biên, topology, assembly và chế tạo.
7. [Sổ lỗi](error-cookbook.md): điều kiện áp dụng và cách xác nhận nguyên nhân.
8. [Môi trường và chuyển máy](environment.md): dependency, capability và preflight.
9. [Fusion qua MCP](fusion-mcp-testing.md): phương thức chạy tùy capability.
10. [Nguồn và bài thực hành](internet-learning.md), [registry nguồn](sources.md).
11. [Template đầu vào, bằng chứng và bàn giao](templates.md).
12. [Tình huống kiểm tra độ bao phủ](examples/readiness-scenarios.md), [kiểm chứng bản phát hành](VALIDATION.md).
13. [Gia cường và kiểm chứng mesh](reinforcement-and-mesh.md): chức năng, chuyển tiếp đáy–bo, ownership bề mặt Boolean, phép đo và ca từ chối; case dustpan kèm hash và phạm vi bằng chứng.

## Dùng độc lập và phân phối

Sao chép toàn bộ thư mục này, gồm tools, tests và examples. Các liên kết file của bộ chung nằm trong thư mục này; bộ chung dùng Python chuẩn để kiểm tra cấu trúc, không cần STL hoặc script của một project cụ thể. Đầu vào CAD, phần mềm CAD, font và thư viện audit thuộc môi trường của nhiệm vụ, được ghi riêng trong [environment](environment.md).

Từ thư mục chứa bộ hướng dẫn:

    python tools/validate-docs.py
    python -m unittest discover -s tests

Validator quét mọi Markdown trong bộ, các liên kết file inline và file bắt buộc. JSON đầu ra cùng exit code xác nhận cấu trúc; nội dung kỹ thuật cần đối chiếu nguồn và kiểm chứng theo task. Phạm vi parser, cách chạy từ thư mục khác và kiểm tra bản copy nằm trong [environment](environment.md).

Agent mới nhận đường dẫn START-HERE cùng task specification. Bài kiểm tra tiếp nhận yêu cầu agent báo lại route, dữ liệu, tiêu chí, capability và phần còn thiếu; kết quả này xác nhận thông tin đã được dùng trong task. Bộ file cung cấp đầu vào tường minh, còn cơ chế tự nạp/context limit phụ thuộc host agent.

Các hồ sơ Snaplock và project khác là ví dụ độc lập, được dẫn bằng URL công khai khi cần. Chúng có source/hash, môi trường và trạng thái riêng. Bộ chung được đọc và kiểm tra offline; bước làm mới nguồn cần truy cập Internet.
