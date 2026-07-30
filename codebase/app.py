from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import os
import sys
from urllib.parse import parse_qs


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
        "Nếu vẫn chia việc, mọi task phải gắn nhãn cần xác minh.",
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
}

STEPS = [
    ("upload", "1", "Nạp tài liệu"),
    ("analysis", "2", "AI phân tích"),
    ("roles", "3", "Chia vai trò"),
    ("progress", "4", "Theo dõi"),
]

STYLE = """
:root{--bg:#f5f7f4;--ink:#18201c;--muted:#647067;--panel:#fff;--line:#d9e1d9;--green:#2f7d52;--green-dark:#215b3d;--amber:#c77918;--shadow:0 16px 40px rgba(24,32,28,.08)}
*{box-sizing:border-box}body{margin:0;min-height:100vh;color:var(--ink);background:var(--bg);font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}button,textarea,input{font:inherit}button{cursor:pointer}.app-shell{display:grid;grid-template-columns:320px minmax(0,1fr);min-height:100vh}.sidebar{display:flex;flex-direction:column;gap:28px;padding:28px;color:#f7fbf7;background:#18201c}.sidebar h1,.topbar h2,.panel h3{margin:0;letter-spacing:0}.sidebar h1{margin-top:6px;font-size:32px;line-height:1.05}.subtle{color:#b6c6bb;line-height:1.55}.eyebrow{margin:0 0 8px;color:var(--green);font-size:12px;font-weight:750;text-transform:uppercase;letter-spacing:.08em}.sidebar .eyebrow{color:#8cd6ad}.steps{display:grid;gap:10px}.step{display:grid;grid-template-columns:34px 1fr;align-items:center;gap:12px;width:100%;padding:12px;color:#d8e5dc;background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.12);border-radius:8px;text-align:left}.step span{display:grid;place-items:center;width:34px;height:34px;border-radius:50%;color:#17211b;background:#d9efdf;font-weight:800}.step.is-active{color:#fff;border-color:#8cd6ad;background:rgba(140,214,173,.18)}.checkpoint{margin-top:auto;padding:18px;border:1px solid rgba(255,255,255,.14);border-radius:8px}.checkpoint ul{margin:0;padding-left:18px;line-height:1.7;color:#d8e5dc}.workspace{padding:28px}.topbar{display:flex;justify-content:space-between;gap:16px;align-items:center;margin-bottom:22px}.topbar h2{font-size:clamp(26px,4vw,42px)}.status-pill{min-width:112px;padding:9px 14px;border:1px solid var(--line);border-radius:999px;color:var(--green-dark);background:#edf7ef;text-align:center;font-weight:750}.panel{padding:22px;border:1px solid var(--line);border-radius:8px;background:var(--panel);box-shadow:var(--shadow)}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}.wide{grid-column:1/-1}.upload-panel{display:grid;gap:16px}.textarea-label{font-weight:750}textarea{min-height:280px;resize:vertical;width:100%;padding:16px;border:1px solid var(--line);border-radius:8px;color:#253029;background:#fbfcfb;line-height:1.55}.actions{display:flex;flex-wrap:wrap;gap:12px;margin-top:18px}.primary,.ghost{min-height:42px;padding:0 16px;border-radius:8px;font-weight:800}.primary{color:#fff;background:var(--green);border:1px solid var(--green)}.ghost{color:var(--ink);background:transparent;border:1px solid var(--line)}ul,ol{line-height:1.65}.deliverables,.roles-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}.deliverable,.role-card{padding:14px;border:1px solid var(--line);border-radius:8px;background:#f8faf8}.deliverable strong{display:block;margin-bottom:8px}.role-card{display:grid;gap:12px}.role-card label{color:var(--muted);font-size:13px;font-weight:700}.role-card input{width:100%;padding:10px 12px;border:1px solid var(--line);border-radius:8px}.role-toolbar{display:flex;align-items:center;justify-content:space-between;gap:16px;margin-bottom:16px}.progress-layout{display:grid;grid-template-columns:280px minmax(0,1fr);gap:16px}.role-tabs{display:grid;align-content:start;gap:10px}.role-tab{width:100%;padding:12px;border:1px solid var(--line);border-radius:8px;background:#f8faf8;text-align:left}.role-tab.is-active{border-color:var(--green);background:#edf7ef}.task-head{display:flex;justify-content:space-between;align-items:center;gap:16px;margin-bottom:18px}.progress-ring{display:grid;place-items:center;width:70px;height:70px;border:8px solid #d9eadd;border-top-color:var(--green);border-radius:50%;color:var(--green-dark);font-weight:850}.task-list{display:grid;gap:12px}.task-item{display:grid;grid-template-columns:auto 1fr;gap:12px;padding:14px;border:1px solid var(--line);border-radius:8px;background:#fbfcfb}.task-item input{width:18px;height:18px;margin-top:3px}.task-item strong{display:block;margin-bottom:4px}.task-item p{margin:0;color:var(--muted);line-height:1.5}.source-box,.ai-note{margin-top:16px;padding:16px;border-radius:8px;line-height:1.55}.source-box{border:1px solid #d6e1ef;background:#f2f7ff}.ai-note{border:1px solid #ead8bd;color:#6d4614;background:#fff8ed}@media(max-width:920px){.app-shell{grid-template-columns:1fr}.sidebar{min-height:auto}.grid,.roles-grid,.progress-layout,.deliverables{grid-template-columns:1fr}.topbar,.role-toolbar,.task-head{align-items:flex-start;flex-direction:column}}
.field-grid{display:grid;grid-template-columns:1fr 1fr;gap:14px}.field{display:grid;gap:8px}.field label{font-weight:750}.link-input,.edit-input,.mini-textarea{width:100%;padding:11px 12px;border:1px solid var(--line);border-radius:8px;color:#253029;background:#fbfcfb}.mini-textarea{min-height:74px}.link-preview{display:grid;gap:8px;margin-top:12px;color:var(--muted);font-size:14px}.summary-stat{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}.stat{padding:14px;border:1px solid var(--line);border-radius:8px;background:#f8faf8}.stat strong{display:block;font-size:24px;color:var(--green-dark)}.role-output{padding:12px;border:1px solid #d6e1ef;border-radius:8px;background:#f2f7ff;color:#24415f}.task-edit{display:grid;gap:8px}.task-edit label{color:var(--muted);font-size:13px;font-weight:700}@media(max-width:920px){.field-grid,.summary-stat{grid-template-columns:1fr}}
"""


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


