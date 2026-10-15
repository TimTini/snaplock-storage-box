# Recipe chẩn đoán OpenSCAD, Fusion và dữ liệu hình học

Tài liệu này gom quy trình xử lý lỗi có thể dùng lại giữa các dự án. Lưu ca cụ thể, log nguyên bản, hash, kích thước và kết quả native trong hồ sơ dự án; giữ recipe ở đây theo điều kiện áp dụng và loại bằng chứng. [Ví dụ ca theo dự án](https://github.com/TimTini/snaplock-storage-box/blob/main/docs/examples/project-error-cases.md) là nơi đặt dữ liệu riêng khi có.

Các recipe chung là engineering_practice để chẩn đoán; một recipe không mang mặc định verified cho mọi model. Case áp dụng giữ knowledge_state và evidence theo [template](templates.md#ghi-lỗi-và-bài-học). Nguồn API xác nhận contract, ca native xác nhận build/input đã ghi; phần chưa thử giữ unverified/blocked.

## Cách dùng recipe

- Chọn recipe theo triệu chứng và giai đoạn xảy ra: đọc đầu vào, dựng biểu thức, tạo sketch, thêm feature, recompute, xuất mesh, truyền request hay lắp ráp.
- Ghi lại phiên bản ứng dụng/API, hash source và đầu vào, đơn vị, hệ tọa độ, cấu hình tham số, bước lỗi và log gốc trước khi sửa.
- Tách **nguyên nhân đã xác nhận** khỏi **giả thuyết**. Đánh dấu đã xác nhận khi bằng chứng phân biệt được nguyên nhân với các khả năng gần nhất và phép thử sau sửa tái hiện đúng hành vi mong đợi.
- Chạy kiểm tra ở đúng lớp: source/static, test offline, ứng dụng native, đầu ra xuất, hoặc thử lắp/vật lý. Mỗi kết quả chỉ xác nhận phạm vi phép đo đó.
- Ghi dependency hoặc dữ liệu đầu vào còn thiếu thành blocker cụ thể: tên gói/tệp/phiên bản cần có, bước bị chặn và bằng chứng cần thu tiếp.

## Recipe 1 — Kiểm tra mesh, tỉ lệ và đơn vị đầu vào

**Điều kiện áp dụng.** STL/OBJ/3MF mở sai kích thước, chi tiết đặt sai vị trí, mesh không kín, hoặc phép đo thay đổi theo cách nhập hay transform.

**Triệu chứng và bằng chứng.** Đọc đơn vị khai báo, nguồn tạo tệp, transform khi import, bounds, số thành phần, winding, thể tích và trạng thái watertight. So sánh một kích thước nhận diện với thông số nguồn; kiểm tra đơn vị ở cả exporter lẫn importer.

**Nguyên nhân / giả thuyết.** Ghi nguyên nhân đã xác nhận khi tỉ lệ/transform trong luồng nhập giải thích được sai số quan sát. Giữ nhãn “giả thuyết” khi chỉ có bounds lệch và bằng chứng còn thiếu bước đổi đơn vị hoặc datum.

**Hành động.** Chốt đơn vị và hệ trục bằng dữ liệu nguồn; áp một phép scale/transform có ghi lại lên bản sao làm việc; giữ mesh gốc bất biến. Với dữ liệu hở, định vị cạnh/mặt lỗi và xác định mục tiêu là sửa mesh, dựng surface hay dựng lại solid.

**Xác minh và phạm vi.** Đo lại bounds và kích thước nhận diện sau transform; so sánh hash, thành phần, thể tích và mặt cắt trước/sau. Watertight xác nhận tính kín của mesh theo phép kiểm đã chạy; kích thước thiết kế và khả năng lắp cần phép đo riêng. Dùng [S01](sources.md#s01), [S03](sources.md#s03), [S04](sources.md#s04), [S05](sources.md#s05), [S08](sources.md#s08).

## Recipe 2 — Sửa biểu thức và thứ tự phụ thuộc tham số

**Điều kiện áp dụng.** Fusion từ chối expression, tham số derived không cập nhật, hoặc kết quả số có đơn vị không tương thích.

**Triệu chứng và bằng chứng.** Ghi tên tham số, expression chính xác, đơn vị khai báo, API trả lỗi, thứ tự tạo tham số và các tham số được tham chiếu. Kiểm tra expression trong Fusion bằng [`UnitsManager.isValidExpression`](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/core_UnitsManager_isValidExpression.htm) và đọc lỗi gốc tại đúng lệnh tạo/cập nhật tham số.

**Nguyên nhân / giả thuyết.** Xác nhận lỗi grammar, tên tham số chưa tồn tại, kiểu đơn vị sai hoặc dependency cycle bằng thông báo/thử nhỏ cô lập được. Lỗi từ một parser offline chỉ xác nhận parser đó; biểu thức được chấp nhận trong native Fusion cần bằng chứng native.

**Hành động.** Sắp thứ tự tạo theo quan hệ phụ thuộc; giữ biểu thức Fusion riêng với biểu thức Python dùng cho tính toán; ghi đơn vị tường minh khi đầu vào có thể phụ thuộc setting tài liệu. Autodesk mô tả chiều dài nội bộ bằng cm và góc bằng radian trong Design API [S05](sources.md#s05). Bọc lỗi với tên tham số và expression nhưng giữ traceback/API failure gốc.

**Xác minh và phạm vi.** Kiểm tra giá trị/đơn vị sau khi thêm, chạy recompute, rồi đổi một tham số gốc để quan sát tham số derived. Test giả lập xác nhận chẩn đoán và luồng mã; chỉ native run xác nhận parser, đơn vị và recompute trong Fusion.

## Recipe 3 — Khóa sketch và đổi hệ tọa độ đúng frame

**Điều kiện áp dụng.** Sketch báo còn tự do hoặc over-constrained; profile nằm sai hướng trên mặt đã chọn; dimension có số lượng đúng nhưng hình học vẫn dịch/chảy.

**Triệu chứng và bằng chứng.** Ghi plane, `xDirection`/`yDirection`, normal, transform model↔sketch, entity type, tọa độ, constraint/dimension và trạng thái solver. Đánh giá mức khóa từ trạng thái solver và entity liên quan; số lượng dimension là dữ liệu chẩn đoán bổ sung.

**Nguyên nhân / giả thuyết.** Xác nhận khi xác định được bậc tự do còn lại, ràng buộc mâu thuẫn, mapping trục sai hoặc thứ tự dựng khiến solver cập nhật khác dự kiến. `Sketch.isFullyConstrained` là trạng thái boolean của solver theo [Autodesk API](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/fusion_Sketch_isFullyConstrained.htm); mock xác nhận contract của test, còn trạng thái sketch cần kiểm tra native.

**Hành động.** Chuyển điểm, tâm cung, vector và hướng feature qua cùng frame đã đo. Đặt datum rõ, nối cạnh rồi ràng buộc theo loại hình học và bậc tự do cần triệt tiêu. Tách dimension driving khỏi dimension reference; dùng contract riêng cho text, construction geometry và profile thường.

**Xác minh và phạm vi.** Kiểm tra tọa độ trước/sau, entity liên quan, profile kín và solver native. Test cấu trúc có thể xác nhận số điểm/cạnh/lời gọi API; chỉ Fusion xác nhận solver của sketch thực và phía vật liệu của feature.

## Recipe 4 — Font, SketchText và profile chữ

**Điều kiện áp dụng.** Tạo text thất bại theo font/nội dung; chữ thiếu glyph mong đợi; extrude chữ báo input không hợp lệ.

**Triệu chứng và bằng chứng.** Ghi giá trị font API, hệ điều hành/Fusion version, nội dung gồm dấu, kích thước khung, trạng thái `SketchText`, các profile sau thao tác và đoạn traceback. Xác định lỗi xảy ra khi tạo text, lấy glyph hay tạo feature.

**Nguyên nhân / giả thuyết.** Xác nhận thiếu family/glyph khi đối chiếu font được cài với font API chấp nhận; xác nhận nhầm kiểu đầu vào khi feature nhận `SketchText` ở nơi cần profile. Autodesk nêu [`SketchText.explode()`](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/fusion_SketchText_explode.htm) tạo curves và xóa đối tượng SketchText gốc.

**Hành động.** Chọn font đã kiểm tra trong môi trường chạy và bảo toàn văn bản gốc trong log. Nếu feature cần vùng kín, explode theo API rồi kiểm tra curve/profile kết quả trước khi tạo feature. Tạo lại glyph sau khi đổi nội dung hoặc cỡ chữ; áp ràng buộc phù hợp với text entity.

**Xác minh và phạm vi.** Chạy native với đúng nội dung/font, xác nhận dấu, profile kín, thể tích/body và hình hiển thị. Kiểm tra font cài đặt hoặc test mock xác nhận môi trường cài đặt hay luồng mã; Fusion native xác nhận font được nạp và glyph trên môi trường đã chạy.

## Recipe 5 — Ownership, Combine và Pattern

**Điều kiện áp dụng.** Join/Cut/Intersect đổi nhầm body, tool biến mất ngoài dự kiến, Mirror/Pattern tạo sai đối tượng hoặc số lượng.

**Triệu chứng và bằng chứng.** Tại feature đầu tiên sai, ghi component sở hữu target/tool, kiểu entity đầu vào, danh sách input, operation, keep-tools, hướng, quantity/distance, feature result và body sau recompute. Autodesk định nghĩa riêng `targetBody`/`toolBodies` cho [`CombineFeatureInput`](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/fusion_CombineFeatureInput.htm); pattern nhận loại entity có quy định trong [`createInput`](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/fusion_RectangularPatternFeatures_createInput.htm).

**Nguyên nhân / giả thuyết.** Xác nhận ownership sai khi danh sách đối tượng thực tế khác producer→consumer mong đợi; xác nhận hướng/số lượng sai khi input đo được mâu thuẫn với kết quả. Giữ giả thuyết nếu chỉ dựa vào tên hiển thị hoặc ảnh canvas.

**Hành động.** Lấy body từ output feature đúng loại; gán target và tools tường minh; đặt operation và chính sách giữ tool theo ý đồ. Khai báo cả hai chiều pattern khi API có hai hướng; ghi nguồn direction và kiểu khoảng cách. Chọn body theo index/name sau khi đối chiếu owner và trạng thái còn hiệu lực.

**Xác minh và phạm vi.** Sau recompute, đối chiếu body/component, số solid, vị trí, bounds, volume và tool còn lại theo contract. Test mock xác nhận cách tạo input; native xác nhận feature giải quyết đúng topology và ownership trong tài liệu đang chạy.

## Recipe 6 — Topology, feature lỗi và recompute

**Điều kiện áp dụng.** Feature được tạo nhưng profile/solid sai, feature báo unhealthy, tham chiếu downstream mất hiệu lực hoặc thay tham số không cập nhật đầy đủ.

**Triệu chứng và bằng chứng.** Ghi stage đầu tiên lỗi, timeline, input entity và validity, profile kín/hở, số solid, warning/error feature, kết quả compute/recompute và trạng thái tham số trước/sau. Tách lỗi tạo input khỏi lỗi kernel hoặc cập nhật downstream.

**Nguyên nhân / giả thuyết.** Xác nhận khi một input/topology cụ thể làm lỗi tái hiện trong bản sao cô lập và việc loại/thay input phù hợp khôi phục hành vi. “Feature success” hoặc process exit code xác nhận bước tạo feature; trạng thái downstream cần kiểm tra timeline và feature health.

**Hành động.** Thu hẹp tới feature đầu tiên sai; kiểm tra profile, axis/plane, participant/target, validity và dependency trước khi đổi hình học. Recompute theo luồng API hiện có; giữ lỗi nguyên gốc cùng stage trong chẩn đoán và dừng luồng tại feature lỗi.

**Xác minh và phạm vi.** Chạy lại cùng source/đầu vào, đổi một tham số đại diện và kiểm tra feature health, solid, bounds cùng volume ở cuối timeline. Offline tests xác nhận luồng kiểm tra; native run xác nhận kernel/timeline trong phiên bản Fusion đó.

## Recipe 7 — Tessellation, BRep và mesh là các phép đo khác nhau

**Điều kiện áp dụng.** Xuất mesh quá lớn/chậm, boolean mesh và BRep bất đồng, file hở sau export, hoặc chuyển mesh sang solid thất bại.

**Triệu chứng và bằng chứng.** Ghi source body, loại biểu diễn, export settings/preset, số mặt/triangle, kích thước file, hash, bounds, watertight, volume/intersection và đơn vị. Chạy phép so sánh trên cùng frame và cùng cấu hình.

**Nguyên nhân / giả thuyết.** Xác nhận lỗi export/topology khi chỉ ra vùng cạnh/mặt cụ thể; xác nhận độ mịn ảnh hưởng khi thay tessellation làm thay đổi số mặt và sai số đo. Mesh biểu diễn xấp xỉ tessellation; BRep và mesh booleans cho kết quả theo representation và tolerance tương ứng.

**Hành động.** Chọn preset/độ mịn theo kích thước, sai số cho phép và tài nguyên thực đo; thử trên một part trước. Giữ dữ liệu gốc, ghi rõ mọi simplification và sai lệch. Autodesk phân biệt chuyển mesh faceted/prismatic/organic và nêu điều kiện watertight ảnh hưởng đến solid hay surface [S08](sources.md#s08); xác định ngưỡng mặt theo máy và phiên bản đang chạy.

**Xác minh và phạm vi.** Audit mesh xuất riêng về kín, bounds, volume và mặt cắt; audit BRep bằng body health, interference và phép đo native tương ứng. Đặt tên riêng cho giao thể tích mesh và BRep; mỗi representation cùng chất lượng in có checkpoint đo riêng.

## Recipe 8 — Transport/API và phạm vi phiên

**Điều kiện áp dụng.** MCP/API trả initialize hoặc tool list thành công nhưng lệnh tiếp theo mất session, sai route, timeout hoặc response không khớp request.

**Triệu chứng và bằng chứng.** Ghi transport, endpoint/path, method, header định danh phiên, request ID, status, body đầy đủ, thứ tự message và phạm vi client/server đang giữ trạng thái. Che token và dữ liệu xác thực khỏi log chia sẻ.

**Nguyên nhân / giả thuyết.** Xác nhận sai scope/session khi request không tuân thủ protocol version hoặc server contract đang chạy. Tách lỗi transport, validation API, quyền truy cập và lỗi ứng dụng phía server. MCP 2026-07-28 đã bỏ handshake/session cấp giao thức; revision đến 2025-11-25 dùng initialize và session theo contract legacy ([MCP release](https://blog.modelcontextprotocol.io/posts/2026-07-28/)).

**Hành động.** Chốt protocol version và transport contract từ server trước khi áp lifecycle; truyền session/header/order đúng khi revision yêu cầu; parse response theo status và content type. Giữ logic retry/khởi tạo phiên theo quy tắc chính thức của endpoint. [S09](sources.md#s09) là nguồn giao thức trong [registry nguồn chung](sources.md).

**Xác minh và phạm vi.** Chạy handshake/discovery/call theo protocol version đã chốt và ghi response cùng trạng thái cuối. Client mock xác nhận serialization/ordering; kết quả native xác nhận kết nối cụ thể. Giới hạn kết luận theo server, route và phiên bản đã chạy.

## Recipe 9 — Assembly, đường chuyển động và mức chứng cứ

**Điều kiện áp dụng.** Các part vừa ở vị trí cuối nhưng vướng khi đưa vào, va chạm theo hành trình, hoặc báo cáo lắp đóng mâu thuẫn với mesh/export.

**Triệu chứng và bằng chứng.** Ghi transform/datum từng part, tọa độ và orientation, cặp kiểm tra, tolerance, trạng thái cơ cấu/chuyển động, pose lấy mẫu hoặc swept path, representation và đơn vị phép đo.

**Nguyên nhân / giả thuyết.** Xác nhận va chạm tĩnh bằng interference/boolean tại pose cụ thể; xác nhận va chạm theo đường bằng kiểm tra quét liên tục hoặc bước lấy mẫu có mật độ/giới hạn sai số đã nêu. Pose cuối xác nhận trạng thái cuối; đường lắp cần phép kiểm tra hành trình.

**Hành động.** Kiểm tra mating datums và quan hệ tham số trước khi chỉnh khe; đánh giá từng cặp có tương tác chức năng, vị trí lắp cuối và hành trình cần thiết. Chỉ thay offset/clearance theo sai số đo được của quy trình, kích thước, vật liệu hoặc tessellation cụ thể; ghi giá trị hiệu chỉnh và cơ sở.

**Xác minh và phạm vi.** Chạy bộ pose/biến thể đại diện cùng trạng thái mở/đóng, đo interference/clearance theo representation đã chọn. Native BRep, mesh export và thử in/lắp là các checkpoint tách biệt; bằng chứng ở một lớp chỉ chứng minh lớp đó. Dùng [quy trình đổi tham số](parameter-change-validation.md) để xác định miền biến thể và [hướng dẫn Fusion](fusion-python-tu-hoc.md) cho phép đo.

## Recipe 10 — Sliver ở góc Boolean và winding loft

**Điều kiện áp dụng.** Gia cường rời hợp lệ nhưng union với thành cong sinh mặt diện tích 0, cạnh lỗi hoặc thể tích có dấu âm.

**Bằng chứng và hành động.** Cô lập feature và tổ hợp, nạp lại export theo đúng backend/format. Kiểm tra winding, tọa độ cung và tiếp tuyến; chọn một builder sở hữu mặt ngoài và giữ phần đắp bên trong vật liệu thân. Với chuyển tiếp đáy, nâng đáy và bo bằng cùng hàm. [Quy trình và case dustpan](reinforcement-and-mesh.md#2-dựng-chuyển-tiếp-và-giao-quyền-sở-hữu-bề-mặt) ghi các lần thử và phạm vi cụ thể.

**Xác minh.** Kiểm tra mặt có diện tích dương, winding, thể tích, shell, Euler theo contract và probe tại góc/seam/overlap cho từng option, tổ hợp và biến thể. Ghi kiểm tra tự giao riêng theo acceptance.

## Recipe 11 — Phép đo ray phát RuntimeWarning hoặc ca lỗi nhận output cũ

**Điều kiện áp dụng.** Ray trên tam giác gần thẳng hàng làm phép đo bất ổn, hoặc ca input sai vẫn có artifact của lần chạy trước.

**Bằng chứng và hành động.** Xác định tam giác/vùng gây warning; chọn mặt cắt và nội suy đoạn thẳng cho phép đo ngang phù hợp. Với ca từ chối, dùng output thử riêng, dọn output thử cũ và thu diagnostics từ cả stdout/stderr.

**Xác minh.** Giữ RuntimeWarning thành lỗi, đo lại giao điểm/bề dày và các vùng lân cận. Xác nhận return code, thông báo đúng contract và trạng thái output. [Case dustpan](reinforcement-and-mesh.md#6-case-dustpan--bằng-chứng-ngày-15102026) có hash verifier và phạm vi bằng chứng; [quy trình chung](reinforcement-and-mesh.md) phân biệt screen FDM, slicer và tải thực.

## Ghi nhận ca mới

Mỗi bản ghi lưu: điều kiện áp dụng; triệu chứng; bằng chứng quan sát; nguyên nhân đã xác nhận hoặc giả thuyết; thay đổi; lệnh/phép thử; kết quả; phiên bản/hash; phạm vi kiểm chứng tiếp theo. Lưu ca gắn với dự án trong [examples/project-error-cases.md](https://github.com/TimTini/snaplock-storage-box/blob/main/docs/examples/project-error-cases.md); recipe dùng lại được bổ sung ở phần phù hợp sau khi đã rút được điều kiện và phép xác minh tổng quát.

Nguồn kỹ thuật theo registry: [S01 OpenSCAD], [S03 Trimesh], [S04 CGAL], [S05 Fusion Units], [S06 Fusion proxies], [S07 Sketch/Text/Constraints], [S08 Mesh], [S09 MCP], [S10 Parameters], [S11 Feature selection]. API claim trên trang này trỏ trực tiếp tới tài liệu Autodesk chính thức.
