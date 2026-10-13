# Quy trình kiểm tra toàn bộ model khi thay đổi tham số

Quy trình áp dụng cho model SCAD và bản Fusion chuyển từ cùng baseline. Agent kiểm tra cả hình học từng part, quan hệ lắp, cơ cấu, chuyển động và khổ in. Hồ sơ thử được gắn với source/hash, phiên bản công cụ, tham số và đầu ra cụ thể. Nội dung này bổ sung bước kiểm chứng bắt buộc trước khi chốt một preset in thử hoặc chuyển baseline sang Fusion.

## 1. Agent chốt miền thiết kế và giới hạn sử dụng.

Agent lập bảng tham số đầu vào, công thức phụ thuộc, topology và các cặp part lắp với nhau. Miền source, miền cơ cấu hoạt động và miền vừa máy in được ghi riêng. Giới hạn 250 mm được áp dụng lên kích thước bao thực của từng part theo hướng in; kích thước vỏ là đầu vào thiết kế.

Khổ kiểm tra mặc định của bài thử này là **250 × 250 × 250 mm** và phần chừa brim/support bằng **0 mm**. Hồ sơ máy/slicer xác định khổ hữu dụng cùng phần chừa thực tế cho lần in. Công thức kiểm tra mỗi trục là `kích_thước_bao_part + phần_chừa_hai_phía <= khổ_hữu_dụng`. Dung sai số học mesh được ghi riêng với khe lắp và khoảng chừa in.

Trong baseline Snaplock được lưu cùng ma trận 65 ca, bộ nhỏ sát miền source theo bước 0,1 mm có dài 107,9 mm, rộng 30,1 mm, thân cao 30,2 mm và nắp cao 11,7 mm. Bộ nhỏ đạt tiêu chí latch đã đo dùng **nắp 15 mm**. Hai bộ này minh họa sự khác biệt giữa miền render hợp lệ và miền cơ cấu đã kiểm tra. Cấu hình thân 25 mm giảm vát là một bộ tham số riêng.

## 2. Agent xây dựng ma trận từ cực tiểu đến biên 250 mm.

Mỗi trục được thử độc lập trong khi các tham số còn lại giữ baseline. Agent thử thêm các tổ hợp biên và các tương tác giữa tham số. Mỗi ca có tên, đầu vào, mục tiêu, trạng thái dự kiến và phép đo cần đạt.

| Nhóm | Bộ giá trị trong ma trận baseline 65 ca |
|---|---|
| Chiều dài | 107,9 / 120 / 150 / 180 / 210 / 240 / 250 mm |
| Chiều rộng | 30,1 / 50 / 80 / 120 / 180 / 220 / 232,7 / 250 mm |
| Chiều cao thân | 30,2 / 40 / 50 / 75 / 100 / 150 / 200 / 245,7 / 250 mm |
| Chiều cao nắp | 11,7 / 12,5 / 14 / 15 / 16 / 20 mm và các biên mới của thiết kế |
| Tổ hợp cực trị | Nhỏ–nhỏ–nhỏ, lớn–lớn–lớn và mọi tổ hợp nhỏ/lớn của ba trục |
| Tổ hợp đại diện | Lưới nhỏ/vừa/lớn của ba trục, gồm ít nhất 27 tổ hợp |
| Ca sát giới hạn | Biên hợp lệ, bước kế tiếp phía trong và bước kế tiếp phía ngoài miền |
| Topology | Tám tổ hợp ba công tắc gân tại mẫu nhỏ, mẫu vừa và mẫu lớn |
| Tương tác | Thành–đáy–vát; chiều cao nắp–pivot–catch; độ dày latch–khe đàn hồi; spacing–số trạm–góc tròn |

Agent phân loại các ca vượt giới hạn thành `rejected_source_bounds` hoặc `exceeds_print_envelope`. Các ca này cung cấp bằng chứng biên của model. Sau mỗi thay đổi, agent chạy lại ca tái hiện lỗi, ca lân cận và toàn bộ ma trận chốt của phiên bản mới.

## 3. Agent render và kiểm tra từng part.

Agent dùng render solid cuối của SCAD với warning được xử lý theo hợp đồng dự án. Mỗi part được kiểm tra số component, độ kín, winding, thể tích dương, bounds và kích thước đặc trưng. Lỗ, lòng chứa, thành mỏng, đáy, bo/vát, tai, chốt và gân được đo theo chức năng.

Agent xuất từng part theo đơn vị mm và lưu hash. Làm sạch fragment mesh áp dụng ngưỡng diện tích/thể tích đã ghi, kèm số mặt được loại và kiểm tra solid sau xử lý. Độ mịn cùng dung sai số học được lưu với kết quả.

