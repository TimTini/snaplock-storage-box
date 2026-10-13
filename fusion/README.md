# Fusion

- [`SnaplockStorageBox/`](SnaplockStorageBox/) chứa add-in chính, manifest và script `SnaplockStorageBox.py`. Script Python là entrypoint của add-in; trong Fusion, đăng ký thư mục này. Kết quả native của add-in được ghi cạnh source trong `SnaplockStorageBox/exports/`.
- [`tests/`](tests/) chứa các add-in độc lập dùng để khảo sát Plane, Sketch, Loft và Sweep. Mỗi thư mục con có README và manifest riêng; đăng ký đúng thư mục con cần chạy.

Kiểm thử offline cho source nằm trong [`../tests/`](../tests/). Audit đầu ra và hướng dẫn chạy nằm ở [README gốc](../README.md) và [mục lục tài liệu](../docs/README.md). Fusion production 0.5.1 giữ baseline cơ khí trước cập nhật latch trong SCAD; native run theo SCAD mới là bước xác nhận tiếp theo.
