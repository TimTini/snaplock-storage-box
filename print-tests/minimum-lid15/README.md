# Nắp 15 mm đối chứng cho bộ minimum đã in

[Nắp lid.stl](lid.stl) dùng dài 107,9 mm, rộng 30,1 mm và cao 15 mm. Thân cao 30,2 mm cùng hai latch của [bộ minimum](../minimum/README.md) được sử dụng tiếp trong bài thử này. In riêng một nắp ở tỷ lệ 100%, đơn vị mm, đáy nắp đặt trên bàn in theo hướng STL.

Mẫu minimum cũ dùng nắp 11,7 mm, trong khi latch giữ kích thước của mẫu nắp 15 mm. Khi đóng nắp đúng bản lề, ổ cầu trên nắp và latch hạ 3,3 mm; hai răng latch nằm thấp so với hốc thân. Phép lắp cứng đo khoảng 34,684 mm³ giao nhau giữa mỗi latch với thân. Nắp đối chứng 15 mm đưa sai khác này về khoảng 0,000173 mm³. [Báo cáo lắp](../../docs/latch-minimum-fit.md) ghi tọa độ và ảnh mặt cắt.

Đây là mẫu đối chứng hình học để thử lại cơ cấu bằng nắp mới. Kiểm chứng in thực tế xác nhận khe lắp, độ đàn hồi, lực khóa và độ kín của cụm. Body–Lid có giao nhau khoảng 6,275 mm³ trong cả hai cấu hình, chủ yếu ở vùng bản lề của cơ cấu tham chiếu hiện có và được theo dõi riêng trong báo cáo.

[Preset](parameters.json) giữ ba kích thước thân của minimum và dùng chiều cao nắp 15 mm. Lệnh render tại thư mục repo:

```powershell
openscad --backend Manifold --hardwarnings --export-format binstl -p print-tests/minimum-lid15/parameters.json -P minimum-lid15-control -D 'part="lid"' -o print-tests/minimum-lid15/lid.stl snaplock-storage-box.scad
```
