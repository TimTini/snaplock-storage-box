# Kiểm chứng và evidence của bộ tài liệu

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

## Kết quả release 1.0 — 14/10/2026

- Windows, Windows PowerShell 5.1, Python 3.12.14: validator quét 15 Markdown và 97 liên kết nội bộ, 0 issue.
- Sáu ca regression của CLI đạt, không skip trên host này: bản copy/cwd/Unicode; missing file/required document; absolute/outside path; fragments; code examples/unsafe schemes; external symlink hoặc junction.
- Ca junction tái hiện validator cũ báo sạch dù required file ở ngoài bundle; kiểm tra containment sau resolve làm ca đó bị từ chối đúng. Bộ test dùng symlink khi OS cho phép, Windows junction khi thiếu quyền; môi trường thiếu cả hai khả năng ghi skip rõ.
- Bản copy 17 file vào đường dẫn có khoảng trắng và tiếng Việt, chạy từ cwd ngoài bundle: validator với Python -I -S đạt và sáu regression đạt; SHA256 từng file khớp bản nguồn trước chạy. Đây là bằng chứng trên cùng máy ở đường dẫn khác, chưa phải runtime máy thứ hai.
- Review độc lập kiểm tra core/validator và nguồn API chính; finding containment đã sửa và review lại. Một agent mới chỉ đọc bundle đã lập intake phù hợp cho scan hở, unit chưa rõ và host chưa có Fusion. Đây là acceptance ở mức tài liệu, không phải chạy model.
- Root project có 66 test: 62 đạt, bốn SCAD integration skip vì executable chưa được đặt vào PATH/OPENSCAD của lượt lệnh này. Source CAD/runtime giữ nguyên; các kết quả Fusion trước đây vẫn thuộc hồ sơ project.

Nguồn primary của claim được mở và đối chiếu trong lượt biên soạn, lưu URL/phạm vi/ngày ở [sources](sources.md). OpenSCAD local --version/--help xác nhận build 2026.09.29 và các flags được ghi S02. macOS/Linux, Python khác, Fusion native, slicer và physical giữ phạm vi chưa chạy trong release tài liệu này.

## Phân phối từ Git

Sau khi commit, tại repo chứa docs/guides:

    git archive --format=zip --output=stl-openscad-fusion-guide-v1.0.2.zip HEAD:docs/guides

ZIP chứa nội dung guides ở root, không cần repo chứa model. Giải nén vào thư mục mới và chạy lại validator/tests trước khi chuyển đi. Với bản copy không có Git, nén toàn bộ thư mục sau cùng acceptance; lưu SHA256 và phiên bản tài liệu cùng bản phân phối.

## Hợp nhất bài học dustpan — 1.0.2

Ngày15/10/2026, bổ sung [quy trình gia cường và mesh](reinforcement-and-mesh.md), liên kết từ START-HERE/cẩm nang/ma trận và thêm hai recipe trong sổ lỗi. Nội dung mới ưu tiên câu khẳng định. Case dustpan giữ source/hash và evidence date riêng; lệnh render thuộc checkpoint hình học trước, lượt tài liệu này đối chiếu source, verifier, report và artifact đã lưu. Slicer, bản in, thử tải và kiểm tra tự giao độc lập giữ trạng thái `not_run` của case.

Recheck phát hiện một link case minimum đổi dấu datum trong fusion-mcp-testing trỏ ra ngoài bundle. Link hiện dùng URL công khai của hồ sơ project; bundle có thể sao chép độc lập.

Kiểm chứng trên Windows/Python3.12.14: validator source và bản copy có đường dẫn tiếng Việt/khoảng trắng, chạy từ cwd ngoài bundle, đều trả `markdown_files=16`, `local_links=124`, `issues=[]`, exit0. Sáu unit test đạt trên từng bản, zero skipped. Mười tám file trong bản copy khớp SHA256 với source trước chạy. Validator/test source và CAD source giữ nguyên; kết quả này xác nhận cấu trúc tài liệu và regression của validator trên cùng máy.

Đối chiếu local: năm hash source/verifier/STL/baseline/file người dùng khớp report hoặc snapshot tiếp nhận; 29 liên kết file trong tài liệu dustpan và mục lục workspace trỏ tới đích hiện có. Năm tài liệu dustpan/quy trình mới được quét từ phủ định và lỗi replacement character; kết quả0match. Các con số này mô tả lượt rà tài liệu; mức xác nhận runtime giữ ngày/build và scope trong case.

## Record tiếp nhận của agent mới — release 1.0

Nhãn project_observation, knowledge_state verified cho **đọc hiểu tình huống giả định**, ngày 14/10/2026. Record này trích lược report fresh_reader_acceptance và tiêu chí đã chấm trong phiên biên soạn; nó không là kết quả mở/đo STL hoặc native run.

Input: một STL scan hở của vỏ trang trí organic, units chưa xác định, yêu cầu Fusion editable và sai số mm; host có Python/OpenSCAD, chưa có Fusion. Agent chỉ được đọc bundle từ README/START-HERE và các mục liên quan, không được đọc source/history project hoặc chạy CAD.

Actual đã bàn giao:

