# Snaplock Storage Box — SCAD và Fusion Python

[Bài thử Sweep Parallel cho cung khe đàn hồi](fusion/SlotSweepTest/README.md) cung cấp add-in riêng, cập nhật chiều dày bằng tham số và log đo native. [Quy trình SCAD → Fusion](docs/scad-to-fusion-task.md) ưu tiên các phép dựng trực tiếp và đặt Loft nhiều tiết diện ở bước lựa chọn cuối cùng.

## Bản SCAD theo STL — 12/10/2026

Bản [in test kích thước nhỏ](print-tests/minimum/README.md) có STL sẵn và preset giảm riêng chiều dài, chiều rộng, chiều cao thân và chiều cao nắp theo bước 0,1 mm.

Mở [snaplock-storage-box.scad](snaplock-storage-box.scad) trong OpenSCAD. File độc lập, dựng hình bằng primitive, phép boolean, mặt cắt có tham số và module. Chọn `part` trong Customizer: `layout` hiện thân, nắp và hai khóa; `body`, `lid`, `latch` hiện từng chi tiết. F6 render solid; các tham số nằm đầu file.

**Checkpoint SCAD 13/10/2026:** [răng khóa dùng trụ R5, elip và hai vùng bao lồi ngắn](docs/scad-catch-csg.md) thay 25 tiết diện của phần răng. [Khe đàn hồi hybrid](docs/scad-slot-hybrid.md) dùng đuôi Extrude và tám tiết diện phần trước; cực đại khoảng cách quan sát với snapshot là 0,02426 mm qua ba chiều dày 5/6/6,5 mm, theo ngưỡng 0,03 mm. Fusion Python 0.4.0 dùng cùng cấu trúc và công thức, với bước Run native riêng.

Kích thước vỏ chính đo từ mẫu là **237,85 × 123,15 mm**, cao thân **52 mm**, cao nắp **15 mm**; đáy thân **2 mm**, đáy nắp **3 mm**, thành **3 mm**. Tên STL ghi 240×120; bản SCAD dùng số đo hình học thực tế. `length`, `width`, `body_height`, `lid_height`, độ dày và khe hở được chỉnh trong Customizer; giới hạn tham số được kiểm tra bằng `assert`.

Customizer đặt nhóm `Main dimensions` lên đầu với `length`, `width` và `body_height`. Thân và nắp dùng chung `length` và `width`; `lid_height` nằm trong nhóm `Lid and shell details`. Các nhóm cơ cấu, bố trí in và độ mịn nằm phía dưới.

Mẫu giữ gân loe, mặt vát, đầu cầu/ổ cầu, mép ngàm côn 50°, hốc trụ với chamfer và tiết diện đàn hồi thay đổi theo chiều dày khóa. [Chi tiết hình học và kiểm chứng](docs/scad-reference.md) ghi phép dựng cùng vùng xấp xỉ.

**Kiểm chứng hiện tại:** cấu hình mặc định và biến thể vỏ 280 × 155 mm, thân cao 70 mm, đều tạo bốn solid kín trong layout. So sánh boolean với bốn phần chính của STL xác nhận sai khác thể tích đối xứng: thân **0,0927%**, nắp **0,0659%**, mỗi khóa **0,0492%**. Sai lệch tọa độ bao lớn nhất **0,0097 mm**. Đây là các chỉ số hình học; thử in, lực khóa và độ bền là mốc kiểm chứng vật lý tiếp theo.

Chạy lại build/audit và ảnh đối chiếu:

OpenSCAD có backend Manifold được cài vào PATH. Biến môi trường `OPENSCAD` nhận đường dẫn executable khi dùng bản portable. Python dùng các dependency trong `requirements.txt`. Các lệnh bên dưới chạy tại thư mục gốc repo.

Audit dùng bản STL tham chiếu do người chạy cung cấp tại `reference/Snaplock_Storage_Boxes_240x120(2).stl`, với SHA256 ghi cuối tài liệu. Thư mục `reference/` được giữ local; bộ public gồm mô hình tái dựng, số đo và báo cáo kiểm chứng.

```powershell
python -m pip install -r requirements.txt
python audit-scad.py
python audit-scad.py --variant
python compare-scad.py
```

STL từng chi tiết, `layout.stl`, `audit.json`, `preview.png` và `sections.png` được lưu trong `exports/default/`; biến thể ở `exports/variant/`. Khóa trong layout xuất hiện hai lần; xuất riêng `latch.stl` rồi đặt số lượng 2 trong slicer. Script audit dùng môi trường Python hiện có (`numpy`, `trimesh`, `manifold3d`); file SCAD tự dựng hình trong OpenSCAD.

