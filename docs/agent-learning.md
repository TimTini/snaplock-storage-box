# Agent học từ quy trình OpenSCAD đến Fusion Python.

Bộ tài liệu dùng chung cho năm dự án, gồm [cẩm nang này](agent-learning.md), [sổ lỗi và cách sửa](error-cookbook.md), [mẫu giao việc](scad-to-fusion-task.md) và [tài liệu kỹ thuật chi tiết](fusion-python-tu-hoc.md). Nội dung dùng câu khẳng định và các chỉ dẫn tích cực. Mỗi kết luận kỹ thuật gắn với source, test hoặc báo cáo của phiên bản tương ứng.

Lộ trình [đọc nguồn internet và thực hành](internet-learning.md) bổ sung tài liệu OpenSCAD, Autodesk Fusion API, BOSL2, Trimesh, CloudCompare và CGAL, kèm bài thử cùng bằng chứng cần lưu.

[Quy trình STL → SCAD](stl-to-scad.md) hệ thống hóa việc đo mesh, suy ra quy luật hình học, dựng tham số và đối chiếu, kèm mẫu giao việc dùng lại. [Quy trình SCAD → Fusion](scad-to-fusion-task.md) tiếp nối từ baseline đã chốt.

## Agent tổ chức tri thức theo bằng chứng.

Agent đọc README, source, manifest, dependency, test, Git status và checkpoint của dự án trước khi sửa. Agent lập bảng bộ phận, tham số gốc, công thức phụ thuộc, đặc trưng nhận diện và quan hệ lắp ghép. Agent lưu snapshot và SHA256 của đầu vào tham chiếu, cùng quy ước đơn vị và hệ trục.

Tri thức được ghi theo cấu trúc **hiện tượng → bằng chứng → nguyên nhân hoặc giả thuyết → thay đổi → kiểm chứng → phạm vi áp dụng**. Nhãn “nguyên nhân đã xác định” đi cùng bằng chứng trực tiếp. Nhãn “giả thuyết đang kiểm chứng” đi cùng kế hoạch chạy xác nhận. Kết quả mới bổ sung checkpoint cùng hash source và giữ mốc cũ làm lịch sử.

Tài liệu chia sẻ chứa kiến thức kỹ thuật, dữ liệu demo, công thức và nguồn công khai. Bản transcript, log nguyên bản, đường dẫn máy và đầu vào riêng được lưu trong vùng local của người vận hành. Các giấy phép và nguồn thiết kế được giữ cùng sản phẩm.

## Quy trình SCAD trước rồi Fusion Python sau tạo hai vòng phản hồi rõ ràng.

Chuỗi làm việc là **đọc mẫu → dựng SCAD → render và đo → chốt hình học → dựng Python Fusion → chạy native và đổi tham số → so sánh đầu ra → thử lắp/in**.

SCAD cung cấp mô hình trung gian có thể render tự động, sửa công thức nhanh và audit bằng mesh. Fusion Python chuyển hình học đã hiểu sang sketch, feature và biểu thức native. Vòng SCAD tập trung vào hình dáng, số đo và cơ cấu; vòng Fusion tập trung thêm vào solver, ownership, timeline và recompute.

Với đầu vào STL, STL giữ vai trò căn cứ hình học gốc; SCAD giữ vai trò mô hình tái dựng có tham số. Với yêu cầu thiết kế mới, bảng yêu cầu và các số đo được duyệt giữ vai trò căn cứ. Mức bám mẫu được xác định theo mục tiêu của từng task: tái dựng đo lường hoặc tương đương hình dáng, chức năng và lắp ghép.

### Giai đoạn đọc mẫu tạo bản mô tả hình học có thể kiểm tra.

Agent xác định kích thước sử dụng, lòng chứa, bề dày, đáy, bo/vát, các lỗ, ren, khớp và hướng đưa từng part vào vị trí. Agent tách các chi tiết về hệ tọa độ quy ước và lưu phép biến đổi đã dùng. Mặt cắt tại nhiều cao độ làm rõ tai, ngàm, gân và tiết diện thay đổi.

