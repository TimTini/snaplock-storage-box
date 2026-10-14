# Tự học Fusion Python cho mô hình native

Tài liệu này là hướng dẫn dùng lại để khảo sát, dựng và kiểm tra mô hình tham số trong Autodesk Fusion bằng Python API.
Hướng dẫn tách **API chính thức**, **thực hành kỹ thuật** và **bài tập đề xuất**.
Kết quả chỉ được xác nhận ở mức có bằng chứng đã lưu; source, kiểm thử offline, Fusion native, mesh xuất và thử nghiệm vật lý là các lớp riêng.

**API chính thức** bên dưới dựa trên các trang Autodesk được liên kết. **Thực hành kỹ thuật** gồm contract, pipeline, cổng và phép đo áp dụng theo task. **Bài tập đề xuất** là ví dụ học tập, không phải yêu cầu mặc định.

## Chọn đường đi theo đầu vào và mục tiêu

| Đầu vào và mục tiêu | Quy trình phù hợp |
|---|---|
| SCAD và cần cây feature Fusion có thể chỉnh sửa | Đọc SCAD để hiểu quan hệ hình học; dựng hoặc đồng bộ feature native theo contract của task. |
| STL/OBJ/mesh và chỉ cần BRep để tiếp tục thao tác trực tiếp | Nhập mesh, đánh giá tình trạng lưới, rồi cân nhắc Convert Mesh sang faceted/prismatic BRep. Đây là chuyển đổi từ tessellation, không tái tạo ý nghĩa tham số ban đầu. |
| Mesh làm căn cứ và cần model native có ý nghĩa thiết kế | Đo và xác định datums/profile trước; dựng lại các đặc trưng theo hình học và mục tiêu chỉnh sửa. Giữ mesh làm đối chiếu. |
| Cần giữ mặt tam giác hoặc phát hành mesh | Giữ mesh representation phù hợp và định nghĩa riêng chất lượng/định dạng xuất. |

Convert Mesh phù hợp với nhu cầu BRep trực tiếp khi không cần dựng lại quan hệ tham số.
Khi task đòi hỏi User Parameters, công thức, feature có ý nghĩa hoặc chỉnh sửa lịch sử, dựng lại native theo yêu cầu đó.
Không gán độ chính xác hay khả năng chỉnh sửa vượt quá căn cứ đầu vào.

## 1. Chốt đầu vào, ownership và hệ tọa độ

1. Đọc hướng dẫn dự án, README, manifest, checkpoint và trạng thái thay đổi trước khi dựng.
2. Ghi từng input: đường dẫn tương đối, vai trò, kích thước file, SHA-256, phiên bản/nguồn và trạng thái được phép sử dụng.
3. Tạo snapshot ổn định cho dữ liệu tham chiếu cần giữ nguyên. Hash lại sau khi hoàn tất để phát hiện thay đổi ngoài dự kiến.
4. Ghi bảng part/component, tên và ownership. Mỗi feature khai báo component sở hữu sketch, tool, target, body kết quả và ngữ cảnh occurrence.
5. Ghi đơn vị đầu vào, đơn vị Fusion, trục, gốc, hướng nhìn, handedness, transform và datum dùng để so sánh.
6. Tách miền hợp lệ của tham số khỏi yêu cầu sản phẩm, khổ máy, khoảng hở thao tác hoặc giới hạn vật lý. Chỉ áp dụng giới hạn được task chỉ rõ.
7. Đánh dấu các chi tiết đo trực tiếp, suy ra, xấp xỉ và chưa biết. Gắn mục tiêu sai số hoặc tiêu chí chức năng cho vùng quan trọng.

Tọa độ sketch được suy ra từ frame của plane/face và `xDirection`/`yDirection`.
Lập phép đổi tọa độ tường minh: điểm và tâm chịu rotation/translation; vector hướng chỉ chịu phần tuyến tính phù hợp, normal dùng phép đổi normal tương ứng. Kiểm tra cùng frame và phân biệt loại đại lượng.
Kiểm tra vài điểm datum đã biết để xác nhận dấu trục, chiều xoay và hướng extrusion.

