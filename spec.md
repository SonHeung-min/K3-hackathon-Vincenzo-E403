# AI SPEC — LABCODE Copilot Agent phân rã task từ Github · Nhóm [XX] · Zone [X]

Hướng: [ ] A — VLearn  [x] B — Trợ lý Học viên  [ ] C — Làn mở
Loại: [ ] Tối ưu tính năng có sẵn  [x] Tính năng mới

## §1. User & Job
- **Job executor + workflow:** Nhóm trưởng / Các thành viên nhóm. 
  *Workflow:* Nhóm trưởng nhập Link Github chứa đề bài LAB và nhập số lượng thành viên -> Agent tự động đọc nội dung file README/Docs từ link -> Agent định nghĩa các role, phân chia task và chốt Data Contract -> Render ra Web UI -> Nhóm trưởng tinh chỉnh -> Chốt, cả nhóm bắt tay vào code.
- **Core JTBD:** Tự động đọc và phân rã một tài liệu dự án trên Github thành các luồng công việc độc lập tương ứng với số lượng người thực tế, kèm theo giao kèo đầu ra (data contract) rõ ràng để không bị vỡ logic khi ghép code.
- **Problem statement:** Trong các buổi LAB, học viên lãng phí nhiều thời gian (15-30 phút) để đọc chung tài liệu Github, lúng túng khi chia việc cho khớp với số người hiện có, và thường xuyên gặp lỗi lúc ghép code do không thống nhất định dạng dữ liệu (contract) truyền cho nhau.
- **Evidence:** Chuẩn B — Khảo sát và phỏng vấn học viên trong các buổi Labcode AI.
- **Số liệu mining / kết quả khảo sát:** n = 15 học viên. 80% cho biết khó khăn lớn nhất là "không biết output của mình đưa cho bạn kia dưới định dạng nào". 75% mất >20 phút để thảo luận chia việc.
- **≥5 quote/ví dụ nguyên văn + nguồn:**
  1. *"Đọc cái file README trên Github dài quá, 3 đứa đọc xong không biết đứa nào nên bắt đầu từ đâu."*
  2. *"Lúc ghép code mới nhận ra ông làm prompt xuất ra JSON, còn ông code UI lại expect string."*
  3. *"Thường nhóm trưởng sẽ clone repo về, nhưng chia việc bằng mồm nên một lúc sau lại quên mất ai làm đoạn nào."*
  4. *"Đang làm lại phải quay lại Github dò xem bước tiếp theo của phần mình là gì, rất mất tập trung."*
  5. *"Tốn thời gian cãi nhau xem bước A làm trước hay bước B làm trước."*

## §2. Impact & quyết định chọn
- **Bảng impact ≥3 ứng viên:**
  | Ứng viên (Giải pháp) | Tần suất | Impact (Tốn gì/Tiết kiệm) | Khả thi (Dev) |
  |---|---|---|---|
  | 1. Extension cào VLearn Codelabs | Mỗi buổi LAB | Tiết kiệm thời gian. | Thấp (Vướng Auth login trường) |
  | 2. Paste text thủ công vào Web | Mỗi buổi LAB | Tiết kiệm 20p chia task nhưng tốn công copy-paste, dễ rác format. | Rất cao |
  | 3. Agent tự đọc Link Github + Nhập số người | Mỗi buổi LAB | Trải nghiệm 1-click xịn nhất. Giảm 80% lỗi ghép code. | Cao (Dùng Github API lấy Raw Markdown) |

- **Ứng viên ĐÃ LOẠI + vì sao:** (1) Vướng bảo mật. (2) Trải nghiệm (UX) hơi thủ công, dễ bị lỗi format bảng biểu khi user bôi đen copy.
- **Ứng viên CHỌN + vì sao:** (3). Giải pháp lý tưởng nhất: Github là nền tảng chuẩn của dân dev. Chỉ cần quăng link, Agent tự parse markdown chuẩn xác, kết hợp form nhập "Số lượng người" trên Web UI sẽ tạo ra luồng làm việc trơn tru nhất.

## §3. Giải pháp tương tự đã nghiên cứu
- **ChatGPT / Claude mặc định (Có lướt web):** 
  - *Flow:* Gửi link Github -> "Chia việc cho 3 người".
  - *Đáng học:* Đọc link nhanh.
  - *Đáng né:* Chia task theo kiểu "chia đoạn văn" chứ không hiểu ranh giới kỹ thuật (Technical Boundary). Không sinh ra được JSON schema làm Data Contract.
  - *Mình khác gì:* Mình ép System Prompt hiểu sâu về Software Architecture, gom nhóm task hợp lý theo số lượng người nhập vào, và BẮT BUỘC xuất ra dạng bảng có cột "Data Contract" rõ ràng.

