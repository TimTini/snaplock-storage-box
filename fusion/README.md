# Fusion

[Hướng dẫn test MCP](../docs/guides/fusion-mcp-testing.md) và [wrapper dùng lại](tests/McpNativeTest/README.md) cung cấp đường chạy native từ CLI. Lệnh `python tools/fusion-mcp-test.py` đọc trạng thái; `python tools/fusion-mcp-test.py --run` tạo document test, kiểm tra recompute/BRep và xuất bộ bằng chứng.

- [`SnaplockStorageBox/`](SnaplockStorageBox/) chứa add-in chính, manifest và script `SnaplockStorageBox.py`. Script Python là entrypoint của add-in; trong Fusion, đăng ký thư mục này. Kết quả native của add-in được ghi cạnh source trong `SnaplockStorageBox/exports/`.
- [`tests/`](tests/) chứa các add-in độc lập dùng để khảo sát Plane, Sketch, Loft và Sweep. Mỗi thư mục con có README và manifest riêng; đăng ký đúng thư mục con cần chạy.

Kiểm thử offline cho source nằm trong [`../tests/`](../tests/). Fusion Python **0.6.1** dùng công thức latch và tâm tai theo SCAD ngày 14/10/2026, đã chạy native với 10 biến thể recompute và bộ STL đã qua audit kín. [Hồ sơ đồng bộ và cách Run](../docs/geometry/fusion-parametric-sync.md) ghi kiểm chứng BRep lắp đóng, giới hạn mesh và bước in vật lý tiếp theo. Audit đầu ra và hướng dẫn chạy nằm ở [README gốc](../README.md) và [mục lục tài liệu](../docs/README.md).