Trong assembly, phân biệt object native thuộc component với proxy trong occurrence context.
Chọn đối tượng đúng ngữ cảnh khi tạo sketch/feature trên mặt của occurrence.
Lưu ownership cùng tham số/feature thay vì tìm lại qua tên không duy nhất.

## 2. Xây contract tham số và hình học

Tạo bảng gồm tên, nghĩa thiết kế, loại/đơn vị, miền hợp lệ, giá trị baseline, nguồn và biểu thức phụ thuộc.
Dùng User Parameters cho kích thước thiết kế; biểu diễn quan hệ bằng expression dùng tên tham số.
Giữ số literal cho hằng số hình học hoặc numerical tolerance đã ghi rõ.

Phân loại mỗi đầu vào thành:

- **Kích thước liên tục:** thường có thể cập nhật qua Change Parameters và recompute.
- **Lựa chọn topology/cấu trúc:** số profile, số instance, số body hoặc nhánh hình học; thay đổi có thể cần dựng lại feature/cây.
- **Thiết lập xuất/kiểm tra:** định dạng, độ mịn, tolerances và bộ đo; ghi trong manifest, không trộn với kích thước part.

Nêu invariant phải giữ, chẳng hạn mặt phẳng tham chiếu, đối xứng, tâm đồng trục, bề dày tối thiểu hoặc quan hệ part.
Ràng buộc miền bằng điều kiện đầu vào có thông báo rõ.
Không giả định mọi bộ tham số đều giữ cùng topology hoặc làm feature hợp lệ.

### Đơn vị API

Tài liệu Autodesk cho biết Design API dùng cm cho chiều dài, radian cho góc, và cm³ cho thể tích.
Các giá trị số thực truyền/nhận theo API dùng đơn vị nội bộ của loại đại lượng; giá trị có chuỗi expression có thể kèm đơn vị.
Dùng `UnitsManager` khi đổi đơn vị hiển thị và chỉ chuyển một lần ở ranh giới I/O.

Ghi rõ đơn vị cho từng số trong log/manifest.
Ví dụ: tọa độ/chiều dài nội bộ là cm, góc là radian, thể tích là cm³.
Quy đổi thể tích API cm³ sang báo cáo mm³ bằng nhân 1000; đổi mm³ về cm³ bằng chia 1000. Đối chiếu hai giá trị sau khi đưa về cùng đơn vị.

## 3. Chọn feature theo hình học, độ chính xác và khả năng sửa

Chọn phương pháp theo bề mặt/tiết diện, dữ liệu đầu vào, độ chính xác cần có và loại chỉnh sửa mong muốn.
Đánh giá các lựa chọn trên cùng vùng, cùng datum và cùng tiêu chí.

| Điều kiện hình học | Phương pháp nên đánh giá |
|---|---|
| Tiết diện không đổi chạy theo một hướng | Sketch + Extrude; kiểm tra profile, chiều và extent. |
| Tiết diện quay quanh một trục | Sketch profile + Revolve; kiểm tra trục, góc và đóng/mở profile. |
| Tiết diện di chuyển theo path | Sweep; kiểm tra path, hướng profile, orientation, rail/surface nếu cần. |
| Tiết diện biến đổi giữa các vị trí | Loft; thử số tiết diện cần thiết, thứ tự/corner matching, rail hoặc centerline. |
| Hình tham chiếu là lưới tam giác và yêu cầu là thao tác BRep | Convert Mesh theo faceted/prismatic/organic khi phương pháp và năng lực môi trường phù hợp. |

Extrude, Revolve, Sweep và Loft không có thứ tự ưu tiên cố định.
So sánh sai lệch hình học, độ ổn định khi tham số đổi, mức rõ ràng của timeline, số đầu vào độc lập và chi phí cập nhật.
Ghi lựa chọn cùng căn cứ; chọn Loft khi nó phù hợp tốt hơn các ứng viên đã đánh giá.