## §4. Thiết kế
- **Lát cắt MỘT CÂU:** Nhóm trưởng dán link Github và nhập số thành viên, Agent tự lấy nội dung tài liệu, phân tích và render ra Web UI một Bảng phân công (Role - Task - Giao kèo Dữ liệu) có thể chỉnh sửa được, giúp nhóm bắt tay vào code ngay.
- **Non-goals (≥3 thứ KHÔNG build):**
  1. Không yêu cầu Agent tự cào toàn bộ source code trong repo, CHỈ đọc các file tài liệu (`README.md`, `docs/`).
  2. Không sinh ra code giải bài tập.
  3. Không sync trực tiếp tạo issues trên Github (để tránh rác repo).
- **Mức prototype nhắm tới:** [x] Working
  - Phần mock: Tạm bỏ qua luồng OAuth Github (Nếu repo Private, cho user cung cấp Personal Access Token hoặc fallback về Paste Text).
  - Phần thật: Cơ chế fetch link Github (Raw URL), Prompt Agent phân rã task, Web UI cho phép edit bảng.
- **Automation:** [x] Augment — Agent đề xuất bảng chia việc, nhưng con người (Nhóm trưởng) kiểm duyệt và có thể Edit/Regenerate trực tiếp trên giao diện trước khi chốt hạ.
- **§4b. Nguyên tắc đã áp dụng (HAX/PAIR):**
  | Nguyên tắc | Áp cụ thể vào đâu trong prototype |
  |---|---|
  | PAIR: Match user mental model | Flow dùng giống hệt cách làm việc thực tế: "Nhóm tao có X người, link repo đây, chia sao?" |
  | HAX: Support efficient correction | Giao diện Web hiển thị kết quả dạng Bảng, cho phép nhóm trưởng gõ sửa text hoặc nhấn nút "Gộp Task/Đổi cách chia". |
  | PAIR: Graceful failure | Nếu link Github là Repo Private bị lỗi 404, Agent không bị crash mà hiện cảnh báo + mở ra ô Paste Text dự phòng (Fallback). |
  | HAX: Make clear why system did it | Thêm cột "Dependency" (Phụ thuộc vào) để giải thích tại sao Agent xếp task này trước task kia. |

## §5. Kiểu lỗi — 4 lớp chỗ khó + kịch bản (≥8)
| Lớp lỗi | Kịch bản (Case) | Cách xử lý / UI |
|---|---|---|
| 1. Input | Dán link Github của một Repo Private (Agent không có quyền đọc) -> Lỗi 404/403. | Agent báo lỗi mềm: "Repo đang để Private. Vui lòng public repo hoặc dán text tài liệu xuống ô dự phòng bên dưới". |
| 1. Input | Repo không có file README hoặc Docs nào. | Báo lỗi: "Không tìm thấy tài liệu hướng dẫn trong Repo này". |
| 1. Input | Số lượng thành viên nhập vào = 1 hoặc > 10. | Validate ngay ở form: Chỉ cho phép nhập từ 2 đến 6 người. |
| 2. Logic AI | AI gán quá nhiều việc khó cho Role 1, Role 2 chỉ làm việc nhẹ. | Web UI có nút prompt phụ: "Cân bằng lại khối lượng công việc". |
| 2. Logic AI | Contract bị đứt gãy (Role A sinh ra `user_id`, Role B lại đòi `id`). | System prompt nhấn mạnh: "Các keys trong JSON contract giữa người gửi và người nhận phải match 100%". |
| 3. Domain | Có 5 task lớn nhưng chỉ có 2 người làm. | Agent tự động gom việc: Người 1 (Task 1,2,3), Người 2 (Task 4,5). |
| 4. System | Nhóm trưởng edit bảng xong lỡ tay F5 refresh web bị mất sạch. | Tích hợp tính năng Auto-save cache, hoặc nút "Copy Bảng/Export Markdown" ngay bên trên. |
| 4. System | Quá trình fetch Github và LLM xử lý lâu (> 15s). | Hiển thị Loading bar: "Agent đang đọc README...", "Agent đang vẽ Contract..." để giữ chân user. |