Tên file đóng vai trò nhãn nhận diện. Số đo mesh và bảng tham số quyết định kích thước tái dựng. Snaplock dùng kích thước vỏ chính đo được 237,85 × 123,15 mm dù tên tham chiếu chứa nhãn 240×120.

Đầu ra giai đoạn này gồm bảng part, đơn vị, hệ trục, kích thước, hash tham chiếu và các vùng xấp xỉ có mô tả cụ thể.

### Giai đoạn SCAD tạo mô hình và báo cáo hình học.

Agent dựng primitive, profile, module theo chức năng và quan hệ đối xứng. Tham số gốc biểu diễn lựa chọn thiết kế; tham số derived biểu diễn quan hệ phụ thuộc. `assert` diễn đạt miền hợp lệ của kích thước, bán kính, độ dày và khe hở.

Thứ tự boolean được giữ như một phần ý đồ hình học. Snaplock ghép tai vào vỏ rồi khoét lòng để giữ vùng giao của tai và khoang. Vòng lặp và mirror biểu diễn các phần lặp theo công thức chung.

Agent render cấu hình mặc định và bộ biến thể đại diện. Audit khảo sát solid, tính kín, winding, bounds, thể tích, lỗ và các đặc trưng chức năng. Bản so sánh dùng cùng tỷ lệ, đơn vị và hệ tọa độ cho cả hai đối tượng.

Bounds, thể tích thừa/thiếu, sai khác đối xứng, khoảng cách bề mặt và ảnh mặt cắt cung cấp các lớp thông tin bổ sung cho nhau. Chênh thể tích tổng đo lượng vật liệu có dấu; boolean thừa/thiếu đo vị trí vật liệu khác nhau.

Mốc chốt SCAD gồm source/hash, bộ tham số, mesh/hash, số liệu audit và ảnh đối chiếu. Các vùng xấp xỉ đi cùng kích thước, vị trí và ảnh hưởng đến chức năng.

### Giai đoạn chuyển đổi chọn feature theo ý đồ thiết kế.

Agent chọn Extrude cho tiết diện đều, Revolve cho hình tròn xoay, Loft cho tiết diện thay đổi, Fillet/Chamfer cho bo/vát và Pattern/Mirror cho phần lặp. Các phép Join/Cut/Intersect có body đích và tool xác định rõ.

Agent nhận diện cung tròn, elip và mặt có quy luật để ưu tiên dựng bằng primitive, Extrude/Cut hoặc Revolve trước khi lấy nhiều tiết diện Loft. Các đoạn chuyển tiếp dùng số tiết diện theo độ chính xác cần đạt. Agent giữ baseline, kiểm tra biến thể công thức, đo sai khác cục bộ và thời gian native trước khi chốt thay thế. [Bản thử răng khóa R5/elip](latch-analytic-construction.md) ghi riêng bằng chứng offline và checkpoint Fusion cần xác nhận.

Cây feature Fusion biểu diễn ý đồ thiết kế bằng công cụ native. Hình dáng nhận diện, kích thước sử dụng, lòng chứa, đáy, các part, quan hệ lắp và chức năng được giữ theo phạm vi đã chốt. Mọi đơn giản hóa có mô tả trước/sau và phép kiểm chứng phù hợp.

Snaplock dùng khoét lòng riêng để giữ thành 3 mm, đáy thân 2 mm, đáy nắp 3 mm và tiết diện vát. Hộp bàn chải dùng surface helix + Sweep trong source hiện tại. Thời khóa biểu dùng cung tròn native cùng offset liên kết cho biên trang trí. Các lựa chọn này phản ánh hình học và phạm vi của từng mẫu.

### Giai đoạn tham số hóa giữ công thức trong tài liệu Fusion.

Agent tạo User Parameters cho kích thước gốc và biểu thức derived. Dimension, vị trí sketch, offset, chiều cao feature và số lượng pattern liên kết với tên tham số. Giá trị số ban đầu phục vụ khởi tạo; expression lưu quan hệ để recompute.

Fusion Design API dùng cm cho chiều dài và radian cho góc trong giá trị nội bộ. Báo cáo theo mm dùng hệ số 10 cho chiều dài và 1000 cho thể tích cm³ sang mm³. Chuỗi như `3 mm` mang đơn vị rõ ràng. [Tài liệu đơn vị Autodesk](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/Units_UM.htm) mô tả quy ước này.