## Mốc Fusion Python

Bản dựng lại có tham số từ STL `Snaplock_Storage_Boxes_240x120(2).stl`. Script độc lập, dùng API `adsk` có sẵn trong Fusion cùng thư viện chuẩn Python khi chạy.

**Bản Python 0.2.0 đã chạy thành công trong Fusion sau sửa của người dùng ở Mirror khe đàn hồi.** Source SHA256 `4cad327eab71f336bfe42e6dca9e688672e2635e3ba56e83fd2be63386d688f3` khớp log và manifest xuất STL. Kiểm tra bốn body, timeline/sketch và hai biến thể tham số đều hoàn tất. Cả hai khóa rộng đúng 28 mm. Script giữ một component gốc chứa `Body`, `Lid`, `Latch`, `Latch 2`, sketch có kích thước và timeline chỉnh sửa được.

[Tài liệu tự học OpenSCAD và Fusion Python](docs/fusion-python-tu-hoc.md) tổng hợp bài học từ năm dự án, hệ tọa độ sketch, Pattern 2 × 1, quản lý body, timeline và kiểm chứng.

Phần cập nhật gồm tai loe và footprint vát, lip vòng côn 50°, hốc trụ có hai chamfer 1 mm, chốt cầu được giới hạn đúng vùng, mép trước khóa R5 và răng/khe đàn hồi loft qua 25 tiết diện theo chiều dày. Lòng hộp được khoét sau khi ghép tai theo thứ tự boolean của SCAD. Fusion loft nội suy giữa các tiết diện, còn SCAD nối các tiết diện bằng mặt phẳng; sai khác của đầu ra native sẽ được đo từ STL xuất bởi Fusion.

## Chạy trong Fusion

**Bản thử 0.4.0:** [răng khóa bằng cung R5 và elip](docs/latch-analytic-construction.md) dùng bốn tiết diện XZ, một Extrude và hai Loft ngắn. [Khe hybrid](docs/scad-slot-hybrid.md) dùng một Extrude đuôi cùng Loft tám tiết diện. 36 test offline xác nhận công thức, vị trí tiết diện và ownership tool mô phỏng. Lần Run tiếp theo cung cấp bằng chứng native cho solver, Loft, Join, Mirror và biến thể độ dày. Log ghi `BUILD_METRICS` cùng `SLOT_BUILD`; mỗi audit lưu source hash xác định checkpoint.

[Add-in thử chuỗi Plane → Sketch → Loft](fusion/LoftSketchTest/README.md) dựng năm tiết diện ở năm cao độ, rồi dùng một Loft nối thành khối. Log ghi công thức, vị trí và kết quả kiểm tra biến thể.

[Add-in thử Plane và Sketch](fusion/PlaneSketchTest/README.md) so sánh ba cách tạo cùng hình học: plane riêng, plane dùng chung và Extrude Start Offset. Bài thử tạo ba document mới và kiểm tra thay đổi tham số trực tiếp trong Fusion.

Log chẩn đoán xác định bốn cạnh `Latch plate` còn tự do trong khi các điểm đã đủ ràng buộc. Script tại commit `6bc9da4` đổi thứ tự dựng profile: tạo điểm/cạnh trước, áp dimension và constraint tọa độ sau. Bộ 28 test offline xác nhận luồng thứ tự và chẩn đoán. Hướng sửa đang ở mốc kiểm chứng offline; lần chạy native tiếp theo xác nhận tác dụng trong Fusion. Mốc native thành công bên trên thuộc source `4cad327e…`, trước thay đổi này.

1. Mở **Utilities > Add-Ins > Scripts and Add-Ins** (thường là **Shift+S**), tab **Scripts**.
2. Bấm **+**, chọn thư mục `fusion/SnaplockStorageBox` chứa cả `.py` và `.manifest`.
3. Chọn **SnaplockStorageBox > Run**. Script tạo document mới và dựng các chi tiết ở bố trí tách rời để quan sát/in. Document đang làm được giữ nguyên.
4. Mở **Modify > Change Parameters** để chỉnh kích thước. Giữ công thức của các tham số derived.

Mặc định `VERIFY_VARIANTS = True`: sau khi dựng, script đổi kích thước sang 280 × 155 × 70 mm và đổi khe hở lên 0,2 mm, kiểm tra timeline/solid/sketch/kích thước bao rồi phục hồi giá trị ban đầu. Việc này kiểm chứng recompute; kiểm chứng assembly là một mốc riêng. Document dở dang được giữ lại tại bước phát sinh lỗi để xem feature; đoạn cuối `last-run.log` ghi rõ bước đó.

