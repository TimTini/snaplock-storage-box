# Môi trường, preflight và chuyển máy

## Bộ tài liệu và môi trường CAD là hai phần riêng

Bộ tài liệu dùng Markdown UTF-8; validator/test đi kèm dùng Python chuẩn, thiết kế cho Python 3.10+. Bản phát hành ghi phiên bản thực đã chạy ở [VALIDATION](VALIDATION.md). Sao chép toàn bộ thư mục guides giữ cấu trúc tương đối; dùng [START-HERE](START-HERE.md) để giao task cho agent mới.

Python audit ngoài ứng dụng và Python/adsk trong Fusion có môi trường riêng. Script adsk chạy trong Fusion theo phiên bản API đích. Thư viện Python hệ thống và virtualenv ngoài Fusion được cài cho các audit ngoài ứng dụng; dependency của từng audit do project đó xác định.

## 1. Kiểm tra cấu trúc từ một thư mục bất kỳ

Trong các lệnh sau, thay đường dẫn minh họa bằng vị trí bộ tài liệu thực tế.

PowerShell:

    python 'C:\CAD Guide\tools\validate-docs.py'
    python 'C:\CAD Guide\tools\validate-docs.py' --root 'C:\CAD Guide'
    python -m unittest discover -s 'C:\CAD Guide\tests'

macOS/Linux shell:

    python3 '/path/to/CAD Guide/tools/validate-docs.py'
    python3 -m unittest discover -s '/path/to/CAD Guide/tests'

Validator mặc định lấy root theo vị trí script, không theo current working directory. Exit 0 nghĩa là các check cấu trúc đã đạt; exit 1 có danh sách issues. Nó kiểm tra required files, mọi Markdown, liên kết file inline, fragment tới heading/HTML id và việc link file nằm trong bộ phân phối. Nó bỏ qua URL ngoài và nội dung fenced code/inline code. Cú pháp hỗ trợ: link/image inline với target không chứa khoảng trắng, hoặc target trong dấu < >; URL-encoded path cũng được giải mã. Reference-style link, HTML link, cú pháp đích có ngoặc lồng và việc xác nhận facts/URL ngoài thuộc review riêng.

Với bản copy, chạy lại validator/tests sau khi giải nén tại đường dẫn có khoảng trắng và từ một cwd khác. Ghi OS/Python, số file/link, exit code và hash ZIP. Windows, macOS và Linux được hướng dẫn về cách gọi; runtime đã thử của release được ghi riêng.

### Bài học pipeline Unicode — scope đã kiểm chứng

Trigger: harness gửi source Python qua stdin từ Windows PowerShell 5.1, source chứa tên đường dẫn có dấu. Lượt 14/10/2026 quan sát WinError 123 với tên đường dẫn bị đổi thành dấu hỏi; chỉ đặt Console.OutputEncoding cho stdout vẫn gặp lỗi đó. Giữ source/data UTF-8 và kiểm tra đúng giá trị nhận ở phía Python, riêng với stdout.

Hướng đã dùng thành công: source harness qua stdin dùng Unicode escape ASCII cho tên path; Python dựng tên Unicode thật rồi copy bundle vào đó. Validator/tests từ cwd khác và hash các file đạt, theo [evidence bản phát hành](VALIDATION.md). Knowledge_state verified ở phạm vi Windows/Python/build đó; việc này xác nhận path Unicode sau dựng, không xác nhận arbitrary Unicode qua pipeline.

Chọn UTF-8 cho pipeline hoặc lưu source vào file UTF-8 là engineering_practice đề xuất, knowledge_state unverified trong evidence release 1.0: hai hướng này chưa được thử trong lượt đó. Khi dùng, chạy probe kiểm tra round-trip của source/data thực rồi mới nâng thành verified.

## 2. Chuẩn bị OpenSCAD theo capability của task

