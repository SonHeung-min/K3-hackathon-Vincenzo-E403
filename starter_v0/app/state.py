DEFAULT_GIT_LINK = "https://github.com/nhom-demo/labcode-cp2"
DEFAULT_LAB_LINK = "https://vlearn.vinuni.edu.vn/labcode/ai-product-hackathon/cp2"

SAMPLE_DOC = """Buổi LABCODE: AI Product Hackathon

Mục tiêu:
- Nhóm cần chọn một pain cụ thể, có bằng chứng, và build prototype một tính năng AI.
- CP2 yêu cầu prototype Sketch/Mock: flow chính bấm đi hết được, có commit đầu.
- CP3 yêu cầu ít nhất một lời gọi AI thật ở quyết định trung tâm, có log/trace trong repo.
- CP4 chốt spec gần cuối, có automation, HAX/PAIR, rủi ro và quality bar.
- CP5 validate với ít nhất 5 người ngoài nhóm, có quote nguyên văn và changelog.

Cần làm song song:
1. Evidence: mining hoặc khảo sát để chứng minh pain.
2. Build flow: giao diện bấm được cho demo 5 phút.
3. Prompt và golden set: tạo case thường, case khó, case thiếu thông tin.
4. Spec: ghi rõ lát cắt, non-goals, automation và tiêu chí đo.
5. Demo: chuẩn bị happy path và case lỗi được xử lý.

Ràng buộc:
- Không commit API key.
- Chỉ dùng data giả hoặc data pack được phép.
- Khi AI không chắc, phải nói rõ và hỏi lại, không đoán liều."""

RISKY_DOC = """Buổi LABCODE: Tài liệu bị thiếu

Nhóm cần nộp sản phẩm đúng hạn. Hãy chia việc cho từng người.

Thông tin còn thiếu:
- Chưa có danh sách checkpoint.
- Chưa có yêu cầu đầu ra.
- Chưa có số thành viên và vai trò mong muốn."""

NORMAL_ANALYSIS = {
    "summary": [
        "Nhóm cần biến tài liệu LABCODE dài thành một kế hoạch hành động ngắn gọn.",
        "CP2 chỉ cần prototype Sketch/Mock bấm được hết flow chính.",
        "CP3 mới bắt buộc nối AI thật vào quyết định trung tâm và lưu trace.",
        "Mỗi vai trò cần có task riêng, nguồn liên quan, và trạng thái tiến độ.",
        "Khi tài liệu thiếu thông tin, trợ lý phải báo giới hạn và hỏi lại.",
    ],
    "timeline": [
        "Chốt lát cắt một câu và pain cần giải quyết.",
        "Dựng nhanh flow chính: nạp tài liệu, phân tích, chia vai, theo dõi.",
        "Tạo prompt/golden set cho case thường và case khó.",
        "Nối AI thật ở CP3 và chạy đo lượt đầu.",
        "Validate với user thật, sửa prototype, chuẩn bị demo.",
    ],
    "deliverables": [
        ("codebase/", "Prototype CP2 bấm được."),
        ("spec.md", "Lát cắt, automation, rủi ro, quality bar."),
        ("eval/", "Golden set và kết quả đo."),
        ("validation/", "Feedback log từ user test."),
    ],
}

RISKY_ANALYSIS = {
    "summary": [
        "Tài liệu không đủ căn cứ để chia việc chính xác.",
        "Chưa có checkpoint, đầu ra, và số thành viên.",
        "Trợ lý chỉ nên tạo khung tạm và yêu cầu bổ sung thông tin.",
        "If vẫn chia việc, mọi task phải gắn nhãn cần xác minh.",
        "Case này dùng để demo hành vi low-confidence.",
    ],
    "timeline": [
        "Hỏi lại người dùng về checkpoint và đầu ra.",
        "Tạm chia 4 nhóm việc chung: đọc tài liệu, build, prompt, demo.",
        "Đánh dấu tất cả task là cần xác minh.",
        "Cập nhật lại sau khi có tài liệu đầy đủ.",
    ],
    "deliverables": [
        ("Cần xác minh", "Deadline và checkpoint."),
        ("Cần xác minh", "Danh sách đầu ra."),
        ("Cần xác minh", "Thành viên và kỹ năng."),
        ("Khung tạm", "Task nháp cho nhóm."),
    ],
}

