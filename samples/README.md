# Mẫu in SCAD và Fusion

Mỗi mẫu SCAD chứa preset và STL cùng source, kèm hash trong `audit.json`. Mẫu Fusion minimum chứa STL native, manifest và audit đối chiếu SCAD cùng tham số. Nắp và latch được ghép theo cùng chiều cao nắp. Mỗi hộp dùng một thân, một nắp và hai latch.

| Bộ mẫu | Mục đích |
|---|---|
| [fusion-minimum](fusion-minimum/README.md) | STL native Fusion 0.6.2: thân 107,9 × 30,1 × 30,2 mm, nắp 11,7 mm và hai latch |
| [minimum](minimum/README.md) | Thân 107,9 × 30,1 × 30,2 mm, nắp 11,7 mm, latch ngắn tương ứng |
| [minimum-lid15](minimum-lid15/README.md) | Nắp 15 mm và latch baseline; dùng thân của minimum |
| [reinforced-240x220](reinforced-240x220/README.md) | Gân baseline: độ nhô 3 mm, chân 12 mm, chừa đầu 20 mm |
| [reinforced-240x220-enhanced](reinforced-240x220-enhanced/README.md) | Gân độ nhô 5 mm, chân 20 mm, chừa đầu 5 mm |

STL dùng đơn vị mm, tỷ lệ 100%. Từng chi tiết được xếp theo envelope riêng trong slicer; layout là bản bố trí tham khảo. [Hồ sơ cập nhật latch](../docs/geometry/latch-parametric-fix.md) ghi kết quả assembly; bước tiếp theo là in mẫu để đo độ khít và lực khóa thực tế.
