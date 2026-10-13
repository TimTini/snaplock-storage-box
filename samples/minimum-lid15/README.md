# Mẫu minimum với nắp 15 mm

[Preset](parameters.json) dùng thân 107,9 × 30,1 × 30,2 mm và nắp cao 15 mm. Bộ này ghép [thân minimum](../minimum/body.stl) với [lid.stl](lid.stl) tại đây và **hai bản [latch.stl](latch.stl) tại đây**. Latch có kích thước bao khoảng 28,00 × 31,84 × 6 mm; span tương ứng chiều cao nắp 15 mm.

Các STL dùng tỷ lệ 100%, đơn vị mm. [audit.json](audit.json) ghi hash source và các part đã xuất lại ngày 14/10/2026. [Hồ sơ sửa cơ cấu](../../docs/geometry/latch-parametric-fix.md) ghi kiểm tra assembly và phạm vi xác nhận. Bước kiểm chứng tiếp theo là in mẫu để đo độ khít, khe lắp và lực khóa.

Preset tái tạo từng part bằng `part=lid` hoặc `part=latch` trong OpenSCAD cùng bộ tham số `minimum-lid15-control`.