Ưu tiên cạnh/face/profile được tìm từ geometry và quan hệ thiết kế.
Tránh phụ thuộc vào index không ổn định hoặc tên chung như `Face7`.
Nếu cần chọn BRep sau khi thay đổi, lọc theo loại hình học, vị trí, hướng pháp tuyến, bán kính/kích thước và ngữ cảnh component; xác nhận ứng viên duy nhất hoặc dừng với lỗi mô tả rõ.

Trong sketch, dựng geometry, dimension và geometric constraints theo ý nghĩa.
Kiểm tra profile kín/mở theo mục đích feature, entity tham chiếu và bậc tự do.
Fully constrained là một chỉ số solver; nó không tự chứng minh profile đúng kích thước hoặc đúng vị trí.

## 4. Tổ chức source và pipeline có thể kiểm tra

Chia script theo nhiệm vụ nhỏ: đọc/validate input, tạo document, tạo tham số, dựng component/feature, kiểm tra, xuất, thu dọn và ghi report.
Dùng tên feature diễn đạt vai trò.
Giữ luồng tuyến tính, thông báo lỗi theo stage và giữ traceback gốc.

Mỗi lần chạy ghi: task/run ID, UTC timestamp, phiên bản Fusion/API nếu lấy được, hash source và input, tham số, nhánh topology, stage bắt đầu/kết thúc, kết quả kiểm tra, đường dẫn output và hash output.
Manifest máy đọc được liên kết các phần này.
Không lưu credential, dữ liệu cá nhân hoặc log nhạy cảm.

| Cổng | Đầu vào | Kết quả phải ghi | Điều kiện qua |
|---|---|---|---|
| Input | Source, mesh/CAD, bảng tham số | Hash, đơn vị, frame, quyền dùng, version | Input còn nguyên và contract hợp lệ |
| Offline | Script, fixtures/mock, công thức | Lệnh, kết quả, phạm vi thực thi | Cú pháp và ca logic thuộc phạm vi đạt |
| Native | Script trong Fusion và document test mới | Fusion/API version, source hash, log theo stage | Recompute, health, ownership và invariant đạt |
| Export | Body/occurrence được chọn | Định dạng, đơn vị, độ mịn, file/hash | File tồn tại, đọc được và audit phù hợp |
| Vật lý | Mẫu chế tạo và quy trình xác định | Vật liệu, thiết bị, thông số, phép đo | Tiêu chí vật lý của task được đo trực tiếp |

Tạo document test riêng để kiểm chứng.
Chạy ca baseline, biến thiên liên tục, sát biên hợp lệ và các thay đổi topology được yêu cầu.
Trước mỗi ca, ghi tham số gốc; sau mỗi ca, đo giá trị thực, trạng thái feature và số body.
Cuối ma trận, khôi phục expression gốc trong `finally`, gọi recompute và xác nhận lại giá trị, health và invariant baseline.

Nếu Fusion native hoặc automation runtime không có, hoàn tất phần offline khả thi rồi ghi `offline_only`/`not_run` cho native.
Nêu môi trường hoặc bằng chứng còn thiếu.
Không suy ra native pass từ mock, syntax check hay nguồn đã đọc.

## 5. Recompute, health và topology

Sau khi thêm hoặc thay đổi một nhóm feature, gọi phương thức compute/recompute tương ứng với API và trạng thái document hiện tại.
Đọc health của feature và ghi lỗi/warning cùng tên feature, stage và tham số.
Kiểm tra document/model có lỗi solver, profile rỗng, body sai ownership, số lượng ngoài contract hoặc thể tích không hợp lệ.

Recompute xác nhận Fusion đã tính lại trạng thái parametric hiện tại; nó không chứng minh hình học phù hợp thiết kế.
Kiểm tra thêm datum, bounds, thể tích, mặt cắt, kích thước đặc trưng và quan hệ giữa part theo contract.
Đặt tolerance theo nguồn đo và mục tiêu task.

