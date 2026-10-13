# Quy trình STL → SCAD tạo mô hình tham số có bằng chứng hình học.

Tài liệu này hướng dẫn agent tái dựng một mẫu STL thành SCAD có thể sửa kích thước và tiếp tục chuyển sang Fusion Python. STL cung cấp bề mặt tam giác để đo; SCAD biểu diễn quy luật, tiết diện, primitive, module và quan hệ thiết kế được suy ra từ mẫu. Mục tiêu bám mẫu cùng mức xấp xỉ được chốt theo nhiệm vụ.

Quy trình là **bảo toàn mẫu → phân tích mesh → tách part → chuẩn hóa tọa độ → đo và suy ra hình học → dựng SCAD → đối chiếu → thử biến thể → chốt baseline**. [Cẩm nang agent](agent-learning.md) nối baseline này với quy trình Fusion; [mẫu SCAD → Fusion](scad-to-fusion-task.md) dùng bản hình học đã chốt làm đầu vào.

## 1. Hồ sơ đầu vào xác định mẫu và mục tiêu.

Agent lưu snapshot cùng SHA256 của STL, nguồn/giấy phép, kích thước file và số tam giác. Agent ghi mục đích của mẫu: tái dựng hình học, giữ chức năng, lấy một số đo tham khảo hoặc thiết kế biến thể. Các part và đặc trưng thuộc phạm vi được liệt kê rõ.

Đơn vị được xác nhận qua số đo đáng tin cậy, mô tả nguồn hoặc đối chiếu kích thước sử dụng. Bounds ban đầu và hệ số đổi đơn vị được lưu cùng căn cứ. Tên file đóng vai trò nhãn; giá trị đo quyết định bảng kích thước.

Bảng mục tiêu gồm hình dáng ngoài, lòng chứa, độ dày, lỗ, bo/vát, ren, khóa, đường lắp và các chi tiết nhận diện. Mỗi mục có tiêu chí đo hoặc tiêu chí chức năng tương ứng. Ngưỡng chấp nhận được chọn theo task và đặc trưng sử dụng.

Đầu ra bước này là hồ sơ nguồn, bảng part, đơn vị, mục tiêu và danh sách phép kiểm chứng.

## 2. Phân tích mesh tạo bản đồ chi tiết và chất lượng dữ liệu.

Agent kiểm tra số connected component, bounds, winding, độ kín, thể tích và các vùng tự giao theo công cụ được chọn. Connected component cung cấp gợi ý tách mesh; vai trò part được xác định thêm từ vị trí, hình dáng và quan hệ cơ cấu. Hai khóa giống nhau có thể dùng chung một module và xuất số lượng theo layout.

Các mảnh rời rất nhỏ được ghi diện tích, thể tích, vị trí và số mặt trước khi phân loại. Mọi xử lý mesh được thực hiện trên bản làm việc, với tiêu chí, hash trước/sau và báo cáo thay đổi. Snapshot đầu vào giữ vai trò căn cứ đối chiếu.

Agent xem tổng thể và khảo sát vùng chức năng riêng. Các đường nối, tai, gân và ngàm được đối chiếu với part lân cận để xác định vai trò và trình tự lắp.

