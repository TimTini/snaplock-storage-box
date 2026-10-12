# Tự học OpenSCAD và Fusion Python

Tài liệu tổng hợp bài học thực hành và tài liệu của **năm dự án OpenSCAD**. Mốc rà soát là **13/10/2026**. [Báo cáo rà soát](learning-doc-review.md) ghi phạm vi kỹ thuật và nguồn đối chiếu.

Mỗi kết quả gắn với phiên bản, source hoặc báo cáo tương ứng. Source hiện tại, log native, kết quả mesh và thử nghiệm vật lý có phạm vi bằng chứng riêng.

Bộ bổ sung cho agent gồm [quy trình làm việc](agent-learning.md), [sổ lỗi và cách sửa](error-cookbook.md) và [mẫu giao việc SCAD → Fusion](scad-to-fusion-task.md). Các tài liệu dùng câu khẳng định và chỉ dẫn tích cực, với phạm vi kiểm chứng riêng cho từng checkpoint.

## 1. Lộ trình từ mẫu tham chiếu đến mô hình tham số

Chuỗi thực hành là **đo mẫu → dựng SCAD → đối chiếu hình học → dựng Fusion Python → kiểm tra recompute → đối chiếu đầu ra Fusion → thử in và lắp**.

| Bước học | Sản phẩm thực hành | Bằng chứng hoàn thành bước |
|---|---|---|
| Đọc mẫu | Bảng kích thước, bộ phận và hệ tọa độ | Số đo, mặt cắt, hash file nguồn |
| Viết SCAD | Primitive, module và công thức tham số | Render, mesh kín, biến thể kích thước |
| So sánh hình học | Mesh căn tọa độ và ảnh chồng | Thể tích thừa/thiếu, bounds, mặt cắt |
| Viết Fusion Python | Sketch và feature native | Source, kiểm thử công thức và contract API |
| Chạy Fusion | BRep, timeline và tham số liên kết | Log cùng hash source, trạng thái sketch/feature, recompute |
| Kiểm tra đầu ra | STL từng body và manifest | Hash, đơn vị, số body và sai khác hình học |
| Thử vật lý | Mẫu in, cơ cấu lắp và tải thử | Khe hở, đường lắp, lực thao tác, độ bền |

Bài tập gồm một profile, một feature và một tham số phụ thuộc giúp người học quan sát quan hệ giữa code và hình học. Các bài tập lớn mở rộng từ quan hệ đã kiểm chứng đó.

## 2. Đọc STL và chọn căn cứ hình học

STL biểu diễn bề mặt bằng tam giác. Việc tái dựng tham số lấy căn cứ từ hình dáng, kích thước, mặt cắt và quan hệ lắp ghép đo được. Đơn vị và hướng trục được ghi thành quy ước của từng dự án.

Snaplock có bốn phần chính: thân, nắp và hai khóa. Dữ liệu đo dùng mm. Vỏ chính dài **237,85 mm**, rộng **123,15 mm**, thân cao **52 mm**, nắp cao **15 mm**. Kích thước bao cả tai/chốt của thân đạt khoảng **237,85 × 140,15 × 56,25 mm**. Tên file `240x120` là nhãn mẫu; bảng kích thước lấy giá trị từ mesh.

Mỗi chi tiết được tách và đưa về hệ tọa độ quy ước trước khi đối chiếu. Phép đổi trục và tịnh tiến được lưu trong [tài liệu hình học Snaplock](scad-reference.md). Phép chuẩn hóa giữ nguyên tỷ lệ và số đo thiết kế.

Vùng tai, ngàm, ổ cầu, gân và đầu ren được khảo sát bằng mặt cắt tại nhiều vị trí. Các điểm đo đặc trưng được gom vào profile có tên, cùng nguồn số đo và mô tả xấp xỉ.

Với mẫu chỉ dùng làm tham chiếu cho một số đo, phạm vi tái sử dụng được ghi rõ từ đầu. Bản thiết kế mới được lưu thành dự án riêng, cùng snapshot và hash của căn cứ đo.

## 3. Viết SCAD bằng quy luật hình học