ROLES = [
    {
        "id": "pm",
        "name": "Product Lead",
        "member": "Bạn A",
        "focus": "Lát cắt, ưu tiên, demo script",
        "tasks": [
            ("Chốt lát cắt một câu", "Viết rõ 1 user, 1 việc, 1 quyết định AI, 1 kết quả."),
            ("Kiểm tra non-goals", "Loại các tính năng quá lớn như quản lý dự án đầy đủ."),
            ("Chuẩn bị demo 5 phút", "Chọn 1 happy path và 1 case thiếu thông tin."),
        ],
        "output": "Lát cắt một câu, non-goals, demo script CP2.",
        "source": "Guide §3.1, §3.2 và rubric R2/R5.",
        "note": "AI gợi ý Product Lead vì vai này cần nối pain, prototype và demo thành một câu chuyện thống nhất.",
    },
    {
        "id": "builder",
        "name": "Prototype Builder",
        "member": "Bạn B",
        "focus": "UI bấm được và trạng thái của flow",
        "tasks": [
            ("Dựng flow 4 bước", "Nạp tài liệu, xem phân tích, chia vai trò, theo dõi tiến độ."),
            ("Làm trạng thái low-confidence", "Khi tài liệu thiếu, hiện cảnh báo và câu hỏi cần bổ sung."),
            ("Đảm bảo demo không cần can thiệp tay", "Tất cả màn hình chuyển bằng nút bấm."),
        ],
        "output": "Prototype Python mock chạy được và bấm hết flow.",
        "source": "Guide §3.1: CP2 flow chính bấm đi hết được.",
        "note": "AI chưa cần thật ở CP2; lời gọi AI thật sẽ nối vào nút Phân tích tài liệu ở CP3.",
    },
    {
        "id": "prompt",
        "name": "Prompt & Eval",
        "member": "Bạn C",
        "focus": "Prompt phân tích tài liệu và golden set",
        "tasks": [
            ("Viết prompt đầu tiên", "Bắt AI trả JSON gồm mục tiêu, đầu việc, đầu ra, vai trò, citations."),
            ("Tạo 20 case golden set", "Có case thường, case khó, case thiếu thông tin và ngoài phạm vi."),
            ("Định nghĩa quality bar", "Ví dụ đạt khi 80% case pass và 100% case không có căn cứ không bị đoán liều."),
        ],
        "output": "Prompt nháp, cấu trúc JSON, golden set bản đầu.",
        "source": "Guide §2.6 và rubric R4.",
        "note": "Đây là người sẽ biến mock CP2 thành AI thật CP3.",
    },
    {
        "id": "evidence",
        "name": "Evidence Lead",
        "member": "Bạn D",
        "focus": "Bằng chứng pain và validation",
        "tasks": [
            ("Khảo sát 20 học viên", "Hỏi lần gần nhất đọc tài liệu LABCODE mất bao lâu và kẹt ở đâu."),
            ("Giữ quote nguyên văn", "Lưu câu hỏi, câu trả lời, tên/vai trò người trả lời."),
            ("Chuẩn bị 5 user test", "Đặt lịch test 10 phút cho CP5."),
        ],
        "output": "Log khảo sát/mining, quote nguyên văn, danh sách user test.",
        "source": "Guide §1.3 và §4.2.",
        "note": "Không có bằng chứng thì slide và spec sẽ yếu, dù prototype bấm rất mượt.",
    },
    {
        "id": "spec",
        "name": "Spec Owner",
        "member": "Bạn E",
        "focus": "Spec, rủi ro, changelog",
        "tasks": [
            ("Lập 8 kịch bản rủi ro", "Phủ 4 lớp: nguồn sự thật, mơ hồ, ngoài phạm vi, domain."),
            ("Gắn HAX/PAIR vào prototype", "Mỗi nguyên tắc phải trỏ được vào một chỗ cụ thể trong UI."),
            ("Cập nhật changelog", "Mỗi thay đổi sau feedback cần có lý do."),
        ],
        "output": "Spec.md bản nháp có rủi ro, HAX/PAIR, quality bar.",
        "source": "Template spec §4-§9 và guide §2.5.",
        "note": "Vai này giúp nhóm không chỉ có màn hình, mà có chuỗi quyết định để được chấm điểm.",
    },
]

STATE = {
    "step": "upload",
    "git_link": DEFAULT_GIT_LINK,
    "lab_link": DEFAULT_LAB_LINK,
    "doc": SAMPLE_DOC,
    "low_confidence": False,
    "members": {role["id"]: role["member"] for role in ROLES},
    "role_tasks": {role["id"]: [task for task, _ in role["tasks"]] for role in ROLES},
    "role_outputs": {role["id"]: role["output"] for role in ROLES},
    "active_role": "pm",
    "done": {"pm": {"0"}},
    "num_members": 3,
    "error_msg": "",
    "show_fallback": False,
    "pasted_doc": "",
}

STEPS = [
    ("upload", "1", "Nạp tài liệu"),
    ("analysis", "2", "AI phân tích"),
    ("roles", "3", "Chia vai trò"),
    ("progress", "4", "Theo dõi"),
]

def active_analysis():
    return RISKY_ANALYSIS if STATE["low_confidence"] else NORMAL_ANALYSIS

def role_by_id(role_id):
    return next(role for role in ROLES if role["id"] == role_id)

def page_title():
    return {
        "upload": "Nạp link Git và link LABCODE",
        "analysis": "Tổng hợp thông tin lab",
        "roles": "Bổ sung vai trò và đầu ra",
        "progress": "Task riêng và tiến độ",
    }[STATE["step"]]
