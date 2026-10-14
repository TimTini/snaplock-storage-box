> Hồ sơ ví dụ theo checkpoint đã ghi; các bước còn chờ trong hồ sơ thuộc thời điểm đó. Trạng thái hiện hành của Snaplock nằm ở [SCAD](../geometry/latch-parametric-fix.md) và [Fusion](../geometry/fusion-parametric-sync.md). Quy trình chung bắt đầu tại [bộ hướng dẫn](../guides/README.md).

# Agent kiểm chứng Fusion native qua MCP local

Quy trình này nối baseline SCAD đã chốt với script Fusion, solver native, BRep lắp, STL xuất và mẫu in. Agent ghi nguồn, hash, tham số, phiên bản Fusion và phạm vi của từng phép kiểm tra. [Hồ sơ native 0.6.1](../geometry/fusion-parametric-sync.md) minh họa một lần áp dụng thực tế.

## 1. Agent chốt baseline trước khi chạy native

Agent đo mẫu, dựng SCAD bằng hình học có tham số rồi kiểm tra solid, hình bao và quan hệ lắp. Các phép dựng trực tiếp như Extrude, Revolve, Sweep, Mirror và Pattern được ưu tiên theo hình học của vùng cần dựng. Loft nhiều tiết diện là lựa chọn cuối sau khi các cách dựng trực tiếp đã được đánh giá.

Agent chuyển các quan hệ kích thước sang User Parameters và expression của Fusion. Agent dùng chung datum cho các part lắp nhau; chiều dài nối, vị trí răng, khe đàn hồi và ramp cùng bám tham số sở hữu quan hệ. Các miền hợp lệ và công tắc topology được ghi rõ trong [quy trình đổi tham số](../guides/parameter-change-validation.md).

Agent chạy regression offline trước khi mở bài test native. Hồ sơ source, offline, native BRep, STL, slicer và in vật lý có trạng thái riêng.

## 2. Agent chuẩn bị kết nối local

Fusion Preferences → General → API bật **Fusion MCP Server**. Agent lấy port từ Preferences; lần kiểm chứng ngày 14/10/2026 dùng `http://127.0.0.1:27182/mcp`. CLI trong repo kết nối loopback tại `127.0.0.1` và nhận port bằng `--port`.

Connector Fusion MCP đã cấu hình trong phiên cung cấp đường gọi công cụ trực tiếp. [CLI local](../../tools/fusion-mcp-test.py) cung cấp đường chạy qua HTTP bằng thư viện chuẩn Python. Python chạy CLI và Python trong Fusion có môi trường riêng; Fusion thực thi phần dùng `adsk` bên trong ứng dụng.

Các lệnh dưới đây chạy tại thư mục gốc repo:

```powershell
python tools/fusion-mcp-test.py --list-tools
python tools/fusion-mcp-test.py
```

Lệnh đầu lưu schema công cụ hiện tại và in tên công cụ. Lệnh thứ hai đọc phiên bản Fusion, số document mở và active command bằng script `readOnly=true`. Tham số `--port 27182` chọn port theo Preferences.

## 3. Agent giữ đúng vòng đời phiên MCP

Trong Fusion 2705.1.30 đã thử, các lời gọi dưới đây đi qua **cùng một kết nối HTTP persistent**:

1. `initialize` gửi protocol version, capabilities và clientInfo.
2. Client nhận `MCP-Session-Id` từ response và đưa ID vào header các request tiếp theo.
3. `notifications/initialized` hoàn tất khởi tạo.
4. `tools/list` lấy tên, schema và hướng dẫn công cụ từ server hiện tại; hoặc `tools/call` chạy công cụ đã xác định.
5. Client đọc xong response trước khi gửi request tiếp theo và đóng kết nối sau khi hoàn tất lượt gọi.

CLI mở một phiên đầy đủ cho mỗi lệnh. Protocol version `2024-11-05` là phiên bản đã được server này chấp nhận. Agent đọc metadata initialize và tools/list khi chuyển sang phiên bản Fusion khác.

CLI này yêu cầu response JSON bằng `Accept: application/json`, đúng với Fusion local đã kiểm chứng. Server trả event stream SSE thuộc adapter transport riêng; agent chọn client có parser SSE khi dùng backend đó.