Các kích thước đầu vào nằm ở đầu file hoặc Customizer. Các kích thước phụ thuộc được tính bằng công thức. Module có tên theo chức năng như thân, nắp, tai, khóa và lỗ thoát nước.

| Nhu cầu | Cách biểu diễn SCAD |
|---|---|
| Tiết diện phẳng | `polygon()`, `circle()`, `square()`, `offset()` |
| Chiều cao đều | `linear_extrude()` |
| Hình tròn xoay | `rotate_extrude()`, `cylinder()`, `sphere()` |
| Hợp và khoét | `union()`, `difference()`, `intersection()` |
| Đối xứng | `mirror()` với tâm/trục theo công thức |
| Các phần lặp | Vòng lặp `for` và khoảng cách tham số |
| Chuyển tiếp đặc trưng | Các tiết diện đo được, có kiểm tra hình học đầu ra |

Thứ tự boolean là một phần của thiết kế. Snaplock hợp tai vào vỏ rồi khoét lòng hộp; thứ tự này giữ phần tai giao với khoang theo bản tham chiếu.

Miền hợp lệ được diễn đạt bằng `assert`. Bán kính góc, bề dày đáy và vát trong tạo tiết diện có kích thước dương. Bộ biến thể gồm mặc định, kích thước lớn hơn và các trường hợp sát giới hạn hợp lệ.

## 4. Tham số liên kết và phạm vi cập nhật

Tham số gốc diễn tả lựa chọn thiết kế như dài, rộng, cao, dày thành, đường kính lỗ và khe hở. Tham số derived diễn tả quan hệ như `inner_width = width - 2 * wall` hoặc vị trí tâm theo chiều cao tai.

Trong Fusion, biểu thức dimension và feature giữ liên kết với **Change Parameters**. Giá trị số khởi tạo hình học; biểu thức giữ ý nghĩa thiết kế khi recompute. API Fusion dùng cm cho chiều dài nội bộ; công cụ báo cáo Snaplock chuyển kết quả sang mm và mm³.

| Ví dụ | Quan hệ cần giữ |
|---|---|
| Khay bông tắm | Tâm móc đi theo chiều cao tai; lưới lỗ căn giữa theo dài/rộng |
| Hộp bàn chải | Đường kính lòng, bề dày đáy, ren thân và gờ ren nắp theo bộ kích thước chung |
| Thời khóa biểu | Kích thước ô, khoảng cách hàng/cột và khung đi theo tham số |
| Snaplock | Tâm chốt, tai tương ứng, khoảng cách hai khóa và khe hở dùng công thức liên kết |

Tham số kích thước cập nhật các feature hiện có. Các lựa chọn tạo topology hoặc nội dung tại lúc **Run** được ghi riêng: `HOOK_COUNT` của khay, số nhãn/ngày và số cung theo bước sóng của thời khóa biểu. Một lần Run mới tạo lại cấu trúc theo các lựa chọn đó.

## 5. Chọn feature native theo hình học

| Hình học | Feature phù hợp trong các dự án |
|---|---|
| Tấm, thành và gân có tiết diện đều | Sketch + Extrude |
| Khối có các tiết diện thay đổi | Loft |
| Chốt, ổ cầu và dụng cụ tròn xoay | Revolve |
| Bo, vát | Fillet, Chamfer |
| Biên liên kết | Offset sketch với ràng buộc tương ứng |
| Chi tiết lặp và đối xứng | Pattern, Mirror |
| Hợp/khoét các body xác định | Combine Join/Cut/Intersect |
| Ren có đường dẫn tham số | Surface helix + Sweep trong script hộp bàn chải hiện tại |

Shell phù hợp với cấu trúc bề dày đồng đều theo cách feature biểu diễn. Snaplock dùng khối ngoài và khoét lòng riêng để giữ thành **3 mm**, đáy thân **2 mm**, đáy nắp **3 mm** cùng tiết diện vát.

Hộp bàn chải dùng ren ngoài trên thân và gờ ren Join trong lòng nắp. Tiết diện Sweep tròn và fade đầu ren là các vùng cần đối chiếu với SCAD. Bài probe Coil trong lịch sử có mục đích khảo sát API; script hiện tại dùng surface helix và Sweep.

