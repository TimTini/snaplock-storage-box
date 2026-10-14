# Template nhiệm vụ, bằng chứng và bàn giao

Các trường trong ngoặc vuông là chỗ điền theo nhiệm vụ. Agent ghi not_applicable/none cùng lý do cho trường ngoài phạm vi; giữ blocked và dữ liệu cần bổ sung cho trường bắt buộc chưa có.

## Chốt nghĩa của editable

Ghi rõ mức cần sửa: mesh trực tiếp; BRep/solid/surface thao tác tiếp; hoặc feature tree native với User Parameters/expressions và recompute. Với model scan/freeform, mỗi mức có chi phí và mức xấp xỉ khác nhau. Chốt mức này trước khi chọn route; chuyển mesh thành BRep tự nó xác nhận loại biểu diễn, không xác nhận parametric intent gốc.

## Job specification

    Mục tiêu và sản phẩm: [report / SCAD editable / Fusion native / mesh / assembly / chế tạo]
    Đầu vào: [file tương đối, vai trò, source URL/license, SHA256]
    Căn cứ đơn vị: [đơn vị, số đo/metadata đáng tin, scale]
    Route và lý do: [inspection / STL→SCAD / SCAD→Fusion / mesh-direct / design-new]
    Part và ownership: [part, component, occurrence, quantity]
    Hệ tọa độ: [origin, axes, handedness, alignment, assembly transform]
    Tham số: [name, unit, baseline, valid domain, dependencies]
    Topology: [native-expression updates / Run-time generation / rebuild thresholds]
    Yêu cầu giữ: [feature, shape, usable volume, chức năng, quan hệ]
    Xấp xỉ được phép: [vùng, thuật toán, ngưỡng và căn cứ]
    Kiểm chứng bắt buộc: [source/offline/native/export/slicer/physical]
    Metrics/ngưỡng: [tên, đơn vị, method, threshold, measurement uncertainty]
    Miền chế tạo nếu có: [máy/technology, usable envelope, orientation, allowance]
    Quyền thao tác: [file được sửa, runtime được chạy, publication scope]
    Output: [source, manifest, mesh/native, report, images, runbook]
    Còn thiếu và phụ thuộc: [thông tin/capability, việc bị chặn, điều kiện tiếp tục]

Đọc [mẫu SCAD → Fusion](scad-to-fusion-task.md) cho contract native chi tiết; dùng job specification này cho các route khác.

## Evidence manifest

    run_id, date, task_scope
    source_files: [{path, sha256, commit}]
    inputs: [{path, sha256, role, source_license, units, units_basis}]
    environment: {os, python_audit, packages, openscad_build, backend, fusion_build, fonts}
    route, design_type, component_ownership, transforms
    case_matrix: [{name, parameters, topology_mode, expected_status}]
    checks: [{layer, case, metric, method, unit, threshold, actual, status, evidence_path}]
    outputs: [{path, sha256, part, units, export_settings}]
    approximation_regions, source_claim_ids, unresolved_questions, next_step

Các trường thể hiện schema ghi chép, không phải JSON runtime migration. Project chọn JSON/CSV/Markdown phù hợp và giữ nghĩa của trường. Evidence path trỏ tới file được giữ cùng task hoặc nguồn xác định; local/private assets có cách cung cấp và hash riêng.

Status theo từng check:

- passed: phép kiểm tra đã chạy, actual đạt threshold và evidence tồn tại.
- failed: phép kiểm tra đã chạy, actual hoặc lỗi trái acceptance.
- rejected_input: source từ chối đầu vào ngoài miền như dự kiến; báo expected/actual riêng.
- blocked: thiếu dữ liệu/capability quyết định; ghi điều kiện mở chặn.
- not_run: phép kiểm tra thuộc mục tiêu và chưa thực hiện.
- not_applicable: phép kiểm tra ngoài phạm vi hoặc feature tương ứng vắng; ghi lý do.

Phân biệt nhãn tri thức với status phép thử: official_reference, engineering_practice, project_observation và proposed_exercise được định nghĩa tại [sources](sources.md).

## Ghi lỗi và bài học

    Hiện tượng và trigger:
    Điều kiện áp dụng, input/source/hash, môi trường/ngày:
    Bằng chứng trực tiếp, log/stage/metric:
    Nguyên nhân đã xác định hoặc giả thuyết:
    Hướng đã thử và kết quả thực:
    Thay đổi tại owner của quan hệ:
    Lệnh/phép kiểm chứng, actual và threshold:
    Mức source/offline/native/export/physical:
    Giới hạn và trường hợp cần kiểm tra thêm:
    Tài liệu/recipe liên quan và checkpoint thay thế:

Một quy trình thành công lần đầu vẫn có thể lưu với bằng chứng thật. Bài học được bổ sung vào recipe liên quan sau khi xác định điều kiện áp dụng; lịch sử run giữ dữ liệu riêng.

## Handoff cho agent hoặc máy khác

    Đã đọc: [entrypoint, workflow và source IDs liên quan]
    Đã chốt: [route, units, features, parameters, approximation, tolerances]
    Đã sửa: [file và commit]
    Đã kiểm chứng: [commands, actuals, evidence, version/hash]
    Chưa xác minh: [native/platform/physical cùng lý do]
    Dữ liệu đi cùng: [manifest, hashes, license, private input provisioning]
    Thiết lập lại: [tool versions/lock, executable config, font/library, commands]
    Bước tiếp theo: [thao tác cụ thể, input cần có và acceptance]

Agent tiếp nhận báo lại route, input căn cứ, check và phần thiếu; đối chiếu source/hash hiện tại trước khi thực hiện next step. Tài liệu cũ có checkpoint superseded chỉ tới bản thay thế; lịch sử vẫn giữ ngày/version/evidence của lần đó.