def sidebar():
    buttons = []
    active_index = [step[0] for step in STEPS].index(STATE["step"])
    for index, (step_id, number, label) in enumerate(STEPS):
        disabled = "disabled" if index > active_index else ""
        active = " is-active" if step_id == STATE["step"] else ""
        buttons.append(
            f"""
            <form method="post">
              <input type="hidden" name="action" value="goto">
              <input type="hidden" name="step" value="{step_id}">
              <button class="step{active}" {disabled}>
                <span>{number}</span>
                <strong>{label}</strong>
              </button>
            </form>
            """
        )
    return f"""
    <aside class="sidebar">
      <div>
        <p class="eyebrow">AI Thực Chiến</p>
        <h1>LABCODE Copilot</h1>
        <p class="subtle">Trợ lý phân tích tài liệu LABCODE và điều phối công việc nhóm.</p>
      </div>
      <nav class="steps" aria-label="Các bước CP2">{''.join(buttons)}</nav>
      <section class="checkpoint">
        <p class="eyebrow">CP2 cần show</p>
        <ul>
          <li>Flow chính bấm hết được</li>
          <li>Data giả, chưa cần AI thật</li>
          <li>Có case thiếu thông tin</li>
          <li>Prototype chạy bằng Python</li>
        </ul>
      </section>
    </aside>
    """


