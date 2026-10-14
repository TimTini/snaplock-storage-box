> Hồ sơ ví dụ theo checkpoint đã ghi; các bước còn chờ trong hồ sơ thuộc thời điểm đó. Trạng thái hiện hành của Snaplock nằm ở [SCAD](../geometry/latch-parametric-fix.md) và [Fusion](../geometry/fusion-parametric-sync.md). Quy trình chung bắt đầu tại [bộ hướng dẫn](../guides/README.md).

# Rà phương pháp dựng toàn project Snaplock

Mốc rà soát ngày 13/10/2026 dùng source `48f001a` làm đầu vào và bản Fusion 0.5.1 làm đầu ra hiệu chỉnh. Phạm vi gồm SCAD chính, toàn bộ luồng dựng Fusion, các bài thử độc lập, tham số, công cụ đối chiếu, preset in và tài liệu đang hướng dẫn sử dụng. SCAD đã chốt tại `bd919e1` tiếp tục là baseline hình học.

## Bảng phương pháp theo vùng

| Vùng | SCAD hiện tại | Fusion hiện tại | Kết luận |
|---|---|---|---|
| Vỏ và thành đứng | Rounded offset và Extrude | Cung tròn/đường thẳng, Extrude | Phép dựng diễn đạt trực tiếp tiết diện |
| Vát đáy và lòng | Hull giữa hai profile | Loft hai profile và Extrude Cut | Hai profile mô tả chuyển tiếp bán kính/inset của vỏ |
| Gân tai và footprint | Profile YZ, Extrude, giao biên XY | Extrude và Combine Intersect | Các profile khác nhau biểu diễn gân loe và vùng giới hạn |
| Tai và vị trí lặp | Module, vòng lặp và đối xứng | Mirror đầu cụm, Pattern theo chiều dài | Hình học lặp dùng lại mẫu |
| Đầu cầu và ổ cầu | Sphere và phép giao/cắt | Revolve 360° từ nửa đường tròn và boolean | Hình học giải tích |
| Rãnh cong ở khóa | Rotate Extrude | Trụ, Fillet R2 và Cut | Hình học theo quy luật tròn |
| Răng khóa | Trụ R5, elip và hai hull ngắn | Trụ R5, elip và hai Loft hai profile | Đã thay cấu trúc 25 tiết diện |
| Khe đàn hồi | Đuôi Extrude và tám profile phần trước | Đuôi Extrude và Loft tám profile | Giữ lựa chọn đã so dung sai và tổng bước |
| Ba nhóm gân trong | Profile, Extrude và vòng lặp theo trạm | Sáu profile mẫu tối đa, Extrude/Mirror/Pattern | Số profile mẫu giữ cố định khi số trạm tăng |
| Khóa thứ hai | Gọi lại module | Body Pattern | Bản sao liên kết hình học khóa gốc |
| Lip vòng côn và hốc chamfer | Trụ/nón, giao và cắt | Loft hai profile, trụ Extrude và boolean | Có ứng viên Revolve để khảo sát tiếp |

Các vùng SCAD được định nghĩa tại `rounded`, `bevel`, `shell_blank`, `cavity`, `body_mount`, `lid_mount`, `internal_reinforcement`, `notch_tool`, `latch_tooth` và `latch`. Luồng Fusion tương ứng nằm trong `build_shell`, `cut_cavity`, bốn hàm `mount_make_*`, `build_mounts`, `build_latch_teeth`, `build_latch_relief`, `build_reinforcement` và `build_latch` của [script](../../fusion/SnaplockStorageBox/SnaplockStorageBox.py).

## Các điểm đã hiệu chỉnh ở 0.5.1

### Plane dùng chung theo tham chiếu và công thức

`Native.plane()` trước hiệu chỉnh tạo ConstructionPlane mới cho mọi offset khác literal `0 mm`. Call trace của source `48f001a` có bảy nhóm trùng sau ở cấu hình mặc định:

| Base | Biểu thức offset nguyên văn | Hai consumer |
|---|---|---|
| XY | `outer_bevel_height` | Tiết diện thành ngoài Body và Lid |
| YZ | `(mount_end) + (-22 mm)` | Gân tai sau và gân ngàm trước thân |
| YZ | `(mount_end) + (-12.75 mm)` | Lip base và bore thân |
| XY | `body_height - 10.5 mm` | Cuối chamfer dưới và đầu đoạn trụ hốc |
| XY | `6 mm` | Clip lip nắp và nửa đường tròn ổ cầu nắp |
| XY | `latch_thickness` | Cắt mặt trên đầu cầu và tiết diện cuối khe đàn hồi |
| YZ | `-2 mm` | Cắt mép trước R5 và cắt ramp mở khóa |

Bật cả ba nhóm gân thêm ba nhóm trùng: YZ ở `rib_margin + rib_step_x - rib_thickness / 2`, XZ ở `rib_margin + rib_step_y - rib_thickness / 2`, và XY ở `body_floor - 0.001 mm`. Hai nhóm đầu phục vụ cả gân đứng lẫn chân tam giác; nhóm cuối phục vụ hai phương của lưới đáy.

Bản 0.5.1 dùng một danh sách plane trong từng instance `Native`. Cùng base và cùng chuỗi biểu thức nhận cùng object plane. Base khác hoặc chuỗi biểu thức khác tiếp tục tạo plane riêng. Literal `0 mm` dùng Origin; offset chứa tham số giữ expression kể cả khi giá trị hiện tại bằng 0. Mỗi plane giữ tên của consumer tạo đầu tiên.

Call trace trước hiệu chỉnh có 46 lần tạo plane ngoài Origin ở mẫu mặc định và 54 khi bật đủ gân. Tập key duy nhất tương ứng là 39 và 44. Sau hiệu chỉnh, dự kiến giảm **7 plane** ở mẫu mặc định và **10 plane** khi bật đủ gân. Đây là số suy từ luồng source; `BUILD_METRICS` trong log lần Run cung cấp số object và timeline native thực tế.

Chia sẻ plane giữ một quan hệ offset chung; đổi tham số cập nhật plane cùng mọi sketch đang tham chiếu nó. Các biên dạng khác chức năng tiếp tục có sketch riêng. Việc hiệu chỉnh tập trung vào object dựng trùng với cùng tham chiếu/công thức.

### Hốc trụ dùng chung profile tròn

`mount_make_body_front()` trước hiệu chỉnh tạo hai circle sketch tại cùng XY, cùng cao độ `body_height - 10.5 mm`, cùng tâm và bán kính 5 mm: cuối chamfer dưới và đầu đoạn trụ. Bản 0.5.1 dùng sketch `bottom2` cho cả endpoint Loft và Extrude đoạn trụ dài 4,5 mm. Các biểu thức hình học giữ nguyên.

Cách một profile phục vụ Loft và Extrude đã xuất hiện trong `build_shell()` và `cut_cavity()`. Hiệu chỉnh hốc giảm thêm **một sketch**, ngoài phần plane đã tính trong bảng. Tổng mức giảm theo source là tám mục plane/sketch ở mẫu mặc định và mười một khi bật đủ gân. Các modeling feature của hốc tiếp tục giữ nguyên.

### Tài liệu chỉ dẫn phương pháp hiện hành

README mô tả răng bằng R5/elip và khe bằng đuôi Extrude cùng tám tiết diện. Số 25 tiết diện được giữ trong các checkpoint lịch sử và bộ đối chiếu snapshot. Lệnh đối chiếu export 0.5.x dùng `tools/audit-fusion-ribs.py --native`, dựng SCAD theo `parameters_mm` và `reinforcement` trong manifest. `tools/audit-fusion.py` phục vụ phép so baseline kích thước mặc định, gân tắt với STL gốc và SCAD mặc định.

Hướng dẫn gân phân biệt preset enhanced 5/20/5 mm với preset baseline 3/12/20 mm theo thứ tự độ nhô/chân/khoảng chừa đầu. Các giá trị này có preset và báo cáo riêng.

## Các ứng viên tối ưu tiếp theo

### Hốc trụ có hai chamfer ưu tiên thử Revolve Cut

Hốc trước có quy luật tròn quanh trục Z: bán kính 4 → 5 mm qua chamfer dưới 1 mm, đoạn trụ R5 dài 4,5 mm, rồi bán kính 5 → 4 mm qua chamfer trên 1 mm. Source 0.5.1 dùng bốn circle sketch, hai Loft, một Extrude và một Combine Cut.