Thời khóa biểu dùng cung tròn native và viền offset liên kết. Hình học cung thay thế có mô tả riêng so với biên dạng sóng tham chiếu. Chữ được xử lý theo luồng `SketchText → explode() → Profiles → NewBody → Combine` đã được sửa qua lỗi runtime.

Outline glyph được tạo tại lúc explode. Việc đổi cỡ chữ hoặc nội dung sau bước này đi cùng một lần Run mới để tạo lại glyph. Contract kiểm tra SketchText và sketch glyph có phạm vi riêng được mô tả trong README Fusion thời khóa biểu.

## 6. Hệ tọa độ và ràng buộc sketch

Hệ trục sketch được đọc từ `xDirection` và `yDirection`. Điểm, tâm đường tròn và cung đều dùng cùng phép đổi tọa độ. Với mặt YZ trong ca Snaplock, tọa độ model `(Y, Z)` được biểu diễn theo hướng sketch `(-Z, Y)`.

Sketch có profile kín, dimension theo công thức và ràng buộc hình học phù hợp. Kiểm tra fully constrained khảo sát cả điểm lẫn curve. Datum có endpoint được ràng buộc rõ ràng để dimension tọa độ có tham chiếu ổn định.

Chẩn đoán sketch ghi tên entity, loại entity, tọa độ và số dimension/constraint. Ca `Latch plate` ghi **2 constraint, 6 dimension**, các điểm đủ ràng buộc và bốn cạnh còn tự do. Số lượng dimension mô tả dữ liệu chẩn đoán; `isFullyConstrained` là kiểm tra solver riêng.

Bản sửa **thứ tự profile** tạo điểm và cạnh trước, rồi áp dimension/constraint tọa độ. Bộ mock kiểm tra thứ tự dựng đạt **28 test** ở checkpoint 12/10/2026. Giả thuyết về cập nhật trạng thái solver đang ở mốc kiểm chứng offline; lần chạy native tiếp theo xác nhận tác dụng trong Fusion.

## 7. Quy trình SCAD trước, Fusion Python sau

STL gốc là chuẩn của hình dáng, kích thước và quan hệ lắp ghép. SCAD là mô hình trung gian để kiểm tra hình học bằng công cụ chạy tự động. Fusion Python biểu diễn hình học đã đối chiếu bằng cây feature native có thể chỉnh sửa.

1. File nguồn được lưu cùng SHA256, bảng đơn vị, hệ trục và danh sách bộ phận.
2. SCAD được dựng từ primitive, module, công thức, đối xứng và các tiết diện đặc trưng.
3. Mesh SCAD được đối chiếu với STL qua bounds, boolean thể tích và mặt cắt cùng tọa độ.
4. Các vùng xấp xỉ được ghi nhận theo vị trí và ảnh hưởng hình học.
5. Bản SCAD cùng bảng kích thước được chốt làm căn cứ chuyển đổi.
6. Fusion Python được dựng bằng feature native phù hợp với từng vùng.
7. Đầu ra Fusion được đối chiếu với STL gốc và SCAD, sau đó chuyển sang kiểm chứng đường lắp và mẫu in.

Độ bám mẫu, solid hợp lệ và khả năng recompute là ba kết quả riêng. Cây feature có thể khác giữa SCAD và Fusion; phép so sánh đầu ra xác nhận mức tương đồng hình học.

## 8. Body, Pattern và timeline có mục đích rõ ràng

Snaplock tổ chức một component gốc chứa **`Body`, `Lid`, `Latch`, `Latch 2`**. Script đặt tên document và tên từng body. Kiểm tra cuối khảo sát số solid, tên, bounds và thể tích.

Pattern một phương khai báo rõ **`quantityOne = 2`**, **`quantityTwo = 1`**. Bản sao khóa được lấy từ kết quả Pattern và kiểm tra vị trí dịch **48 mm**. Phạm vi body đích của Cut/Intersect và danh sách tool của Combine được xác định rõ, giúp các chi tiết chung component giữ đúng ownership.

Sửa Mirror khe đàn hồi dùng **Loft NewBody → Mirror body dụng cụ → Combine Cut**. Log native của source `4cad327e…` xác nhận hai khóa rộng **28 mm** sau thay đổi này.