Kích thước cập nhật qua Change Parameters trong topology hiện có. Các lựa chọn quyết định số đối tượng được tạo bằng vòng lặp Python được lưu trong cấu hình Run. Nội dung chữ sau `explode()`, số móc theo `HOOK_COUNT` và số cung theo bước sóng được tạo lại trong lần Run tương ứng.

### Giai đoạn native xác nhận solver, kernel và recompute.

Agent chạy script trong Fusion với log ghi hash source và tên stage. Kiểm tra cuối khảo sát `computeAll`, health của feature, profile, constraint, số solid, tên body, bounds và thể tích dương. Contract kiểm tra được chọn theo loại sketch và mục đích feature.

Bộ biến thể thay đổi kích thước tổng, độ dày và khe hở theo miền hợp lệ. Script phục hồi expression gốc trong `finally`, rồi kiểm tra lại mô hình mặc định. Log native ghi giá trị trước/sau và kết quả của từng biến thể.

Bộ test offline xác nhận logic, công thức và contract API được mô phỏng. Lần chạy native xác nhận hành vi solver và BRep của source trong log. Hai loại bằng chứng được ghi thành hai mốc riêng.

### Giai đoạn xuất và thử lắp xác nhận đầu ra theo mục tiêu.

Mỗi body được xuất riêng với đơn vị, hash, độ mịn và tên part trong manifest. Agent đối chiếu đầu ra Fusion với mẫu gốc và SCAD đã audit. Kiểm tra hình dạng dùng phép căn tọa độ được mô tả; kiểm tra assembly giữ vị trí tương đối của các part.

Ren, khóa và chốt được kiểm tra ở vị trí cuối cùng và dọc đường lắp. Thử coupon cung cấp bằng chứng khe hở, lực thao tác và độ bền theo vật liệu, hướng in và máy in thực tế. Audit khổ in dùng thể tích in hữu dụng, chiều cao và khoảng dành cho brim/support của cấu hình slicer.

## Layout, chữ và màu có bộ kiểm chứng riêng.

Thời khóa biểu biểu diễn số ngày bằng tham số scalar và suy ra danh sách nhãn tương ứng. Số hàng sáng/chiều được tính độc lập; thay đổi layout được đối chiếu bằng render, hash và bounds của từng cấu hình. Biên trang trí được kiểm tra dọc cạnh và tại góc, cùng quan hệ giữa độ mềm, biên độ và profile thực.

SCAD dùng `textmetrics()` để tính kích thước chữ và khoảng đệm cho bảng tên. Bản công cụ, feature experimental và cấu hình font được ghi trong checkpoint; CLI dùng `--enable=textmetrics` theo README thời khóa biểu. Font đi cùng đường dẫn tương đối và giấy phép của từng file. Kích thước glyph được kiểm tra trên bộ nội dung ngắn, dài và có dấu tiếng Việt.

Bộ 3MF thời khóa biểu tách bảng, nhóm bảng tên và nhóm thẻ môn bằng `output_part`. Tùy chọn `export-3mf/material-type=color` lưu màu theo luồng xuất đã ghi trong README. Kiểm tra ZIP/XML xác nhận mesh, object và color group; nhập slicer xác nhận cách ứng dụng diễn giải object, màu và vật liệu. Màu preview, màu 3MF và filament đã gán trong slicer là ba lớp dữ liệu được đối chiếu riêng.