Sau khi dựng và kiểm tra thành công, script xuất bốn STL theo mm vào `fusion/SnaplockStorageBox/exports/<timestamp>/`. Hộp thoại cuối và `last-run.log` ghi thư mục cụ thể. `manifest.json` lưu hash source Python, hash từng STL và độ mịn mesh (surface deviation 0,005 mm). Mỗi lần chạy có thư mục riêng.

Chạy so sánh đầu ra Fusion với STL gốc và SCAD đã audit:

```powershell
python audit-fusion.py 'fusion/SnaplockStorageBox/exports/<timestamp>'
```

Thay `<timestamp>` bằng thư mục được ghi trong log. Script chỉ bù tịnh tiến từng chi tiết về góc nhỏ nhất để so hình dạng, giữ nguyên tỷ lệ và hướng; kết quả `comparison.json` ghi thể tích thừa/thiếu, sai khác thể tích đối xứng và sai lệch bounds. Mục tiêu audit là bounds <0,03 mm và thể tích đối xứng <0,3% cho từng chi tiết so với cả hai bản tham chiếu. Đây là ngưỡng kiểm tra, chưa phải kết quả đạt của Fusion. Vị trí assembly, khoảng cách toàn bề mặt, lực khóa và in thử cần kiểm chứng riêng.

## Feature được dùng

| Phần | Feature Fusion |
|---|---|
| Vỏ và vát đáy thân/nắp | Loft giữa hai tiết diện có đường thẳng/cung tròn, Extrude thành đứng, Loft Cut và Extrude Cut cho lòng |
| Ổ/chốt cầu | Revolve 360° từ nửa đường tròn; Cut, Intersect và Combine để giữ đúng vùng chi tiết |
| Khóa | Loft 25 tiết diện cho răng/khe đàn hồi; Revolve đầu cầu; Extrude Cut mép trước R5; cylinder tool + Fillet R2 + Combine Cut cho rãnh cong; Extrude Cut mặt dốc mở khóa |
| Tai ghép | Extrude tiết diện YZ, Intersect footprint XY, Loft côn tròn và boolean lip vòng; ổ trụ với hai đầu côn 1 mm |
| Chi tiết lặp | Mirror hai đầu của mỗi cụm; Rectangular Pattern hai cụm theo chiều dài; Body Pattern tạo khóa thứ hai |
| Bố trí | Move feature có biểu thức liên kết tham số; một component gốc chứa Body, Lid, Latch, Latch 2 |

Hình học được dựng bằng sketch có kích thước, công thức, đường thẳng và cung tròn. Mẫu có đáy thân 2 mm, đáy nắp 3 mm, thành 3 mm và vát trong khác nhau; các feature khoét lòng riêng giữ các tiết diện và độ dày này.

Bản này bố trí chi tiết tách rời; Joint chuyển động thuộc bước xây dựng assembly tiếp theo. Cả bốn body nằm trong mục Bodies của một component gốc. Khóa thứ hai được tạo bằng Body Pattern nên thay đổi feature/tham số của khóa gốc sẽ cập nhật bản sao khi recompute. Các chi tiết được dựng lần lượt tại gốc rồi chuyển đến vị trí in trước khi dựng chi tiết kế tiếp, giúp mỗi phép Join xử lý đúng chi tiết đích. Mounting Combine chỉ lấy các tai vừa tạo của chi tiết đang dựng.

