# Gân trong SCAD → Fusion Python 0.5.0

SCAD tại checkpoint `bd919e1` là baseline đã được người dùng chốt. Fusion 0.5.0 chuyển ba nhóm gân trong lòng hộp sang các feature có tham số: Extrude, Mirror và Rectangular Pattern. Răng khóa, khe đàn hồi, nắp và tai bản lề tiếp tục dùng cấu trúc của bản 0.4.0.

## Chọn cấu hình lúc Run

Ba công tắc đầu [script](../fusion/SnaplockStorageBox/SnaplockStorageBox.py) chọn topology khi tạo document. Giá trị mặc định của cả ba là `False`, đồng bộ với file SCAD chính.

| Công tắc | Hình học |
|---|---|
| `wall_ribs` | Gân đứng trên bốn thành, đầu vát và khoảng chừa phía nắp |
| `wall_floor_ribs` | Chân tam giác nối thành với đáy |
| `floor_ribs` | Lưới gân trên mặt trong đáy |

Mẫu đã chốt 240 × 220 × 100 mm dùng cả ba công tắc `True`. Đặt dòng `BUILD_RIBS` như sau, rồi sửa ba giá trị `length`, `width`, `body_height` trong `DEFAULTS` thành `240.0`, `220.0`, `100.0`.

```python
BUILD_RIBS = {'wall_ribs': True, 'wall_floor_ribs': True, 'floor_ribs': True}
```

Giữ các mục còn lại trong `DEFAULTS`. Chạy **Utilities → Add-Ins → Scripts and Add-Ins → Scripts → SnaplockStorageBox → Run**. Script tạo document mới, kiểm tra biến thể và xuất STL theo cấu hình ban đầu sau khi phục hồi tham số.

Các kích thước gân chỉnh tiếp trong **Modify → Change Parameters**. Công thức native của plane, sketch, Extrude, Mirror và Pattern tham chiếu trực tiếp các tham số này. Việc chọn lại nhóm gân được áp dụng qua `BUILD_RIBS` và lần Run tạo document mới. STL được xuất tại thời điểm Run; thao tác chỉnh document sau đó tạo ra trạng thái mới để xuất lại bằng Fusion.

| Tham số | Mặc định, mm | Ý nghĩa |
|---|---:|---|
| `rib_spacing` | 45 | Khoảng cách mục tiêu để suy ra số trạm gân |
| `rib_thickness` | 2,4 | Bề dày gân |
| `floor_rib_height` | 4 | Chiều cao lưới gân tính từ đáy trong |
| `wall_rib_depth` | 5 | Độ nhô của gân đứng vào lòng hộp |
| `wall_rib_foot` | 20 | Kích thước chân tam giác |
| `wall_rib_top_clearance` | 5 | Khoảng chừa từ đầu gân đến miệng thân |

## Công thức và cấu trúc dựng

Với mỗi phương có chiều dài `span`, công thức dùng `margin = max(corner_radius, wall + rib_thickness/2)`, `count = max(1, ceil((span - 2*margin)/rib_spacing) - 1)` và `step = (span - 2*margin)/(count + 1)`. Trạm đầu ở `margin + step`; Pattern dùng khoảng cách `step` và số lượng `count`. `rib_count_x`, `rib_count_y` là tham số đơn vị rỗng; khoảng cách và tọa độ dùng mm.

Chiều cao gân đứng lấy `body_height - wall_rib_top_clearance`. Độ nhô và chân tam giác được giới hạn theo chiều cao sử dụng và một phần tư bề rộng lòng nhỏ nhất, cùng công thức với SCAD. Mẫu nhỏ tự giảm chân gân và số trạm theo kích thước.

Mỗi nhóm có hai sketch mẫu cho hai phương. Mỗi sketch được Join Extrude vào `Body`; hai nhóm bám thành dùng Mirror tạo thành đối diện, rồi Pattern lặp cặp feature theo trạm. Bật cả ba nhóm tạo sáu sketch mẫu, sáu Join Extrude, bốn Mirror và sáu Pattern. Bốn sketch tam giác trên Origin plane cùng bốn Extrude Cut giới hạn phần dưới theo mặt vát ngoài. Số sketch mẫu giữ cố định khi số trạm tăng; các gân dùng tiết diện thẳng và phép lặp trực tiếp.

Miền dựng native yêu cầu bề dày trạm gân nằm trong đoạn thành thẳng: `first_station - rib_thickness/2 >= corner_radius`. Hàm kiểm tra báo rõ cấu hình chạm vùng góc tròn. Bộ kiểm tra Run và các biến thể xác nhận miền này cùng giới hạn kích thước hiện có.