Chuỗi **plane → sketch → feature** diễn tả ba nhiệm vụ: đặt tiết diện, định nghĩa biên dạng và tạo khối. Khóa dày **6 mm** dùng **25 tiết diện**, cách **0,25 mm**, cho phần răng và khe thay đổi theo chiều dày.

Hai sketch cùng cao độ có thể dùng chung một plane và giữ mục đích profile riêng. Rà soát checkpoint 12/10/2026 ghi **28 cặp plane** là ứng viên dùng chung: 25 cặp răng/khe khóa và ba cặp ở các vùng khác. Mỗi thay đổi chia sẻ plane hoặc giảm tiết diện đi cùng kiểm tra tham chiếu, recompute và sai khác hình học.

| Thống kê Snaplock 0.2.0 | Ý nghĩa bằng chứng |
|---|---|
| 69 mốc tạo feature thành công | Số dòng tiến trình trong log native đã lưu |
| 119 sketch, 94 plane | Kiểm kê từ luồng source tại checkpoint audit |
| 28 cặp plane cùng base/offset | Ứng viên tối ưu tham chiếu |
| 4 body cuối | Kết quả native của source `4cad327e…` |

Số lời gọi builder, số dòng log và số timeline object là các phép đếm riêng. Bản kiểm kê ghi rõ cách đếm, phiên bản source và mục đích của tool được consume.

## 9. Đo sai khác và đọc đúng chỉ số

Bounds đo tọa độ bao. Thể tích tổng đo lượng vật liệu. Boolean thừa/thiếu đo phần hình học của hai khối khác nhau. Khoảng cách bề mặt đo sai lệch cục bộ theo mm. Mặt cắt chỉ rõ vị trí thay đổi hình dạng.

Với khối dựng `A` và khối tham chiếu `B`, báo cáo Snaplock dùng:

```text
Thừa = volume(A \ B)
Thiếu = volume(B \ A)
Sai khác đối xứng (%) = 100 * (Thừa + Thiếu) / volume(B)
Chênh thể tích có dấu (%) = 100 * (volume(A) - volume(B)) / volume(B)
```

Hai khối có thể có thể tích tổng bằng nhau và khác vị trí vật liệu. Chênh thể tích có dấu được đọc cùng boolean và mặt cắt. Khoảng cách bề mặt hai chiều bổ sung thông tin về vùng lồi và vùng lõm.

### Kết quả SCAD Snaplock đã lưu

Source SCAD có SHA256 `905322f5338d6685ad3f4358f270e81659eed66be9e8c7b49aab171c05a9fba1`.

| Chi tiết | Thừa, mm³ | Thiếu, mm³ | Sai khác đối xứng | Sai lệch bounds, mm |
|---|---:|---:|---:|---:|
| Thân | 134,654 | 18,489 | 0,0927% | 0,00409 |
| Nắp | 39,017 | 35,776 | 0,0659% | 0,00966 |
| Khóa | 0,446 | 1,062 | 0,0429% | 0,00201 |

Nguồn số liệu là [audit mặc định](validation/scad-audit-default.json), [audit biến thể](validation/scad-audit-variant.json) và [ảnh chồng mặt cắt](../exports/default/sections.png). Bounds và tỷ lệ thể tích có phạm vi đo như tên cột. Bản đồ khoảng cách toàn bề mặt là bài kiểm chứng bổ sung.

### Kết quả Fusion Snaplock đã lưu

Log ngày 12/10/2026 có marker `NATIVE_BUILD_AND_RECOMPUTE_OK`, cùng source SHA256 **`4cad327eab71f336bfe42e6dca9e688672e2635e3ba56e83fd2be63386d688f3`**. Lần chạy đó xác nhận bốn solid, sketch, timeline và hai biến thể: **280 × 155 × 70 mm**, **`fit_clearance = 0,2 mm`**.