Ảnh vật liệu dùng preview/CAD làm căn cứ về hình dạng, màu và số part. Agent kiểm tra các mặt lộ ra để giữ đúng chi tiết thiết kế. Ảnh minh họa AI mang nhãn minh họa; ảnh mẫu in đi cùng thông tin mẫu thử. [README thời khóa biểu](https://github.com/TimTini/thoi-khoa-bieu-openscad/blob/main/README.md) và [prompt hình ảnh](https://github.com/TimTini/thoi-khoa-bieu-openscad/blob/main/exports/photoreal/prompts.md) cung cấp căn cứ thực hành.

## Agent tối ưu timeline theo vai trò và phụ thuộc.

Chuỗi plane → sketch → feature lần lượt đặt tiết diện, định nghĩa profile và tạo hình khối. Một tiết diện Loft có cao độ riêng tạo ra nhu cầu plane/sketch tương ứng. Hai sketch dùng cùng base và expression offset có thể chia sẻ một plane sau khi kiểm chứng tham chiếu và recompute.

Agent lập bảng producer → consumer cho sketch, tool body và feature. Body dụng cụ được theo dõi đến phép Combine hoặc feature tiêu thụ. Body cuối được đối chiếu với contract thiết kế. Số object và thời gian dựng được đo tại checkpoint có hash rõ ràng.

Baseline Snaplock tại commit `1b88b6b` dùng 25 tiết diện cách 0,25 mm cho răng/khe khóa dày 6 mm. [Checkpoint SCAD tròn/elip](scad-catch-csg.md) chuyển phần răng sang trụ R5 và hai vùng bao lồi ngắn, giữ khe đàn hồi 25 tiết diện và xác nhận sai lệch qua ba chiều dày. Fusion 0.3.0 dùng bốn tiết diện XZ cho phần răng và có bước xác nhận native riêng. Rà source Fusion trước tối ưu đã nhận diện 28 cặp plane cùng base/offset là ứng viên dùng chung. Giảm plane và giảm số tiết diện là hai thay đổi có phép kiểm chứng riêng: một thay đổi tác động tham chiếu, một thay đổi tác động xấp xỉ hình học.

Số lời gọi builder, số marker log, số sketch/plane suy ra từ source và số timeline item native được ghi thành các chỉ số riêng. Mốc native thành công được giữ làm baseline cho từng thay đổi tối ưu.

## Năm dự án cung cấp các bài học có thể tái sử dụng.

| Dự án | Bài học được áp dụng. |
|---|---|
| [Hộp bàn chải](https://github.com/TimTini/electric-toothbrush-case/blob/main/fusion/README.md) | Agent tái dựng chỉnh sửa F3D/STEP thành trục, pivot và góc đi theo helix; ren thân và ren nắp giữ ownership rõ ràng. |
| [Khay bông tắm](https://github.com/TimTini/bath-sponge-tray/blob/main/fusion/README.md) | Agent căn tâm lưới lỗ theo dài/rộng và đặt tâm móc theo chiều cao tai; kích thước sử dụng và cấu hình số móc có phạm vi cập nhật riêng. |
| [Thời khóa biểu](https://github.com/TimTini/thoi-khoa-bieu-openscad/blob/main/fusion/README.md) | Agent tách layout theo dữ liệu, tham số hình học và nội dung được tạo lúc Run; khung chữ và glyph có contract riêng. |
| [Thùng rác V4](https://github.com/TimTini/thung-rac-4-goc/blob/main/README-v4.md) | Agent kiểm tra đường đưa chốt và thể tích quét; khe offset đi theo pháp tuyến và winding của profile. |
| [Snaplock](../README.md) | Agent đo mặt cắt, chốt SCAD bằng audit rồi dựng native; lỗi sketch, Mirror và mesh lớn được xử lý theo bằng chứng từng checkpoint. |

## Hồ sơ bàn giao giúp agent tiếp tục đúng checkpoint.

Một hồ sơ bàn giao chứa mục tiêu, phạm vi, source/hash, tham số, quyết định hình học, diff, lệnh chạy, kết quả, trạng thái runtime và bước xác nhận kế tiếp. Sổ lỗi giữ regression cho ca đã sửa và nêu miền áp dụng của recipe.

Agent tiếp nối đọc checkpoint trước, đối chiếu Git status và hash hiện tại, rồi thực hiện bước còn lại của mục tiêu. Kiến thức đã rút được lưu thành tài liệu dự án có version; dữ liệu lần chạy được lưu thành báo cáo riêng theo source/hash.

[Hồ sơ Snaplock](validation/README.md) minh họa cách phân biệt mốc SCAD, native thành công, chẩn đoán sketch và audit streaming. [Sổ lỗi](error-cookbook.md) ghi các ca sửa cụ thể. [Mẫu giao việc](scad-to-fusion-task.md) chuyển quy trình thành yêu cầu dùng lại cho một model mới.
