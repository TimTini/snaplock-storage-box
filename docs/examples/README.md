# Ví dụ dự án và phạm vi tái lập

[Bộ chung](../guides/README.md) chứa quy trình dùng cho model mới. Thư mục này giữ hồ sơ kỹ thuật của những checkpoint cụ thể; các giá trị, số part, khổ, dung sai và cách sửa ở đây thuộc case đã ghi.

## Hồ sơ Snaplock

- [Trạng thái SCAD hiện tại](../geometry/latch-parametric-fix.md) và [Fusion native](../geometry/fusion-parametric-sync.md) là điểm tra trạng thái source/model.
- [Workflow MCP đã chạy](fusion-mcp-testing.md): adapter, wrapper và capability/build cụ thể.
- [Các ca lỗi theo project](project-error-cases.md): bằng chứng lịch sử của các recipe chung.
- [Rà phương pháp dựng](modeling-method-review.md), [gân SCAD → Fusion](fusion-reinforcement.md) và [review học từ năm project](learning-doc-review.md): checkpoint theo ngày/hash trong từng hồ sơ. Các bước next/pending trong các bản lịch sử được đọc ở thời điểm checkpoint.

## Input và công cụ riêng

Script tools/audit-scad.py trong repo đặt sẵn SCAD, tên STL/hash, cách tách component và transform của Snaplock. compare-scad.py và audit-fusion.py dùng cùng reference contract. Chúng minh họa một adapter theo model, không nhận STL bất kỳ làm bộ audit chung.

STL riêng nằm tại reference/Snaplock_Storage_Boxes_240x120(2).stl, SHA256 73faaa2d438b02038b9f84002202435973a09f92ec2a48315577e0e00baea167. File này được Git bỏ qua; người vận hành cung cấp từ nguồn có quyền sử dụng rồi đối chiếu hash trước khi chạy. Khi chưa có file, các phép so với reference mang blocked; báo cáo công khai vẫn đọc được. Bộ hướng dẫn chung có validator/tests riêng và dùng độc lập với input này.

## Snapshot môi trường audit

Đối chiếu local ngày 14/10/2026: Windows, Python 3.12.14, OpenSCAD 2026.09.29; numpy 2.5.3, trimesh 5.1.1, manifold3d 3.5.4, matplotlib 3.11.2, scipy 1.18.1, networkx 3.7 và rtree 1.4.1. Đây là inventory môi trường audit hiện có; lượt cập nhật tài liệu chỉ chạy help/version và tests offline, không chạy lại model native.

requirements.txt ở root chỉ liệt kê package và chưa khóa version. Khi tái lập ví dụ, dựng environment riêng theo OS, đối chiếu versions/capabilities trên đây và lưu resolved lock sau smoke thực tế. Snapshot này không đảm bảo wheel hoặc hành vi giống nhau trên mọi OS/Python.

Fusion 2705.1.30 và native source/hash thuộc [báo cáo đã lưu](../validation/fusion-parametric-native.json); thử vật lý còn riêng. Các log/output timestamp local không nằm đầy đủ trong Git; hồ sơ public lưu số đo/hash đã loại đường dẫn máy.

## Các ví dụ khác

[Hộp bàn chải](https://github.com/TimTini/electric-toothbrush-case), [khay](https://github.com/TimTini/bath-sponge-tray), [thời khóa biểu](https://github.com/TimTini/thoi-khoa-bieu-openscad) và [thùng rác](https://github.com/TimTini/thung-rac-4-goc) có source/README/evidence riêng. Agent đọc phiên bản và scope của ví dụ trước khi rút recipe; bộ chung lấy part/units/parameter/envelope từ task mới.