Tool thực thi đã kiểm chứng có tên `fusion_mcp_execute`, nhận `featureType=script` và `object.script`. Script định nghĩa hàm `run(_context: str)`. Script chỉ đọc dùng `readOnly=true`; script dựng model dùng `readOnly=false`. Hộp thoại thao tác đang mở được đọc bằng chế độ chỉ đọc; lượt thay đổi thiết kế bắt đầu sau khi thao tác trong hộp thoại đã hoàn tất.

```json
{
  "name": "fusion_mcp_execute",
  "arguments": {
    "featureType": "script",
    "object": {
      "readOnly": true,
      "script": "import adsk.core\ndef run(_context: str):\n    print(adsk.core.Application.get().version)\n"
    }
  }
}
```

Agent giữ exception của hàm run để MCP trả traceback gốc. CLI kiểm tra HTTP status, JSON-RPC error, `isError` và trường `success` trong nội dung trả về của Fusion.

## 4. Agent chạy test native bằng wrapper trong repo

[Wrapper native](../../fusion/tests/McpNativeTest/native_test.py) gọi trực tiếp các hàm của script chính. Transport truyền `PROJECT_ROOT` theo vị trí checkout, giúp cùng source chạy ở các đường dẫn khác nhau.

CLI là transport local dùng lại được; wrapper và công thức lắp trong project này thuộc Snaplock. Với model khác, agent xây wrapper gọi hàm dựng/kiểm tra của model đó và đặt rigid transform theo datum lắp đã đo. Các hệ tọa độ và hằng số cơ cấu được xác định lại theo thiết kế đích.

```powershell
python -m unittest discover -s tests
python tools/fusion-mcp-test.py --run
```

Lệnh `--run` tạo document test mới và giữ các document đang mở. Wrapper thực hiện lần lượt:

1. Ghi thời điểm, phiên bản Fusion và SHA256 source vào log.
2. Gọi `dimensions`, `build` và `check_model` của script chính.
3. Gọi `verify_variants` để kiểm tra recompute, bounds, bốn solid, sketch fully constrained, vị trí tiết diện và feature healthy.
4. Đặt bản sao temporary BRep vào tư thế đóng; kiểm tra sáu cặp part của baseline và bốn cấu hình minimum, nắp 20 mm, nắp 233,1 mm, cỡ 250 × 232,7 × 245,7 mm.
5. Kiểm tra mỗi boolean thành công và thể tích giao dưới 0,01 mm³.
6. Khôi phục biểu thức tham số, xác minh lại baseline rồi xuất STL, manifest, archive F3D và ảnh viewport.
7. Lưu `native-test.json` với hash source/wrapper, tham số, công tắc gân, kết quả BRep và số feature.

Wrapper dùng các công tắc `BUILD_RIBS` hiện tại của source. Bộ mặc định hiện tại có ba công tắc gân tắt. Kiểm chứng các công tắc bật là một đợt chạy có cấu hình và bằng chứng riêng.

Log từng stage của wrapper nằm tại `work/fusion-mcp/<timestamp>/native-test.log`, theo đường dẫn CLI in ngay khi gửi lệnh. Mỗi lượt có thư mục log riêng; log production được bảo toàn. Kết quả native nằm trong `fusion/SnaplockStorageBox/exports/<timestamp>/`; response MCP thành công nằm trong cùng thư mục log dưới tên `response.json`. Lần test native có thể kéo dài vài phút; agent theo dõi log giữa các lần kiểm tra tiến trình của lệnh CLI đang chạy.

Wrapper tạo mô hình và xuất file local. Document test vẫn mở sau khi hoàn tất. Các phép lắp dùng temporary BRep, còn timeline chính giữ bố trí in và tham số baseline.

## 5. Agent kiểm tra STL bằng công cụ độc lập

Agent lấy đúng timestamp được trả về sau lượt chạy:

```powershell
python tools/audit-fusion.py fusion/SnaplockStorageBox/exports/<timestamp>
```