def render_upload():
    return f"""
    <form method="post" class="panel upload-panel">
      <div>
        <p class="eyebrow">Nguồn đầu vào</p>
        <h3>Nạp link Git và link code lab</h3>
        <p>CP2 dùng link mẫu để chứng minh flow. Ở CP3, nút phân tích này sẽ gọi AI thật để đọc repo/lab link và lưu trace trong repo.</p>
      </div>
      <div class="field-grid">
        <div class="field">
          <label for="git_link">Link Git của nhóm</label>
          <input class="link-input" id="git_link" name="git_link" value="{escape(STATE["git_link"])}" placeholder="https://github.com/..." />
        </div>
        <div class="field">
          <label for="lab_link">Link code/tài liệu LABCODE</label>
          <input class="link-input" id="lab_link" name="lab_link" value="{escape(STATE["lab_link"])}" placeholder="https://vlearn... hoặc link bài lab" />
        </div>
      </div>
      <div class="source-box">
        <p class="eyebrow">AI sẽ phân tích gì?</p>
        <p>Repo để hiểu cấu trúc code/nơi nộp bài; link LABCODE để lấy mục tiêu, checkpoint, đầu ra, thứ tự làm và phần tài liệu liên quan.</p>
      </div>
      <div class="actions">
        <button class="primary" name="action" value="analyze">Phân tích</button>
        <button class="ghost" name="action" value="load_risky">Thử link thiếu thông tin</button>
      </div>
    </form>
    """


def render_analysis():
    data = active_analysis()
    summary = "".join(f"<li>{escape(item)}</li>" for item in data["summary"])
    timeline = "".join(f"<li>{escape(item)}</li>" for item in data["timeline"])
    deliverables = "".join(
        f'<div class="deliverable"><strong>{escape(title)}</strong><span>{escape(desc)}</span></div>'
        for title, desc in data["deliverables"]
    )
    return f"""
    <section class="grid">
      <article class="panel wide">
        <p class="eyebrow">Tổng quan nhanh</p>
        <h3>Lab này cần làm gì?</h3>
        <div class="summary-stat">
          <div class="stat"><strong>4</strong><span>bước chính trong flow CP2</span></div>
          <div class="stat"><strong>5</strong><span>vai trò gợi ý cho nhóm</span></div>
          <div class="stat"><strong>{'Cần hỏi lại' if STATE["low_confidence"] else 'Đủ mock'}</strong><span>mức tin cậy của phân tích</span></div>
        </div>
        <div class="link-preview">
          <span><strong>Git:</strong> {escape(STATE["git_link"])}</span>
          <span><strong>Lab:</strong> {escape(STATE["lab_link"])}</span>
        </div>
      </article>
      <article class="panel">
        <p class="eyebrow">Tóm tắt</p>
        <h3>Thông tin lab trong 5 dòng</h3>
        <ul>{summary}</ul>
      </article>
      <article class="panel">
        <p class="eyebrow">Thứ tự thực hiện</p>
        <h3>Timeline gợi ý</h3>
        <ol>{timeline}</ol>
      </article>
      <article class="panel wide">
        <p class="eyebrow">Đầu ra cần nộp</p>
        <div class="deliverables">{deliverables}</div>
      </article>
    </section>
    <form method="post" class="actions">
      <button class="primary" name="action" value="assign_roles">Tạo role và task</button>
      <button class="ghost" name="action" value="back_upload">Quay lại</button>
    </form>
    """