Agent kiểm tra envelope ở hướng in và kiểm tra riêng bố trí nhiều part trên plate. Các part được phân plate theo nhu cầu. Kích thước bao của assembly đóng được dùng cho bố trí sử dụng; kích thước bao của part in được dùng cho giới hạn máy.

## 4. Agent lắp toàn bộ cụm và kiểm tra tất cả cặp tiếp xúc.

Agent ghi phép biến đổi lắp bằng hệ trục, tâm khớp, chiều áp dụng và ma trận. Tâm bản lề, tâm bi/ổ, pitch, khoảng cách pivot–catch, độ sâu răng trong hốc và vị trí mép đóng được đo từ cả công thức và mesh.

Agent đo riêng latch–Body, latch–Lid, latch–latch, Body–Lid, gân–Lid và các cặp chức năng khác. Mỗi phép đo lưu vùng giao, thể tích giao, khoảng cách hoặc độ xuyên cục bộ, ảnh mặt cắt và tiêu chí chức năng. Khe hở dương, tiếp xúc, cấn cứng và vùng ép đàn hồi theo thiết kế có nhãn riêng.

Giao thể tích toàn cụm được đọc cùng độ xuyên và vị trí tiếp xúc. Vùng tiếp xúc tồn tại ở baseline được giữ thành một hạng mục đánh giá cơ cấu. Agent xác nhận lý do, mức chấp nhận và bằng chứng vật lý trước khi chốt chức năng của vùng đó. `latch_clear` xác nhận một tiêu chí latch; trạng thái lắp khít toàn bộ có bộ tiêu chí riêng.

Baseline cơ cấu trước bản cập nhật latch có khoảng 6,27 mm³ giao Body–Lid, chủ yếu ở bản lề, và độ lệch tâm bi–ổ 0,25 mm mỗi bên theo X. Các phép đo này thuộc baseline đó. Ngưỡng 0,01 mm³ của audit latch phân loại giao mesh tại tư thế đóng; khe lắp FDM được xác nhận bằng mẫu in.

## 5. Agent kiểm tra đường lắp và miền chuyển động.

Agent chia chu trình thành trạng thái gắn latch vào nắp, mở khóa, đóng nắp, cài khóa và mở nắp. Latch được giải phóng theo cơ cấu trước khi khảo sát nắp mở. Mỗi part chuyển động theo đúng trục/pivot và bậc tự do của trạng thái đó.

Agent lấy mẫu góc/vị trí trên toàn hành trình, gồm hai đầu, các trạng thái trung gian và vùng gần tiếp xúc. Vùng gần tiếp xúc được chia nhỏ thích nghi; hồ sơ ghi bước lấy mẫu, giới hạn sai số và các khoảng đã khảo sát. Phép quét có cận sai số hoặc kiểm tra liên tục được dùng khi mục tiêu yêu cầu xác nhận toàn hành trình.

Các tương tác chốt–ổ, răng–ngàm, gân–nắp và thành–latch được kiểm tra ở từng trạng thái. Lực cài, biến dạng đàn hồi, mỏi và độ kín có bài thử vật lý hoặc mô phỏng phù hợp đi kèm.

## 6. Agent kiểm tra cập nhật công thức trong Fusion.

Agent chuyển baseline SCAD đã đạt tiêu chí sang Fusion. User Parameters, expression, sketch, plane, feature và số lượng Pattern được kiểm tra theo cùng ma trận. Các ca số lượng Pattern bằng một, đổi số lượng, chạm giới hạn clamp và thay topology có hồ sơ riêng.

Agent chạy `computeAll`, health, ràng buộc sketch, số body, bounds và kích thước cơ cấu trong Fusion. Biểu thức ban đầu được phục hồi và kiểm tra sau mỗi biến thể. STL xuất thật được so với SCAD cùng tham số và công tắc, rồi được lắp lại để áp dụng các bước kiểm tra cụm.

Bằng chứng công thức, mock API, CSG offline, Fusion native và mẫu in được ghi thành các mức xác nhận riêng. Mốc chốt dùng đúng hash source đã chạy và xuất.

## 7. Agent chốt preset và cập nhật hồ sơ tự học.

Agent chốt preset sau khi bộ tiêu chí hình học, cơ cấu, chuyển động và khổ in của nhiệm vụ đã có kết quả. Các hạng mục đang mở được ghi kèm phạm vi sử dụng của preset. Mẫu in thử dùng kích thước nhỏ giữ đúng hình học chức năng và miền cơ cấu của bản sản phẩm.