Cài binary đúng OS từ [OpenSCAD downloads](https://openscad.org/downloads.html). Xác định executable thực tế: trên Windows bản có console thường dùng openscad.com; macOS có executable trong app bundle; Linux dùng binary/package/AppImage tương ứng. Ghi đường dẫn vào cấu hình local của project thay vì commit đường dẫn cá nhân.

PowerShell, sau khi đặt OPENSCAD theo executable đã cài:

    & $env:OPENSCAD --version
    & $env:OPENSCAD --help

macOS/Linux, sau khi đặt OPENSCAD:

    "$OPENSCAD" --version
    "$OPENSCAD" --help

Chọn backend/experimental feature/export options theo help của binary. Manifold, textmetrics và tùy chọn 3MF/color có thể phụ thuộc build; ghi flag và backend dùng thật. Một lệnh xuất cơ bản:

    openscad -o result.stl model.scad

Thay openscad bằng executable đã chọn. File model.scad là input của nhiệm vụ; result.stl ghi trong thư mục output được phép. Khi dùng -D, ghi chính xác argument sau xử lý quoting của shell. Ghi độ mịn, exit code, warnings và hash file; đọc lại mesh để xác nhận nội dung [S01, S02](sources.md).

## 3. Chuẩn bị audit Python

Đọc requirements/lockfile của project trước khi cài. Dựng môi trường mới cho host mới; cài từ dependency/lock đã được dự án kiểm chứng. Chỉ cài package cần cho audit đã chọn. Với task mới chưa có lock, chọn phiên bản tương thích, chạy smoke/regression rồi lưu lock hoặc snapshot dependency cùng Python/OS.

PowerShell, mẫu project có requirements.txt:

    python -m venv .venv
    .\.venv\Scripts\python.exe -m pip install -r requirements.txt
    .\.venv\Scripts\python.exe -m pip freeze > environment-resolved.txt

macOS/Linux:

    python3 -m venv .venv
    .venv/bin/python -m pip install -r requirements.txt
    .venv/bin/python -m pip freeze > environment-resolved.txt

Nếu project có uv.lock/hướng dẫn uv, dùng quy trình uv của project. pip freeze ghi môi trường đã resolve trên host đó; tái lập đa OS cần kiểm tra wheel/platform và input lock tương ứng. Bộ guides tự nó dùng stdlib, nên validator chạy được trước mọi cài đặt mesh/CAD.

Trimesh cần dependency tùy operation, ví dụ spatial index, boolean engine hoặc graph tools. Kiểm tra đúng phép section/proximity/boolean sẽ dùng; ghi version thực và exception khi thiếu [S03](sources.md). CGAL và BOSL2 là lựa chọn riêng theo nhu cầu, không phải dependency bắt buộc của mọi task.

## 4. Chuẩn bị Fusion

Cài và chạy Fusion trên OS được Autodesk hỗ trợ; đối chiếu [system requirements](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/System-requirements-for-Autodesk-Fusion-360.html) khi triển khai. Ghi build thực, design type, API symbol/version, entitlement cần thiết và font. Trên host chưa có Fusion desktop phù hợp, native giữ blocked/not_run; các bước offline vẫn có acceptance riêng.

Đăng ký entrypoint Scripts/Add-Ins theo cấu trúc source của nhiệm vụ. Chạy một probe nhỏ trên document test mới để xác nhận đơn vị, feature và log trước build đầy đủ. Symbol preview/retired có nhãn và đường dùng rõ; chọn released API phù hợp cho bản phân phối [S05–S11](sources.md).

MCP là cách tự động hóa tùy capability, hướng dẫn ở [fusion-mcp-testing](fusion-mcp-testing.md). Chạy script qua Scripts/Add-Ins là một route native khác khi task cho phép. Tài liệu chung cung cấp quy trình; adapter script của mỗi project có input/output contract riêng.

## 5. Preflight và acceptance khi đổi máy

1. Đối chiếu file bộ hướng dẫn, source/input hash và license; chạy validator của bộ.
2. Ghi tool/build/OS/Python và dependencies; xác nhận tính năng được yêu cầu trong runtime đích.
3. Xác nhận input/units/font/library. File riêng được cấp qua manifest của task với đường dẫn tương đối và SHA256.
4. Chạy ca baseline nhỏ theo đúng route; so output/metrics và tolerance đã chốt.
5. Báo từng lớp source/offline/native/export/physical và các check skipped/blocked.
6. Lưu intake, commands, resolved versions, evidence và next step theo [templates](templates.md).

Khả năng đọc/copy tài liệu và khả năng chạy lại CAD là hai acceptance riêng. Bằng chứng bản phát hành hỗ trợ máy mới thực hiện preflight; mỗi môi trường mới có lượt xác nhận của chính nó.
