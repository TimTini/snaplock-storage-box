# Kiểm chứng bản tài liệu 1.0

Mục này ghi evidence phát hành ngày 14/10/2026. Phạm vi là tài liệu, validator và bản copy; CAD runtime có hồ sơ riêng theo từng model.

## Acceptance của bộ chung

- Điểm vào README/START-HERE nêu phần cần đọc, route và handoff acceptance.
- Core links ở trong bundle; nguồn ngoài là URL được dẫn rõ.
- Template lấy units/part/envelope/tolerance/topology từ task mới.
- Claim API có registry Sxx và ngày đối chiếu; engineering practice/observation/exercise có nhãn.
- Input faults, organic/mesh-direct, SCAD-only, offline/native và topology có nhánh riêng.
- Validator/test chạy trên bản copy tại đường dẫn mới, từ cwd khác.

## Kiểm tra cần chạy khi phát hành

    python tools/validate-docs.py
    python -m unittest discover -s tests

JSON của validator báo counts/issues; unit tests kiểm tra lỗi link, containment, fragment và cwd. Kết quả final của release được cập nhật sau verification. URL ngoài, API/native, slicer, physical và hệ điều hành khác được đối chiếu riêng; structural success không chứng nhận các lớp đó.

## Kết quả đã xác nhận — 14/10/2026

- Windows, Windows PowerShell 5.1, Python 3.12.14: validator quét 15 Markdown và 97 liên kết nội bộ, 0 issue.
- Sáu ca regression của CLI đạt, không skip trên host này: bản copy/cwd/Unicode; missing file/required document; absolute/outside path; fragments; code examples/unsafe schemes; external symlink hoặc junction.
- Ca junction tái hiện validator cũ báo sạch dù required file ở ngoài bundle; kiểm tra containment sau resolve làm ca đó bị từ chối đúng. Bộ test dùng symlink khi OS cho phép, Windows junction khi thiếu quyền; môi trường thiếu cả hai khả năng ghi skip rõ.
- Bản copy 17 file vào đường dẫn có khoảng trắng và tiếng Việt, chạy từ cwd ngoài bundle: validator với Python -I -S đạt và sáu regression đạt; SHA256 từng file khớp bản nguồn trước chạy. Đây là bằng chứng trên cùng máy ở đường dẫn khác, chưa phải runtime máy thứ hai.
- Review độc lập kiểm tra core/validator và nguồn API chính; finding containment đã sửa và review lại. Một agent mới chỉ đọc bundle đã lập intake phù hợp cho scan hở, unit chưa rõ và host chưa có Fusion. Đây là acceptance ở mức tài liệu, không phải chạy model.
- Root project có 66 test: 62 đạt, bốn SCAD integration skip vì executable chưa được đặt vào PATH/OPENSCAD của lượt lệnh này. Source CAD/runtime giữ nguyên; các kết quả Fusion trước đây vẫn thuộc hồ sơ project.

Nguồn primary của claim được mở và đối chiếu trong lượt biên soạn, lưu URL/phạm vi/ngày ở [sources](sources.md). OpenSCAD local --version/--help xác nhận build 2026.09.29 và các flags được ghi S02. macOS/Linux, Python khác, Fusion native, slicer và physical giữ phạm vi chưa chạy trong release tài liệu này.

## Phân phối từ Git

Sau khi commit, tại repo chứa docs/guides:

    git archive --format=zip --output=stl-openscad-fusion-guide-v1.0.zip HEAD:docs/guides

ZIP chứa nội dung guides ở root, không cần repo chứa model. Giải nén vào thư mục mới và chạy lại validator/tests trước khi chuyển đi. Với bản copy không có Git, nén toàn bộ thư mục sau cùng acceptance; lưu SHA256 và phiên bản tài liệu cùng bản phân phối.
