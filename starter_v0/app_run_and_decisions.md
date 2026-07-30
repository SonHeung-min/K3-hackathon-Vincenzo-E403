# HƯỚNG DẪN VẬN HÀNH & CÁC QUYẾT ĐỊNH THIẾT KẾ QUAN TRỌNG

Tài liệu này tổng hợp hướng dẫn chi tiết cách chạy hệ thống **LabSplitter** (đã tái cấu trúc tại thư mục `starter_v0/`) và làm rõ các quyết định kỹ thuật quan trọng kèm theo lý do lựa chọn.

---

## 1. Hướng dẫn cách chạy hệ thống

### Các yêu cầu ban đầu (Prerequisites)
- Python 3.9+ trở lên.
- Đã cấu hình khóa API trong file `/home/nhatnm/code/vin-project/lab/K3-hackathon-Vincenzo-E403/starter_v0/.env`:
  ```ini
  GEMINI_API_KEY=AQ.Ab8... (API key của bạn)
  ```

### Các lệnh vận hành chính

#### A. Khởi chạy Web Server
Chạy ứng dụng từ thư mục gốc của dự án:
```bash
python3 starter_v0/app.py
```
- Mặc định server sẽ chạy tại địa chỉ: `http://127.0.0.1:8000`
- Nếu muốn chạy trên một cổng khác (ví dụ: `8015`), sử dụng biến môi trường `PORT`:
  ```bash
  PORT=8015 python3 starter_v0/app.py
  ```

#### B. Chạy bộ kiểm thử tự động (Automated Test Suite)
Để kiểm tra tính đúng đắn của toàn bộ mô-đun (State, Github Fetcher, Gemini API, Fallback UI) trước khi triển khai:
```bash
python3 starter_v0/test_app.py
```

---

## 2. Các quyết định thiết kế quan trọng và Rationale (Tại sao?)

### Quyết định 1: Cấu trúc mô-đun hóa đặt trong gói con `starter_v0/app/`
*   **Lựa chọn:** Chia nhỏ file đơn khối cũ `codebase/app.py` thành:
    - `state.py`: Quản lý trạng thái và dữ liệu mock.
    - `github.py`: Trích xuất file README.
    - `ai.py`: Kết nối Gemini API.
    - `views.py`: Render HTML/CSS.
    - `server.py`: Thiết lập HTTP Server và xử lý router.
    - `app.py` (nằm ở thư mục ngoài): Đóng vai trò là runner/entrypoint chính.
*   **Tại sao?:** 
    - Để tránh làm "ô nhiễm" thư mục gốc của `starter_v0/` (nơi đã có sẵn các file đánh giá benchmark như `chat.py`, `run_eval.py`, `agent.py`).
    - Tăng tính đóng gói (encapsulation), giúp việc phát triển hoặc sửa đổi UI (trong `views.py`) hoàn toàn độc lập với việc thay đổi prompt AI (trong `ai.py`).

### Quyết định 2: Chuyển đổi model LLM sang `gemini-3.5-flash`
*   **Lựa chọn:** Đổi model gọi REST API từ `gemini-1.5-flash` cũ sang `gemini-3.5-flash`.
*   **Tại sao?:** 
    - Trong môi trường chạy của hệ thống hiện tại, các model cũ như `gemini-1.5-flash` đã bị loại bỏ/ngừng hỗ trợ dẫn đến lỗi `HTTP Error 404: Not Found` khi gọi API.
    - Sử dụng `gemini-3.5-flash` giúp đảm bảo khả năng tương thích 100% với môi trường thực tế hiện tại và tối ưu hóa thời gian sinh phản hồi JSON.

### Quyết định 3: Cơ chế quản lý State thông qua Module Import (`from . import state`)
*   **Lựa chọn:** Trong `views.py` và `server.py`, thay vì import trực tiếp biến như `from .state import ROLES`, ta import cả module `from . import state` và tham chiếu qua `state.ROLES`, `state.STATE`.
*   **Tại sao?:** 
    - Khắc phục lỗi tham chiếu tĩnh (stale references) trong Python. Khi gán lại biến (`state.ROLES = new_roles`) ở `server.py`, nếu `views.py` chỉ import trực tiếp `ROLES` từ trước đó, nó sẽ vẫn giữ địa chỉ ô nhớ cũ và render ra dữ liệu cũ. Việc import cả module giúp đảm bảo dữ liệu hiển thị trên Web luôn cập nhật đồng bộ 100%.

### Quyết định 4: Sử dụng `env_loader.py` có sẵn để load file `.env`
*   **Lựa chọn:** Sử dụng hàm `load_lab_env` viết bằng thư viện thuần (standard library) của Python có sẵn trong `starter_v0/env_loader.py` thay vì cài đặt thư viện bên ngoài `python-dotenv`.
*   **Tại sao?:** 
    - Tránh phát sinh lỗi `ModuleNotFoundError` khi chạy trên các máy ảo hoặc môi trường test chưa được cài đặt thư viện ngoài.
    - Giảm thiểu tối đa dependencies bên ngoài, giúp hệ thống hoạt động cực kỳ nhẹ nhàng và dễ triển khai.

### Quyết định 5: Cơ chế lưu vết Trace log định dạng JSON trong `eval/traces/`
*   **Lựa chọn:** Tự động ghi lại kết quả gọi AI bao gồm prompt, raw response từ API và dữ liệu JSON đã phân tích thành các file `trace_<timestamp>.json` đặt tại `eval/traces/`.
*   **Tại sao?:** 
    - Đáp ứng trực tiếp yêu cầu của Checkpoint 3 về việc lưu lại dấu vết (trace) hoạt động của AI trong repo để đo đạc độ tin cậy và phục vụ đánh giá sau này.

### Quyết định 6: Giao diện Fallback dán Text tài liệu
*   **Lựa chọn:** Nếu việc cào repo từ GitHub trả về lỗi (do repo private hoặc không tìm thấy README), hệ thống sẽ hiển thị một soft warning cùng khung Textarea để người dùng dán thủ công tài liệu vào.
*   **Tại sao?:** 
    - Đảm bảo trải nghiệm người dùng không bị gián đoạn (Graceful Failure). Ngay cả khi API GitHub bị giới hạn (rate limit) hoặc không có quyền truy cập, người dùng vẫn có thể tiếp tục sử dụng tính năng phân chia vai trò bằng cách dán nội dung đề bài trực tiếp.