Audit xác minh hash script/STL, số part, solid kín, tính liên thông, bounds và sai khác thể tích đối xứng với SCAD cùng STL gốc. Audit dùng baseline mặc định tại `outputs/default/` và STL tham chiếu local trong `reference/`. Bộ native xuất với tham số khác được đối chiếu với SCAD render bằng cùng tham số trước khi dùng kết quả so sánh.

Native BRep và mesh có tiêu chí lắp riêng. Mesh xấp xỉ mặt cong có thể sinh lớp giao nhỏ tại mặt tiếp xúc. Agent ghi cả số đo BRep và mesh khi hai kết quả khác nhau, cùng ngưỡng và trạng thái của từng phép kiểm tra. Mẫu in xác nhận khe lắp, lực gài, retention và tuổi thọ thực tế ở checkpoint tiếp theo.

## 6. Agent xử lý lỗi theo bằng chứng

| Tình huống | Cách xử lý đã kiểm chứng |
|---|---|
| Phiên MCP bị mất trạng thái hoặc kết nối bị reset | Agent giữ initialize, initialized và lượt tools/call trong cùng HTTP connection; agent khởi tạo phiên mới trước lượt gọi mới |
| Script CLI đọc schema có ký tự Unicode | Agent đọc/ghi JSON UTF-8 và cấu hình stdout UTF-8 ở entrypoint CLI |
| Fusion run bị chặn bởi messageBox | Wrapper gọi trực tiếp build/check/variants/export và trả exception qua MCP; log stage ghi tiến trình |
| Offline đạt và native phát sinh lỗi | Agent giữ traceback, stage và source/hash rồi tái hiện ca native trước khi sửa nguồn |
| BRep solid và STL có cạnh hở | Agent đo cạnh hở, định vị trên hình học nguồn và thử hiệu chỉnh số học nhỏ; mỗi thử nghiệm có trước/sau và audit kín |
| File STL tăng lên hàng trăm MB | Agent đo số triangle/kích thước file, thử preset mesh native rồi kiểm tra lại fidelity và solid |
| BRep lắp kín và mesh có giao | Agent ghi riêng từng kết quả; báo cáo giữ ngưỡng mesh và giá trị giao quan sát |

Ca Snaplock đã định vị seam tại mép ngàm gần trùng mặt côn với cung web. Khoảng phân cách bán kính 0,001 mm xử lý seam, còn preset High giảm tessellation thừa. Các giá trị này thuộc ca hình học đã đo; agent xác định nguyên nhân và miền áp dụng trước khi dùng recipe cho model khác.

## 7. Agent lưu hồ sơ để tiếp tục ở phiên sau

Hồ sơ bàn giao gồm commit/source SHA256, phiên bản Fusion, wrapper hash, tham số và công tắc, log stage, ma trận recompute, số solid/feature, giao BRep, manifest/hash STL, audit đối chiếu, ảnh và archive F3D local. Agent đọc checkpoint và Git status trước khi chạy lại.

Agent giữ dữ liệu tham chiếu, response MCP và kết quả local trong các thư mục được Git ignore. Bản công khai chứa báo cáo đã chuẩn hóa đường dẫn và kiến thức có thể dùng lại. Commit theo đúng phạm vi đã kiểm chứng giúp source và tài liệu cùng phiên bản.

## Kiểm chứng công cụ trong repo — 14/10/2026

[Báo cáo workflow MCP](../validation/fusion-mcp-workflow.json) gắn hash CLI/wrapper với lượt chạy thực tế trong Fusion 2705.1.30. Bộ 66 test đạt, gồm bảy regression cho transport và bảo toàn log. Lệnh inspect, tools/list và toàn bộ `--run` đã chạy thành công; 30 cặp BRep có giao bằng 0 và bộ STL đạt audit độc lập. Hash log production trước/sau trùng nhau. Các report native/STL giữ phạm vi kiểm tra riêng; hồ sơ in vật lý tiếp tục theo mẫu thử.

Hồ sơ giữ hash CLI của lượt native và hash CLI cuối riêng. Sau lượt native, header Accept được chốt về JSON; inspect và tools/list đã được chạy lại với header cuối. Wrapper native giữ cùng hash đã kiểm chứng.
