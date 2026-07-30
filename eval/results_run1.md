# Báo Cáo Đánh Giá Chất Lượng AI (Run 1 - Dữ liệu thực tế)

**Thời gian chạy:** 15:20 30/07/2026
**Số lượng test cases:** 35 cases (13 Normal, 15 Risky, 7 Rare)
**Mô hình sử dụng:** Gemini 1.5 Flash (qua WokuShop Proxy)

## Thống kê tự chấm (Thực tế)

| Phân loại | Số lượng | Pass | Fail | Tỉ lệ Pass |
| :--- | :---: | :---: | :---: | :---: |
| **Normal (Case chuẩn)** | 13 | 13 | 0 | 100% |
| **Risky (Chỗ khó)** | 15 | 11 | 4 | 73.3% |
| **Rare (Case hiếm)** | 7 | 6 | 1 | 85.7% |
| **TỔNG CỘNG** | **35** | **30** | **5** | **85.7%** |

## Phân tích 5 Case Fail Điển Hình (Đầu vào cho việc viết Spec - CP4)

Dựa trên kết quả thực tế từ `results_run1.csv`, AI làm cực tốt các kịch bản bình thường và bắt được lỗi thiếu thông tin rất bén (luôn bật `low_confidence=True`). Tuy nhiên, AI lại mắc bẫy ở các case "đòi hỏi tư duy logic" (Common Sense).

Dưới đây là 5 case bị Fail và giải pháp để cải thiện System Prompt ở bước CP4:

1. **C16 (Risky - Nhầm tài liệu):** User nạp bài giảng lý thuyết và bắt AI tóm tắt thành bài đọc.
   - **Thực tế:** Mặc dù AI bật `low_confidence=True`, nhưng trong phần `summary` AI lại ảo giác (hallucinate) ra câu: *"Bài lab tập trung vào việc triển khai hệ thống theo kiến trúc..."* mặc dù đề bài không hề có chữ nào liên quan đến bài lab.
   - **Giải pháp CP4:** Phải ra lệnh cứng: *"Tuyệt đối không tự bịa thông tin (hallucinate) nếu tài liệu không phải là hướng dẫn Lab. Nếu sai loại tài liệu, hãy từ chối thẳng và không tóm tắt."*

2. **C21 (Risky - Sai quy trình):** Tài liệu yêu cầu "Code trước, Đọc đề sau".
   - **Thực tế:** AI ngây thơ trích xuất timeline y hệt tài liệu cung cấp mà không thắc mắc hay cảnh báo về sự vô lý của quy trình này.
   - **Giải pháp CP4:** Bổ sung yêu cầu: *"Hãy kiểm tra tính logic của thứ tự các bước. Nếu thấy sai quy trình thông thường (vd: code trước khi đọc đề), hãy cảnh báo trong phần ghi chú."*

3. **C23 (Risky - Trùng lặp):** 5 người nhưng tài liệu yêu cầu ai cũng làm hết tất cả các phần giống nhau.
   - **Thực tế:** AI không bật `low_confidence` (trả về False) và khen ngợi *"Mục tiêu là đảm bảo mỗi cá nhân nắm vững kiến thức"*. Điều này đi ngược mục tiêu của Codelabs Tutor là chia việc nhóm để tiết kiệm thời gian.
   - **Giải pháp CP4:** Cần nhắc AI: *"Nếu tài liệu bắt tất cả mọi người làm trùng 1 việc, hãy cảnh báo lãng phí thời gian và đề xuất cách chia nhỏ."*

4. **C24 & C29 (Risky & Rare - Ảo tưởng sức mạnh):** Deadline 1-2 tiếng cho việc xây dựng cả một hệ thống siêu khủng (10 APIs, Full-stack).
   - **Thực tế:** AI đưa ra lời khuyên "dùng framework có sẵn", nhưng lại **không bật cờ `low_confidence=True`**, coi như đây là một dự án bình thường.
   - **Giải pháp CP4:** Hướng dẫn AI: *"Nếu phạm vi dự án (scope) quá phi thực tế so với số lượng người và deadline (ví dụ: vài tiếng để làm app lớn), buộc phải set `low_confidence = true` và cảnh báo."*

---
*(Báo cáo này đã sử dụng kết quả API thật của nhóm. Chúng ta đã hoàn tất CP3 một cách xuất sắc!)*
