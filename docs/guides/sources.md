# Registry nguồn và phạm vi xác nhận

Ngày đối chiếu nguồn cho bản 1.0: **14/10/2026**. Registry ghi claim cụ thể và giới hạn, không thay việc kiểm tra symbol trên runtime đích. Nguồn web có thể đổi; lần áp dụng sau ghi URL, ngày, API/build và snapshot/commit nếu dùng corpus.

## Nhãn tri thức

- official_reference: nguồn primary mô tả API/format/công cụ; xác nhận nội dung của nguồn, không xác nhận task đã chạy.
- engineering_practice: quy trình tổng hợp, công thức suy dẫn hoặc heuristic có điều kiện; được đánh giá bằng acceptance của task.
- project_observation: kết quả thật có input/source/hash, ngày/build, lệnh và report của một project.
- proposed_exercise: bài thử chưa có kết quả; bổ sung observation sau khi chạy.

Mỗi kết luận mới ghi nhãn, claim ID, phạm vi/điều kiện, URL/section, version, ngày đối chiếu và evidence thực nếu có. Hướng dẫn core đặt link Sxx cạnh claim hoặc section có cùng phạm vi; case riêng giữ source/hash trong hồ sơ project.

<a id="s01"></a>
## S01 — Ngôn ngữ OpenSCAD

