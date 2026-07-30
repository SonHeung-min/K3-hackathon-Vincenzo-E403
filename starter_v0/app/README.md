# LABCODE Copilot - Web Application Architecture

Ứng dụng LabSplitter (LABCODE Copilot) đã được phân rã thành các mô-đun nhỏ hơn đặt tại thư mục `starter_v0/app/` để dễ quản lý, bảo trì và tích hợp như một phần cấu trúc tác nhân (agent) chính.

## Cấu trúc thư mục các File

```
starter_v0/
├── app.py                  # Entry-point khởi chạy chính của ứng dụng
└── app/
    ├── __init__.py         # Khởi tạo package và expose hàm chạy server
    ├── state.py            # Lưu trữ trạng thái động (STATE) và hằng số Mock
    ├── github.py           # Cơ chế tải tài liệu README từ GitHub (có fallback)
    ├── ai.py               # Kết nối Gemini API để phân tích chia task & contract
    ├── views.py            # Định nghĩa toàn bộ giao diện HTML/CSS và các hàm render
    └── server.py           # Thiết lập HTTP Server và xử lý sự kiện/form (Routing)
```

## Chi tiết chức năng từng mô-đun

1. **`app.py` (Runner)**
   - Nạp các biến môi trường từ file `starter_v0/.env` bằng thư viện sẵn có `env_loader`.
   - Gọi `run_server` từ gói `app` để mở cổng chạy ứng dụng.

2. **`app/state.py` (Trạng thái và Hằng số)**
   - Quản lý dictionary `STATE` toàn cục (lưu giữ bước hiện tại, số lượng thành viên, link tài liệu, lỗi nếu có, các tác vụ đã hoàn thành, v.v.).
   - Chứa hằng số mock như `SAMPLE_DOC`, `RISKY_DOC`, `NORMAL_ANALYSIS`, `RISKY_ANALYSIS`, `ROLES`.

3. **`app/github.py` (Công cụ GitHub)**
   - Hỗ trợ hàm `parse_github_url` để chuẩn hóa các link GitHub nhập vào.
   - Hàm `fetch_github_readme` cố gắng đọc nội dung file README qua GitHub API (có hỗ trợ authorization token nếu cấu hình `GITHUB_TOKEN` để tránh bị giới hạn rate limit).
   - Nếu lỗi xảy ra (ví dụ: repo private hoặc quá giới hạn), tự động dự phòng (fallback) thử lấy dữ liệu raw qua `raw.githubusercontent.com`.

4. **`app/ai.py` (Tích hợp AI)**
   - Gọi API Gemini (`gemini-1.5-flash`) truyền prompt phân công công việc thông minh dựa trên số thành viên động (`num_members`).
   - Yêu cầu AI phân tích và thiết lập giao kèo định dạng dữ liệu (Data Contract) dưới dạng JSON trong mô tả của các task có sự trao đổi giữa các role.
   - Ghi lại các lịch sử trace log vào `eval/traces/` để lưu vết phục vụ việc đo đạc ở các checkpoint tiếp theo.

5. **`app/views.py` (Giao diện hiển thị)**
   - Chứa mã CSS của ứng dụng (`STYLE`) để cấu hình giao diện.
   - Triển khai giao diện từng bước: `render_upload` (Nạp link), `render_analysis` (AI phân tích), `render_roles` (Bổ sung vai trò), `render_progress` (Theo dõi).
   - Bao quanh bởi `render_shell` làm khung trang chính.

6. **`app/server.py` (Mạng và Điều phối)**
   - Triển khai `LabcodeHandler` kế thừa từ `BaseHTTPRequestHandler` để xử lý các luồng GET/POST.
   - Hàm `handle_form` chịu trách nhiệm điều phối hành vi khi người dùng submit form (gọi API GitHub, gọi API Gemini, lưu trữ kết quả phân tích vào `state` và định hướng chuyển bước).

## Cách chạy

Chạy server tại thư mục gốc của dự án bằng python interpreter của hệ thống:

```bash
python3 starter_v0/app.py
```

Mặc định ứng dụng sẽ chạy trên cổng `8000`. Bạn có thể thay đổi cổng chạy thông qua biến môi trường `PORT`:

```bash
PORT=8015 python3 starter_v0/app.py
```