Hồ sơ gồm manifest tham số, source/hash, part/hash, bảng kết quả từng ca, cấu hình máy/slicer, hình lắp, mặt cắt, trạng thái native và kết quả in. Sổ lỗi lưu ca regression; cẩm nang agent lưu nguyên nhân cùng quy tắc thiết kế có thể áp dụng lại. Lỗi cơ cấu do tham số được sửa ở công thức/module sở hữu quan hệ đó, rồi chạy lại đầy đủ ma trận trước khi chuyển tiếp.

## 8. Bằng chứng hiện có và lệnh chạy.

SCAD có hash `e1cbc7402b7a04ba5b5039f9260fea86289bbeafb99687790e8fd816ac3fdc55`. Cơ cấu latch dùng `latch_span_delta = lid_height - 15` để liên kết chiều dài latch với chiều cao nắp, đồng thời giữ anchor body/lid trùng nhau. Bán kính cutter ổ bi dùng hệ số `1/cos(180/$fn)^2` để bù độ hụt mặt cầu đa giác; phép đặt assembly STL lượng tử hóa datum theo float32 trước khi biến đổi mesh.

Ma trận SCAD hiện tại có 112 ca: 107 ca trong miền source cho kết quả `closed_clear`, 5 ca ngoài miền nhận `rejected_source_bounds`; trong 107 ca hợp lệ, 104 ca nằm trong bao in 250 mm và 3 ca vượt bao. 48 pose mở xác nhận latch đã được tháo khỏi cụm trước khi xoay nắp. Bộ regression có 54 unit test. Báo cáo gắn với source nằm ở [ma trận lắp SCAD](../validation/scad-parametric-assembly.json); audit preset nằm ở [SCAD mặc định hiện tại](../validation/scad-current-default.json). Cờ `geometry_checks_passed` có giá trị true; cờ `reference_targets_met` có giá trị false vì sai khác nắp 0,248098451% vượt mục tiêu hình học tham chiếu 0,2%. Ngưỡng lịch sử giữ nguyên.

Các ca giới hạn giữ hai cửa sổ clearance phía trước riêng biệt; kênh sau 1 mm chạy theo catch. Ma trận xác nhận hình học và khoảng hở, còn lực tác động, biến dạng thực, tuổi thọ và lắp vừa sau in thuộc các phép thử vật lý kế tiếp. Fusion production 0.5.1 giữ baseline cơ khí trước sửa SCAD; native run cho cập nhật SCAD là checkpoint xác nhận tiếp theo.

[Ma trận baseline 65 cấu hình](../geometry/latch-size-matrix.md) bao phủ 51 bộ kích thước thân, với chiều dài lớn nhất 240 mm. [Hai ca biên 250 mm](../validation/parameter-boundary250.json) là phép đo của source SCAD tại checkpoint lịch sử đó:

| Đầu vào vỏ L × W × H, nắp 15 mm | Bao Body, mm | Bao Lid, mm | Kiểm tra khổ 250 mm từng trục |
|---|---|---|---|
| 250 × 250 × 250 | 250 × 266,997 × 254,249 | 250 × 267,240 × 19,496 | Vượt giới hạn rộng và cao |
| 250 × 232,7 × 245,7 | 250 × 249,697 × 249,949 | 250 × 249,940 × 19,496 | Đạt phép đo envelope, phần chừa 0 mm |

Cả hai ca biên lịch sử đạt tiêu chí latch ở tư thế đóng. Body–Lid có giao ở baseline cơ cấu tương ứng. Ca sát khổ 250 ghi envelope của checkpoint đó; khoảng chừa in và kết quả lắp vật lý được xác nhận theo cấu hình thực tế.

Các lệnh audit hiện có chạy tại thư mục repo với môi trường đã cấu hình:

```powershell
python tools/audit-latch-fit.py
python tools/audit-latch-matrix.py
python tools/audit-fusion-ribs.py
python tools/audit-fusion-ribs.py --native 'fusion/SnaplockStorageBox/exports/<timestamp>'
```

`tools/audit-latch-matrix.py` chạy ma trận 112 cấu hình hiện tại. `tests/test_scad_assembly.py` bổ sung regression cho chiều cao nắp, datum STL và góc quay bản lề ở nhiều độ mịn. Ma trận 65 ca được giữ trong báo cáo lịch sử. Mỗi đợt thay đổi tham số bổ sung ma trận biên mới, phép đo envelope và kiểm tra chuyển động theo các bước trên; báo cáo ghi rõ source/hash, kiểm tra đã chạy và bước xác nhận tiếp theo.
