# Kiểm chứng Fusion native qua MCP theo capability

MCP là một route chạy native; Scripts/Add-Ins hoặc công cụ tự động hóa được nhiệm vụ cho phép cũng có thể thực thi cùng contract. Tài liệu này mô tả **engineering practice**, nguồn primary ở [S09](sources.md). Adapter và wrapper của từng project có interface riêng.

## 1. Chốt input/output

Dùng [task template](scad-to-fusion-task.md). Ghi source/hash, entrypoint, document test, parameter matrix, phạm vi read/write, log path và outputs cần có. Kiểm chứng offline bảo vệ logic; native xác nhận solver/kernel của build đích.

Wrapper gọi builder của model theo interface được model cung cấp, hoặc chạy entrypoint đã được thiết kế để test. Contract tối thiểu: nhận cấu hình xác định; dựng trong document test mới; log stage và exception gốc; đo checks; phục hồi expressions khi thử biến thể; xuất manifest/hash nếu cần. Tên hàm và part count lấy từ source của nhiệm vụ.

## 2. Discover runtime và công cụ

Autodesk local MCP yêu cầu Fusion desktop đang chạy, server bật tại Preferences → General → API và client trỏ đúng endpoint [S09](sources.md). Lấy port/endpoint từ Preferences/tài liệu build đang dùng, giữ loopback theo đường local được hỗ trợ.

Đọc metadata/schema công cụ hiện tại. Ghi tool name, arguments, execute/read-only capability, protocol revision và Fusion version. Toolset có thể đổi theo release; payload chạy được ở build trước là bằng chứng lịch sử.

Thiếu server/client phù hợp: dùng Scripts/Add-Ins nếu route đó được cho phép, hoặc giữ native blocked/not_run và bàn giao source/offline evidence cùng yêu cầu thiết lập còn thiếu.

## 3. Lifecycle và transport theo server đích

Chọn client hỗ trợ revision server công bố. Đọc specification của đúng revision trước khi xử lý initialize/session/notifications, JSON/SSE, IDs hoặc reconnect. Ví dụ specification 2025-11-25 có lifecycle legacy và session header theo điều kiện; revision khác có thể có cơ chế khác.

Request hoàn tất khi nhận response tương ứng và đã kiểm tra HTTP, JSON-RPC error, tool-level error cùng kết quả ứng dụng. Tách accepted/running với completed. Giữ log/stage/run ID để theo dõi việc dài; timeout client có thể để ứng dụng vẫn chạy, nên đọc trạng thái trước khi gửi lại.

Persistent connection, JSON-only Accept, tool name, port và protocol version từng quan sát ở một adapter giữ nhãn project_observation. Đối chiếu server contract trước khi dùng ở máy/build khác.

## 4. Probe và ma trận

1. Đọc trạng thái ứng dụng/lệnh/hộp thoại đang hoạt động bằng công cụ phù hợp.
2. Chạy probe nhỏ trên document mới: xác nhận log, units, một feature và cách nhận lỗi.
3. Dựng baseline theo hash; kiểm tra health, profiles/constraints theo contract và số part.
4. Chạy dimension variants và topology rebuild theo [parameter validation](parameter-change-validation.md).
5. Đo BRep đúng frame khi task có assembly; dùng API/kernel build hỗ trợ.
6. Phục hồi/kiểm tra baseline, xuất files/manifest khi thuộc mục tiêu.
7. Đọc outputs độc lập, ghi hash, actual và threshold.

Quyền thay đổi document theo task. Mỗi run có log/output riêng, bảo toàn evidence trước. Exception gốc được trả về client và lưu cạnh stage; lỗi native được tái hiện tại đúng source/stage.

## 5. Handoff và phạm vi bằng chứng

BRep, STL tessellation, sampled_motion, slicer và physical có checks riêng. BRep solid/response success xác nhận phạm vi của chúng; mesh quality, fidelity, lực cơ cấu cần phép kiểm tra tương ứng.

Handoff gồm tool schema/capability, protocol/build, source/wrapper hash, parameters, stage logs/errors, matrix, BRep metrics, export settings/hash và audit. Bài học adapter ghi điều kiện áp dụng, kết quả và hướng thất bại thực sự đã thử.

[Ví dụ workflow MCP Snaplock](https://github.com/TimTini/snaplock-storage-box/blob/main/docs/examples/fusion-mcp-testing.md) minh họa một adapter/build cụ thể. Ví dụ cần source/input của project đó; bộ chung hoạt động khi assets riêng vắng.