Giới hạn Personal Use là [10 tài liệu đang cho phép chỉnh sửa](https://www.autodesk.com/products/fusion-360/blog/the-10-document-limit-for-personal-use-explained-in-7-steps/). Script tạo một tài liệu mới cho toàn bộ mẫu.

## Rà soát feature và timeline

- Bỏ construction plane offset literal `0 mm`; sketch dùng trực tiếp mặt phẳng gốc. Những offset bằng biểu thức/tham số vẫn được giữ, kể cả khi giá trị hiện tại bằng 0, để chỉnh tham số còn cập nhật đúng.
- Các Body Pattern đặt phương một bằng 2 và phương hai bằng 1. Bỏ `patternComputeOption` khỏi helper này vì cả ba caller đều pattern body; tùy chọn đó chỉ áp dụng khi pattern feature. Xem [quantityTwo](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/fusion_RectangularPatternFeatureInput_quantityTwo.htm).
- Sketch tiết diện, datum line và kích thước dùng để giữ ràng buộc/công thức; body dụng cụ tạo cầu, giới hạn chốt và cylinder+Fillet tạo rãnh đều có feature tiêu thụ. Giữ các phụ thuộc này; final check vẫn chặn body dụng cụ còn thừa.
- Hai Move bố trí in có liên kết tham số và giúp tách các chi tiết trước khi dựng phần tiếp theo trong cùng component. Các Mirror/Pattern tạo phần đối xứng/lặp nên được giữ.
- Bản 0.2.0 bổ sung sketch/feature để biểu diễn tai loe, lip côn và tiết diện khóa theo chiều dày. Kiểm kê 40 feature/25 sketch của bản 0.1.0 là số liệu lịch sử; số lượng timeline mới cần lấy từ document native sau khi dựng thành công.

Rà bản 0.2.0 sau sửa của người dùng: log ghi 69 lần tạo modeling/layout feature thành công. Theo luồng gọi source có 119 sketch và 94 lần tạo construction plane; các số này là kiểm kê source, chưa phải số timeline item lấy trực tiếp từ Fusion. Mọi sketch có consumer, mọi tool body được tiêu thụ và final check xác nhận đúng bốn body. Chưa thấy feature rác có thể xóa ngay. Có 28 cặp plane cùng base/biểu thức offset có thể dùng chung: 25 cặp tiết diện răng/khe khóa; mặt phẳng trim mép trước/ramp của khóa; mặt phẳng lip base/bore thân; mặt phẳng pocket lower end/barrel start. Chia sẻ plane là tối ưu cần chạy lại Fusion sau khi sửa; giữ source hiện tại để bảo toàn mốc native đã xác minh. Các sketch biên dạng và feature tạo/khoét tool vẫn cần thiết.

## Kích thước và tham số

Các tọa độ STL được diễn giải theo mm dựa trên số đo và quy mô cơ cấu của mẫu.

| Tham số | Mặc định | Ý nghĩa |
|---|---:|---|
| `length`, `width` | 237,85; 123,15 | Chiều dài và chiều rộng phần vỏ chính |
| `body_height`, `lid_height` | 52; 15 | Cao phần vỏ chính |
| `wall`, `body_floor`, `lid_floor` | 3; 2; 3 | Dày thành, đáy thân, đáy nắp |
| `corner_radius`, `body_inner_radius` | 12; 8 | Bo ngoài, bo lòng thân; bo lòng nắp = bo ngoài − thành |
| `bottom_bevel`, `body_inner_bevel` | 5; 4,7 | Khoảng chạy ngang của vát ngoài/vát trong thân, góc 60° |
| `mount_end` | 32,9 | Tâm cụm đầu thân; cụm sau tự theo chiều dài |
| `pin_radius`, `latch_ball_radius` | 5; 3,75 | Bán kính cầu bản lề và cầu khóa |
| `fit_clearance` | 0 | Tăng bán kính ổ cầu so với số đo nguồn; cần xác minh trước khi chọn giá trị in |
| `latch_thickness` | 6 | Dày khóa; cơ cấu đo được chỉ hỗ trợ khoảng nhỏ 5–6,5 mm |
| `layout_gap` | 20 | Khoảng bố trí thân/nắp/khóa tách rời |

Tâm cụm trên nắp lệch +0,1 mm theo X so với thân, giữ vị trí đo được ở nguồn. Khoảng cách giữa hai cụm vẫn dùng chung `mount_spacing = length - 2 * mount_end`. Khi tăng chiều dài/rộng/cao, kích thước chốt và khóa giữ nguyên theo kích thước cơ cấu đã đo.

Kích thước bao tham chiếu: thân khoảng 237,85 × 140,15 × 56,25; nắp 237,85 × 140,40 × 19,50; khóa 28 × 31,835 × 6 mm. STL có facet nên đỉnh thân trong mesh là 56,245 mm, còn cung tròn native đạt 56,25 mm.

## Mức độ bám mẫu và phần cần kiểm tra

- Giữ kích thước vỏ, lòng, dày đáy/thành, vát 60°, vị trí hai cụm ghép, bán kính cầu và rãnh đàn hồi chính theo mesh đã đo.
- Các gân đỡ tai/chốt dùng tiết diện và footprint của bản SCAD đã đo, thêm lip vòng côn và giới hạn chốt cầu. Chỉ số sai khác của SCAD ở đầu tài liệu thuộc đầu ra OpenSCAD; chỉ số cho Fusion sẽ lấy từ `audit-fusion.py` sau lần chạy native mới.
- Các góc lòng thân và đoạn chuyển tiếp nhỏ của khóa được làm bằng cung tròn native theo tiết diện đo. Audit sai số toàn bề mặt là mốc kiểm chứng bổ sung.
- Rãnh dưới khóa dùng cylinder R5 với Fillet hai mép R2 để dựng dải cong ở hai đầu. Mặt cầu R3,75 đã fit trực tiếp từ mesh; hai đầu rãnh cần đối chiếu sau khi Fusion tạo fillet.
- `fit_clearance = 0` giữ bán kính đo từ nguồn. Giá trị khe hở phục vụ in thực tế sẽ được chọn theo kết quả mẫu thử.
- Script kiểm tra giới hạn kích thước trước khi dựng. Sau khi chỉnh trong Change Parameters, áp dụng các giới hạn ở `dimensions()`; hàm kiểm tra chạy trong lần thực thi script.

## Kiểm chứng

Offline:

```powershell
python -m unittest discover -s tests -v
python -m py_compile fusion/SnaplockStorageBox/SnaplockStorageBox.py
```

Trong Fusion, script kiểm tra computeAll, feature health, số occurrence con bằng 0, đúng bốn solid mang tên Body, Lid, Latch, Latch 2, mọi sketch đủ ràng buộc, thể tích dương và kích thước bao của từng body. Dòng `NATIVE_BUILD_AND_RECOMPUTE_OK` trong log cùng SHA256 script xác nhận lần chạy native tương ứng; test offline xác nhận số học và các hợp đồng API được mô phỏng.

Lần chạy bản 0.2.0 ngày 12/10/2026 có log SHA256 khớp source và `NATIVE_BUILD_AND_RECOMPUTE_OK`; lưu bằng chứng ở `docs/validation/fusion-native-success.log`. Sửa của người dùng thay Mirror feature Loft Cut bằng Mirror hai body dụng cụ rồi Combine Cut, loại bỏ tình trạng khóa rộng 30 mm. Log mới xác nhận cả hai khóa rộng 28 mm, đúng bốn solid, feature/sketch và hai lần đổi tham số đều đạt.

Đầu ra native có khoảng 43,7 triệu tam giác, tổng 2,19 GB. Phép boolean đầy đủ bằng `audit-fusion.py` đã dừng do mức sử dụng bộ nhớ; chưa có kết quả symmetric difference cho Fusion. Kiểm tra streaming từng tam giác xác nhận hash cả bốn file, bounds và thể tích; số liệu ở `docs/validation/fusion-native-export-metrics.json`. Chênh thể tích có dấu so với STL gốc: thân +0,0773%, nắp +0,0073%, mỗi khóa −0,0171%. Chênh thể tích tổng không đo được các vùng thừa/thiếu bù nhau. Kiểm chứng assembly và in thử cụm khóa/bản lề là mốc tiếp theo.

Nguồn API chính thức:

- [Sketch.xDirection](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/fusion_Sketch_xDirection.htm) và [Sketch.yDirection](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/fusion_Sketch_yDirection.htm): đổi biểu thức tọa độ model sang trục thực của sketch, kể cả mặt YZ có trục X hướng -Z.
- [Fusion API: scripts và add-ins](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/UserManualIndex_UM.htm)
- [Mẫu tạo Loft](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/loftFeatures_add_Sample.htm)
- [Mẫu tạo Revolve](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/revolveFeatures_add_Sample.htm)
- [FilletFeatures.add](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/fusion_FilletFeatures_add.htm)

STL nguồn giữ nguyên, SHA256: `73faaa2d438b02038b9f84002202435973a09f92ec2a48315577e0e00baea167`.

## Bộ tài liệu agent tự học.

[Cẩm nang agent](docs/agent-learning.md) trình bày quy trình SCAD trước rồi Fusion Python sau, quản lý tham số, timeline và bằng chứng. [Sổ lỗi](docs/error-cookbook.md) tổng hợp các ca lỗi cùng cách sửa và mức xác nhận. [Mẫu giao việc](docs/scad-to-fusion-task.md) áp dụng quy trình cho model mới.

[Lộ trình đọc nguồn internet](docs/internet-learning.md) bổ sung tài liệu chính thức, bài thử về Fusion API, boolean, độ mịn và phép đo sai lệch bề mặt, cùng tiêu chí kiểm chứng cho từng bài.

[Quy trình STL → SCAD](docs/stl-to-scad.md) hướng dẫn tái dựng tham số từ mesh, đo mặt cắt, đối chiếu hình học và chốt baseline trước khi chuyển sang Fusion.