Pattern khởi tạo với hai instance, sau đó gán biểu thức `quantityOne` về `rib_count_x` hoặc `rib_count_y`. Trường hợp số lượng bằng một được đưa vào biến thể native để kiểm chứng trực tiếp. Log `RIB_BUILD`, `RIB_BUILD_COMPLETE` và `RIB_CHECK` ghi công tắc, số trạm, vị trí và kích thước suy ra.

## Bằng chứng offline và bước xác nhận native

[Báo cáo offline](validation/fusion-reinforcement-offline.json) chứa hash Python, hash SCAD, cấu hình và 24 trường hợp: tám tổ hợp công tắc ở mẫu gốc, mẫu 240 × 220 × 100 mm và mẫu 107,9 × 30,1 × 30,2 mm. Mẫu nhỏ dùng nắp cao 12,5 mm theo miền validation của script Fusion.

Audit đánh giá chính các biểu thức profile, khoảng cách, số lượng, Mirror và bốn wedge trim trong source Fusion bằng CSG offline, rồi so với SCAD cùng đầu vào. Phần gân được trim trước khi hợp với vỏ SCAD độc lập; vỏ SCAD dùng hull có lớp epsilon, còn vỏ Fusion dùng mặt vát lý tưởng. Phép thử này xác nhận hình học gân và công thức; lần Run Fusion cung cấp bằng chứng cho solver sketch, kernel, feature Pattern có Mirror phụ thuộc và cập nhật số lượng bằng một.

24 trường hợp đạt ngưỡng offline bounds <0,005 mm và sai khác thể tích đối xứng <0,2 mm³. Sai khác lớn nhất đo được khoảng 0,087 mm³. Audit ghi riêng số mặt zero-width được loại theo hợp đồng kiểm tra fragment của audit SCAD; các fragment này có diện tích <0,00001 mm² và thể tích tuyệt đối <0,00000001 mm³. Bộ 47 unit test xác nhận công thức, công tắc, hướng plane/sketch, hợp đồng Pattern mô phỏng và manifest export. Smoke test đường đọc manifest dùng bốn STL fixture sinh từ SCAD để kiểm tra công cụ audit.

`VERIFY_VARIANTS = True` kiểm tra các biến thể sẵn có cùng mẫu 240 × 220 × 100 mm, mẫu nhỏ một trạm, và bộ spacing 32 mm / thickness 3 mm / top clearance 8 mm. Script phục hồi toàn bộ tham số ban đầu sau mỗi biến thể. Dòng `NATIVE_BUILD_AND_RECOMPUTE_OK` cùng hash source trong log là bằng chứng lần Run tương ứng.

Manifest export 0.5.0 lưu `parameters_mm`, `reinforcement`, hash source và hash từng STL. Công cụ sau dựng lại SCAD từ chính tham số export để so bốn part:

```powershell
python audit-fusion-ribs.py --native 'fusion/SnaplockStorageBox/exports/<timestamp>' --output 'exports/fusion-rib-native-check'
```

`<timestamp>` lấy từ `last-run.log`. Ngưỡng native là bounds <0,03 mm và sai khác thể tích đối xứng <0,3% cho từng part. Audit bù tịnh tiến về góc nhỏ nhất, giữ tỷ lệ và hướng. Kiểm chứng vị trí lắp, chuyển động, lực chịu tải và mẫu in là các bước riêng.

Lệnh tái lập kiểm chứng offline:

```powershell
python -m unittest discover -s tests -q
python audit-fusion-ribs.py
```

Audit dùng Python có `numpy`, `trimesh`, `manifold3d` và OpenSCAD qua biến môi trường `OPENSCAD`. Script chạy trong Fusion dùng API `adsk` cùng thư viện chuẩn Python.

## Nguồn API

[Tài liệu tham số Autodesk](https://help.autodesk.com/cloudhelp/ENU/Fusion-Model/files/GUID-76272551-3275-46C4-AE4D-10D58B408C20.htm) mô tả `ceil`, `min`, `max` và dấu chấm phẩy phân cách đối số. Biểu thức native dùng `min`/`max` hai đối số và lồng nhau khi cần ba giới hạn.

[RectangularPatternFeatures.createInput](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/fusion_RectangularPatternFeatures_createInput.htm) nhận collection feature để lặp. [RectangularPatternFeature.quantityOne](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/fusion_RectangularPatternFeature_quantityOne.htm) cung cấp ModelParameter cho biểu thức số lượng. [Trao đổi Autodesk về số lượng một](https://forums.autodesk.com/t5/fusion-support-forum/single-quantity-rectangular-pattern-suggestion/m-p/10804362) trình bày cách sửa số lượng qua Parameters; biến thể Run xác nhận hành vi cho phiên bản Fusion đang sử dụng.
