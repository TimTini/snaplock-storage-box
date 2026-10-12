# Rà soát tài liệu OpenSCAD và Fusion Python

Mốc rà soát là **13/10/2026**. [Tài liệu tự học](fusion-python-tu-hoc.md) tập hợp các bài học về dựng hình, tham số, API và kiểm chứng của năm dự án.

## Phạm vi kỹ thuật

| Dự án | Nội dung đối chiếu |
|---|---|
| [Hộp bàn chải điện](https://github.com/TimTini/electric-toothbrush-case) | Vỏ, lòng, đáy, ren, lỗ thoát nước và MoveFace theo helix |
| [Khay bông tắm](https://github.com/TimTini/bath-sponge-tray) | Kích thước khay, lưới lỗ, tai/móc và công thức vị trí |
| [Thời khóa biểu](https://github.com/TimTini/thoi-khoa-bieu-openscad) | Layout theo dữ liệu, chữ, cung native, offset và màu 3MF |
| [Thùng rác bốn góc](https://github.com/TimTini/thung-rac-4-goc) | V4, đường đưa chốt, thể tích quét và feature native |
| [Snaplock](../README.md) | Tái dựng STL, audit SCAD, bốn body, Pattern, Mirror và ràng buộc sketch |

Các căn cứ gồm source, README, test, báo cáo đo và log của các phiên bản tương ứng. Kết quả offline, native, slicer và mẫu in có phạm vi xác nhận riêng.

## Nội dung đã hiệu chỉnh

| Chủ đề | Nội dung sau review |
|---|---|
| Khay bông tắm | Bản hiện tại có 35 lỗ đáy Ø6, lưới 7 × 5, bước 12 mm |
| Hộp bàn chải | Bản hiện tại có 19 lỗ đáy Ø3, lòng thân Ø42,4, lòng nắp Ø48; ren dùng surface helix + Sweep |
| Coil | Bài probe có mục đích khảo sát API; script hộp bàn chải giữ cách dựng Sweep |
| Chữ thời khóa biểu | Source dùng explode → Profiles → Extrude NewBody → Combine Join; outline glyph được tạo lại bằng Run |
| Thùng rác | V4 là tham chiếu hiện tại; đường đưa chốt và trạng thái lắp cuối được kiểm tra riêng |
| Snaplock native | Log thành công gắn source `4cad327e…`; bản sửa thứ tự profile gắn source `e09a8281…` và mốc kiểm chứng offline |
| Sai khác mesh | Boolean đối xứng SCAD và chênh thể tích có dấu Fusion có tên, công thức và phạm vi riêng |
| Timeline | Số lời gọi builder, số dòng log và số object Fusion có cách đếm riêng |
| Ảnh và công bố | Ảnh minh họa, ảnh in thật, draft và published gắn với bằng chứng tương ứng |

## Bằng chứng Snaplock

[Hồ sơ kiểm chứng](validation/README.md) cung cấp báo cáo SCAD mặc định/biến thể, số đo tham chiếu, log native thành công, log chẩn đoán và báo cáo mesh streaming. Các bản công khai giữ số đo cùng hash source, với đường dẫn máy local được lược bỏ.

Source Python bản sửa thứ tự profile có SHA256 `e09a82813f0831d98fec28d0dcf609ff71ad05832a74064c11d83f16cc5cf2f2`. Source SCAD có SHA256 `905322f5338d6685ad3f4358f270e81659eed66be9e8c7b49aab171c05a9fba1`.

Bộ test offline Snaplock đạt 28/28 ngày 13/10/2026. Lần chạy native của bản sửa thứ tự profile, phép đo sai khác đối xứng Fusion và thử lắp/in là các mốc xác nhận tiếp theo.