def render_roles():
    cards = []
    for role in ROLES:
        task_inputs = []
        for index, task in enumerate(STATE["role_tasks"][role["id"]]):
            task_inputs.append(
                f"""
                <div class="task-edit">
                  <label for="{role["id"]}-task-{index}">Việc cần làm {index + 1}</label>
                  <input class="edit-input" id="{role["id"]}-task-{index}" name="task_{role["id"]}_{index}" value="{escape(task)}">
                </div>
                """
            )
        member = escape(STATE["members"][role["id"]])
        output = escape(STATE["role_outputs"][role["id"]])
        cards.append(
            f"""
            <article class="role-card">
              <div>
                <p class="eyebrow">{escape(role["focus"])}</p>
                <h3>{escape(role["name"])}</h3>
              </div>
              <label for="{role["id"]}-member">Thành viên phụ trách</label>
              <input id="{role["id"]}-member" name="member_{role["id"]}" value="{member}">
              <label for="{role["id"]}-output">Output cần nộp</label>
              <textarea class="mini-textarea" id="{role["id"]}-output" name="output_{role["id"]}">{output}</textarea>
              {''.join(task_inputs)}
            </article>
            """
        )
    return f"""
    <form method="post">
      <div class="panel role-toolbar">
        <div>
          <p class="eyebrow">Nhóm 5 người</p>
          <h3>AI đã tạo role, nhóm có thể sửa trước khi nhận việc</h3>
        </div>
        <button class="primary" name="action" value="confirm_roles">Tạo task riêng</button>
      </div>
      <div class="roles-grid">{''.join(cards)}</div>
    </form>
    """


def render_progress():
    active_role = role_by_id(STATE["active_role"])
    tabs = []
    for role in ROLES:
        active = " is-active" if role["id"] == STATE["active_role"] else ""
        tabs.append(
            f"""
            <form method="post">
              <input type="hidden" name="action" value="select_role">
              <input type="hidden" name="role_id" value="{role["id"]}">
              <button class="role-tab{active}">
                <strong>{escape(role["name"])}</strong><br>
                <span>{escape(STATE["members"][role["id"]])}</span>
              </button>
            </form>
            """
        )
    done = STATE["done"].get(active_role["id"], set())
    task_items = []
    task_titles = STATE["role_tasks"][active_role["id"]]
    for index, task in enumerate(task_titles):
        help_text = active_role["tasks"][index][1]
        checked = "checked" if str(index) in done else ""
        task_items.append(
            f"""
            <label class="task-item">
              <input type="checkbox" name="done" value="{index}" {checked}>
              <span>
                <strong>{escape(task)}</strong>
                <p>{escape(help_text)}</p>
              </span>
            </label>
            """
        )
    percent = round(len(done) / len(active_role["tasks"]) * 100)
    note = (
        "Cảnh báo AI: Tài liệu đầu vào thiếu căn cứ. Các task hiện tại là khung tạm, cần xác minh checkpoint và đầu ra trước khi làm thật."
        if STATE["low_confidence"]
        else active_role["note"]
    )
    return f"""
    <div class="progress-layout">
      <aside class="panel role-tabs" aria-label="Danh sách vai trò">{''.join(tabs)}</aside>
      <section class="panel">
        <div class="task-head">
          <div>
            <p class="eyebrow">{escape(active_role["focus"])}</p>
            <h3>{escape(active_role["name"])} - {escape(STATE["members"][active_role["id"]])}</h3>
          </div>
          <div class="progress-ring">{percent}%</div>
        </div>
        <div class="role-output">
          <p class="eyebrow">Output của vai trò</p>
          <strong>{escape(STATE["role_outputs"][active_role["id"]])}</strong>
        </div>
        <form method="post">
          <input type="hidden" name="action" value="update_progress">
          <input type="hidden" name="role_id" value="{active_role["id"]}">
          <div class="task-list">{''.join(task_items)}</div>
          <div class="actions">
            <button class="primary">Cập nhật tiến độ</button>
          </div>
        </form>
        <div class="source-box">
          <p class="eyebrow">Phần tài liệu liên quan</p>
          <p>{escape(active_role["source"])}</p>
        </div>
        <div class="ai-note">{escape(note)}</div>
      </section>
    </div>
    """


def render_body():
    return {
        "upload": render_upload,
        "analysis": render_analysis,
        "roles": render_roles,
        "progress": render_progress,
    }[STATE["step"]]()