Nguồn phương pháp gồm [Trimesh API](https://trimesh.org/trimesh.html#trimesh.Trimesh.is_volume) và [CGAL Polygon Mesh Processing](https://doc.cgal.org/latest/Polygon_mesh_processing/). Phép kiểm tra volume, winding và tự giao được ghi thành các kết quả riêng.

## 3. Chuẩn hóa tọa độ giữ hình dạng và quan hệ lắp.

Agent lưu tọa độ assembly gốc trước khi đưa từng part về hệ đo riêng. Trục quy ước được chọn theo mặt đáy, trục đối xứng, tâm chốt hoặc hướng extrusion. Phép xoay và tịnh tiến được ghi thành ma trận biến đổi có chiều áp dụng rõ ràng.

Phép chuẩn hóa hình dạng dùng rigid transform; phép đổi tỷ lệ dùng hệ số đơn vị đã xác nhận ở hồ sơ đầu vào. Agent lưu cả phép biến đổi thuận và nghịch để đưa part về vị trí assembly.

Đối chiếu hình dạng của từng part dùng hệ tọa độ đã chuẩn hóa. Đối chiếu lắp ráp dùng vị trí tương đối cùng tâm, trục và khe của các part. Hai phép đối chiếu có báo cáo riêng.

Bằng chứng gồm bounds trước/sau, ma trận, tâm/trục chuẩn, ảnh và kích thước đặc trưng. [Hồ sơ Snaplock](../geometry/scad-reference.md) minh họa hệ trục và phép dựng theo số đo thực tế.

## 4. Mặt cắt và phép khớp giúp suy ra quy luật hình học.

Agent cắt mesh ở nhiều vị trí có ý nghĩa: đầu, giữa, cuối; sát đáy; vùng bo/vát; tâm chốt; đầu ren và vùng đàn hồi. Mỗi mặt phẳng cắt được lưu bằng origin, normal và phép chuyển 3D ↔ 2D. Các mặt cắt STL và SCAD dùng cùng mặt phẳng, tỷ lệ và hệ trục.

Agent tìm các quy luật đơn giản trước: mặt phẳng, đoạn thẳng, cung tròn, trụ, cầu, nón, hình tròn xoay, đối xứng và tiết diện lặp. Tham số fit đi cùng phạm vi dữ liệu, cách lấy mẫu, RMS và sai lệch lớn nhất trên tập đo. Sai số fit phản ánh mức khớp tập đo; kiểm tra các mặt cắt khác bổ sung bằng chứng cho vùng hình học đó.

[Bài thực hành răng Snaplock](../geometry/scad-catch-csg.md) suy cung R5 và elip từ công thức 25 tiết diện, chuyển sang primitive rồi so với snapshot và STL. Agent kiểm tra riêng đường cong tiết diện và mặt nối trung gian; `hull()` tạo bao lồi, còn Loft native có quy luật nội suy của CAD. Cách dựng được chốt theo sai lệch, biến thể tham số và mục tiêu chuyển sang Fusion.

[Bài thực hành khe hybrid](../geometry/scad-slot-hybrid.md) tách vùng cố định sang Extrude và chọn tám tiết diện cho vùng biến đổi bằng bộ thử 5–9 tiết diện. Ngưỡng 0,03 mm phản ánh mục tiêu đối chiếu của chi tiết; hồ sơ giữ cả số đo với snapshot, STL gốc và các mức vượt ngưỡng. Agent chọn dung sai theo mục đích sử dụng, tách kiểm chứng hình học khỏi thử in và lực cơ cấu.

| Dấu hiệu trên mẫu | Cách biểu diễn được khảo sát. |
|---|---|
| Các mặt cắt có cùng biên qua chiều cao. | Agent khảo sát profile 2D cùng `linear_extrude`. |
| Các mặt cắt vuông góc trục có dạng tròn đồng tâm. | Agent khảo sát trụ, nón, cầu hoặc `rotate_extrude` từ tiết diện dọc trục. |
| Các cụm có cùng hình dạng và cách nhau đều. | Agent dùng một module cùng vòng lặp hoặc phép đối xứng theo tâm đã đo. |
| Mặt cắt thay đổi dọc theo một hướng. | Agent mô tả các section cùng quy luật nội suy và kiểm chứng mặt cắt trung gian. |
| Các ngàm, rãnh hoặc gân có hình dạng địa phương. | Agent gom số đo vào profile có tên, giữ vị trí theo công thức và ghi vùng xấp xỉ. |

Nguồn thực hành: [Trimesh section example](https://trimesh.org/section.html), [extrusion của OpenSCAD](https://en.wikibooks.org/wiki/OpenSCAD_User_Manual/2D_to_3D_Extrusion) và [bài học nguồn Internet](internet-learning.md).

## 5. SCAD biểu diễn hình học bằng tham số và module.

Agent chia code theo chức năng: vỏ, lòng, đáy, tai, chốt, khóa, ren và layout. Tham số gốc diễn tả lựa chọn thiết kế; công thức derived giữ quan hệ như `inner_width = width - 2 * wall`, tâm cụm theo chiều dài và khoảng lùi, hoặc vị trí hai part dùng chung trục lắp.

SCAD chính dựng hình bằng primitive và profile đã đo. Mesh tham chiếu phục vụ đo, ảnh chồng và audit. Module có tên diễn đạt ý nghĩa thiết kế; các tọa độ đo địa phương được gom thành bảng/profile có nguồn và đơn vị rõ ràng.

Agent dựng theo thứ tự vùng chính → lòng/đáy → đặc trưng chức năng → vùng chuyển tiếp → layout. Thứ tự union/difference được đối chiếu với mẫu tại các vùng giao. Epsilon phục vụ độ ổn định boolean; clearance là tham số lắp được chọn và thử riêng.

`assert` diễn đạt miền hợp lệ của độ dày, bán kính, kích thước và vị trí. Selector `part` cho phép dựng từng chi tiết cùng layout. `$fa`, `$fs`, `$fn` và số section được chọn theo sai lệch hình học cùng tài nguyên đo được.

Nguồn: [OpenSCAD Documentation](https://openscad.org/documentation.html), [CSG Modelling](https://en.wikibooks.org/wiki/OpenSCAD_User_Manual/CSG_Modelling) và [nguồn về boolean/độ mịn](internet-learning.md).

## 6. Đối chiếu dùng nhiều chỉ số cho cùng bộ dữ liệu.

Agent render từng part với phiên bản công cụ, selector, tham số và thư mục output xác định. Báo cáo lưu SHA256 source, STL tham chiếu và STL dựng. Mesh được kiểm tra độ kín, winding, số component và thể tích theo contract trước khi diễn giải boolean.

Bounds mô tả bao hình học; thể tích có dấu mô tả lượng vật liệu; boolean thừa/thiếu mô tả vùng vật liệu khác nhau. Với `A` là SCAD và `B` là STL tham chiếu, báo cáo dùng các đại lượng sau.

```text
Thừa = volume(A \ B)
Thiếu = volume(B \ A)
Sai khác đối xứng (%) = 100 × (Thừa + Thiếu) / volume(B)
Chênh thể tích có dấu (%) = 100 × (volume(A) − volume(B)) / volume(B)
```

Ảnh chồng và mặt cắt xác định vị trí sai khác. Phép đo khoảng cách bề mặt thực hiện hai chiều và ghi seed, số mẫu, đơn vị, độ mịn cùng thống kê. Cực đại lấy mẫu mang tên cực đại quan sát được; phép Hausdorff có cận sai số ghi thuật toán và `error_bound` tương ứng.

Hausdorff đối xứng lấy cực đại của hai khoảng cách có hướng A → B và B → A. CGAL cung cấp `bounded_error_symmetric_Hausdorff_distance` cho phép tính có cận sai số này; báo cáo ghi riêng từng hướng và giá trị tổng hợp đối xứng.

Vùng lắp, thành mỏng và điểm đổi tiết diện có kiểm tra địa phương riêng. Kết quả tổng thể được đọc cùng số đo của các vùng này. Agent sửa đúng module hoặc công thức tạo vùng sai, rồi chạy lại phép đo liên quan cùng audit tổng thể của bản mới.

Nguồn và ví dụ: [audit SCAD](../../tools/audit-scad.py), [ảnh chồng mặt cắt](../../tools/compare-scad.py), [Trimesh proximity](https://trimesh.org/trimesh.proximity.html) và [CGAL distance](https://doc.cgal.org/latest/Polygon_mesh_processing/group__PMP__distance__grp.html).

## 7. Biến thể xác nhận ý đồ tham số và chức năng.

[Quy trình test tham số từ cực tiểu đến biên 250 mm](parameter-change-validation.md) bổ sung ma trận từng trục, tổ hợp biên, topology, kiểm tra toàn cụm và envelope thực tế. Agent kiểm tra miền hoạt động của cơ cấu cùng miền render, ghi riêng trạng thái tiếp xúc, chuyển động và thử in cho từng cấu hình.

Bộ biến thể gồm mặc định, kích thước đại diện lớn hơn/nhỏ hơn và các ca sát miền hợp lệ. Agent kiểm tra số part, solid, độ dày, vị trí lỗ, tâm khớp và khoảng cách giữa các cụm. Các đặc trưng cơ khí giữ kích thước chung hoặc thay đổi theo công thức đã chốt.

Đối chiếu với STL gốc xác nhận hình học ở cấu hình tham chiếu. Audit biến thể xác nhận hình học và quan hệ tham số của cấu hình đã thay đổi. Thử coupon cùng mẫu lắp cung cấp bằng chứng về khe hở, lực thao tác, hướng in và độ bền.

Baseline sẵn sàng cho Fusion gồm SCAD có module/parameter, bảng kích thước, vùng xấp xỉ, bộ biến thể và các báo cáo đo. [Quy trình SCAD → Fusion](scad-to-fusion-task.md) dùng các hồ sơ này để chọn sketch, feature native và expression tương ứng.

## 8. Hồ sơ Snaplock minh họa một checkpoint đã đo.

Snaplock được tái dựng thành thân, nắp và hai khóa. Vỏ chính đo được 237,85 × 123,15 mm. [Audit mặc định đã lưu](../validation/scad-audit-default.json) ghi sai khác thể tích đối xứng 0,0927% cho thân, 0,0659% cho nắp và 0,0429% cho khóa. Sai lệch bounds lớn nhất trong bảng đo là khoảng 0,00966 mm.

Các số trên thuộc source/hash và cấu hình của [hồ sơ kiểm chứng](../validation/README.md). Phép đo toàn bề mặt, hành trình cơ cấu và thử vật lý có checkpoint riêng. [Tài liệu hình học Snaplock](../geometry/scad-reference.md) ghi mặt cắt, phương trình, vùng xấp xỉ và cách xử lý các mảnh mesh xuất rất nhỏ của trường hợp cụ thể này.

## 9. Mẫu giao việc STL → SCAD dùng lại cho model mới.

Đầu vào của nhiệm vụ là `[file STL]`; mục tiêu là `[mức bám mẫu, chức năng và part]`; bộ kiểm chứng là `[cấu hình, chỉ số và ngưỡng]`.

Agent đọc mẫu, lưu snapshot/hash và xác nhận đơn vị. Agent phân tích mesh, xác định part và lập bảng đặc trưng hình học cùng quan hệ lắp. Agent lưu phép đổi tọa độ, đo nhiều mặt cắt và suy ra primitive/profile theo quy luật.

Agent dựng SCAD bằng tham số, công thức derived, module chức năng, vòng lặp và đối xứng. Số đo địa phương được gom trong profile có tên cùng nguồn đo. Miền hợp lệ được ghi bằng assert; selector part cung cấp từng chi tiết và layout.

Agent render cấu hình tham chiếu, kiểm tra solid và đối chiếu bounds, boolean thừa/thiếu, mặt cắt cùng khoảng cách bề mặt theo phạm vi đã chốt. Các vùng xấp xỉ có vị trí, kích thước và ảnh hưởng rõ ràng. Agent chạy biến thể để kiểm tra công thức cùng quan hệ cơ cấu.

Bộ bàn giao gồm SCAD chỉnh sửa được, bảng tham số, preview, STL từng part, manifest/hash, báo cáo đo, vùng xấp xỉ và checkpoint. Kiểm chứng source, mesh, biến thể, assembly và vật lý được ghi theo bằng chứng tương ứng. Baseline được chốt làm đầu vào cho Fusion Python trong bước tiếp theo.

## Phạm vi tài liệu gắn với nguồn và checkpoint.

Quy trình tổng hợp phương pháp từ source/audit Snaplock và các tài liệu nguồn đã liên kết. Các bước dùng cho model mới là hướng dẫn thực hành; kết quả mỗi lần áp dụng được lưu theo source/hash và bộ tham số của lần chạy. Nội dung dùng câu khẳng định và chỉ dẫn tích cực.
