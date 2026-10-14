# Cẩm nang chung cho công việc STL, OpenSCAD và Fusion

Đọc [START-HERE](START-HERE.md) khi bắt đầu. Quy trình này là **engineering practice**: tổ chức công việc và bằng chứng, được điều chỉnh theo đầu vào, mục tiêu và capability. Các sự kiện API có nguồn Sxx trong [sources](sources.md); kết quả của một model thuộc hồ sơ model đó.

## Chọn route theo sản phẩm cần bàn giao

1. **Chỉ khảo sát STL:** bảo toàn input → xác nhận đơn vị → kiểm tra chất lượng → đo/section → báo cáo. Mục tiêu kết thúc ở thông tin, không phát sinh mô hình thay thế.
2. **Tái dựng tham số:** input → suy quy luật có số đo → dựng SCAD → render/đối chiếu → kiểm tra biến thể → chốt baseline.
3. **SCAD → Fusion native:** baseline đã chốt → map feature/parameter → dựng native → recompute/health → xuất và đối chiếu.
4. **Chỉnh mesh trực tiếp:** khảo sát mesh → đánh giá Mesh tools/Convert Mesh → kiểm tra kết quả solid/surface và khả năng sửa. Faceted, Prismatic và Organic phục vụ loại hình khác nhau; Organic cần entitlement tương ứng [S08](sources.md).
5. **Thiết kế mới:** bảng yêu cầu và số đo được duyệt → chọn SCAD/Fusion phù hợp đầu ra → biến thể/kiểm chứng. Yêu cầu thiết kế là căn cứ; STL tham khảo giữ đúng vai trò đã giao.

Route có thể kết hợp hoặc dừng ở một giai đoạn. Tính editability được đánh giá bằng tham số thực sự sửa được và khả năng recompute, riêng với hình dạng bám mẫu.

## Bảo toàn và hiểu hình học

Lưu input/hash/giấy phép, đơn vị có căn cứ, hệ trục và phép biến đổi. Phân biệt connected component với part chức năng, layout in với vị trí assembly. Dùng bounds, section, mặt cong, lỗ, bề dày và quan hệ lắp để mô tả đặc trưng.

Với mesh hở hoặc tự giao, phân loại mục tiêu surface/solid và lỗi dữ liệu trước khi dùng thể tích hay boolean. Sửa bản làm việc với tiêu chí và báo cáo trước/sau; snapshot gốc giữ nguyên. Mesh scan/freeform có thể cần fit mặt, approximation hoặc workflow mesh; ghi phần suy đoán và giới hạn đo.

## Dựng OpenSCAD bằng quan hệ

Chia module theo chức năng. Tham số gốc biểu diễn lựa chọn thiết kế; derived formula giữ quan hệ như bề dày, trục đối xứng, pitch và vị trí theo kích thước chung. Ghi miền hợp lệ bằng assert.

Chọn primitive, profile/extrusion, phép xoay, boolean, loop và mirror theo hình học [S01](sources.md). Thứ tự union/difference ảnh hưởng các vùng giao; kiểm tra bằng section. hull tạo bao lồi; việc ghép section bằng hull có cách nội suy riêng, cần đo mặt trung gian khi dùng thay cho một mặt CAD.

Chọn độ phân mịn theo sai số hình học và thời gian render. Epsilon phục vụ ổn định tính toán, clearance phục vụ chức năng lắp, allowance phục vụ chế tạo; mỗi loại có căn cứ và phép thử riêng.

## Chọn feature Fusion theo ý đồ

Extrude cho profile dịch theo phương phù hợp, Revolve cho quy luật tròn xoay, Sweep cho profile theo path, Loft cho chuyển tiếp qua section. Fillet/Chamfer, Pattern/Mirror và surface tools được chọn theo quan hệ hình học [S11](sources.md).

So sánh phương pháp trên cùng vùng và tolerance: độ bám hình, số đầu vào độc lập, độ ổn định tham số, ownership, số feature phụ và thời gian native. Số section ít hay nhiều là quyết định đo được; Loft nhiều section có thể là phương án phù hợp cho mặt biến đổi. Dung sai thuộc nhiệm vụ.

Native parameters và expressions giữ quan hệ trong tài liệu Fusion. Dimension/offset/count được liên kết theo contract; lựa chọn tạo topology lúc Run có hướng dẫn rebuild riêng. Đọc frame thực của sketch và assembly context của entity; API Design dùng cm/radian [S05, S06](sources.md).

## Kiểm chứng theo từng lớp

- **Source:** công thức, ownership, entrypoint, input contract và nhãn API.
- **Offline:** logic/regression/mock; đo mesh hoặc CSG nếu công cụ và dữ liệu đủ.
- **Native:** solver, feature health, BRep, constraints, recompute và API trên build được ghi.
- **Export:** đơn vị, hash, tessellation, solid/surface, fidelity và assembly của file xuất.
- **Slicer/chế tạo:** orientation, envelope hữu dụng, margin, vật liệu và điều kiện gia công/in.
- **Physical:** kích thước thực, fit, tải, lực, độ bền theo yêu cầu.

Mỗi lớp có passed/failed/blocked/not_run/not_applicable cùng lý do. Số lượng test và trạng thái skip được báo rõ. Một lớp đạt xác nhận phạm vi của lớp đó.

Độ bám mẫu cần nhiều phép đo bổ sung: bounds, chênh thể tích có dấu, boolean thừa/thiếu, section và khoảng cách hai chiều. Cực đại lấy mẫu là cực đại quan sát; Hausdorff có cận sai số cần thuật toán và error_bound [S03, S04](sources.md). Ngưỡng riêng được đặt cho vùng chức năng.

## Layout, chữ, màu và tài nguyên ngoài

Layout theo dữ liệu có biến thể hàng/cột/số lượng và kiểm tra bounds, khoảng cách, trùng lặp. Font, glyph tiếng Việt, version và license thuộc manifest; font có sẵn trên máy trước là bằng chứng của máy đó.

SketchText và glyph sau explode có contract khác; đổi text sau khi tạo curve cần workflow tái tạo hoặc script quản lý tương ứng [S07](sources.md). Với OpenSCAD, kiểm tra feature/cờ experimental bằng phiên bản thực, ví dụ textmetrics.

3MF/màu có ba bước xác nhận riêng: exporter tạo mesh/object/color data; ứng dụng nhận diễn giải dữ liệu; slicer gán vật liệu/filament. Ghi tool/version/cấu hình cho từng bước. Ảnh minh họa dùng CAD/preview làm căn cứ hình dạng và được gắn nhãn minh họa.

## Tự học và tiếp tục công việc

Ghi tri thức theo **hiện tượng → bằng chứng → nguyên nhân xác định hoặc giả thuyết → thay đổi → kiểm chứng → điều kiện áp dụng**. Nguồn tài liệu, engineering practice, project observation và proposed exercise có nhãn riêng.

Một recipe chỉ được nâng thành quy trình đã kiểm chứng khi có phép thử đạt, source/hash và môi trường. Ghi hướng thất bại thực sự đã thử; phần chưa xác nhận giữ nhãn. Cập nhật mục liên quan thay vì nhân bản tri thức giữa runbook và guide.

Handoff dùng [templates](templates.md), lỗi dùng [cookbook](error-cookbook.md), thay đổi kích thước dùng [parameter validation](parameter-change-validation.md). Agent sau đối chiếu checkpoint với source hiện tại rồi tiếp tục phần còn lại. Các hồ sơ dự án lưu riêng, ví dụ [Snaplock documentation](https://github.com/TimTini/snaplock-storage-box/tree/main/docs).
