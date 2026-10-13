# Sổ lỗi OpenSCAD và Fusion ghi cách sửa cùng phạm vi kiểm chứng.

Sổ lỗi thuộc [bộ tài liệu agent](agent-learning.md). Mỗi ca ghi hiện tượng, bằng chứng, thay đổi và mức xác nhận. Các recipe sketch được áp dụng theo loại entity và cấu trúc cụ thể của từng dự án.

## Ca 1 xác định expression bị Fusion từ chối.

**Hiện tượng được tái hiện trong regression:** test thời khóa biểu mô phỏng Fusion từ chối `core_width` bằng `3 : Invalid expression` trong bước tạo User Parameters.

**Bằng chứng:** source hiện tại lưu biểu thức derived theo cú pháp Fusion với `if(điều_kiện; giá_trị_đúng; giá_trị_sai)` và dấu `;` giữa đối số. `_add_user_parameters` bọc lỗi bằng tên tham số, expression và đơn vị. Test `test_parameter_failure_names_the_rejected_expression` mô phỏng việc parser từ chối `core_width` để xác nhận thông báo chẩn đoán.

**Cách xử lý:** agent đọc expression cụ thể trong log, đối chiếu tên tham số đã tạo, thứ tự phụ thuộc, đơn vị và cú pháp Fusion. Biểu thức Python dùng trong tính toán offline và biểu thức lưu trong Fusion được xử lý theo grammar tương ứng. Chẩn đoán giữ nguyên lỗi gốc cùng ngữ cảnh tham số.

**Mức xác nhận:** source và regression offline xác nhận cách phát hiện lỗi, thông báo và cấu trúc expression. Lần Run native của source tương ứng xác nhận parser Fusion chấp nhận bộ tham số.

