# Hướng dẫn chạy và Quyết định Thiết kế quan trọng

Tài liệu này tổng hợp hướng dẫn chạy ứng dụng LabSplitter mới cấu trúc lại trong `starter_v0/`, cùng các quyết định thiết kế cốt lõi (Important Decisions) được đưa ra trong quá trình phát triển và lý do tại sao chúng được chọn.

---

## 1. Hướng dẫn khởi chạy ứng dụng

### Bước 1: Thiết lập môi trường và cấu hình API Key
Ứng dụng sử dụng file môi trường đặt tại `starter_v0/.env`. Đảm bảo các biến môi trường sau đây đã được định nghĩa:
*   `GEMINI_API_KEY`: API Key kết nối với Google Gemini.
*   `GITHUB_TOKEN` (Tùy chọn): Personal Access Token của GitHub để nâng giới hạn gọi API (Rate limits) khi đọc các repository public hoặc cho phép đọc các repo private mà tài khoản đó có quyền.

### Bước 2: Chạy kiểm thử tự động
Trước khi chạy ứng dụng thật, bạn nên chạy file test tích hợp mô-đun để xác minh các chức năng kết nối mạng và AI hoạt động trơn tru:
```bash
python3 starter_v0/test_app.py
```
*Kết quả ĐẠT nếu bộ test trả về: `Exit code: 0`.*

### Bước 3: Khởi chạy máy chủ Web
Mở terminal tại thư mục gốc của dự án và chạy lệnh sau để khởi động server:
```bash
python3 starter_v0/app.py
```
Mặc định ứng dụng sẽ chạy trên cổng `8000` tại địa chỉ: `http://127.0.0.1:8000`.

*Mẹo: Để cấu hình chạy trên cổng khác (ví dụ: 8015):*
```bash
PORT=8015 python3 starter_v0/app.py
```

---

## 2. Các Quyết định Thiết kế quan trọng & Lý do (Important Decisions)

### Quyết định 1: Phân rã mã nguồn đơn khối (monolithic) thành cấu trúc gói mô-đun hóa đặt trong gói `app/`
*   **Chi tiết quyết định**: Tách file `codebase/app.py` (hơn 700 dòng code trộn lẫn UI, Logic mạng, State và AI) thành các file mô-đun độc lập trong gói `starter_v0/app/` (`state.py`, `github.py`, `ai.py`, `views.py`, `server.py`).
*   **Tại sao chọn?**: 
    *   **Bảo trì dễ dàng**: Tách biệt rõ ràng các mối bận tâm (Separation of Concerns). Khi cần sửa UI chỉ cần vào `views.py`; khi cần sửa Prompt AI chỉ cần vào `ai.py`.
    *   **Tránh làm ô nhiễm thư mục gốc**: Đặt toàn bộ các file thành phần của ứng dụng web trong thư mục `app/` thay vì đặt rải rác ngoài thư mục gốc của `starter_v0/` (nơi có các file chạy đánh giá agent như `chat.py`, `run_eval.py`). Điều này giúp mã nguồn ngăn nắp và tránh xung đột import.

### Quyết định 2: Chuyển đổi Model từ `gemini-1.5-flash` sang `gemini-3.5-flash`
*   **Chi tiết quyết định**: Thay đổi tên model được cấu hình trong REST API endpoint thành `gemini-3.5-flash`.
*   **Tại sao chọn?**: 
    *   **Khắc phục lỗi 404**: Trong môi trường chạy thử nghiệm sandbox mô phỏng (khoảng thời gian tương lai 2026), danh sách model của Google Cloud Generative Language API đã loại bỏ/deprecated model `gemini-1.5-flash` và chuyển sang các model thế hệ mới như `gemini-3.5-flash` và `gemini-2.5-flash`.
    *   **Tương thích tối đa**: Giúp đảm bảo các lượt gọi API của hệ thống diễn ra thành công và kế thừa hiệu suất xử lý prompt tốt hơn từ model thế hệ mới.

### Quyết định 3: Sử dụng thư viện `urllib` mặc định thay vì các SDK hoặc module bên thứ ba (như `requests`, `python-dotenv`)
*   **Chi tiết quyết định**: Toàn bộ HTTP Request (đọc file từ GitHub và gọi API Gemini) được thực hiện qua `urllib.request`. Việc nạp file `.env` được thực hiện qua hàm custom `load_lab_env` kế thừa từ `env_loader.py`.
*   **Tại sao chọn?**:
    *   **Không phụ thuộc vào thư viện cài đặt**: Môi trường sandbox chạy lab có thể không cài sẵn `requests` hay `python-dotenv` và dễ gặp lỗi `ModuleNotFoundError`. Sử dụng thư viện built-in của Python giúp ứng dụng có thể chạy ngay ở mọi máy mà không cần chạy `pip install`.

### Quyết định 4: Cơ chế tự động fallback khi fetch GitHub không thành công (Soft Error Handling)
*   **Chi tiết quyết định**: Nếu link GitHub bị lỗi (ví dụ: Private repo không có quyền truy cập, link nhập sai định dạng), ứng dụng hiển thị một thông báo cảnh báo nhẹ nhàng trên màn hình (Soft warning) và mở rộng thêm một khung Textarea dự phòng (`show_fallback = True`) để người dùng có thể chủ động dán trực tiếp đề bài lab bằng tay.
*   **Tại sao chọn?**:
    *   **Trải nghiệm người dùng tốt hơn (Graceful Failure)**: Tránh làm sập ứng dụng (hard crash). Giúp người dùng luôn có phương án dự phòng để hoàn thành công việc chia task ngay cả khi kết nối mạng hoặc API GitHub gặp sự cố.