Một profile bán kính–cao độ khép kín cùng Revolve Cut 360° là ứng viên gọn hơn và diễn đạt trực tiếp quy luật này. Bộ thử cần đối chiếu riêng tool/hốc với baseline, vị trí trục theo `mount_end` và `width`, chiều cao theo `body_height`, participant body cùng recompute. Sau đối chiếu đạt, cấu trúc Revolve có thể thay trọn cụm hốc. Ứng viên hiện ở mức đề xuất từ source.

### Lip vòng côn ưu tiên khảo sát profile quay

Lip thân có mặt ngoài côn 50° và bore trụ; lip nắp có mặt ngoài trụ cùng lỗ côn. Revolve tiết diện dọc trục là ứng viên thay các circle sketch/Loft và tool cắt. Profile phải giữ vùng giao của mặt côn với bán kính bore, góc 50°, footprint và các mặt giới hạn hiện có. Bộ đối chiếu đo vùng lip, thể tích và bounds của tai hoàn chỉnh ở các kích thước cơ cấu được phép.

### Hai mặt phẳng cắt đầu cầu ưu tiên so tổng bước

`Flat sphere tops` và `Flat sphere bottoms` hiện dùng hai rectangle sketch cùng hai Extrude Cut. Mirror một cut qua mặt giữa `latch_thickness / 2` là ứng viên liên kết đối xứng. Phương án cần thêm midplane và Mirror; tổng bước được so với hai sketch/cut hiện có, cùng khả năng nhận seed cut và recompute. Mức giảm thực tế quyết định việc áp dụng.

## Các cấu trúc được giữ theo bằng chứng

Khe đàn hồi tám tiết diện là chuỗi còn hơn năm Plane → Sketch. [Bộ thử 5–9 tiết diện](../validation/scad-slot-section-probes.json) chọn tám là mức thấp nhất đạt ngưỡng lấy mẫu 0,03 mm qua ba chiều dày. [Bài thử Sweep Parallel](../../fusion/tests/SlotSweepTest/README.md) xác nhận một mặt cung native với phạm vi riêng. [Quy trình lựa chọn](../guides/scad-to-fusion-task.md) giữ Loft hybrid theo tổng bước và khả năng chỉnh sửa của toàn khe.

Các Loft hai profile ở vỏ/vát lòng và các chuyển tiếp elip–tròn diễn đạt biến đổi tiết diện có chủ đích. Hốc và lip có quy luật tròn để khảo sát Revolve như trên. Gân tai có footprint khác nhau nên mỗi profile giữ chức năng riêng. Origin plane, datum line, sketch đầy đủ ràng buộc, tool có consumer, Mirror/Pattern và Move bố trí có biểu thức đều có vai trò trong luồng dựng.

`PlaneSketchTest`, `LoftSketchTest` và `SlotSweepTest` là bài thử độc lập có manifest/README. Các script audit catch/slot giữ chức năng hồi quy và so phương pháp; snapshot, preset baseline và log native theo hash giữ vai trò bằng chứng lịch sử.

## Kiểm chứng và ranh giới xác nhận

Ba regression mới kiểm tra dùng chung plane theo base/chuỗi biểu thức, phạm vi riêng mỗi builder và dùng chung profile hốc. Hai regression tái hiện việc tạo trùng ở source cũ, rồi đạt sau hiệu chỉnh. Bộ đầy đủ có **50 test**. [Audit 24 tổ hợp gân](../validation/fusion-reinforcement-offline.json) được tái lập theo hash Python 0.5.1; source SCAD giữ nguyên.

Unit test kiểm tra hợp đồng API mô phỏng và biểu thức. CSG offline kiểm tra hình học gân. Lần Run Fusion xác nhận tham chiếu plane dùng chung, sketch có hai consumer, solver, feature health, bốn body và các biến thể recompute. `BUILD_METRICS`, `RIB_CHECK`, hash source và `NATIVE_BUILD_AND_RECOMPUTE_OK` ghi bằng chứng của lần Run đó. Export native được so lại bằng `tools/audit-fusion-ribs.py --native` với cấu hình manifest.

Lực chịu tải, độ đàn hồi và lắp ráp của mẫu in có bước kiểm chứng vật lý riêng.
