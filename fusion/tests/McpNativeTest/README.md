# Test native qua MCP Fusion

[CLI ở gốc repo](../../../tools/fusion-mcp-test.py) truyền vị trí checkout vào `native_test.py`, rồi chạy wrapper bên trong Fusion qua MCP.

```powershell
python tools/fusion-mcp-test.py
python tools/fusion-mcp-test.py --run
```

Lệnh mặc định chỉ đọc trạng thái. Lệnh `--run` tạo document mới, gọi build/check/recompute của source chính, kiểm tra BRep lắp đóng baseline cùng bốn biến thể, khôi phục tham số và xuất STL/F3D/ảnh/báo cáo. Wrapper phục vụ tool MCP `featureType=script`; entrypoint CLI cung cấp `PROJECT_ROOT` theo checkout.

[Hướng dẫn đầy đủ](../../../docs/guides/fusion-mcp-testing.md) ghi giao thức, port, log, audit STL và giới hạn kiểm chứng.

CLI truyền thêm `RUN_DIRECTORY` cho log riêng tại `work/fusion-mcp/<timestamp>/native-test.log`. [Báo cáo workflow](../../../docs/validation/fusion-mcp-workflow.json) xác nhận lượt chạy native và bảo toàn log production.