Nguồn: [Documentation chính thức](https://openscad.org/documentation.html), [Cheat Sheet](https://openscad.org/cheatsheet/).

Claim: primitive, biến/module, loop, transform, boolean, extrusion và các biến độ phân mịn có trong ngôn ngữ; tài liệu chính thức dẫn tới manual từng phần. hull tạo bao lồi; section/profile sampling cần kiểm tra vùng nội suy khi mô hình hóa mặt cong.

Nhãn: official_reference cho tính năng; engineering_practice cho cách chọn cấu trúc model. Cheat Sheet mang nhãn 2021.01; backend/experimental/API mới cần đối chiếu build đích. Local source/profile có thể dùng số đơn vị theo contract task; đổi tỷ lệ chỉ sau xác nhận đơn vị.

<a id="s02"></a>
## S02 — OpenSCAD CLI và build

Nguồn: [OpenSCAD downloads](https://openscad.org/downloads.html), [source chính thức](https://github.com/openscad/openscad).

Claim đối chiếu trực tiếp local: help của OpenSCAD 2026.09.29 có -o, -D, -p/-P, --version, --backend CGAL/Manifold, --enable=textmetrics và --help-export. Đây là observation của binary đã thử; availability ở build khác được xác nhận bằng --help của build đó. Phiên bản, backend, flags và preset thuộc manifest từng run.

Nhãn: official_reference cho nguồn phát hành; project_observation cho help/version local trong [VALIDATION](VALIDATION.md). Bộ tài liệu tự chứa không phân phối binary OpenSCAD.

<a id="s03"></a>
## S03 — Trimesh: chất lượng mesh, section và proximity

Nguồn: [Trimesh API](https://trimesh.org/trimesh.html), [section](https://trimesh.org/section.html), [proximity](https://trimesh.org/trimesh.proximity.html), [sampling](https://trimesh.org/trimesh.sample.html), [repair](https://trimesh.org/trimesh.repair.html).

Claim: is_watertight kiểm tra hai mặt trên mỗi cạnh; is_volume bổ sung winding nhất quán/hướng ra ngoài. Các check này được báo riêng với tự giao hình học. closest_point trả điểm trên tam giác gần nhất; signed distance dương trong/âm ngoài và dương ở vùng tol.merge. sample_surface hỗ trợ seed; thống kê mẫu chỉ xác nhận bộ điểm đã lấy. Section có phép chuyển hệ 3D/2D.

Nhãn: official_reference. Trang nguồn đọc có version 5.1.1; API/dependency được đối chiếu với version đã cài. Cực đại quan sát không tạo bảo đảm toàn bề mặt.

<a id="s04"></a>
## S04 — CGAL: tự giao và khoảng cách

Nguồn: [Polygon Mesh Processing](https://doc.cgal.org/latest/Polygon_mesh_processing/), [Distance Functions](https://doc.cgal.org/latest/Polygon_mesh_processing/group__PMP__distance__grp.html).

Claim: does_self_intersect là phép kiểm tra tự giao riêng. Hausdorff đối xứng lấy cực đại của hai hướng. bounded_error_Hausdorff_distance và bounded_error_symmetric_Hausdorff_distance có error_bound; approximate sampling và bounded-error có mức bảo đảm riêng.

Nhãn: official_reference. Trang latest đọc mang version 6.2.1. Record input preconditions, method, đơn vị và cận khi dùng; engineering_practice chọn tolerance theo chức năng của task.

<a id="s05"></a>
## S05 — Fusion Design API units

Nguồn: [Understanding Units](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/Units_UM.htm).

Claim: Design API dùng cm/radian và cm³ cho các đại lượng tương ứng; expressions có đơn vị được quản lý bởi UnitsManager. Engineering derivation: cm → mm nhân 10; cm³ → mm³ nhân 1000.

Nhãn: official_reference cho units, engineering_practice cho tổ chức chuyển đổi ở I/O. Đọc unit contract của symbol/product cụ thể trước khi mở rộng sang API khác.

<a id="s06"></a>
## S06 — Design, component, occurrence và proxy

Nguồn: [Design Intent](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/DesignIntent_UM.htm), [Components/Proxies](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/ComponentsProxies_UM.htm), [BRepFace.nativeObject](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/fusion_BRepFace_nativeObject.htm).

Claim: design có loại Part/Assembly/Hybrid; component giữ hình học, occurrence biểu diễn instance/context. Proxy xác định đường occurrence; nativeObject/assemblyContext được đọc theo trạng thái native/proxy. nativeObject có thể null với native entity.

Nhãn: official_reference. DesignIntent và proxy support phụ thuộc symbol/version; check document type và API đích. Engineering_practice: giữ ownership và selection rule tường minh, kiểm tra ambiguity.

<a id="s07"></a>
## S07 — Sketch, text, compute và identity

Nguồn: [isFullyConstrained](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/fusion_Sketch_isFullyConstrained.htm), [SketchText.explode](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/fusion_SketchText_explode.htm), [isComputeDeferred](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/fusion_Sketch_isComputeDeferred.htm), [entityToken](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/fusion_BRepFace_entityToken.htm).

Claim: fully constrained là trạng thái boolean của sketch; explode tạo curve và xóa SketchText gốc. Compute deferred có lưu ý với sketch đã có feature phụ thuộc; phục hồi/timeline phải theo nguồn và tình trạng document. Token string có thể đổi, identity được kiểm tra trên entity resolve, không qua so chuỗi token.

Nhãn: official_reference. Recipe datum/constraint/font và thứ tự xây cụ thể là engineering_practice hoặc observation, có probe native riêng.

<a id="s08"></a>
## S08 — Mesh → solid/surface trong Fusion

Nguồn: [Convert Mesh](https://help.autodesk.com/cloudhelp/ENU/Fusion-Mesh/files/MESH-CONVERT-TO-SOLID.htm).

Claim: Faceted, Prismatic và Organic là các phương pháp khác nhau. Prismatic nhóm mặt theo feature; Organic phục vụ hình hữu cơ/scan và thuộc Fusion Design Extension. Mesh kín chuyển thành solid, mesh hở có thể thành surface; Stitch/Patch thuộc workflow surface.

Nhãn: official_reference. Kiểm tra capability/entitlement và chất lượng dữ liệu trên host đích. Chuyển mesh không tự khôi phục lịch sử thiết kế gốc; yêu cầu parametric intent cần contract riêng.

<a id="s09"></a>
## S09 — Fusion MCP và version của protocol

Nguồn: [Autodesk Fusion MCP overview](https://help.autodesk.com/view/fusion360/ENU/?guid=FMCP-OVERVIEW), [MCP transports 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25/basic/transports).

Claim: Fusion local MCP cần Fusion desktop đang chạy, bật server và HTTP client; toolset được discover và có thể đổi. Session/Accept/lifecycle được lấy từ revision server thực dùng. Nguồn protocol 2025-11-25 mô tả Streamable HTTP có JSON/SSE và session header theo điều kiện; các revision khác cần đọc đúng specification.

Nhãn: official_reference. Adapter persistent/JSON-only/version cụ thể của một project là project_observation, không đại diện mọi server/revision.

<a id="s10"></a>
## S10 — Parameter và expression Fusion

Nguồn: [UserParameter](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/fusion_UserParameter.htm), [isValidExpression](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/core_UnitsManager_isValidExpression.htm), [Parameters expressions](https://help.autodesk.com/cloudhelp/ENU/Fusion-Model/files/GUID-76272551-3275-46C4-AE4D-10D58B408C20.htm).

Claim: UserParameter có expression/unit; UnitsManager kiểm tra expression với units. Cú pháp và hàm expression lấy từ reference đích. Việc dimension hoặc topology nào cập nhật được được xác minh bằng native recompute/rebuild của task.

Nhãn: official_reference cho API; engineering_practice cho dependency order và parameter matrix.

<a id="s11"></a>
## S11 — Feature theo quy luật hình học

Nguồn: [Fusion solid features from sketches](https://help.autodesk.com/cloudhelp/ENU/Fusion-Model/files/SLD-CREATE-SOLID-FROM-SKETCH.htm), [Fusion API User Manual](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/UserManualIndex_UM.htm).

Claim: Extrude/Revolve/Sweep/Loft biểu diễn các quy luật tạo hình khác nhau; chọn input/extent/operation theo feature cụ thể. Registry này dẫn mục tổng quan; từng task thêm trang API đúng symbol/chữ ký đang gọi.

Nhãn: official_reference cho công cụ; engineering_practice cho đánh giá geometry/editability/cost. Không có thứ tự feature tối ưu chung cho mọi hình dạng.
