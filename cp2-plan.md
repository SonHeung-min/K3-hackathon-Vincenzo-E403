# CP2 - Kế hoạch bấm được cho LABCODE Copilot

## Mục tiêu CP2

Prototype Mock phải cho TA thấy flow chính bấm đi hết được:

`Nạp link Git + link LABCODE -> AI tổng hợp thông tin lab -> chia vai trò -> task riêng theo vai trò -> theo dõi tiến độ`

Ở CP2 chưa cần AI thật. Quyết định AI trung tâm đang được mock bằng data mẫu trong `codebase/app.py`. Ở CP3, nhóm thay mock bằng một lời gọi AI thật và lưu log/trace.

## Lát cắt một câu

Một học viên trong nhóm LABCODE cần biến link Git và link hướng dẫn lab thành kế hoạch làm việc của nhóm; AI quyết định cách tách mục tiêu, đầu việc, đầu ra và vai trò; kết quả là mỗi thành viên nhận task riêng kèm output, nguồn liên quan và trạng thái tiến độ có thể cập nhật.

## Demo script CP2

1. Chạy `python codebase/app.py`, mở `http://127.0.0.1:8000`.
2. Màn hình 1: nhập link Git và link LABCODE, bấm `Phân tích`.
3. Màn hình 2: chỉ ra trang tổng hợp nhanh: nguồn đầu vào, tóm tắt lab, timeline, deliverables.
4. Bấm `Tạo role và task`.
5. Màn hình 3: sửa tên thành viên, việc cần làm hoặc output khi AI tạo chưa đúng, bấm `Tạo task riêng`.
6. Màn hình 4: chọn từng vai trò, xem task, output, nguồn liên quan, tick tiến độ.
7. Quay lại màn hình 1, bấm `Thử link thiếu thông tin`, bấm `Phân tích` để show case AI không chắc và cần xác minh.

## Phân công gợi ý cho nhóm 5 người

| Vai trò | Việc chính | Đầu ra CP2 |
|---|---|---|
| Product Lead | Chốt lát cắt, non-goals, demo script | `cp2-plan.md` + flow demo |
| Prototype Builder | Dựng UI mock bấm được bằng Python | `codebase/` |
| Prompt & Eval | Chuẩn bị prompt và case cho CP3 | khung golden set |
| Evidence Lead | Khảo sát/mining pain | log bằng chứng |
| Spec Owner | Viết spec, rủi ro, HAX/PAIR | `spec.md` bản nháp |

## Non-goals cho CP2

- Chưa build quản lý dự án đầy đủ như Jira/Trello.
- Chưa cần upload file thật hoặc đọc PDF/docx; CP2 chỉ nhận link.
- Chưa cần đăng nhập, database, phân quyền.
- Chưa cần AI thật cho đến CP3.

## Cần nối tiếp cho CP3

- Tạo prompt yêu cầu AI trả JSON gồm `summary`, `timeline`, `deliverables`, `roles`, `tasks`, `citations`, `confidence`.
- Gọi AI thật tại nút `Phân tích` để đọc link Git/lab link.
- Lưu trace prompt/input/output vào `eval/` hoặc `logs/`.
- Tạo golden set ít nhất 20 case và chạy lượt đo đầu.
