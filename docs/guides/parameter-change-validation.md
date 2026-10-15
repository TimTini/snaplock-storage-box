# Kiểm chứng model khi thay đổi tham số

Đây là **engineering practice**, dùng cho model SCAD/Fusion theo [job specification](templates.md). Miền hợp lệ, part, cơ cấu và công nghệ chế tạo thuộc nhiệm vụ. Bộ kiểm tra chọn theo feature thực có; phần ngoài phạm vi mang trạng thái not_applicable và lý do.

## 1. Xác định miền và contract

Lập danh sách tham số gốc, công thức phụ thuộc, đơn vị, giới hạn và quan hệ giữa tham số. Phân biệt:

- Miền source tính được hoặc render được.
- Miền hình học hợp lệ: bề dày, bán kính, số part và tính liên thông theo yêu cầu.
- Miền chức năng: tiếp xúc, khoảng hở, hành trình, tải hoặc lưu lượng liên quan.
- Miền chế tạo: envelope, hướng, margin và giới hạn công nghệ thực tế.

Tham số thay dimension trong topology hiện có và tham số quyết định topology có contract riêng. Khi vượt ngưỡng sinh/xóa feature, xác định cần rebuild hay script đã hỗ trợ topology đó. Giá trị nằm ngoài miền phải được từ chối rõ, thay vì tạo hình sai mà vẫn báo đạt.

## 2. Tạo ma trận có mục tiêu

Mỗi ca ghi tên, input, mục tiêu, trạng thái dự kiến, phép đo và dung sai:

1. Baseline đã chốt.
2. Từng trục độc lập: nhỏ, lớn, sát giới hạn và giá trị ngoài miền dự kiến bị từ chối.
3. Tổ hợp tương tác: bề dày với bán kính; pitch/count với chiều dài; khoảng hở với feature lắp.
4. Ngưỡng topology: ngay trước/sau bước đổi count, bỏ feature hoặc đổi liên thông.
5. Cấu hình sử dụng/chế tạo đại diện và các vùng quan trọng riêng.

Ma trận hữu hạn xác nhận những ca đã chạy. Bao phủ toàn miền liên tục cần thêm chứng minh toán học, cận sai số hoặc phương pháp kiểm tra phù hợp. Ghi độ phân giải thử và vùng chưa khảo sát.

## 3. Kiểm tra từng part

Render/recompute theo input và ghi hash/version/backend. Kiểm tra số body/shell, solid hoặc surface theo contract, bounds, độ dày, lỗ, vị trí đặc trưng và volume khi volume có ý nghĩa.

So baseline/reference bằng phép căn tọa độ đã mô tả. Báo cáo tách shape fidelity ở cấu hình tham chiếu với tính đúng của biến thể. Đối chiếu phần local quan trọng riêng; phép đo tổng có thể che sai lệch vùng nhỏ.

## 4. Kiểm tra assembly và chuyển động khi có

Lập danh sách cặp cần tiếp xúc/có khoảng hở/được phép giao. Đặt part vào frame assembly, giữ phép biến đổi và datum. Mỗi cặp có ngưỡng giao, gap và mục tiêu chức năng riêng; intentional overlap hoặc tiếp xúc thiết kế được diễn giải theo contract.

Đường lắp và hành trình cần tư thế đầu/cuối, pose trung gian và vùng gần tiếp xúc. Chia nhỏ vùng cần khảo sát, ghi step/cận sai số. Lấy mẫu hữu hạn mang nhãn sampled_motion; xác nhận toàn hành trình dùng kiểm tra liên tục hoặc cận đã chứng minh.

BRep native và mesh tessellation có số đo riêng. Ghi cả hai khi kết quả khác nhau cùng error budget; thử vật lý bổ sung fit, biến dạng và lực thực.

## 5. Kiểm tra công thức Fusion

Chạy source trên Fusion build đã ghi; đổi parameter expression theo từng ca và recompute. Kiểm tra health, profile/constraints theo loại sketch, số part, feature phụ thuộc và kích thước mục tiêu [S05–S07, S10](sources.md).

Phục hồi expression/cấu hình trong finally rồi recompute và kiểm tra baseline. Thử trên document test riêng; giữ thiết kế của người vận hành. Với ca topology cần Run lại, ghi rõ tạo document/model mới và đối chiếu part contract.

Đầu ra native thật được so với SCAD cùng input khi nhiệm vụ yêu cầu tương đương hai mô hình. Mock API bảo vệ cách gọi và logic; native log xác nhận solver/kernel thực.

## 6. Kiểm tra chế tạo khi thuộc mục tiêu

Lấy kích thước hữu dụng, orientation, brim/support/tool allowance và giới hạn Z từ máy/slicer/công nghệ được chọn. Tính bounds sau orientation của từng part; so từng trục:

    kích_thước_bao + phần_chừa_phía_âm + phần_chừa_phía_dương <= khổ_hữu_dụng

Kích thước vỏ danh nghĩa có thể nhỏ hơn bounds gồm tai/chốt/gân. Margin bằng 0 chỉ hợp lệ khi hồ sơ task chọn rõ mục tiêu kiểm tra số học đó. Coupon và mẫu thật xác nhận shrink/fit/strength theo vật liệu và cấu hình.

## 7. Chốt và bàn giao

Với đáy/bo/vành/gân, dùng thêm [ma trận gia cường](reinforcement-and-mesh.md#4-chạy-ma-trận-và-ca-từ-chối): baseline tắt option, từng option, tổ hợp, cấu hình đổi kích thước và ca ngoài miền. Đo hai phía tiếp tuyến, seam và overlap; chọn Euler theo topology. Ca từ chối dùng output thử riêng, stdout/stderr, return code và xác nhận output sau chạy. Đọc danh sách file verifier ghi và bảo toàn artifact đang có thay đổi người dùng bằng bản sao cô lập.

Dùng [evidence manifest](templates.md): source/hash, inputs, case matrix, commands, tool versions, outputs/hash, thresholds, actuals và trạng thái từng lớp. Ghi rejected_input riêng với failed_geometry; skipped/blocked/native_not_run có lý do.

Lỗi công thức được sửa tại module/builder sở hữu quan hệ; chạy lại ca lỗi và các ca tương tác liên quan trước khi xác nhận ma trận cuối. Sổ lỗi ghi regression, cẩm nang ghi quy tắc dùng lại có điều kiện. Kết quả physical được bổ sung sau thử thực tế.
