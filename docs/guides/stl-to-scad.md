# Phân tích STL và chọn route OpenSCAD/Fusion

Hướng dẫn này áp dụng cho dự án mới. STL cung cấp mặt tam giác để quan sát và đo; OpenSCAD biểu diễn quy luật hình học bằng tham số, profile, module và phép dựng. Fusion tiếp nhận baseline hình học đã có hồ sơ đo và mục tiêu chuyển đổi.

Chọn mục tiêu **tái tạo hình dáng**, **khôi phục ý đồ tham số** hoặc kết hợp cả hai. Mục tiêu hình dáng ưu tiên sai lệch so với bề mặt mẫu. Mục tiêu tham số suy ra các kích thước điều khiển, quan hệ và miền hoạt động; STL cung cấp lưới tam giác, còn bản vẽ, mẫu chức năng và tài liệu thiết kế cung cấp căn cứ cho công thức.

Quy trình đi qua các cổng: `đầu vào rõ → mesh phân loại → hệ tọa độ chốt → hình học suy luận → SCAD dựng được → kiểm chứng phù hợp → bàn giao`. Mỗi cổng ghi `PASS`, `blocked` hoặc `blocked`, kèm bằng chứng và bước kế tiếp.

Nguồn phương pháp được lập chỉ mục tại [sources.md](sources.md): [S01 OpenSCAD](sources.md#s01), [S03 Trimesh](sources.md#s03), [S04 CGAL](sources.md#s04), [S08 Fusion mesh](sources.md#s08). Tài liệu điều phối liên quan: [agent-learning.md](agent-learning.md), [parameter-change-validation.md](parameter-change-validation.md), [scad-to-fusion-task.md](scad-to-fusion-task.md) và [error-cookbook.md](error-cookbook.md).

## 1. Chốt đầu vào, mục tiêu và căn cứ

1. Ghi đường dẫn, kích thước, định dạng, nguồn, giấy phép và SHA-256 của STL. Giữ một snapshot chỉ đọc làm chuẩn; tạo bản làm việc riêng cho mọi phép sửa mesh.
2. Ghi mục tiêu, part thuộc phạm vi, đặc trưng chức năng, cách sử dụng và phép nghiệm thu. Chọn mục tiêu hình dáng, ý đồ tham số hoặc cả hai; mô tả đầu ra mong đợi theo từng mục tiêu.
3. Xác nhận đơn vị bằng tài liệu nguồn, kích thước đáng tin cậy hoặc đặc trưng vật lý. Vì STL lưu tọa độ mà không kèm đơn vị, hãy ghi đơn vị đầu vào, đơn vị làm việc, hệ số quy đổi và căn cứ.
4. Ghi bounds, số mặt, số đỉnh, ứng dụng/thư viện và phiên bản, import options, cảnh báo khi nạp, tọa độ gốc và ma trận instance nếu có.
5. Đặt dung sai theo yêu cầu chức năng, kích thước, vật liệu, quy trình sản xuất và độ phân giải của mẫu. Ghi đại lượng, đơn vị, vùng áp dụng và lý do; dùng ngưỡng riêng cho kích thước, lắp, hình dáng và phép gần đúng.

Đầu ra là hồ sơ nguồn, mục tiêu, đơn vị, danh sách part/đặc trưng và bảng tiêu chí nghiệm thu. Trạng thái `blocked` áp dụng khi đơn vị, nguồn hoặc mục tiêu còn thiếu căn cứ.

## 2. Phân loại mesh trước khi dựng

Kiểm tra bounds, số connected component, cạnh biên, độ kín (watertight), manifold, hướng mặt (winding), mặt suy biến, tự giao và thể tích có dấu. Lưu mỗi kết quả riêng cùng công cụ/phương pháp sử dụng.

Connected component là vùng mặt liên thông theo quan hệ kề. Một component có thể chứa nhiều chi tiết thiết kế; một part thiết kế có thể gồm nhiều component, mặt rời, chốt hoặc mảnh trang trí. Gán vai trò part bằng vị trí, hình dáng, chức năng và quan hệ lắp. Ghi bảng ánh xạ `component → part → vai trò`; xác nhận nhóm lặp, mảnh rời và bề mặt nội thất bằng quan sát.

Phân luồng theo trạng thái mesh:

| Kết quả kiểm tra | Trạng thái và bước tiếp theo |
|---|---|
| Mesh kín, orientable, manifold, winding nhất quán, số tự giao bằng 0; volume hợp lệ | `SOLID_CANDIDATE`; dùng kiểm tra thể tích và các phép so khối sau khi xác nhận đơn vị và trục. |
| Có cạnh biên hoặc lỗ hở | `SURFACE_ONLY`; lập bản đồ lỗ và mục đích bề mặt. Vá lỗ trên bản sao khi có căn cứ hình học; lưu vùng vá và so ảnh/mặt cắt trước-sau. |
| Non-manifold, winding lỗi, mặt suy biến hoặc tự giao | `REPAIR_REQUIRED`; xác định lỗi và ảnh hưởng trước khi chọn thao tác. Sửa trên bản sao, giữ bản gốc/hash, ghi từng thay đổi và chạy lại toàn bộ kiểm tra liên quan. |
| Trạng thái `UNIT_UNCONFIRMED` hoặc tỷ lệ `SCALE_UNCONFIRMED` | `blocked`; giữ nguyên scale, tập trung vào đo hình dạng tương đối và chờ căn cứ trước khi kết luận kích thước, thể tích hoặc lắp. |
| Dữ liệu scan/organic hoặc mục tiêu là giữ bề mặt hữu cơ | `ORGANIC_SURFACE`; giữ mesh làm chuẩn hình dáng, lập vùng cần dựng tham số và đánh giá nhánh Fusion mesh phù hợp. |

Mesh repair có thể đổi topology hoặc hình dáng. Mỗi thao tác có giả thuyết, bản sao đầu vào, hash trước/sau, báo cáo thay đổi và phép xác minh lại. [Trimesh](sources.md#s03) mô tả các kiểm tra/sửa lưới và lưu ý về vá lỗ; [CGAL](sources.md#s04) phân biệt điều kiện manifold với tự giao hình học. Gắn kết quả đo với đúng bản mesh và trạng thái repair đã kiểm tra.

## 3. Chốt hệ tọa độ và biến đổi

Lưu assembly transform ban đầu trước khi đưa part sang hệ đo cục bộ. Chọn trục theo datum quan sát được, như mặt lắp, trục lỗ, đường tâm hoặc hướng kéo; ghi origin, hướng trục, handedness và đơn vị.

Tách các phép biến đổi thành mục đích riêng:

- **Rigid transform**: quay và tịnh tiến để đặt part vào hệ đo; kích thước và hình dạng giữ nguyên.
- **Unit conversion**: nhân tọa độ bằng hệ số chuyển đơn vị đã xác nhận; kích thước số đổi theo đơn vị đích.
- **Scale hình học**: biến đổi kích thước theo một hay nhiều trục khi ý đồ thiết kế xác nhận phép scale. Ghi hệ số từng trục và sự thay đổi hình dạng.
- **Assembly placement**: đặt part trở lại quan hệ lắp, tách khỏi việc chuẩn hóa hình dạng.

Lưu ma trận thuận/nghịch hoặc phép biến đổi có thứ tự rõ ràng. So bounds, kích thước datum và vị trí assembly trước/sau. Khi ma trận chứa scale, tách scale khỏi rigid transform để báo cáo không diễn giải scale như căn chỉnh tọa độ.

## 4. Đo và suy luận hình học

Đo các đặc trưng có liên hệ mục tiêu: mặt chuẩn, biên ngoài/trong, lỗ, trục, chiều dày, bán kính, mặt lắp, khe, vùng đàn hồi và chi tiết lặp. Mỗi số đo ghi hệ tọa độ, đơn vị, cách lấy, vùng dữ liệu, độ phân giải mẫu và khoảng không chắc chắn.

Lấy mặt cắt tại các vị trí đặc trưng theo datum: đầu/giữa/cuối, vùng chuyển tiếp, tâm trục hoặc vùng chức năng. Lưu mặt phẳng (origin, normal), đường bao, phép chiếu 3D↔2D và ảnh có tỉ lệ. Dùng nhiều mặt cắt để phân biệt extrusion, hình tròn xoay, loft, gân, đối xứng và biến thiên theo chiều dài. Lấy thêm mặt cắt trung gian để kiểm tra giả thuyết nội suy. [Trimesh section](sources.md#s03) minh họa mặt cắt theo mặt phẳng và chuyển path về 2D.

Fit primitive/profile trên vùng dữ liệu đã xác định; báo số mẫu, phương pháp, residual RMS, percentile và cực đại quan sát. Kiểm tra mẫu độc lập ở mặt cắt/vùng khác trước khi suy rộng quy luật. Giữ bảng đo địa phương kèm tên, vị trí, đơn vị và nguồn quan sát.

Ghi riêng hai loại kết luận:

- **Shape match**: mức gần bề mặt tham chiếu tại cấu hình đã đo, cùng vùng và phương pháp so sánh.
- **Parametric intent**: kích thước điều khiển, phương trình derived, quan hệ đối xứng/lặp/lắp, ràng buộc và miền hợp lệ được suy ra từ bản vẽ, mẫu chức năng, tài liệu hoặc quyết định thiết kế.

Fit tốt hỗ trợ kết luận shape match. Đánh dấu công thức tham số đang chờ căn cứ là `INFERRED`; chuyển sang trạng thái đã xác nhận khi bản vẽ, mẫu chức năng, tài liệu hoặc biến thể cung cấp bằng chứng.

## 5. Dựng SCAD có cấu trúc

1. Tạo file SCAD độc lập với đường dẫn project cụ thể. Import STL chỉ làm lớp tham chiếu có thể bật/tắt; phần hình học cần chỉnh sửa được dựng từ primitive, profile và phép dựng có tên.
2. Khai báo tham số gốc theo ý nghĩa thiết kế; tính các kích thước phụ thuộc bằng công thức. Dùng `assert` cho miền hợp lệ của độ dày, bán kính, khe và vị trí.
3. Chia module theo part/chức năng và gom tọa độ đo được vào profile/table có chú thích nguồn. Dùng vòng lặp hoặc đối xứng khi dữ liệu xác nhận quy luật đó.
4. Dựng từ khối chính sang lòng/khoang, đặc trưng chức năng và vùng chuyển tiếp. Dùng `union`, `difference` và `intersection` theo hình học giao thực tế. Tách epsilon cho ổn định tính toán khỏi clearance lắp và dung sai sản xuất.
5. Thêm selector để render từng part và assembly; khai báo hướng trục, đơn vị, tham số và độ phân giải tessellation cho đầu ra.

Boolean khối yêu cầu đầu vào có diễn giải thể tích nhất quán. Chạy phép đo thể tích hoặc boolean khi mesh tham chiếu và mesh SCAD đều là solid hợp lệ, với đơn vị, hướng mặt, độ kín và tự giao đã xác nhận. Ghi engine và tùy chọn boolean. Trước cổng solid, dùng bounds, mặt cắt và khoảng cách bề mặt; đánh dấu phép đo khối `blocked` tới khi có bề mặt thể tích đáng tin cậy. [S03 Trimesh](sources.md#s03) nêu điều kiện watertight cho volume; [S04 CGAL](sources.md#s04) cung cấp phép kiểm tra tự giao và mesh processing.

## 6. Đối chiếu với tiêu chí đã chọn

Render từng part và assembly bằng phiên bản OpenSCAD, backend, selector, tham số và độ phân giải đã ghi. Lưu log, ảnh các hướng, bounds, mesh xuất, số component, kiểm tra solid và hash của source/đầu vào/đầu ra.

Chọn phép đo theo loại câu hỏi:

| Câu hỏi | Bằng chứng |
|---|---|
| Bao tổng thể và định vị | Bounds, datum, ma trận và sai lệch theo trục. |
| Thể tích/vật liệu thừa thiếu | Boolean hai chiều `A \ B` và `B \ A` sau khi cả hai mesh đạt điều kiện solid; báo thể tích tham chiếu và tỉ lệ theo cùng đơn vị. |
| Khoảng cách bề mặt | Lấy mẫu có seed, mật độ/chiến lược, khoảng cách hai hướng, phân vị và cực đại mẫu. Gọi kết quả là **surface sampling** hoặc **cực đại quan sát**, ghi rõ nó phụ thuộc vào lấy mẫu. |
| Cận Hausdorff | Chạy thuật toán có cận sai số đã khai báo, ghi error bound, đơn vị, hai hướng và giá trị đối xứng là max của hai hướng. Cận thuật toán và độ phân giải mẫu là hai thông số riêng. |
| Đặc trưng chức năng | Mặt cắt, kích thước địa phương, vị trí lỗ/trục, thành mỏng, khe và quan hệ lắp. |

Hausdorff hai chiều biểu diễn cực đại khoảng cách có hướng trên toàn bề mặt; kiểm tra lấy mẫu hữu hạn báo cáo các điểm đã lấy. Gọi cực đại của mẫu rời rạc là `sampled maximum`; dành tên Hausdorff cho phép tính có định nghĩa và cận sai số tương ứng. [S04 CGAL](sources.md#s04) định nghĩa approximate và bounded-error Hausdorff; [S03 Trimesh](sources.md#s03) cung cấp truy vấn điểm gần mặt và sampling.

Đặt mỗi ngưỡng theo mục đích sử dụng và độ không chắc chắn của nguồn đo. Ghi đơn vị, phạm vi, cách so, mức tin cậy và lý do. Tolerance hình dáng, kích thước, giao lắp, vận hành và sản xuất có thể khác nhau. Dừng kết luận `PASS` khi phép đo không đủ độ phân giải để phân biệt ngưỡng.

## 7. Thử biến thể và chốt baseline

Chạy cấu hình tham chiếu cùng các biến thể đại diện và trường hợp biên trong miền hợp lệ. Kiểm tra render, topology/solid, bounds, độ dày, vị trí đặc trưng, quan hệ part, khe và công thức derived. Đối chiếu STL dùng cấu hình tham chiếu; đánh giá biến thể bằng invariant và mục tiêu thiết kế.

Khi thay đổi tham số làm hỏng hình học hoặc quan hệ lắp, đánh dấu `FAIL` cho cấu hình đó, xác định công thức/module gây lỗi và cập nhật miền hợp lệ trước khi phát hành baseline. Phân loại kiểm chứng thành source/render, đo mesh, lắp ráp, coupon/in thực tế và thử lực/chuyển động; gắn mỗi kết luận với bằng chứng tương ứng.

Baseline bàn giao gồm SCAD chỉnh sửa được, bảng tham số/đơn vị, manifest nguồn và hash, lựa chọn công cụ, preview, STL từng part nếu thuộc phạm vi, báo cáo mesh/đo, biến thể, vùng xấp xỉ và trạng thái từng cổng. Ghi các phần `INFERRED`, `blocked` và `blocked` để bước Fusion nhận đúng giới hạn.

## 8. Chọn nhánh tiếp theo và ghi trạng thái

- Mesh cơ khí có mặt phẳng/trụ/lỗ nhận diện được: tiếp tục dựng SCAD tham số; khi chuyển Fusion, chọn workflow giữ feature native và ý đồ tham số.
- Mesh kín dạng faceted: đánh giá Fusion Convert Mesh theo mục tiêu. Autodesk phân biệt `Faceted` với `Prismatic`; ghi Operation `Parametric` hoặc `Base Feature` theo nhu cầu timeline và kiểm tra kết quả trong Browser/Timeline.
- Scan hoặc hình hữu cơ: giữ mesh làm chuẩn bề mặt; đánh giá Convert Mesh `Organic` trong Fusion khi extension cần thiết có sẵn. Ghi Resolution và lựa chọn `By Accuracy`/`By Face Number`; nếu mesh hở, phân loại surface và hoàn thiện solid theo một workflow bề mặt có kiểm chứng.
- Mesh có lỗi topology hoặc trạng thái `UNIT_UNCONFIRMED`: giữ cổng khối ở `blocked` hoặc đầu vào ở `blocked`; tiếp tục phép đo bề mặt có căn cứ và ghi giới hạn.

Mỗi lần chạy kết thúc bằng một bản ghi: `PASS` nêu tiêu chí và bằng chứng; `FAIL` nêu phép đo không đạt cùng vùng lỗi; `blocked` nêu điều kiện kỹ thuật còn thiếu; `blocked` nêu quyết định/căn cứ cần bổ sung. Gắn đường dẫn artifact và hash để lần sau lặp lại được.
