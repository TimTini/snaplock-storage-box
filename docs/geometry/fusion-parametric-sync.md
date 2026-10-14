# Fusion Python 0.6.0 — đồng bộ cơ cấu theo SCAD

[Script chính](../../fusion/SnaplockStorageBox/SnaplockStorageBox.py) cập nhật `latch_span_delta = lid_height - 15 mm`. Blank, răng, channel và ramp cùng bám công thức; đầu cầu gắn nắp giữ vị trí cục bộ. Tai thân và tai nắp dùng chung `mount_end`. Giới hạn nắp thấp nhận mẫu 11,7 mm theo SCAD; giới hạn chiều dài và vị trí tai được căn theo miền source.

Hai cửa sổ khe đàn hồi dùng chung tám sketch tiết diện. Hai tool Loft dùng lại các sketch này; Move tương ứng 15 mm và `lid_height` đặt cửa sổ phía nắp và phía thân. Hai giá trị Move luôn dương trong miền hợp lệ. Clip phía đầu và giới hạn Y=7 mm ở nắp thấp giữ vật liệu đỡ cầu theo SCAD. Các tool được mirror rồi dùng chung một Cut, cuối cùng còn một latch liên thông theo hình học mục tiêu.

Fusion dựng cầu bằng Revolve chính xác và giữ bán kính ổ `pin_radius + fit_clearance`. SCAD dùng `cos^-2` để bù mặt cầu chia lưới; hệ số đó thuộc biểu diễn mesh. [Autodesk Parameters reference](https://help.autodesk.com/cloudhelp/ENU/Fusion-Model/files/GUID-76272551-3275-46C4-AE4D-10D58B408C20.htm) xác định cú pháp `if(condition; true_value; false_value)` và `min/max` dùng trong biểu thức clip.

## Kiểm chứng và Run

Toàn bộ 58 unit test đã đạt. Regression kiểm tra tâm tai, vị trí bốn tiết diện răng theo chiều cao nắp ở cả hai hướng pháp tuyến, dịch profile và midpoint cung, tái sử dụng tám sketch, tiêu thụ bốn tool sau mirror và bounds/formula phụ thuộc. Các test này kiểm chứng source và phép tính offline. [Manifest kiểm chứng offline](../validation/fusion-parametric-sync-offline.json) ghi hash script và SCAD. [Assembly SCAD](latch-parametric-fix.md) giữ bằng chứng hình học của baseline tương ứng.

Trong Fusion, mở **Utilities → Scripts and Add-Ins → Scripts**, thêm thư mục `fusion/SnaplockStorageBox`, chọn `SnaplockStorageBox` và Run. Script tạo document mới và giữ thiết kế đang mở. Thiết kế đã dựng bằng script cũ giữ timeline cũ; Run 0.6.0 tạo timeline dùng công thức mới.

`VERIFY_VARIANTS=True` chạy kiểm tra recompute cho chiều cao nắp 11,7/20/50/233,1 mm, mẫu mini và cấu hình 250 × 232,7 × 245,7 mm, cùng các biến thể có sẵn. Mỗi lượt kiểm tra bốn solid, bounds, fully constrained sketches, vị trí tiết diện răng và timeline healthy. Sau thử, script khôi phục tham số ban đầu rồi xuất STL cùng manifest/hash.

Log runtime nằm ở `fusion/SnaplockStorageBox/last-run.log`; mesh và manifest nằm trong thư mục timestamp thuộc `fusion/SnaplockStorageBox/exports/`. Từ gốc repo, chạy `python tools/audit-fusion.py fusion/SnaplockStorageBox/exports/<timestamp>` để đối chiếu bộ xuất mặc định với SCAD và STL tham chiếu local. Kiểm chứng kernel, topology qua các biến thể và solver native là checkpoint Run tiếp theo; in FDM tiếp tục xác nhận lực gài và độ khít.
