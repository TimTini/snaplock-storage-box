# Tài liệu

[Fusion Python 0.6.1](geometry/fusion-parametric-sync.md) cập nhật công thức theo SCAD và đã chạy native; hồ sơ phân biệt kiểm chứng offline, BRep, STL và bước in vật lý.

[Cập nhật SCAD và assembly ngày 14/10/2026](geometry/latch-parametric-fix.md) là hồ sơ hiện tại. [Mẫu in](../samples/README.md) dùng STL đã xuất lại. [README checkpoint trước](history/README-before-parametric-fix.md) giữ lịch sử quyết định.

- [Hướng dẫn quy trình](guides/): xem cách dựng SCAD, chuyển sang Fusion, kiểm chứng tham số và xử lý lỗi.
- [Hồ sơ hình học](geometry/): xem quyết định dựng hình, đối chiếu mẫu và kết quả lắp.
- [Bằng chứng kiểm chứng](validation/README.md): xem báo cáo, log và hình ảnh đã lưu.

Các audit Python nằm trong `tools/`; chạy lệnh từ thư mục gốc repo.

[Quy trình agent test Fusion qua MCP](guides/fusion-mcp-testing.md) hướng dẫn kết nối local, wrapper native, xử lý lỗi, kiểm tra BRep/STL và lưu bằng chứng. [CLI dùng lại](../tools/fusion-mcp-test.py) mặc định đọc trạng thái; `--run` tạo và kiểm chứng document test mới.
