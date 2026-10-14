# Mẫu giao việc SCAD → Fusion Python

Dùng mẫu này để yêu cầu chuyển đổi hoặc dựng model native bằng Fusion Python. Điền các trường cần thiết; bỏ mục không thuộc phạm vi. Task ghi rõ đầu vào, đích sử dụng, tiêu chí, output và cấp kiểm chứng.

## Mục tiêu và phạm vi

- Mục tiêu: `[chuyển đổi / đồng bộ / thiết kế native mới / chỉnh sửa model hiện có]`
- Đích sử dụng: `[chỉnh sửa tham số / BRep trực tiếp / xuất mesh / lắp ráp / mục tiêu khác]`
- Phạm vi part/component: `[danh sách và ownership]`
- Đặc trưng phải giữ: `[hình học, quan hệ, chức năng, dung sai]`
- Ngoài phạm vi: `[mục chưa yêu cầu]`
- Mức bám nguồn: `[đo trực tiếp / suy ra / xấp xỉ, theo vùng]`

## Input và nguồn sự thật

- SCAD/source: `[đường dẫn hoặc none]`
- CAD/mesh/reference: `[đường dẫn và vai trò]`
- README, manifest, checkpoint liên quan: `[đường dẫn]`
- Phiên bản/hash đã chốt: `[giá trị hoặc cần ghi khi bắt đầu]`
- Quyền dùng/thay đổi input: `[đọc / sửa trong phạm vi / snapshot bắt buộc]`
- Đường chuyển đổi mong muốn: `[SCAD → native / mesh → BRep trực tiếp / mesh làm căn cứ dựng native / giữ mesh]`
- Lý do cần dựng lại tham số hoặc dùng Convert Mesh: `[giải thích ngắn]`

## Contract hình học và tham số

| Tên | Ý nghĩa | Đơn vị | Giá trị/miền | Expression/phụ thuộc | Nguồn hoặc tiêu chí |
|---|---|---|---|---|---|
| `[name]` | `[meaning]` | `[unit]` | `[baseline; min..max]` | `[formula or none]` | `[source/criterion]` |

- Hệ tọa độ: `[gốc, trục, chiều dương, handedness]`
- Transform/datum: `[quy tắc căn chỉnh và điểm kiểm tra]`
- Hình học/quan hệ bất biến: `[criteria]`
- Tolerance/độ chính xác: `[value, unit, measurement basis]`
- Input liên tục cần recompute: `[list]`
- Input đổi topology cần rebuild: `[list]`
- Giới hạn sản phẩm, máy hoặc vận hành được yêu cầu: `[chỉ khai báo khi áp dụng]`

## Thiết kế Fusion native

- Đơn vị API, đơn vị hiển thị và cách quy đổi: `[contract]`
- Component/body/occurrence ownership: `[mapping]`
- Sketch plane, reference, constraints và datum: `[requirements]`
- Phương pháp cần đánh giá theo vùng: `[Extrude / Revolve / Sweep / Loft / Convert Mesh / other]`
- Tiêu chí lựa chọn feature: `[accuracy, editability, robustness, geometry]`
- Selection rule: `[geometry/relationship criteria; ambiguity behavior]`
- User Parameters/expressions: `[list and dependency]`
- Topology choices tạo lúc Run: `[list]`
- Quy tắc tên feature/body/component: `[convention]`

## Pipeline, output và cổng kiểm tra

- Runtime Fusion/API cần có: `[version/capability]`
- Document test: `[new/isolated document procedure]`
- Ma trận: `[baseline, continuous boundaries, combinations, topology rebuild]`
- Health/recompute checks: `[solver, profiles, healthState, bodies, invariants]`
- Restore cuối: `[expressions/values to restore; recompute and verify]`
- Output: `[native source/document, STEP/STL/other, manifest, reports]`
- Export contract: `[selected geometry, units, mesh settings, destination]`
- Hash/run metadata: `[input/source/output, timestamp, version, parameters]`
- Audit độc lập: `[bounds, volume, sections, surface distance, manifold etc.]`
- Vật lý nếu có: `[sample, material, equipment, procedure, measurements]`

## Bằng chứng và trạng thái

- Offline: `[commands/tests and expected evidence]`
- Fusion native: `[script entrypoint and runtime evidence]`
- Export: `[reader/audit and acceptance criteria]`
- Physical: `[measurement and acceptance criteria]`
- Nếu runtime không có: ghi `offline_only`/`not_run`, nêu môi trường thiếu và kết quả còn chờ.
- Báo cáo riêng source đọc được, test offline, Fusion native, mesh audit và phép thử vật lý.
- Gắn mỗi output/hash với run ID và tham số đã dùng.

## Quyết định và bàn giao

- Các quyết định đã chốt: `[feature strategy, approximations, topology]`
- Câu hỏi/chặn phụ thuộc: `[chỉ mục ảnh hưởng đáng kể]`
- File cần bàn giao: `[editable source, native document, manifest, instructions, reports]`
- Kiểm tra sau bàn giao: `[cách mở/chạy, baseline cần xác nhận]`
- Kết quả chưa xác minh và giới hạn: `[ghi rõ]`
