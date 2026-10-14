# Mẫu minimum xuất từ Fusion 0.6.2

Preset: thân 107,9 × 30,1 × 30,2 mm; nắp 11,7 mm. Ba tùy chọn gân giữ giá trị false. Latch dùng chiều dài tương ứng nắp 11,7 mm.

[layout.stl](layout.stl) chứa một thân, một nắp và hai latch. Envelope khoảng 107,90 × 173,73 × 34,45 mm. Các chi tiết giữ mặt đáy Z=0 từ Fusion. Slicer nhận đơn vị mm và tỷ lệ 100%, có thể tách layout thành bốn object để bố trí.

File riêng: [body.stl](body.stl), [lid.stl](lid.stl), [latch.stl](latch.stl). Mỗi hộp dùng một thân, một nắp và **hai bản latch**. [latch-2.stl](latch-2.stl) là latch thứ hai ở vị trí layout tương ứng.

Fusion 2705.1.30 dựng source 0.6.2 và xuất STL bằng preset High. [Manifest](manifest.json) lưu hash. Bản dựng có bốn solid, 40 plane, 57 sketch và 183 timeline item. [Báo cáo native](minimum-native.json) ghi sáu cặp BRep lắp đóng có giao thể tích 0 mm³.

[Audit ngày 14/10/2026](audit.json) đối chiếu với SCAD minimum cùng tham số bằng dịch chuyển góc nhỏ nhất, giữ nguyên tỷ lệ và hướng. Sai khác thể tích đối xứng: thân 0,03940%, nắp 0,03549%, hai latch khoảng 0,05515%. Sai số bounds lớn nhất 0,00917 mm. Mục tiêu audit là bounds dưới 0,03 mm và sai khác thể tích dưới 0,3%. Bốn STL riêng đều là một solid kín; layout có bốn solid kín.

Mẫu in thực tế tiếp tục xác nhận độ khít, lực gài và độ bền đàn hồi. [Ca datum đổi dấu](../../docs/examples/project-error-cases.md#ca-20-giữ-sketch-cùng-phía-datum-khi-biểu-thức-đổi-dấu) ghi lỗi đã sửa trong quá trình xuất mẫu.
