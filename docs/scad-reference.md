# Bản tham chiếu SCAD từ STL

## Nguồn và hệ tọa độ

Nguồn: `reference/Snaplock_Storage_Boxes_240x120(2).stl`, SHA256 `73faaa2d438b02038b9f84002202435973a09f92ec2a48315577e0e00baea167`. Đơn vị được diễn giải là mm theo quy mô cơ cấu. Audit chọn bốn mesh chính có thể tích dương, ghi nhận riêng ba mảnh nguồn hai mặt có thể tích bằng 0.

- Thân: X = STL Y − 1,242873907; Y = STL X − 377,837585449; Z giữ nguyên. Hoán đổi X/Y đi cùng đảo winding trong mesh tham chiếu.
- Nắp: X = STL X − 9,075012207; Y = STL Y − 65,8; Z giữ nguyên.
- Khóa: trừ tọa độ nhỏ nhất của từng phần. Hai khóa nguồn có cùng hình học trong sai số float STL.

## Các phép dựng

| Vùng | Biểu diễn SCAD | Căn cứ |
|---|---|---|
| Vỏ, lòng, bo góc | `offset`, `linear_extrude`, `hull`, `difference` | Vỏ 237,85×123,15; R ngoài 12; R lòng thân 8; R lòng nắp 9 |
| Vát đáy | Hai tiết diện, góc 60° | Chạy ngang 5 ngoài; 4,7 trong thân; 3,73205 trong nắp |
| Gân thân | Tiết diện YZ và biên XY loe | Mặt nghiêng 20°/45° ở tai sau; chân ngàm trước từ Z=33 |
| Tai sau thân | Cung R4,25, khoét cầu R5 | Tâm YZ=(-4,75;52) ở cấu hình mặc định |
| Ngàm trước thân | Vòng côn 50° quanh trục X và mép tròn | Tâm YZ=(126,15;61), r(X)=-tan(50°)X+37,95061 |
| Hốc ngàm thân | Trụ đứng R5, hai chamfer 1 | Tâm XY=(24,15;126,15), Z=41,5…46; đáy nón R4 tại Z=40,5 |
| Tai khóa trên nắp | Gân từ Z=0, cung R8, mép vòng côn 50°, ổ cầu R3,75 | Nón tâm YZ=(-3;6), r(X)=tan(50°)X−19,09617 |
| Chốt cầu nắp | Gân loe, cung R4,5, cầu R5 giới hạn bởi trụ R4,5 | Tâm chốt đầu X=26; YZ=(127,9;15) |
| Khóa | Cầu R3,75, rãnh trụ R5 bo đầu R2, mặt dốc Y+Z=32,9 | Biên 28×31,835144×6 |
| Đàn hồi khóa | Cung R0,5 và loft các tiết diện địa phương | R5 qua chiều dày; hệ số blend khớp lát cắt Z=0,1/3/5,9 |

Các phương trình trên dùng tọa độ mặc định cho cụm đầu; source SCAD thể hiện dịch tâm, đối xứng hai đầu và hai cụm theo `mount_end`, `length`, `width`, chiều cao. Các mặt nón được fit độc lập từ đỉnh STL với RMS khoảng 3×10⁻⁶ mm. Hốc trụ có chamfer tuyến tính: mặt dưới thỏa Z=ρ+36,5 với ρ=4…5; mặt trên thỏa Z=51−ρ.

## Đánh giá hình học

`audit-scad.py` render bằng OpenSCAD Manifold với `--hardwarnings`, kiểm tra từng solid kín/thể tích dương/một thành phần, layout bốn thành phần, SHA nguồn và chiều bao. Phép boolean tính:

`Sai khác đối xứng (%) = 100 × (thể tích SCAD + thể tích STL − 2 × thể tích giao) / thể tích STL`.

Ngưỡng kiểm tra mặc định: thân/nắp dưới 0,2%; khóa dưới 0,1%; sai khác tọa độ bao dưới 0,02 mm. Audit biến thể kiểm tra chiều bao 280×172×74,25 cho thân, 280×172,25×19,5 cho nắp (gồm tai), 28×31,835144×6 cho khóa. `compare-scad.py` kiểm tra SHA SCAD, nguồn và từng STL xuất trước khi tạo hình đối chiếu.

| Chi tiết | Thể tích thừa mm³ | Thể tích thiếu mm³ | Sai khác đối xứng | Sai khác tọa độ bao mm |
|---|---:|---:|---:|---:|
| Thân | 134,654 | 18,489 | 0,0927% | 0,00409 |
| Nắp | 39,017 | 35,776 | 0,0659% | 0,00966 |
| Khóa | 0,446 | 1,062 | 0,0429% | 0,00201 |

Các số đo là so sánh thể tích và chiều bao. Chúng hỗ trợ đánh giá độ bám mẫu cùng hình chồng mặt cắt; sai số cục bộ toàn bề mặt và lắp ráp chuyển động cần phép kiểm tra riêng.

## Vùng xấp xỉ và xuất mesh

SCAD dùng đường tròn với `$fn=96`, trong khi STL có mức chia facet riêng cho mỗi vùng. Gân dưới giữ các điểm đổi hướng đã đo. Blend nhỏ của rãnh đàn hồi được nội suy qua 25 tiết diện, với hệ số địa phương ghi trong `slot_profile`; các hệ số này là xấp xỉ có đối chiếu. Vì vậy bản dựng giữ hình tham số mượt và sai khác nhỏ so với mesh nguồn.

Xuất binary STL có thể làm các mặt rất mảnh tại giao trùng tọa độ co lại do float32. Pipeline chỉ bỏ **mảnh rời** có diện tích <10⁻⁵ mm² và |thể tích| <10⁻⁸ mm³, đồng thời yêu cầu mọi phần giữ lại là solid kín. Cấu hình mặc định bỏ 4 mặt ở thân; biến thể bỏ 10; nắp và khóa giữ toàn bộ mặt. Báo cáo ghi số mặt xử lý và SHA của file xuất; hình học SCAD vẫn là nguồn dựng.

Kiểm chứng vật lý gồm thử in, khe hở, lực đàn hồi, góc mở, tải và độ bền. Bản SCAD là mốc hình học tham chiếu của script Fusion 0.2.0. [Tài liệu tự học](fusion-python-tu-hoc.md) ghi kết quả đối chiếu, mốc native theo source và bước xác nhận tiếp theo.