| Body | Bounds native, mm | Thể tích BRep, mm³ | Chênh thể tích STL Fusion so với STL gốc |
|---|---|---:|---:|
| Body | 237,85 × 140,15 × 56,25 | 165378,139 | +0,077286% |
| Lid | 237,85 × 140,3999895 × 19,50 | 113480,103 | +0,007296% |
| Latch | 28 × 31,835144 × 6 | 3513,626 | −0,017146% |
| Latch 2 | 28 × 31,835144 × 6 | 3513,626 | −0,017146% |

Cột cuối là **chênh thể tích có dấu** của mesh xuất. Thể tích BRep và thể tích STL được đo trên hai cách biểu diễn hình học riêng.

Bộ STL xuất có **43.733.174 tam giác**, tổng **2.186.659.036 byte**. Phép đọc streaming đã kiểm tra hash, số tam giác, bounds và thể tích có dấu. Phép boolean toàn mesh dừng ở giới hạn bộ nhớ; sai khác đối xứng Fusion thuộc mốc kiểm chứng tiếp theo. [Log native](validation/fusion-native-success.log) và [báo cáo streaming](validation/fusion-native-export-metrics.json) giữ bằng chứng của lần chạy này.

## 10. Bài học thực hành từ năm dự án

| Dự án | Bài học hình học và tham số | Căn cứ hiện có |
|---|---|---|
| [Hộp bàn chải điện](https://github.com/TimTini/electric-toothbrush-case/blob/main/README.md) | Dáng vỏ, lòng, đáy và chủ sở hữu ren theo tham chiếu; MoveFace từ F3D/STEP dùng trục/pivot theo helix | SCAD dùng 19 lỗ đáy Ø3, lòng Ø42,4, lòng nắp khoảng Ø48; kiểm tra offline mặt phẳng nghiêng 70° |
| [Khay bông tắm](https://github.com/TimTini/bath-sponge-tray/blob/main/README.md) | Tâm móc theo tai, lưới lỗ theo kích thước và số móc chọn khi Run | Mẫu 100 × 70 × 30 mm; 35 lỗ Ø6 theo lưới 7 × 5, bước 12 mm |
| [Thời khóa biểu](https://github.com/TimTini/thoi-khoa-bieu-openscad/blob/main/README.md) | Dữ liệu nhãn, số ngày và layout đi cùng nhau; cung native và offset liên kết có cách dựng riêng | Test layout thay đổi cấu hình; chữ 5,2 mm với growth 0,15 mm ở mốc sửa chữ |
| [Thùng rác bốn góc V4](https://github.com/TimTini/thung-rac-4-goc/blob/main/README-v4.md) | Kiểm tra đường đưa chốt vào và thể tích quét dọc hành trình | V4 đưa chốt theo pháp tuyến ngoài thành; audit đường lắp và mesh có phạm vi riêng |
| [Snaplock](../README.md) | Đo tiết diện khóa, dùng chung tâm lắp, quản lý body và kiểm tra từng lớp bằng chứng | Audit SCAD, log Fusion source `4cad327e…`, chẩn đoán sketch và test thứ tự dựng |

V3 của thùng rác cung cấp bài học về va chạm với gân dọc đường đưa chốt. V4 là bản tham chiếu hiện tại theo hướng chốt mới. Thử in, độ hở và tải chịu lực là các bước xác nhận vật lý.

## 11. Xuất file, ảnh vật liệu và công bố

Mỗi bộ xuất có tên cấu hình, đơn vị, hash source và hash file đầu ra. Độ mịn mesh được chọn theo mục tiêu đo hoặc in, đồng thời theo dõi số tam giác và bộ nhớ.

3MF màu được kiểm tra trong dữ liệu đã serialize và trong slicer. Mốc thời khóa biểu dùng `-O export-3mf/material-type=color` cùng alpha opaque `FF`. Khả năng chọn từng object và mapping filament được xác nhận bằng lần nhập slicer cụ thể.

Ảnh vật liệu dùng CAD, preview, layout, chữ và lỗ làm căn cứ. Mỗi góc nhìn được so với các bề mặt hiện ra trong mẫu. Bộ ảnh hộp bàn chải đã có lượt tạo lại sau khi phát hiện chi tiết đáy được thêm vào hình minh họa.

Ảnh AI/render được ghi đúng loại ảnh minh họa. Ảnh mẫu in thật cung cấp bằng chứng về bề mặt, vật liệu và kết quả chế tạo. Mỗi yêu cầu ảnh được thực hiện theo số lượng và dự án đã chọn.

Các kho công khai dùng dữ liệu demo tổng quát và thông tin nguồn/giấy phép phù hợp. Trạng thái draft, upload, verifying và published được ghi theo bằng chứng từng nền tảng. Những mốc MakerWorld trong lịch sử đang ở các bước chuẩn bị hoặc xác minh; xác nhận published công khai là một bằng chứng riêng.

## 12. Cách tự kiểm tra và ghi bài học

Ghi chép thực hành có mục tiêu, file nguồn, hash, tham số, lệnh chạy, kết quả và bước xác nhận tiếp theo. Lỗi được ghi bằng bước phát sinh, traceback và entity liên quan. Giả thuyết sửa và kết quả chạy được đặt ở hai dòng bằng chứng riêng.

| Lớp kiểm chứng | Phạm vi xác nhận |
|---|---|
| Source review | Công thức, luồng feature, ownership, phạm vi thay đổi |
| Test offline/mock | Logic Python và contract được mô hình hóa trong test |
| SCAD render/audit | Mesh của cấu hình đã xuất và số liệu đối chiếu tương ứng |
| Fusion native | Solver, BRep, timeline và recompute của source ghi trong log |
| Slicer | Đơn vị, object, màu và thiết lập của file đã nhập |
| Vật lý | Lắp, lực, khe hở, hướng in và tải của mẫu thử |

Bộ công cụ đang dùng tốt trong workspace gồm OpenSCAD CLI, Python và các script audit. CloudCompare bổ sung bản đồ khoảng cách; MeshLab bổ sung công cụ đo mesh. Các chức năng được lựa chọn theo loại chỉ số cần xác nhận.

Lệnh sau chạy bộ test offline Snaplock từ đúng thư mục dự án:

```powershell
python -m unittest discover -s tests -v
```

[audit-scad.py](../audit-scad.py) xuất và so sánh SCAD; tùy chọn `--variant` chọn biến thể. [compare-scad.py](../compare-scad.py) tạo ảnh chồng mặt cắt. [audit-fusion.py](../audit-fusion.py) nhận thư mục xuất Fusion chứa `manifest.json` và kiểm tra nguồn/hash trước khi audit. Các lần audit boolean mesh lớn được chuẩn bị theo dung lượng và độ mịn mesh.

Lần thực hành tiếp theo của Snaplock tập trung vào chạy native bản sửa thứ tự profile, đọc chẩn đoán `Latch plate` và đối chiếu hash log với source. Bài tối ưu plane đi sau mốc native đó và có bộ so sánh hình học riêng.

## Tài liệu tham chiếu

- [Mục lục năm dự án](https://github.com/TimTini) và [trạng thái Fusion](../README.md).
- [README Snaplock](../README.md), [hình học tham chiếu](scad-reference.md) và [checkpoint kỹ thuật](validation/README.md).
- [Fusion hộp bàn chải](https://github.com/TimTini/electric-toothbrush-case/blob/main/fusion/README.md), [Fusion khay](https://github.com/TimTini/bath-sponge-tray/blob/main/fusion/README.md), [Fusion thời khóa biểu](https://github.com/TimTini/thoi-khoa-bieu-openscad/blob/main/fusion/README.md), [Fusion thùng rác](https://github.com/TimTini/thung-rac-4-goc/blob/main/fusion/README.md).
- [Autodesk Sketch.xDirection](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/fusion_Sketch_xDirection.htm) và [Sketch.yDirection](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/fusion_Sketch_yDirection.htm).
- [Autodesk Pattern.quantityTwo](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/fusion_RectangularPatternFeatureInput_quantityTwo.htm) và [Pattern.bodies](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/fusion_RectangularPatternFeature_bodies.htm).
- [Autodesk Sketch.isFullyConstrained](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/fusion_Sketch_isFullyConstrained.htm).
- [CloudCompare: so sánh hai đối tượng 3D](https://www.cloudcompare.org/doc/wiki/index.php/How_to_compare_two_3D_entities).
