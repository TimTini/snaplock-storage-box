# Tài liệu

[Bộ chung STL, OpenSCAD và Fusion](guides/README.md) dùng độc lập cho model mới. Agent bắt đầu tại [START-HERE](guides/START-HERE.md), chốt route/input và thiết lập theo [environment](guides/environment.md). [Các ví dụ dự án](examples/README.md) giữ checkpoint riêng.

[Fusion Python 0.6.1](geometry/fusion-parametric-sync.md) cập nhật công thức theo SCAD và đã chạy native; hồ sơ phân biệt kiểm chứng offline, BRep, STL và bước in vật lý.

[Cập nhật SCAD và assembly ngày 14/10/2026](geometry/latch-parametric-fix.md) là hồ sơ hiện tại. [Mẫu in](../samples/README.md) dùng STL đã xuất lại. [README checkpoint trước](history/README-before-parametric-fix.md) giữ lịch sử quyết định.

- [Hướng dẫn quy trình chung](guides/README.md): xem cách dựng SCAD, chuyển sang Fusion, kiểm chứng tham số và xử lý lỗi.
- [Hồ sơ hình học](geometry/): xem quyết định dựng hình, đối chiếu mẫu và kết quả lắp.
- [Bằng chứng kiểm chứng](validation/README.md): xem báo cáo, log và hình ảnh đã lưu.

Các audit Python nằm trong `tools/`; chạy lệnh từ thư mục gốc repo.

[Quy trình chung MCP](guides/fusion-mcp-testing.md) chọn capability/lifecycle theo server đích. [Ví dụ adapter Snaplock](examples/fusion-mcp-testing.md) hướng dẫn CLI và wrapper riêng của model này: [CLI](../tools/fusion-mcp-test.py) mặc định đọc trạng thái; --run tạo và kiểm chứng document test mới.
