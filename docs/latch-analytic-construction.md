# Răng khóa bằng cung R5 và elip — checkpoint thử nghiệm

Phiên bản Fusion Python 0.3.0 thay 25 tiết diện XY của răng khóa bằng bốn tiết diện XZ, một Extrude trụ R5, hai Loft chuyển tiếp ngắn và một envelope giới hạn khối. Phần khe đàn hồi giữ 25 tiết diện đã mô tả theo công thức cũ. Bản SCAD giữ vai trò baseline đối chiếu.

## Quy luật hình học

Gọi `t = latch_thickness`, `u = z - t/2` và `d = 5 - sqrt(25-u²)`. Biên đầu răng `x = 0.5+d` là nhánh trái của đường tròn tâm `(5.5,t/2)`, R5 trong XZ. Biên vai `x = 1.5+1.35*d` là nhánh trái của elip tâm `(8.25,t/2)`, bán trục X=6.75 và Z=5 mm.

Tiết diện vai nằm tại Y=17.0724 và 23.0724 mm. Tiết diện R5 nằm tại Y=18.0724 và 22.0724 mm. Đoạn giữa dùng Extrude dài 4 mm. Hai đoạn chuyển tiếp dài 1 mm dùng hai Loft với hai profile mỗi Loft. Các khối được Join, Intersect với envelope X=[-2,3.5], Y=[17.0724,23.0724], Z=[0,t], rồi Mirror body qua X=14 và Join vào tấm khóa.

Các tâm cung/elip dùng biểu thức `latch_thickness / 2`; chiều cao envelope dùng `latch_thickness`. Sketch giữ dimension của tâm, bán kính và bán trục. Hệ trục sketch được ánh xạ bằng `xDirection` và `yDirection` thực tế. Kiểm tra runtime xác nhận normal của Origin XZ hướng -Y trước khi dùng offset âm.

## Số lượng theo source

| Phần răng, gồm mirror/join | Bản 25 tiết diện | Bản phân tích |
|---|---:|---:|
| Construction plane tạo thêm | 25 | 4 |
| Sketch | 25 | 5 |
| Modeling feature | 2 | 8 |
| Tổng mục theo luồng source | 52 | 17 |

Bản phân tích giảm 35 mục trong phần này theo luồng source. `BUILD_METRICS` trong log native ghi `build_seconds_including_logging`, số plane, sketch và timeline thực tế. Đồng hồ bao trùm `build()` cùng ghi log/UI trong bước dựng. So sánh thời gian dùng cùng phạm vi đo ở cả hai phiên bản. Thời gian chạy và số đếm của Fusion được xác nhận ở checkpoint native.

## Bằng chứng offline

Chạy tại repo với dependency trong `requirements.txt`:

```powershell
python -m unittest discover -s tests -v
python audit-latch-analytic.py
```

Checkpoint offline gồm 30 test: contract body, constraint diagnostic, hệ trục XY/YZ/XZ, công thức, xuất STL và phát hiện tiết diện có tâm theo chiều dày bị cũ. Mesh audit dựng răng cũ bằng 25 tiết diện và biên dạng phân tích bằng 481 tiết diện, rồi đo boolean và sai lệch biên lấy mẫu.

| Độ dày mm | Sai lệch biên tối đa với mẫu tuyến tính mm | Sai khác đối xứng theo thể tích riêng một răng |
|---:|---:|---:|
| 5 | 0.002167 | 0.044284% |
| 6 | 0.003855 | 0.070605% |
| 6.5 | 0.005178 | 0.088377% |

Hai phương trình cung/elip khớp công thức tiết diện cũ trong sai số số học dưới 1e-10 mm. Mesh audit dùng ngưỡng biên lấy mẫu 0.01 mm. [Báo cáo JSON](validation/latch-analytic-offline.json) ghi phạm vi là biên dạng lý thuyết offline. Phép đo này đánh giá quy luật mong muốn; cách nội suy giữa elip và tròn của Fusion được đánh giá bằng STL native riêng.

## Checkpoint native tiếp theo

1. Run script `fusion/SnaplockStorageBox` trong Fusion theo hướng dẫn README.
2. Đọc `last-run.log`: hash source hiện tại, `BUILD_METRICS`, các bước tạo răng, bốn tiết diện XZ, bốn body và các biến thể.
3. Các biến thể gồm kích thước hộp, khe hở, độ dày khóa 5 mm và 6.5 mm; script phục hồi công thức gốc sau kiểm tra.
4. Lưu document để quan sát hai đoạn Loft, ellipse constraints và răng sau Intersect/Mirror/Join.
5. Dùng thư mục export vừa được log chỉ ra để chạy:

```powershell
python audit-fusion.py 'fusion/SnaplockStorageBox/exports/<timestamp>'
```

Audit native đối chiếu bốn body với STL gốc và SCAD bằng hash, bounds và boolean thừa/thiếu. Các mặt cắt tại hai đoạn chuyển tiếp cung cấp bằng chứng bổ sung về cách Loft nội suy. Checkpoint native đạt và phép đo thời gian cung cấp cơ sở chốt phương pháp cho model này.

## Hướng ưu tiên cho trường hợp tương tự

Agent nhận diện đường thẳng, cung tròn, elip và mặt tròn xoay trước khi chọn nhiều tiết diện Loft. Extrude/Cut, Revolve và các primitive native biểu diễn trực tiếp vùng có quy luật tương ứng. Loft ít tiết diện phục vụ các đoạn chuyển tiếp; số tiết diện được chọn theo phép đo hình học. Agent giữ baseline và công thức, đo sai khác cục bộ, chạy biến thể, ghi số feature cùng thời gian trước/sau rồi chốt phương pháp theo bằng chứng.

Checkpoint hiện tại của răng Snaplock là source, review API, unit và mesh offline; checkpoint Fusion runtime tiếp nối các bước trên.

## Tài liệu API

- [SketchEllipses.add](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/fusion_SketchEllipses_add.htm).
- [SketchEllipse.majorAxisLine](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/fusion_SketchEllipse.htm).
- [LoftFeatureInput](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/fusion_LoftFeatureInput.htm).
