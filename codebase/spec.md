# Product Specification: LABCODE Copilot (CP4)

## 1. Vấn đề & Giải pháp
**Vấn đề:** 
Trong các buổi Lab/Hackathon, sinh viên thường phải đối mặt với các tài liệu hướng dẫn (Lab Manual) dài và phức tạp. Việc các thành viên đều phải đọc từ đầu đến cuối và tự chia việc thủ công thường gây lãng phí thời gian, phân công chồng chéo, và trễ deadline.

**Giải pháp:** 
LABCODE Copilot là một trợ lý AI thông minh giúp tự động đọc tài liệu Lab, bóc tách các yêu cầu, tạo ra một bảng Timeline (Lộ trình thời gian), và phân chia công việc thành các Vai trò chuyên biệt (Roles) dựa trên số lượng thành viên của nhóm.

## 2. Quyết định của AI (AI Core Decision)
> **AI quyết định cách bóc tách một tài liệu hướng dẫn thực hành (Lab) nguyên khối thành các nhiệm vụ độc lập, từ đó phân bổ chúng vào các vai trò chuyên biệt (Roles) phù hợp với số lượng thành viên nhóm — sử dụng model `gemini-1.5-flash`.**

Lý do chọn `gemini-1.5-flash`: (1) Hỗ trợ Context Window khổng lồ phù hợp với tài liệu Lab siêu dài, (2) Tốc độ phản hồi (Low Latency) cực nhanh cho Web App, và (3) Khả năng tuân thủ định dạng JSON cứng (Structured Output) xuất sắc.

## 3. Kiến trúc Hệ thống (System Architecture)
Để giải quyết các rào cản kỹ thuật và mang lại trải nghiệm tối ưu nhất, kiến trúc sản phẩm hoàn chỉnh được thiết kế theo mô hình **Continuous Copilot (Không gian làm việc song song)**:

1. **Vượt rào đăng nhập (Data Scraping):** 
   - Backend Python (hoặc Chrome Extension) chịu trách nhiệm cào dữ liệu từ Link VLearn/Github. Hệ thống cung cấp Tool `fetch_web_content` cho AI gọi để tự động kéo nội dung về.
2. **Kiến trúc Split-Screen (Màn hình đôi):**
   - **Workspace (Bên trái):** Hiển thị bảng Dashboard kết quả phân công (Kanban, Roles, Timeline) dưới dạng giao diện trực quan.
   - **Persistent Chat (Bên phải):** Khung chat AI luôn túc trực, đồng hành cùng nhóm.
3. **Luồng hội thoại & Tương tác liên tục:**
   - **Clarification:** Nếu tài liệu mập mờ, AI đặt câu hỏi làm rõ qua khung Chat.
   - **Execution:** Khi rõ ràng, AI chốt hạ bằng khối JSON `[FINAL_PLAN]` để hệ thống vẽ Dashboard bên trái.
   - **Modification (Sức mạnh cốt lõi):** Sinh viên có thể chat tiếp bất cứ lúc nào để yêu cầu tinh chỉnh (VD: "Sửa deadline thành 17h và thêm 1 role Tester"). AI tự động cập nhật khối JSON ẩn, làm Dashboard bên trái thay đổi tức thì, tạo ra một vòng lặp tinh chỉnh liên tục.

## 4. Bộ Kiểm thử & Chuẩn đạt (Evaluation Framework)
Hệ thống sử dụng phương pháp phát triển dẫn dắt bởi kiểm thử (Test-driven).
*   **Kích thước Golden Set:** 35 Test Cases (được trích xuất trực tiếp một phần từ lịch sử Chatlog thực tế của sinh viên).
*   **Bao phủ 4 Tình huống Risky (Điểm mù của AI):**
    1. Thiếu nguồn sự thật (Không có deadline/đầu ra).
    2. Thiếu ngữ cảnh (Nạp 2 tài liệu cùng lúc).
    3. Ngoài phạm vi (Bắt tính điểm, bắt code hộ).
    4. Đặc thù Domain (Quy trình sai logic, chia việc vô nghĩa).
*   **Tiêu chuẩn chốt (Threshhold):**
    - `≥ 80%` câu thử đạt (Đo thực tế trên Run 1: **85.7%** - 30/35 câu).
    - **Lằn ranh đỏ (Zero Tolerance):** AI KHÔNG được phép tự bịa (hallucinate) hạn nộp bài (deadline) hoặc yêu cầu đầu ra (deliverables) dù chỉ một lần. Lỗi này gây hậu quả trực tiếp khiến sinh viên rớt môn.

## 5. Quy tắc Prompt Nâng cấp (System Prompt Upgrades)
Rút kinh nghiệm từ 5 lỗi sai trong đợt chạy đánh giá (Run 1), System Prompt của AI được thiết lập thêm các ràng buộc thép sau:
1. **Chống ảo giác tài liệu:** *Tuyệt đối không tự bịa thông tin nếu người dùng nhập bài giảng lý thuyết. Bắt buộc từ chối.* (Fix Case C16)
2. **Kiểm tra Logic Quy trình:** *Hãy kiểm tra tính logic của thứ tự các bước trong tài liệu. Nếu thấy sai quy trình thông thường (vd: bắt code trước khi đọc đề bài), phải cảnh báo.* (Fix Case C21)
3. **Cảnh báo trùng lặp:** *Nếu tài liệu bắt mọi người làm trùng 1 việc giống hệt nhau, hãy cảnh báo sinh viên về sự lãng phí thời gian và đề xuất cách chia nhỏ.* (Fix Case C23)
4. **Kiểm soát Phạm vi:** *Nếu phạm vi dự án (scope) quá phi thực tế so với số lượng người và deadline, buộc phải set cờ `low_confidence = true` và đưa ra giải pháp giảm tải.* (Fix Case C24, C29)