Thay đổi kích thước liên tục thường kiểm tra đường cập nhật expression trên cây hiện có.
Thay đổi count được native Pattern expression hỗ trợ có thể recompute trên cây hiện có. Số entity tạo bằng vòng lặp lúc Run hoặc thay đổi ngoài topology đã hỗ trợ cần rebuild; tạo document test mới hoặc dựng lại phần liên quan rồi kiểm tra dependency phía sau.
Ghi rõ mỗi biến thể là recompute hay rebuild.

## 6. Phân biệt BRep, tessellation và vật thể thật

BRep mô tả biên hình học bằng mặt/cạnh; mesh tessellation xấp xỉ bề mặt bằng tam giác.
Xuất STL/mesh biến BRep thành tessellation theo thiết lập độ mịn.
So sánh BRep và mesh trong cùng đơn vị, căn chỉnh và tolerance; kiểm tra bounds, thể tích, khoảng cách bề mặt, normals, watertight/manifold khi công cụ audit hỗ trợ.

Convert Mesh tạo solid/surface theo trạng thái mesh và phương pháp chọn.
Faceted giữ nhiều mặt tam giác; prismatic nhóm hình học dạng lăng trụ khi nhận diện được; organic có sẵn tùy năng lực/extension/version.
BRep chuyển từ mesh vẫn phản ánh nguồn tessellation, không khôi phục thiết kế gốc tự động.

Mesh audit không phải bằng chứng về độ bền, lắp vừa, lực, vật liệu, máy in hay chất lượng bề mặt.
Ghi mỗi loại kết quả riêng; chỉ xác nhận vật lý khi có mẫu, điều kiện và phép đo thực tế được lưu.

Khi xuất, khai báo chính xác body/component/occurrence được xuất, định dạng, hệ đơn vị, chord/angle/normal settings nếu API/version cung cấp, đường dẫn và SHA-256.
Đọc lại đầu ra bằng công cụ độc lập khi phù hợp.
Không gọi file tồn tại là pass nếu chưa kiểm tra nội dung.

## 7. Bài tập đề xuất

Bắt đầu với một sketch profile có kích thước và ràng buộc rõ.
Thêm một feature đơn, rồi tạo User Parameter thứ hai có expression phụ thuộc.
Chạy native trong document mới, đổi tham số liên tục, recompute và kiểm tra geometry, health cùng expression.

Tiếp theo thử một vùng phù hợp với Revolve, Sweep hoặc Loft theo hình học thực tế.
Ghi các lựa chọn đã so sánh, đầu vào điều khiển và khác biệt đầu ra.
Sau đó thử một đầu vào làm đổi topology; chạy rebuild và kiểm tra lại các feature phụ thuộc.

Mỗi bài tập chỉ tuyên bố đúng lớp bằng chứng đã thu: API/source, offline, Fusion native, mesh export hoặc vật lý.
Gắn mã nguồn tham khảo theo bảng sources của bộ tài liệu khi claim cần đối chiếu.

## Nguồn API chính thức

- [S05 — Understanding Units in Fusion](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/Units_UM.htm)
- [S06 — Documents, Products, Components, Occurrences, and Proxies](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/ComponentsProxies_UM.htm)
- [S07 — Sketch contract, text và compute](sources.md#s07)
- [S08 — Convert a mesh body to a solid body](https://help.autodesk.com/view/fusion360/ENU/?contextId=MESH-CONVERT-TO-SOLID)
- [S10 — UserParameter Object](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/fusion_UserParameter.htm)
- [S11 — Feature theo hình học](sources.md#s11)
- [Fusion solid features from sketches](https://help.autodesk.com/cloudhelp/ENU/Fusion-Model/files/SLD-CREATE-SOLID-FROM-SKETCH.htm)
- [Compute All](https://help.autodesk.com/cloudhelp/ENU/Fusion-Model/files/SLD-COMPUTE.htm)
- [STL export options](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/fusion_ExportManager_createSTLExportOptions.htm)