Nguồn: [source tham số](https://github.com/TimTini/thoi-khoa-bieu-openscad/blob/main/fusion/TimetableBoard/TimetableBoard.py) và [regression thời khóa biểu](https://github.com/TimTini/thoi-khoa-bieu-openscad/blob/main/tests/test_fusion_timetable.py).

## Ca 2 xử lý datum và điểm còn bậc tự do.

**Hiện tượng:** thùng rác phát sinh `VCS_SKETCH_OVER_CONSTRAINTS` tại `Corner floor`; lần sửa kế tiếp ghi profile còn tự do.

**Bằng chứng:** chẩn đoán chỉ ra điểm, trục và expression đang gắn dimension. Một checkpoint xác định đầu mút datum còn có khả năng trượt dọc đường. Các ca regression kiểm tra thứ tự tạo datum và bốn đầu mút fixed.

**Cách xử lý:** builder dùng `addOffsetDimension` từ hai trục construction làm chuẩn tọa độ. Hai đầu mút của mỗi datum được fixed rõ ràng. Điểm hình học của sản phẩm được điều khiển bằng expression tham số. Agent đọc tọa độ, `isFixed`, `isReference`, constraint và dimension của entity tại bước lỗi.

**Mức xác nhận:** các bản sửa có regression offline và checkpoint source riêng. Lần chạy Fusion hiện tại xác nhận kết quả solver của refactor native tương ứng.

Nguồn: [lịch sử chẩn đoán thùng rác](https://github.com/TimTini/thung-rac-4-goc/blob/main/fusion/README.md) và [test sketch](https://github.com/TimTini/thung-rac-4-goc/blob/main/tests/test_fusion_bin.py).

## Ca 3 khóa cung tròn và rectangle theo loại hình học.

**Hiện tượng:** sketch góc thùng rác và gân đáy có hình dạng nhìn đúng trong khi solver báo còn tự do.

**Bằng chứng:** cung tạo bằng `addByCenterStartEnd` được bổ sung radial dimension driving. Rectangle nhiều phần được kiểm tra theo bốn điểm và tám offset tọa độ. Mock trả `isFullyConstrained=True` vẫn cho phép test bắt việc thiếu lời gọi dimension.

**Cách xử lý:** builder cung thêm expression bán kính cho radial dimension. Builder rectangle của nhóm gân điều khiển cả bốn góc theo datum trước khi nối cạnh. Builder rounded rectangle thời khóa biểu giữ kích thước parent và quan hệ collinear/radius sau trim/fillet theo contract riêng.

**Mức xác nhận:** regression bảo vệ số điểm, số dimension, biểu thức và cấu trúc gọi API. Trạng thái [`Sketch.isFullyConstrained`](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/fusion_Sketch_isFullyConstrained.htm) trong ứng dụng là kết quả solver của sketch thực tế.

Nguồn: [test thùng rác](https://github.com/TimTini/thung-rac-4-goc/blob/main/tests/test_fusion_bin.py) và [test thời khóa biểu](https://github.com/TimTini/thoi-khoa-bieu-openscad/blob/main/tests/test_fusion_timetable.py).

## Ca 4 chẩn đoán cạnh tự do của Latch plate.

**Hiện tượng:** Snaplock dừng ở `Sketch is not fully constrained: Latch plate`.

**Bằng chứng:** log ghi 2 constraint, 6 dimension và bốn SketchLine còn tự do; các điểm đã đủ ràng buộc. Bằng chứng này phân biệt trạng thái điểm với trạng thái curve.

**Cách xử lý:** source sửa thứ tự profile thành tạo điểm → tạo cạnh → áp dimension/constraint tọa độ → kiểm tra sketch. Diagnostic ghi entity, type, tọa độ và số constraint/dimension của cả điểm lẫn curve.

**Mức xác nhận:** source `e09a8281…` có 28 test offline tại checkpoint đã lưu. Bản sửa thứ tự mang trạng thái “đã xác nhận offline”; lần Run native tương ứng là bước xác nhận tác dụng với solver Fusion. Mốc native thành công `4cad327e…` thuộc phiên bản trước thay đổi thứ tự này.

Nguồn: [log chẩn đoán](../validation/fusion-free-lines-failure.log), [profile source](../../fusion/SnaplockStorageBox/SnaplockStorageBox.py) và [hồ sơ hash](../validation/README.md).

## Ca 5 giữ bounds khóa khi Mirror khe đàn hồi.

**Hiện tượng:** khóa Snaplock có bounds rộng 30 mm trong khi contract là 28 mm.

**Bằng chứng:** profile tool của khe vươn đến X = −2 mm. Bản sửa thay Mirror feature Loft Cut bằng việc Mirror body dụng cụ, rồi cắt từ body đích.

**Cách xử lý:** chuỗi dựng là **Loft NewBody → Mirror tool body → Combine Cut**. Danh sách tool và target được chỉ định rõ. Check cuối đo cả `Latch` và `Latch 2`.

**Mức xác nhận:** [log native source `4cad327e…`](../validation/fusion-native-success.log) xác nhận cả hai khóa rộng 28 mm, bốn solid và hai biến thể recompute. Đây là ca có bằng chứng native cho thay đổi cụ thể.

Nguồn: [source Mirror/Combine](../../fusion/SnaplockStorageBox/SnaplockStorageBox.py) và [README kỹ thuật](../../README.md).

## Ca 6 đặt rõ hai chiều của Rectangular Pattern.

**Hiện tượng:** pattern một phương có nguy cơ tạo thêm hàng body khi số lượng chiều hai mang giá trị khác contract.

**Bằng chứng:** helper Snaplock đặt `quantityOne = 2` và `quantityTwo = 1`. Regression kiểm tra chiều hai ngay cả khi mock khởi tạo giá trị khác. Body sao chép được đọc từ kết quả Pattern.

**Cách xử lý:** agent khai báo số lượng từng chiều, lấy body từ feature kết quả và kiểm tra vị trí, tên cùng số solid cuối. Pattern body và pattern feature được chọn theo loại input thực tế.

**Mức xác nhận:** regression offline xác nhận input tường minh; log native Snaplock xác nhận bốn body và bố trí của phiên bản tương ứng.

Nguồn: [test native feature](../../tests/test_native_features.py) và [source pattern](../../fusion/SnaplockStorageBox/SnaplockStorageBox.py).

## Ca 7 điều khiển body đích và body dụng cụ.

**Hiện tượng:** Join/Cut tác động sai chi tiết hoặc body cuối có thêm tool ngoài contract.

**Bằng chứng:** nhiều part được dựng trong cùng component nên các vùng tiếp xúc và tool được consume ảnh hưởng đến lựa chọn feature. Fusion Snaplock 0.5.1 dựng xong từng part rồi chuyển sang bố trí in, và mounting Combine lấy đúng các tai của part tại checkpoint đó. Thùng rác dựng đầu khóa/đầu chốt bằng NewBody rồi Combine vào target xác định.

**Cách xử lý:** agent giữ tham chiếu producer → consumer, chỉ định target/tool và kiểm tra ownership sau Combine, Mirror, Pattern. Check cuối dùng số solid, tên body, thể tích và bounds theo contract.

**Mức xác nhận:** log Snaplock cung cấp bằng chứng native cho bốn body. Các builder của dự án khác có mức xác nhận riêng trong README tương ứng.

Nguồn: [Snaplock](../../README.md) và [Fusion thùng rác](https://github.com/TimTini/thung-rac-4-goc/blob/main/fusion/README.md).

## Ca 8 xử lý khung SketchText và profile glyph.

**Hiện tượng:** thời khóa biểu gặp over-constraint khi khóa khung chữ, lỗi font và lỗi `Some input argument is invalid` khi tạo khối chữ.

**Bằng chứng:** khung multiline SketchText có quan hệ solver riêng. Recipe hiện tại điều khiển `heightParameter`, điểm BL và hai tọa độ BR.x/TL.y; H/V được thử trong phạm vi quan hệ tùy chọn. Font được chọn từ danh sách hệ thống hỗ trợ tiếng Việt. Luồng extrude dùng các profile tạo sau explode.

**Cách xử lý:** agent áp contract riêng cho sketch text, kiểm tra khung và expression cỡ chữ. Chuỗi hình học là **SketchText → explode → Profiles → Extrude NewBody → Combine Join**. [`explode()`](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/fusion_SketchText_explode.htm) tạo curve glyph và xóa đối tượng SketchText gốc. Nội dung và cỡ glyph được tạo lại khi Run.

**Mức xác nhận:** test kiểm tra contract khung, nhánh H/V tùy chọn và pipeline profile. Lần Run native của source hiện tại xác nhận font, dấu tiếng Việt, solver và khối chữ.

Nguồn: [README chữ và sketch](https://github.com/TimTini/thoi-khoa-bieu-openscad/blob/main/fusion/README.md) và [regression](https://github.com/TimTini/thoi-khoa-bieu-openscad/blob/main/tests/test_fusion_timetable.py).

## Ca 9 tái dựng chỉnh sửa đầu ren bằng frame tham số.

**Hiện tượng:** chỉnh sửa đầu ren từ F3D/STEP có trục/pivot riêng và cần đi theo thay đổi pitch, radius, phase và góc.

**Bằng chứng:** source hộp bàn chải tạo frame helix và Move Rotate theo tham số. Test toán học đối chiếu mặt phẳng STEP và các biến thể. Script hiện tại dùng surface helix + circular Sweep; bài probe Coil giữ vai trò khảo sát API.

**Cách xử lý:** agent suy ra trục, pivot và góc từ hình học nguồn, tạo axis sketch liên kết rồi đặt Move Rotate sau Sweep tương ứng. Bộ tham số chung điều khiển ren thân và ren nắp. Fade 45° của SCAD và tiết diện tròn của Sweep được ghi thành đặc điểm đối chiếu riêng.

**Mức xác nhận:** source và test xác nhận frame, công thức và mặt phẳng mục tiêu. BRep sau Move, recompute, giao thoa ren và lực vặn được xác nhận trong Fusion và bằng coupon tương ứng.

Nguồn: [Fusion hộp bàn chải](https://github.com/TimTini/electric-toothbrush-case/blob/main/fusion/README.md) và [test frame/ren](https://github.com/TimTini/electric-toothbrush-case/blob/main/tests/test_fusion_case.py).

## Ca 10 kiểm tra toàn hành trình đưa chốt vào khớp.

**Hiện tượng:** chốt V3 của thùng rác có vị trí cuối vừa khớp trong khi đường đưa vào gặp gân.

**Bằng chứng:** audit phát hiện giao thể tích khoảng 88–106 mm³ tại các mốc lấy mẫu trên đường vào tiếp tuyến dài 51 mm. V4 đổi hướng đưa chốt từ ngoài vào theo pháp tuyến thành và dùng phần thân 14 mm cùng đầu 3 mm.

**Cách xử lý:** agent đánh giá vị trí cuối, các vị trí trung gian và thể tích quét liên tục theo mức kiểm chứng đặt ra. Khóa, ray và chốt được kiểm tra thành bộ cùng phiên bản. Hướng in, khe hở và mẫu coupon đi cùng phép thử lắp.

**Mức xác nhận:** audit hỗ trợ hình học đường lắp của checkpoint đã đo; thử mẫu cung cấp kết quả lực thao tác và khả năng sử dụng thực tế. Lấy mẫu một số vị trí và đo swept-volume liên tục có phạm vi bằng chứng riêng.

Nguồn: [thiết kế và audit V4](https://github.com/TimTini/thung-rac-4-goc/blob/main/README-v4.md).

## Ca 11 xử lý STL lớn theo tài nguyên và loại phép đo.

**Hiện tượng:** bộ STL Fusion Snaplock có khoảng 43,7 triệu tam giác và 2,19 GB; phép boolean toàn mesh dừng ở giới hạn bộ nhớ.

**Bằng chứng:** báo cáo streaming ghi hash, số tam giác, bounds và thể tích có dấu cho bốn file. Chênh thể tích có dấu của thân là +0,077286%, nắp +0,007296%, mỗi khóa −0,017146% tại checkpoint đã lưu.

**Cách xử lý:** agent đọc streaming cho các chỉ số tổng, chọn độ mịn export theo mục tiêu và tài nguyên, rồi lên phép boolean/khoảng cách/mặt cắt tương ứng. Mọi mesh giảm độ mịn được đo sai lệch so với bản nguồn và mang nhãn xấp xỉ.

**Mức xác nhận:** streaming xác nhận các chỉ số đã báo. Sai khác đối xứng và bản đồ khoảng cách toàn bề mặt của Fusion thuộc bước đo bổ sung. Chênh thể tích tổng và sai khác đối xứng có công thức cùng ý nghĩa riêng trong [tài liệu kỹ thuật](fusion-python-tu-hoc.md).

Nguồn: [báo cáo streaming](../validation/fusion-native-export-metrics.json).

## Ca 12 xác nhận tác dụng của thay đổi tham số và công cụ xuất.

**Tình huống kiểm tra:** một lần render/audit dùng selector, bộ tham số, font và môi trường dependency cụ thể; hash cùng số đo giúp xác định tác dụng của cấu hình đã chạy.

**Bằng chứng:** source hiện tại tách số hàng sáng/chiều, các script audit xuất từng part/variant, và dependency được khai báo trong bộ hướng dẫn tương ứng. Hash cùng ảnh, bounds và số part làm rõ cấu hình đã thực sự chạy.

**Cách xử lý:** agent ghi selector `part`, tham số, phiên bản công cụ, dependency và thư mục output. Agent đối chiếu source/hash, thời điểm xuất, ảnh và số đo sau thay đổi. OpenSCAD CLI, cấu hình font và Python environment được chọn rõ trong lệnh của checkpoint.

Thời khóa biểu dùng `textmetrics` đã bật cùng font được tham chiếu trong dự án. Agent kiểm tra giá trị `output_part` thực tế đến OpenSCAD sau bước truyền đối số của shell. Bản xuất 3MF được kiểm tra mesh/object/color group trong ZIP/XML, rồi đối chiếu lại trong slicer. Bộ cấu hình layout gồm số ngày cùng số hàng sáng/chiều độc lập.

**Mức xác nhận:** render/audit của từng cấu hình xác nhận output tương ứng. Kiểm tra slicer tiếp tục xác nhận đơn vị, màu, object và thiết lập in của file đã nhập.

Nguồn: [thời khóa biểu](https://github.com/TimTini/thoi-khoa-bieu-openscad/blob/main/README.md), [audit SCAD Snaplock](../../tools/audit-scad.py) và [dependency Snaplock](../../requirements.txt).

## Ca 13 đổi tọa độ theo frame thực của sketch.

**Hiện tượng:** khay và Snaplock cần profile nằm trên mặt XZ/YZ với hướng khoét vào đúng phía thành.

**Bằng chứng:** khay dùng `modelToSketchSpace` cho vị trí theo model và xác định hướng extrusion theo frame. Snaplock đọc `xDirection`/`yDirection` để đổi biểu thức tọa độ; mặt YZ trong ca đo dùng ánh xạ `(Y, Z) → (−Z, Y)`.

**Cách xử lý:** agent dùng cùng phép đổi cho điểm, tâm, cung và biểu thức dimension. Hướng extrusion được xác định theo normal của sketch và phía vật liệu mục tiêu. Test mô phỏng frame đảo hướng để kiểm tra mapping và chiều khoét.

**Mức xác nhận:** test xác nhận phép đổi và input API; lần Run native xác nhận vị trí profile và phía vật liệu của mô hình thực tế.

Nguồn: [test frame khay](https://github.com/TimTini/bath-sponge-tray/blob/main/tests/test_fusion_parameters.py), [source khay](https://github.com/TimTini/bath-sponge-tray/blob/main/fusion/BathSpongeTray/BathSpongeTray.py) và [source tọa độ Snaplock](../../fusion/SnaplockStorageBox/SnaplockStorageBox.py).

## Ca 14 đặt tên đúng đối tượng và neo đúng endpoint helix.

**Tình huống được bảo vệ bằng regression và source:** test khay mô phỏng lỗi khi gán tên root component; builder hộp bàn chải kiểm tra và điều khiển endpoint helix bằng liên kết sketch.

**Bằng chứng:** khay hiện đặt tên tài liệu qua `doc.name`, có regression bảo vệ thao tác này. Hộp bàn chải tạo datum với cả hai đầu mút ràng buộc, chuyển điểm theo frame và project endpoint đường helix vào sketch tiết diện.

**Cách xử lý:** agent chọn thuộc tính của đúng document/component theo ownership API. Sketch ren giữ liên kết với endpoint thực của đường dẫn, cùng biểu thức chiều cao, phase, radius và pivot. Diagnostic nêu rõ sketch cùng endpoint còn tự do để sửa tại quan hệ thiếu.

**Mức xác nhận:** source và regression bảo vệ contract đặt tên, anchor và biểu thức. Lần Run native tương ứng xác nhận sketch ren cùng feature Sweep/Move sau recompute.

Nguồn: [test đặt tên khay](https://github.com/TimTini/bath-sponge-tray/blob/main/tests/test_fusion_parameters.py) và [source helix](https://github.com/TimTini/electric-toothbrush-case/blob/main/fusion/ElectricToothbrushCase/ElectricToothbrushCase.py).

## Ca 15 liên kết chiều dài latch với chiều cao nắp.

**Tình huống:** các giá trị `lid_height` khác nhau cần giữ vị trí anchor thân/nắp đồng tâm và vùng lắp latch rõ ràng.

**Bằng chứng:** SCAD hash `e1cbc7402b7a04ba5b5039f9260fea86289bbeafb99687790e8fd816ac3fdc55` dùng `latch_span_delta = lid_height - 15`, giữ anchor hai phía bằng nhau và dịch blank, ramp, tooth cùng channel theo biến thể. Pocket cầu dùng cutter bù facet `1/cos(180/$fn)^2`. Bộ assembly 112 ca cho 107 `closed_clear`, 5 `rejected_source_bounds`, 104 ca trong khổ 250 mm và 48 pose mở với latch đã tháo. Audit biến đổi STL lượng tử hóa datum theo float32.

**Cách xử lý:** agent nối chiều dài chi tiết với tham số sở hữu quan hệ, giữ các datum lắp trong cùng frame rồi kiểm tra mesh sau transform. Ma trận hình học đi cùng kiểm tra cửa sổ clearance trước, kênh sau 1 mm và miền tham số. Lực cài, độ biến dạng và tuổi thọ được xác nhận bằng thử vật lý.

**Mức xác nhận:** [Regression assembly](../../tests/test_scad_assembly.py) kiểm tra source, cặp lắp và các pose mở theo ma trận. [Báo cáo assembly](../validation/scad-parametric-assembly.json) và [audit mặc định](../validation/scad-current-default.json) lưu kết quả cùng source hash. Fusion production 0.5.1 giữ baseline trước cập nhật SCAD; native run cho cập nhật này là checkpoint kế tiếp.

Nguồn: [SCAD](../../snaplock-storage-box.scad), [audit transform](../../tools/audit-latch-fit.py), [regression assembly](../../tests/test_scad_assembly.py).
