# Snaplock Storage Box

Cấu trúc thư mục và vai trò dữ liệu: [docs/STRUCTURE.md](docs/STRUCTURE.md).

[Bộ hướng dẫn chung STL, OpenSCAD và Fusion](https://github.com/TimTini/snaplock-storage-box/blob/e9311687b4653a4055597ba93b595d739734020c/docs/guides/README.md) có [điểm vào cho agent](https://github.com/TimTini/snaplock-storage-box/blob/e9311687b4653a4055597ba93b595d739734020c/docs/guides/START-HERE.md), thiết lập chuyển máy, template và registry nguồn. Thư mục guides dùng độc lập; [hồ sơ ví dụ của project](docs/examples/README.md) giữ dữ liệu Snaplock.

Bản chính của hướng dẫn chung nằm tại `H:/OpenSCAD/docs/guides`, dùng cho mọi dự án STL, OpenSCAD và Fusion. [Bản lưu công khai 1.0.2](https://github.com/TimTini/snaplock-storage-box/tree/e9311687b4653a4055597ba93b595d739734020c/docs/guides) giữ nội dung theo commit trước khi chuyển thư mục.

Mở [snaplock-storage-box.scad](snaplock-storage-box.scad) trong OpenSCAD. Chọn `part = body`, `lid`, `latch` hoặc `layout`; chỉnh kích thước trong Customizer rồi F6 để render. Thân và nắp dùng chung chiều dài, chiều rộng. Ba công tắc `wall_ribs`, `wall_floor_ribs`, `floor_ribs` điều khiển gân trong hộp.

**Bản SCAD ngày 14/10/2026** cập nhật chiều dài latch theo chiều cao nắp, căn tâm tai lắp và bù mặt cầu đa giác của ổ bản lề. [Hồ sơ sửa và kiểm chứng](docs/geometry/latch-parametric-fix.md) ghi công thức, phạm vi và kết quả. Các STL mẫu đã được xuất lại từ source này; mỗi bộ dùng nắp và latch cùng preset.

## Thư mục

| Vị trí | Nội dung |
|---|---|
| `snaplock-storage-box.scad` | Source chính, mở trực tiếp trong OpenSCAD |
| [samples/](samples/README.md) | Preset, STL và ảnh mẫu in |
| [tools/](tools/) | Script audit và tạo ảnh đối chiếu |
| `tests/` | Kiểm thử Python và assembly SCAD |
| [docs/](docs/README.md) | Hướng dẫn, hình học và bằng chứng kiểm chứng |
| [fusion/](fusion/README.md) | Script Fusion chính và các bài thử riêng trong `fusion/tests/` |
| `exports/` | Đầu ra audit; `exports/default/` chứa bản xuất mặc định được lưu Git |
| `reference/`, `work/` | STL tham chiếu và dữ liệu làm việc local |

## Mẫu in

- [Minimum 107,9 × 30,1 × 30,2 mm, nắp 11,7 mm](samples/minimum/README.md).
- [Minimum với nắp 15 mm và latch tương ứng](samples/minimum-lid15/README.md).
- [Hộp 240 × 220 × 100 mm có gân baseline](samples/reinforced-240x220/README.md).
- [Hộp 240 × 220 × 100 mm với gân cao, chân lớn](samples/reinforced-240x220-enhanced/README.md).

Nhập STL ở tỷ lệ 100%, đơn vị mm; dùng hai latch cho mỗi hộp. Khổ 250 mm áp dụng lên kích thước bao từng chi tiết, gồm tai và chốt. Slicer xác định phần chừa brim/support theo máy thực tế.

## Kiểm chứng

Ma trận gồm **112 cấu hình**: **107 bộ lắp đóng đạt ngưỡng giao thể tích 0,01 mm³**, **5 đầu vào được source từ chối đúng giới hạn**. Trong 107 bộ, 104 bộ vừa envelope số học 250³ với phần chừa 0 mm, 3 bộ vượt khổ. Bài thử mở lấy mẫu 48 tư thế với latch đã tháo. Bộ unit test gồm 54 test.

Python dùng [requirements.txt](requirements.txt). OpenSCAD dùng backend Manifold; biến môi trường `OPENSCAD` nhận đường dẫn executable portable. Chạy từ thư mục gốc repo:

```powershell
python -m unittest discover -s tests
python tools/audit-latch-matrix.py --output exports/parametric-assembly
python tools/audit-latch-fit.py
python tools/audit-scad.py
python tools/compare-scad.py
```

Audit đối chiếu STL gốc dùng file local reference/Snaplock_Storage_Boxes_240x120(2).stl, được Git bỏ qua. Cung cấp đúng input có SHA256 73faaa2d438b02038b9f84002202435973a09f92ec2a48315577e0e00baea167 trước khi chạy audit-scad.py, compare-scad.py hoặc audit-fusion.py; clone public giữ các check cần file này ở blocked tới khi có input. Các script đó là adapter riêng của Snaplock. [Hồ sơ ví dụ](docs/examples/README.md) ghi môi trường và ranh giới tái lập; bộ hướng dẫn chung chạy độc lập với STL này. [Báo cáo source hiện tại](docs/validation/scad-current-default.json) tách kiểm tra solid khỏi mục tiêu giống STL lịch sử; sai khác nắp 0,2481% được ghi cùng ngưỡng lịch sử 0,2%.

**Fusion Python 0.6.2 đã chạy native trong Fusion 2705.1.30:** 10 biến thể recompute đạt, bộ STL kín và kiểm tra BRep lắp đóng đạt ở baseline cùng bốn biến thể. [Hồ sơ đồng bộ Fusion](docs/geometry/fusion-parametric-sync.md) ghi kết quả, hiệu chỉnh ngàm 0,001 mm và khác biệt giữa BRep với mesh High. Bước kiểm chứng vật lý tiếp theo là in mẫu để đo độ khít, lực gài và tuổi thọ đàn hồi. [README checkpoint trước](docs/history/README-before-parametric-fix.md) giữ các quyết định và báo cáo lịch sử.


[Bộ minimum Fusion 0.6.2](samples/fusion-minimum/README.md) cung cấp STL native đã audit cho mẫu in thử.