def render_page():
    status = "Cần xác minh" if STATE["low_confidence"] else "Sẵn sàng"
    if STATE["step"] == "analysis" and not STATE["low_confidence"]:
        status = "Đã phân tích"
    if STATE["step"] == "roles":
        status = "Đã chia vai"
    if STATE["step"] == "progress":
        status = "Đang theo dõi"
    return f"""<!doctype html>
<html lang="vi">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>LABCODE Copilot - CP2 Python Mock</title>
    <style>{STYLE}</style>
  </head>
  <body>
    <main class="app-shell">
      {sidebar()}
      <section class="workspace">
        <header class="topbar">
          <div>
            <p class="eyebrow">Prototype Python Mock</p>
            <h2>{page_title()}</h2>
          </div>
          <div class="status-pill">{status}</div>
        </header>
        {render_body()}
      </section>
    </main>
  </body>
</html>"""


def handle_form(fields):
    action = fields.get("action", [""])[0]
    if action == "analyze":
        STATE["git_link"] = fields.get("git_link", [STATE["git_link"]])[0].strip()
        STATE["lab_link"] = fields.get("lab_link", [STATE["lab_link"]])[0].strip()
        missing_git = not STATE["git_link"] or "github.com" not in STATE["git_link"]
        missing_lab = not STATE["lab_link"] or len(STATE["lab_link"]) < 12
        STATE["low_confidence"] = missing_git or missing_lab or "thiếu" in STATE["lab_link"].lower()
        STATE["step"] = "analysis"
    elif action == "load_risky":
        STATE["git_link"] = "https://github.com/nhom-demo/labcode-cp2"
        STATE["lab_link"] = "link lab bị thiếu yêu cầu đầu ra"
        STATE["doc"] = RISKY_DOC
        STATE["low_confidence"] = True
        STATE["step"] = "upload"
    elif action == "assign_roles":
        STATE["step"] = "roles"
    elif action == "confirm_roles":
        for role in ROLES:
            key = f"member_{role['id']}"
            if fields.get(key, [""])[0].strip():
                STATE["members"][role["id"]] = fields[key][0].strip()
            output_key = f"output_{role['id']}"
            if fields.get(output_key, [""])[0].strip():
                STATE["role_outputs"][role["id"]] = fields[output_key][0].strip()
            for index in range(len(role["tasks"])):
                task_key = f"task_{role['id']}_{index}"
                if fields.get(task_key, [""])[0].strip():
                    STATE["role_tasks"][role["id"]][index] = fields[task_key][0].strip()
        STATE["step"] = "progress"
    elif action == "select_role":
        STATE["active_role"] = fields.get("role_id", [STATE["active_role"]])[0]
        STATE["step"] = "progress"
    elif action == "update_progress":
        role_id = fields.get("role_id", [STATE["active_role"]])[0]
        STATE["active_role"] = role_id
        STATE["done"][role_id] = set(fields.get("done", []))
        STATE["step"] = "progress"
    elif action == "back_upload":
        STATE["step"] = "upload"
    elif action == "goto":
        target = fields.get("step", [STATE["step"]])[0]
        allowed = [step[0] for step in STEPS]
        current_index = allowed.index(STATE["step"])
        if target in allowed and allowed.index(target) <= current_index:
            STATE["step"] = target


class LabcodeHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.respond()

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length).decode("utf-8")
        handle_form(parse_qs(body))
        self.respond()

    def respond(self):
        page = render_page().encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(page)))
        self.end_headers()
        self.wfile.write(page)

    def log_message(self, format, *args):
        return


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    port = int(os.environ.get("PORT", "8000"))
    while True:
        try:
            server = ThreadingHTTPServer(("127.0.0.1", port), LabcodeHandler)
            break
        except OSError:
            port += 1
            if port > 8010:
                raise
    print(f"LABCODE Copilot đang chạy tại http://127.0.0.1:{port}")
    print("Nhấn Ctrl+C để dừng.")
    server.serve_forever()


if __name__ == "__main__":
    main()
