# CP2 Prototype - LABCODE Copilot

Prototype này chạy bằng Python chuẩn, không cần cài thêm Flask/Streamlit.

## Cách chạy

```powershell
python codebase/app.py
```

Sau đó mở `http://127.0.0.1:8000`.

Nếu cổng 8000 đang bận:

```powershell
$env:PORT='8015'; python codebase/app.py
```

Sau đó mở `http://127.0.0.1:8015`.

## Prototype CP2 đang chứng minh gì?

- Flow chính bấm hết được: nạp link Git + link LABCODE -> AI tổng hợp thông tin lab -> chia vai trò -> xem task, output và tiến độ.
- Data đang là mẫu giả lập, chưa gọi AI thật.
- Nút “Thử link thiếu thông tin” dùng để demo hành vi low-confidence.
- Màn hình role cho phép sửa tên thành viên, việc cần làm và output khi AI gợi ý chưa đúng.
- Ở CP3, thay logic mock trong `app.py` bằng lời gọi AI thật và lưu trace vào repo.

## Đường demo 5 phút

1. Nhập hoặc giữ sẵn link Git và link LABCODE, bấm “Phân tích”.
2. Nói qua trang tổng hợp: nguồn đầu vào, tóm tắt lab, timeline và đầu ra cần nộp.
3. Bấm “Tạo role và task”.
4. Sửa thử một task hoặc output để chứng minh nhóm có quyền chỉnh khi AI tạo chưa đúng.
5. Bấm “Tạo task riêng”, chọn từng vai trò, xem output, nguồn liên quan và tick tiến độ.
6. Quay lại bước 1, bấm “Thử link thiếu thông tin”, rồi phân tích lại để show case khó.