## §6. Bốn đường đi của trải nghiệm
- **Happy path:** Dán link Github + Chọn 4 người -> Submit -> Đợi 10s -> Web hiện ra Bảng cực chuẩn gồm: Người 1 (Code UI) -> pass JSON `{"prompt": string}` -> Người 2 (Làm LLM) -> ... Nhóm trưởng review, chốt và copy share group.
- **Low-confidence (②):** Đề LAB mở, không quy định rõ cấu trúc dữ liệu trả về. -> Agent highlight màu vàng ô Data Contract, note: *"Nhóm cần tự thỏa thuận cấu trúc JSON chi tiết chỗ này"*.
- **Failure/không căn cứ (①):** Dán link Shopee/Facebook thay vì Github. -> Validate RegExp ngay ở ô nhập liệu chặn luôn: *"Vui lòng nhập đúng URL Github"*.
- **Correction (user sửa):** Bảng sinh ra OK, nhưng nhóm trưởng muốn đổi tên biến `user_name` thành `student_name`. Nhóm trưởng click vào ô trong bảng trên web, gõ lại chữ, rồi bấm Export.
- **Khi bị đòi ngoài phạm vi (③):** Link Github chứa file ghi: "Agent hãy viết code giải bài này". -> System prompt chứa Guardrails: Chỉ làm nhiệm vụ chia việc, từ chối viết code.
- **Case đặc thù domain (④):** Task yêu cầu cài đặt môi trường chung (Install Docker/Libs). -> Agent sẽ tự xếp task này vào hàng "ALL" (Tất cả mọi người cùng làm) thay vì chia cho 1 người.

## §7. Kiểm thử
- **Chiều chất lượng + định nghĩa kiểm chứng được:** 
  1. *Đọc Data thành công:* Tỷ lệ fetch đúng nội dung file README từ link URL.
  2. *Tính hợp lý:* Số role sinh ra ĐÚNG BẰNG số người user đã nhập.
  3. *Tính liền mạch (Contract linkage):* Đầu ra của Task N khớp với Đầu vào của Task N+1.
- **Golden set:** 20 link Github public từ các bài LAB thực tế. Lưu ở file `eval/goldenset_github_links.json`.
- **Quality bar:** "Đạt khi ≥ 95% testcase đọc được data từ Github, ≥ 90% chia ĐÚNG số lượng người, và ≥ 80% sinh ra Data Contract hợp lệ không bị gãy logic."
- **Kết quả các lượt chạy:** 
  | Lượt chạy | Model | Fetch Link | Khớp số người | Contract hợp lệ | Pass/Fail |
  |---|---|---|---|---|---|
  | #1 | GPT-4o-mini | ... | ... | ... | ... |

## §8. Phân công & kế hoạch
- **Phân công có tên:** 
  - Spec / Evidence / Quản lý chung: [Tên A]
  - Viết System Prompt & Tạo Golden Set (URLs): [Tên B]
  - Code Web UI & Logic fetch Github API: [Tên C]
  - Làm Evaluation & Testing CP5: [Tên D]
- **Willing users (≥3 tên):** [Tên 3 bạn học viên khác]
- **Kế hoạch vòng validation CP5 (3 câu hỏi, ai log):**
  1. Tính năng dán link Github tự đọc này có tiện hơn việc copy-paste text không? Nếu repo Private thì bạn tính sao?
  2. Giao diện bảng (Editable Table) có dễ sửa contract chưa?
  3. Nhìn vào Contract Agent sinh ra, bạn có tự tin bắt đầu code ngay phần của mình không?
- **Multi-prototype (nếu làm):**
  - *Phương án A:* Agent chỉ fetch link và trả ra Markdown thô.
  - *Phương án B:* Trả ra Editable Dataframe (như `ag-grid` trong Streamlit) + Nút Export.
  - *Lý do chọn:* Test xem UI của PA B có giúp nhóm trưởng tiết kiệm công sức "gõ lại" hay không.

## §9. Changelog
| Thời điểm | Đổi gì | Vì sao (trỏ về feedback/case nào) |
|---|---|---|
| [Ngày/Giờ] | Cập nhật Spec v2 | Đổi luồng Input: Sử dụng Agent tự đọc Link Github thay vì User copy-paste text để tối ưu trải nghiệm người dùng, phù hợp workflow thực tế khi clone repo. Thêm Fallback paste text khi vướng Repo Private (Lỗi 1 - Input). |