1. Chọn khảo sát mesh rồi đánh giá mesh-direct hoặc dựng native theo nghĩa editable; SCAD không là bước bắt buộc.
2. Khi có input thật, có thể snapshot/hash, kiểm tra biên hở, component, bounds và hình dạng tương đối; absolute dimensions/tolerance mm giữ blocked tới khi có căn cứ scale.
3. Native giữ blocked/not_run vì thiếu Fusion; volume/boolean cần solid đáng tin và units.
4. Cần thêm input/license/hash, căn cứ units, mức editable, vùng/tolerance/uncertainty và Fusion/entitlement nếu dùng Organic.
5. Handoff giữ intake/manifest, quality/metrics, scope chưa chạy và điều kiện tiếp tục; không báo hoàn tất mục tiêu native.

Criteria đạt: quyết định trên phù hợp facts input, route/failure gates trong [START-HERE](START-HERE.md) và các tình huống B/C/E trong [scenarios](examples/readiness-scenarios.md). Reviewer cũng chỉ ra ambiguity ở tên route STL, status NEEDS_INPUT và nghĩa editable; bản release đã đổi route label, thống nhất blocked và bổ sung định nghĩa editable. Record xác nhận một tình huống, không suy ra mọi agent/model đều tiếp nhận đủ.

## Record review và regression containment — release 1.0

Nhãn project_observation. Review read-only portable_guide_review phát hiện required file qua symlink/junction có thể nằm ngoài bundle dù is_file trả true. Tạo một directory junction trỏ examples ra ngoài bundle trong test fixture: validator trước fix trả exit 0, 0 issues; regression thất bại đúng assertion yêu cầu exit khác 0. Đây là regression_fixture để xác nhận finding, không phải dữ liệu CAD production bị hỏng.

Fix thêm containment sau resolve trước required-file check và đọc Markdown. Review fix xác nhận guard áp dụng cho file symlink và đường qua junction; cleanup bỏ link/junction, giữ đích riêng. Các ca runtime mới được xác nhận bằng lệnh:

    python -m unittest discover -s tests -v

Tên regression liên quan: test_required_document_through_external_symlink_or_junction_fails tại [test source](tests/test_validate_docs.py). Actual ở Windows/Python 3.12.14: sáu test ok, zero skipped; command exit 0. [Validator source](tools/validate-docs.py) là căn cứ fix; platforms thiếu quyền tạo link/junction có skip được báo rõ.

Review tài liệu/API của release lấy mẫu các claim Units/SketchText/Convert Mesh/Trimesh/CGAL/MCP và không ghi blocker nội dung; registry nguồn giữ scope. Record là kết quả review đó, không chứng nhận từng câu hoặc runtime API đã được thực hiện lại.

## Evidence bản ZIP 1.0 và giới hạn

Commit nguồn: 9ff3023375f6a727f58214f674d1cf012e73056b. ZIP từ HEAD:docs/guides có 17 file, 54648 byte, SHA256 bac59e9fdef8b3bfcd18bacefc20f0518a9794b7e6a5cc8cf726e9b887364906. Đây là hash của artifact 1.0 đã lưu, không phải hash của ZIP 1.0.1.

Sau khi giải nén vào đường dẫn có tiếng Việt/khoảng trắng, cwd ngoài bundle, các argv kiểm chứng là:

    python -I -S <bundle>/tools/validate-docs.py
    python -m unittest discover -s <bundle>/tests

Actual: validator JSON markdown_files=15, local_links=97, issues=[]; exit 0. Unit test Ran 6 tests, OK, exit 0. Input path trong argv thay bằng bundle nhận được, không phụ thuộc thư mục riêng trên máy tác giả. Hash/commit và raw output này là evidence cấu trúc bản cũ; command của bản hiện tại được chạy lại khi phát hành.

## Recheck self-learning — 1.0.1

Ngày 14/10/2026, dùng skill self-learning theo yêu cầu người dùng. Đây là review quy trình quản lý tri thức: retrieval, evidence gate, nơi lưu, state và superseded. Mục [tự học](agent-learning.md#tự-học-và-tiếp-tục-công-việc) và [template bài học](templates.md#ghi-lỗi-và-bài-học) là procedure đã cập nhật, không yêu cầu host phải cài skill đó để đọc bundle.

Finding đã xử lý: knowledge_state tách khỏi source label/check status; metadata có prerequisites và lifecycle thay thế; bản này kèm record acceptance/review để đọc offline. Bài học Unicode chỉ nâng hướng Unicode escape đã thử thành verified; UTF-8 pipeline/file giữ đề xuất unverified trong scope evidence 1.0. Snapshot source/environment/claims cũ giữ ngày/build và được đối chiếu lại trước áp dụng.

Kiểm tra lại source và bản copy 17 file trên cùng Windows/Python 3.12.14, đường dẫn có tiếng Việt/khoảng trắng, cwd ngoài bundle: python -I -S tools/validate-docs.py trả markdown_files=15, local_links=114, issues=[] và exit 0; python -m unittest discover -s tests -v chạy 6 ca ok, zero skipped, exit 0. SHA256 từng file bản copy khớp nguồn trước kiểm tra. Validator/test source và CAD source giữ nguyên trong lượt 1.0.1; chỉ Markdown được sửa. Path độc lập đã kiểm tra trên cùng máy; runtime máy thứ hai/macOS/Linux/Fusion/physical vẫn chưa được chạy.
