# Feedback Log - CP5

Sản phẩm test: LABCODE Copilot  
Ngày test: 31/07/2026  
Mục tiêu test: kiểm tra prototype có giúp học viên hiểu mục tiêu lab, task của mình, phần của teammate, và các đầu ra cần nộp hay không.
Số người test: 5  
Tất cả người test: ngoài nhóm  
Willing user từ CP1: Trần Thị Kiều Oanh, Lê Thị Thúy, Phí Đình Hoàng Anh, Ngô Đình Khánh  

## Kịch bản test chung

Người test được yêu cầu:

1. Mở prototype LABCODE Copilot.
2. Dùng link repo/tài liệu lab mẫu để AI phân tích.
3. Xem mục tiêu lab, timeline, deliverables và role/task.
4. Chọn một role như phần mình được giao.
5. Nhận xét xem output có giúp hiểu phần mình và phần teammate liên quan thế nào không.

## Người test 1 - Trần Thị Kiều Oanh

- Vai trò: Học viên AI Thực Chiến
- Ngoài nhóm: Có
- Willing user từ CP1: Có
- Task test: Xem role Product/Spec và kiểm tra output cần nộp.
- Quan sát: Người test hiểu nhanh các đầu ra chính, nhưng cần citation rõ hơn cho từng deadline.
- Quote nguyên văn: "Mình biết phải làm phần nào nhanh hơn, nhưng deadline nên hiện sát từng task hơn chứ không chỉ nằm trong timeline."
- Mức nghiêm trọng: Medium
- Thay đổi đề xuất: Gắn deadline/checkpoint trực tiếp vào mô tả task.

## Người test 2 - Nguyễn Thế Khải

- Vai trò: Học viên AI Thực Chiến
- Ngoài nhóm: Có
- Willing user từ CP1: Không
- Task test: Xem role Builder và hỏi phần Eval liên quan gì tới demo.
- Quan sát: Người test thích phần chia role, nhưng nói nếu chỉ có task list thì vẫn chưa hiểu phần của người khác.
- Quote nguyên văn: "Nếu nó nói thêm task này phụ thuộc vào ai và output đưa cho ai thì dễ phối hợp hơn."
- Mức nghiêm trọng: High
- Thay đổi đề xuất: Bổ sung input/output giữa các role trong mô tả task.

## Người test 3 - Lê Thị Thúy

- Vai trò: Học viên AI Thực Chiến
- Ngoài nhóm: Có
- Willing user từ CP1: Có
- Task test: Xem role Prompt/Eval và kiểm tra phần golden set.
- Quan sát: Người test hiểu cần làm golden set, nhưng chưa rõ golden set ảnh hưởng gì tới phần demo.
- Quote nguyên văn: "Mình làm eval thì hiểu việc của mình, nhưng cần một câu giải thích vì sao demo cần số này."
- Mức nghiêm trọng: Medium
- Thay đổi đề xuất: Mỗi role cần có note giải thích đóng góp vào mục tiêu lab/demo.

## Người test 4 - Phí Đình Hoàng Anh

- Vai trò: Học viên AI Thực Chiến
- Ngoài nhóm: Có
- Willing user từ CP1: Có
- Task test: Dùng chat để yêu cầu sửa deadline và thêm role Tester.
- Quan sát: Chat sửa được kế hoạch, nhưng người test cần biết thay đổi đó ảnh hưởng role nào.
- Quote nguyên văn: "Sửa deadline được là ổn, nhưng sau khi sửa nên thấy ai bị ảnh hưởng."
- Mức nghiêm trọng: Medium
- Thay đổi đề xuất: Khi cập nhật plan, note rõ role nào đổi task/deadline.

## Người test 5 - Ngô Đình Khánh

- Vai trò: Học viên AI Thực Chiến
- Ngoài nhóm: Có
- Willing user từ CP1: Có
- Task test: Thử case tài liệu thiếu đầu ra.
- Quan sát: Prototype báo cần hỏi lại thay vì bịa output. Người test đánh giá đây là hành vi cần thiết.
- Quote nguyên văn: "Thiếu yêu cầu nộp mà nó hỏi lại thì tốt hơn là tự đoán, vì sai output là mất điểm."
- Mức nghiêm trọng: Low
- Thay đổi đề xuất: Giữ hành vi low-confidence, không tự bịa deadline/deliverables.

## Tổng hợp sau 5 lượt test

### Pattern lặp lại

- 4/5 người test hiểu nhanh hơn danh sách việc cần làm sau khi xem role/task.
- 3/5 người muốn task thể hiện rõ dependency: cần input từ ai và output đưa cho ai.
- 2/5 người nói phần deadline/checkpoint cần gắn sát task hơn.
- 2/5 người cần AI giải thích rõ hơn vì sao role của mình đóng góp vào demo hoặc mục tiêu lab.

### Thay đổi đã làm trước demo

- Bổ sung yêu cầu trong system prompt: mỗi task phải nêu mục tiêu lab liên quan, input cần từ role nào, output đưa cho role nào, và điều tối thiểu cần hiểu về phần teammate.
- Bổ sung yêu cầu trong note của mỗi role: vai trò này đóng góp gì vào mục tiêu lab và cần hiểu gì về các role còn lại để demo/Q&A.
- Đổi link GitHub mặc định sang repo thật của nhóm để tránh lỗi 404 khi mở prototype.

### Giữ nguyên có lý do

- Vẫn giữ flow chia role/task vì đây là bề mặt dễ demo và phù hợp với README lab hiện có.
- Chưa build hệ thống tracking phức tạp vì CP5 ưu tiên chứng minh AI phân tích và hỗ trợ hiểu/phối hợp trong lab.

### Backlog nếu có thêm 1 tuần

- Hiển thị dependency giữa role bằng sơ đồ.
- Thêm chế độ "Tôi làm phần X, giải thích phần Y của teammate".
- Tự tạo 3 câu hỏi Q&A cho từng thành viên trước demo.
