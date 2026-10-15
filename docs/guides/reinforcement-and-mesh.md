# Gia cường, ownership bề mặt và kiểm chứng mesh

Phạm vi: chỉnh đáy, bo đáy–thành, vành hoặc gân của model tham số; chẩn đoán mesh lỗi sau Boolean. Quy trình chung mang nhãn **engineering_practice**. Case dustpan cuối tài liệu mang nhãn **project_observation** với ngày, môi trường và giới hạn riêng. Dùng [template](templates.md#ghi-lỗi-và-bài-học) để ghi knowledge_state cho task mới.

## 1. Chốt chức năng và điều kiện so sánh

Ghi vật chứa, thao tác sử dụng, mặt tựa, vị trí cầm, hướng lực và đường truyền lực. Tách ca đẩy khi vật tựa sàn khỏi ca nhấc vật có tải. Chốt vùng cần giữ: mép tiếp xúc, lối quét, dung tích hữu dụng, mặt dưới, khoảng lắp và envelope. Lấy kích thước gân/bo từ mục tiêu cụ thể và phép kiểm tra tương ứng.

Ghi riêng mục tiêu giảm độ võng, tải phá hỏng và tuổi thọ lặp; giữ điều kiện vật liệu, hướng lớp và thông số in nhất quán khi so sánh. Tỷ lệ tăng thể tích hình học ghi rõ representation: thể tích mesh export là xấp xỉ từ tessellation, thể tích solid lấy từ CAD kernel tương ứng. Khối lượng nhựa theo đường in lấy từ slicer; hiệu quả chịu tải lấy từ phân tích hoặc thử tải có điều kiện xác định. Áp dụng tài liệu thiết kế theo đúng công nghệ: tỷ lệ gân phục vụ co ngót ép phun giữ phạm vi ép phun, còn FDM cần xét lớp in và hướng tải.

## 2. Dựng chuyển tiếp và giao quyền sở hữu bề mặt

Khi nâng đáy, dựng cao độ đáy và bo đáy–thành theo cùng hàm chuyển tiếp. Với đoạn cần nối êm hai đầu, có thể dùng `s(t)=6*t^5-15*t^4+10*t^3`, `t` chặn vào [0,1]. Đạo hàm bậc một và hai tại hai đầu bằng 0; độ mịn mesh phụ thuộc số đoạn. Chọn miền chuyển tiếp và lấy mẫu cả trước, trong, sau overlap.

Khi Boolean sinh sliver hoặc mặt diện tích 0, cô lập feature mới và tổ hợp với thân để tìm giao tuyến đầu tiên sai. Ghi backend, định dạng export, winding, tọa độ cung và tiếp tuyến. Với mặt cong gần trùng, chọn một builder sở hữu mặt ngoài; dựng thành và phần gia cường bằng profile chung khi phù hợp. Các phần đắp bên trong kết thúc trong vật liệu thân, giữ mặt ngoài cho builder đã chọn. Đo lại bề dày và mặt cắt sau thay đổi ownership.

Với loft, kiểm tra thứ tự đỉnh/mặt và thể tích có dấu. Với các đoạn cung gặp nhau, dùng chung tọa độ tiếp tuyến và quy luật chia cung. Sửa quan hệ tại source rồi export lại; xem các thao tác weld/fill/simplify như một route sửa mesh riêng có hồ sơ thay đổi riêng.

## 3. Chọn phép đo theo vùng hình học

Nạp lại đúng tệp export cuối. Kiểm tra watertight, winding, thể tích dương, số shell và diện tích mặt theo contract. Euler mong đợi lấy từ topology của chi tiết; giá trị 2 trong ví dụ dustpan thuộc solid kín dạng đó. Đánh giá tự giao bằng phép kiểm riêng khi task yêu cầu.

Đặt probe ở hai phía tiếp tuyến, góc cong, seam, overlap và vùng có bề dày nhỏ. Với tam giác gần thẳng hàng làm ray barycentric phát RuntimeWarning, cô lập phép đo và kiểm tra tọa độ thực. Mặt cắt phẳng cùng nội suy đoạn thẳng là một lựa chọn cho phép đo ngang. Giữ warning thành lỗi trong lệnh kiểm tra tương ứng và đối chiếu các giao điểm với giá trị mong đợi. Các ray dọc phù hợp vẫn dùng phép đo đã chọn.

## 4. Chạy ma trận và ca từ chối

Lưu hash input/source/verifier trước khi chạy, đọc Git status/diff và xác định mọi file verifier sẽ ghi. Dùng bản sao cô lập khi output đích đang chứa thay đổi người dùng. Ghi hash output hiện có để đối chiếu sau kiểm tra.

Chọn baseline tắt option, từng option độc lập, tổ hợp sử dụng và cấu hình đổi kích thước. Thêm tương tác giữa đáy/bo và vành/thành, cùng ca nằm ngoài miền hợp lệ. Với ca từ chối, dùng output thử riêng, dọn output thử cũ, thu cả stdout/stderr, xác nhận return code, diagnostics đúng contract và trạng thái output. Ghi trạng thái `rejected_input` riêng với `failed_geometry`.

Chỉ cập nhật artifact bàn giao sau khi toàn bộ acceptance tương ứng đạt. Đối chiếu SHA256 của source, verifier và artifact với report. Gắn mỗi claim với cấu hình đã đo; [ma trận tham số](parameter-change-validation.md) hướng dẫn mở rộng miền có mục tiêu.

## 5. Tách kiểm tra hình học FDM, slicer và vật lý

Với screen mặt dưới, ghi orientation, cách chọn mặt mới, tham chiếu góc, ngưỡng diện tích, vùng sát bàn bị loại và cấu hình áp dụng. Ghi kết quả dưới tên **sàng lọc hình học**. Kiểm tra support/toolpath bằng slicer, máy, nozzle, vật liệu và profile đã chọn. Xác nhận độ bền lớp, độ võng, tải và độ bền lặp bằng các ca thử riêng.

Giữ trạng thái từng lớp: `source`, `mesh_export`, `slicer`, `physical`; ghi `not_run` hoặc `blocked` cùng điều kiện tiếp tục. Giá trị ngưỡng trong ví dụ là acceptance của model đó.

## 6. Case dustpan — bằng chứng ngày 15/10/2026

Nhãn `project_observation`; knowledge_state `verified` cho đối chiếu source/hash/report trong lượt hợp nhất tài liệu. Checkpoint render hình học trước được lưu tại commit `341d9c6` và bài học dự án; lần rà tài liệu này đối chiếu hồ sơ đã lưu. Môi trường checkpoint: Windows, OpenSCAD 2026.09.29, Manifold, ASCII STL; dependency audit được pin trong project.

- Chuyển tiếp đáy và hai bo R5 dùng chung quintic. Winding loft được sửa tại source sau khi phép đo cô lập cho thể tích âm.
- `outer_body()` dựng thành cùng vành liên tục ở hai góc bằng tọa độ `arc()` gốc. Sweep cộng rời sinh mặt diện tích 0 sau union; đổi chân sweep vẫn còn lỗi. Thử `rotate_extrude` để lại tám cạnh lỗi tại tiếp tuyến ở case này. Loft tọa độ chung và footprint rear pad lùi vào giữa thành đã qua ma trận đã lưu.
- Verifier lưu sáu case baseline/bốn option/tổ hợp và một cấu hình đổi kích thước: bảy mesh kín, một shell, Euler 2. Source verifier kiểm tra thêm winding, thể tích dương và diện tích mặt dương. Probe đo đáy/bo, vành trên/dưới, hai góc và hai phía tiếp tuyến. Ca `depth=100` chỉ bật rim xác nhận assertion yêu cầu góc nằm trên đoạn mép ngang.
- Screen FDM áp dụng cho tổ hợp mặc định: góc so với mặt ngang 45°, loại vùng 0,3 mm sát bàn, chọn mặt mới bằng khoảng cách centroid tới baseline lớn hơn 0,02 mm. Diện tích dưới ngưỡng khoảng `8,14e-14 mm²`; ngưỡng assertion trong verifier là `<8 mm²`. Cấu hình đổi kích thước có kiểm tra hình học riêng; phạm vi screen FDM giữ ở tổ hợp mặc định.
- STL mặc định có bounds `206 × 215 × 250 mm`, thể tích mesh export tăng khoảng `7,79490%` so baseline theo `trimesh.volume`. Kiểm tra tự giao độc lập, slicing, bản in và thử tải giữ trạng thái `not_run` trong bằng chứng này.

Định danh hồ sơ để đối chiếu khi có project dustpan:

| Tệp | SHA256 |
|---|---|
| `dustpan.scad` | `9f8a284a37d630a114eb1b5773fc276a5a30d8fef1dacd14db03247d8cb54db2` |
| `work/verify_reinforcement.py` | `1e8e168491d56346592bcf23111a43952f7d4822595e9cb52ff9e9be11a8cc0a` |
| `exports/dustpan-reinforced.stl` | `264fdfeafb70c1867f159f24fed92b74c0215b4343dac95e5d10fdfc4f18c2b0` |
| Baseline all-off `work/reinforcement-original.stl` | `fd42026501483a7fa30aac3e9ce2b63c4e84f86168bfd621c5d80912c9c1a765` |

Hồ sơ project: `work/learnings/reinforcement-geometry.md`, `work/reinforcement-verification.json`, `work/verification.json`, `work/progress.md`. Các locator này phục vụ truy xuất project riêng; bundle chung dùng nội dung case và quy trình ở trên khi đọc độc lập.
