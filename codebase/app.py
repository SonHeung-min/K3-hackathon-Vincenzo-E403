from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import os
import sys
import json
import urllib.request
import time
import datetime
import ssl
from urllib.parse import parse_qs

try:
    from dotenv import load_dotenv
    import os
    # When running from codebase/, .env is in the parent directory
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    load_dotenv(dotenv_path=env_path)
except ImportError:
    pass


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

ROLES = []

STATE = {
    "step": "upload",
    "chat_history": [],
    "git_link": DEFAULT_GIT_LINK,
    "doc": SAMPLE_DOC,
    "low_confidence": False,
    "members": {},
    "role_tasks": {},
    "role_outputs": {},
    "active_role": "",
    "done": {},
    "upload_status": "idle"
}

STEPS = [
    ("upload", "1", "Nạp tài liệu"),
    ("analysis", "2", "AI phân tích"),
    ("roles", "3", "Chia vai trò"),
    ("progress", "4", "Theo dõi"),
]

STYLE = """
:root{--bg:#f5f7f4;--ink:#18201c;--muted:#647067;--panel:#fff;--line:#d9e1d9;--green:#2f7d52;--green-dark:#215b3d;--amber:#c77918;--shadow:0 16px 40px rgba(24,32,28,.08)}
*{box-sizing:border-box}body{margin:0;min-height:100vh;color:var(--ink);background:var(--bg);font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}button,textarea,input{font:inherit}button{cursor:pointer}.app-shell{display:grid;grid-template-columns:250px minmax(0,1fr) 5px 350px;min-height:100vh}.sidebar{display:flex;flex-direction:column;gap:28px;padding:28px;color:#f7fbf7;background:#18201c}.sidebar h1,.topbar h2,.panel h3{margin:0;letter-spacing:0}.sidebar h1{margin-top:6px;font-size:32px;line-height:1.05}.subtle{color:#b6c6bb;line-height:1.55}.eyebrow{margin:0 0 8px;color:var(--green);font-size:12px;font-weight:750;text-transform:uppercase;letter-spacing:.08em}.sidebar .eyebrow{color:#8cd6ad}.steps{display:grid;gap:10px}.step{display:grid;grid-template-columns:34px 1fr;align-items:center;gap:12px;width:100%;padding:12px;color:#d8e5dc;background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.12);border-radius:8px;text-align:left}.step span{display:grid;place-items:center;width:34px;height:34px;border-radius:50%;color:#17211b;background:#d9efdf;font-weight:800}.step.is-active{color:#fff;border-color:#8cd6ad;background:rgba(140,214,173,.18)}.checkpoint{margin-top:auto;padding:18px;border:1px solid rgba(255,255,255,.14);border-radius:8px}.checkpoint ul{margin:0;padding-left:18px;line-height:1.7;color:#d8e5dc}.workspace{padding:28px}.topbar{display:flex;justify-content:space-between;gap:16px;align-items:center;margin-bottom:22px}.topbar h2{font-size:clamp(26px,4vw,42px)}.status-pill{min-width:112px;padding:9px 14px;border:1px solid var(--line);border-radius:999px;color:var(--green-dark);background:#edf7ef;text-align:center;font-weight:750}.panel{padding:22px;border:1px solid var(--line);border-radius:8px;background:var(--panel);box-shadow:var(--shadow)}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}.wide{grid-column:1/-1}.upload-panel{display:grid;gap:16px}.textarea-label{font-weight:750}textarea{min-height:280px;resize:vertical;width:100%;padding:16px;border:1px solid var(--line);border-radius:8px;color:#253029;background:#fbfcfb;line-height:1.55}.actions{display:flex;flex-wrap:wrap;gap:12px;margin-top:18px}.primary,.ghost{min-height:42px;padding:0 16px;border-radius:8px;font-weight:800}.primary{color:#fff;background:var(--green);border:1px solid var(--green)}.ghost{color:var(--ink);background:transparent;border:1px solid var(--line)}ul,ol{line-height:1.65}.deliverables,.roles-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}.deliverable,.role-card{padding:14px;border:1px solid var(--line);border-radius:8px;background:#f8faf8}.deliverable strong{display:block;margin-bottom:8px}.role-card{display:grid;gap:12px}.role-card label{color:var(--muted);font-size:13px;font-weight:700}.role-card input{width:100%;padding:10px 12px;border:1px solid var(--line);border-radius:8px}.role-toolbar{display:flex;align-items:center;justify-content:space-between;gap:16px;margin-bottom:16px}.progress-layout{display:grid;grid-template-columns:280px minmax(0,1fr);gap:16px}.role-tabs{display:grid;align-content:start;gap:10px}.role-tab{width:100%;padding:12px;border:1px solid var(--line);border-radius:8px;background:#f8faf8;text-align:left}.role-tab.is-active{border-color:var(--green);background:#edf7ef}.task-head{display:flex;justify-content:space-between;align-items:center;gap:16px;margin-bottom:18px}.progress-ring{display:grid;place-items:center;width:70px;height:70px;border:8px solid #d9eadd;border-top-color:var(--green);border-radius:50%;color:var(--green-dark);font-weight:850}.task-list{display:grid;gap:12px}.task-item{display:grid;grid-template-columns:auto 1fr;gap:12px;padding:14px;border:1px solid var(--line);border-radius:8px;background:#fbfcfb}.task-item input{width:18px;height:18px;margin-top:3px}.task-item strong{display:block;margin-bottom:4px}.task-item p{margin:0;color:var(--muted);line-height:1.5}.source-box,.ai-note{margin-top:16px;padding:16px;border-radius:8px;line-height:1.55}.source-box{border:1px solid #d6e1ef;background:#f2f7ff}.ai-note{border:1px solid #ead8bd;color:#6d4614;background:#fff8ed}@media(max-width:920px){.app-shell{grid-template-columns:1fr}.sidebar{min-height:auto}.grid,.roles-grid,.progress-layout,.deliverables{grid-template-columns:1fr}.topbar,.role-toolbar,.task-head{align-items:flex-start;flex-direction:column}}
.field-grid{display:grid;grid-template-columns:1fr 1fr;gap:14px}.field{display:grid;gap:8px}.field label{font-weight:750}.link-input,.edit-input,.mini-textarea{width:100%;padding:11px 12px;border:1px solid var(--line);border-radius:8px;color:#253029;background:#fbfcfb}.mini-textarea{min-height:74px}.link-preview{display:grid;gap:8px;margin-top:12px;color:var(--muted);font-size:14px}.summary-stat{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}.stat{padding:14px;border:1px solid var(--line);border-radius:8px;background:#f8faf8}.stat strong{display:block;font-size:24px;color:var(--green-dark)}.role-output{padding:12px;border:1px solid #d6e1ef;border-radius:8px;background:#f2f7ff;color:#24415f}.task-edit{display:grid;gap:8px}.task-edit label{color:var(--muted);font-size:13px;font-weight:700}@media(max-width:920px){.field-grid,.summary-stat{grid-template-columns:1fr}}
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
"""


from html.parser import HTMLParser

class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text_parts = []
        self.ignore_tags = {'script', 'style', 'head', 'meta', 'link'}
        self.current_tag = []

    def handle_starttag(self, tag, attrs):
        self.current_tag.append(tag)

    def handle_endtag(self, tag):
        if self.current_tag and self.current_tag[-1] == tag:
            self.current_tag.pop()

    def handle_data(self, data):
        if self.current_tag and self.current_tag[-1] in self.ignore_tags:
            return
        text = data.strip()
        if text:
            self.text_parts.append(text)
            
    def get_text(self):
        return ' '.join(self.text_parts)

def fetch_url(url):
    if not url or not url.startswith('http'): return ""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        with urllib.request.urlopen(req, context=ctx, timeout=5) as response:
            content_type = response.headers.get('Content-Type', '')
            html = response.read().decode('utf-8', errors='ignore')
            if 'text/html' in content_type:
                parser = TextExtractor()
                parser.feed(html)
                return parser.get_text()
            return html
    except Exception as e:
        return f"[Lỗi khi cào dữ liệu từ {url}: {str(e)}]"

def fetch_github_repo_context(repo_url):
    import json
    if "github.com" not in repo_url: return ""
    parts = repo_url.rstrip('/').split('github.com/')
    if len(parts) < 2: return ""
    
    # Lấy chính xác owner/repo để tránh lỗi 404 khi người dùng dán link có thư mục con (VD: tree/main/docs)
    repo_parts = parts[1].split('/')
    if len(repo_parts) < 2: return ""
    repo_path = f"{repo_parts[0]}/{repo_parts[1]}"
    
    context = ""
    try:
        # 1. Gọi API lấy metadata repo
        api_url = f"https://api.github.com/repos/{repo_path}"
        req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        with urllib.request.urlopen(req, context=ctx, timeout=5) as res:
            meta = json.loads(res.read().decode('utf-8'))
            default_branch = meta.get('default_branch', 'main')
            
        # 2. Lấy toàn bộ cây thư mục (recursive)
        tree_url = f"https://api.github.com/repos/{repo_path}/git/trees/{default_branch}?recursive=1"
        req = urllib.request.Request(tree_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=ctx, timeout=10) as res:
            tree_data = json.loads(res.read().decode('utf-8'))
            
        # 3. Lọc file ưu tiên
        valid_exts = ('.md', '.txt', '.py', '.js', '.ts', '.json', '.yml', '.yaml')
        priority_words = ['readme', 'guide', 'lab', 'codelab', 'spec', 'cp', 'rubric', 'template', 'plan']
        
        files = []
        for item in tree_data.get('tree', []):
            if item.get('type') == 'blob':
                path = item.get('path', '')
                path_lower = path.lower()
                if path_lower.endswith(valid_exts):
                    is_priority = any(w in path_lower for w in priority_words)
                    files.append({'path': path, 'priority': is_priority})
                    
        # Ưu tiên các file có từ khóa, sau đó ưu tiên file ở thư mục gốc (ít dấu / nhất)
        files.sort(key=lambda x: (not x['priority'], x['path'].count('/'), x['path']))
        files_to_fetch = files[:6]
        
        # 4. Tải nội dung file raw (Dùng ThreadPool để tải song song siêu tốc)
        import concurrent.futures
        
        def _fetch_single(f):
            raw_url = f"https://raw.githubusercontent.com/{repo_path}/{default_branch}/{f['path']}"
            import time
            time.sleep(0.2) # Thêm độ trễ nhỏ để tránh bị Github Rate Limit chặn IP
            content = fetch_url(raw_url)
            if content and "[Lỗi" not in content:
                return f"--- File: {f['path']} ---\n{content[:3000]}\n\n"
            return ""
            
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            for res in executor.map(_fetch_single, files_to_fetch):
                context += res
                
        if not context:
            return fetch_url(repo_url)
            
        return context
    except Exception as e:
        # Fallback về trang HTML thường nếu bị rate limit hoặc lỗi API
        return fetch_url(repo_url)

def call_gemini_chat(history):
    api_key = os.environ.get("GEMINI_API_KEY")
    openai_url = os.environ.get("OPENAI_BASE_URL")
    
    if not api_key:
        return {"error": "Lỗi: Không tìm thấy GEMINI_API_KEY."}
    
    member_count = STATE.get("member_count", "4")
    system_prompt = """
Bạn là LABCODE Copilot. Nhiệm vụ của bạn là đọc tài liệu Lab và phân chia công việc.
Nếu thông tin đầu vào (tài liệu lab) thiếu các thông tin quan trọng (như deadline, đầu ra), hoặc có yêu cầu phi lý (chia trùng lặp, sai quy trình), bạn KHÔNG ĐƯỢC CHIA VIỆC NGAY. 
Thay vào đó, hãy đặt câu hỏi lại cho người dùng bằng VĂN BẢN THƯỜNG để họ làm rõ.

LƯU Ý VỀ THÀNH VIÊN: Nhóm này ĐÃ CHỐT SỐ LƯỢNG LÀ [MEMBER_COUNT] THÀNH VIÊN. Bạn bắt buộc phải chia công việc thành ĐÚNG [MEMBER_COUNT] Role tương ứng. TUYỆT ĐỐI KHÔNG hỏi lại người dùng về danh sách tên thành viên.
""".replace("[MEMBER_COUNT]", str(member_count)) + """
YÊU CẦU ĐẶC BIỆT (CÂN BẰNG KHỐI LƯỢNG):
1. Đánh giá độ khó của từng task bằng Điểm Nỗ Lực (Story Points) từ 1 đến 5 (1 là rất nhẹ, 5 là cực kỳ nặng).
2. Tên của mỗi task BẮT BUỘC phải bắt đầu bằng "[X điểm] ", ví dụ: "[3 điểm] Thiết kế UI".
3. TỔNG SỐ ĐIỂM (Total Points) của mỗi người (Role) phải XẤP XỈ BẰNG NHAU. Ví dụ: Bạn A làm 1 task 4 điểm, thì bạn B phải làm 2 task 2 điểm.
4. Ở phần "note" của mỗi Role, bắt buộc phải ghi rõ ở đầu dòng: "Tổng khối lượng: X điểm. ".
5. THỜI HẠN (DEADLINE): Bắt buộc trích xuất các mốc thời gian (Checkpoint) từ tài liệu và gắn vào cuối mô tả của từng task tương ứng. Ví dụ: "(Deadline: 12h ngày 1 - CP1)".
6. CHÚ Ý LỊCH TRÌNH: Nếu tài liệu có nhiều mốc thời gian cho các Khoá/Lớp khác nhau (ví dụ Khoá 3 và Khoá 4), hãy MẶC ĐỊNH sử dụng lịch trình của "Khoá 3".

QUAN TRỌNG: 
- Chỉ khi bạn ĐÃ CHẮC CHẮN hiểu rõ toàn bộ yêu cầu, hãy bắt đầu câu trả lời bằng chuỗi [FINAL_PLAN], và NGAY SAU ĐÓ xuất ra DUY NHẤT một khối JSON.
- NẾU người dùng có yêu cầu CHỈNH SỬA, THÊM BỚT hoặc CẬP NHẬT kế hoạch (thêm file, đổi deadline, v.v.), BẠN BẮT BUỘC PHẢI XUẤT LẠI TOÀN BỘ KHỐI JSON mới chứa nội dung đã cập nhật (bắt đầu bằng [FINAL_PLAN]). TUYỆT ĐỐI KHÔNG CHỈ TRẢ LỜI BẰNG VĂN BẢN THƯỜNG.
- YÊU CẦU ĐẦU RA (DELIVERABLES): Trong mảng "deliverables" của JSON, BẠN BẮT BUỘC PHẢI liệt kê ĐẦY ĐỦ tất cả các file và thư mục cần nộp theo đúng cấu trúc yêu cầu của bài lab (ví dụ: README.md, spec.md, codebase/, eval/, validation/,...). Không được bỏ sót.
- PHÂN BỔ ĐẦU RA CHO CÁC ROLE: Tất cả các file/thư mục vừa được liệt kê trong "deliverables" BẮT BUỘC phải được phân bổ HẾT vào trường "output" của các Role tương ứng. Tuyệt đối không được để sót bất kỳ file nào (đặc biệt là README.md) mà không có người chịu trách nhiệm nộp.

Cấu trúc JSON:
{
  "analysis": {
    "summary": ["Câu 1", "Câu 2"],
    "timeline": ["Bước 1", "Bước 2"],
    "deliverables": [["Tên", "Mô tả"]]
  },
  "roles": [
    {
      "id": "pm",
      "name": "Product Lead",
      "focus": "Trọng tâm",
      "tasks": [
        ["[3 điểm] Task 1", "Mô tả 1. (Deadline: Trước 12h - CP1)"],
        ["[1 điểm] Task 2", "Mô tả 2. (Deadline: Trước 17h - CP2)"]
      ],
      "output": "Đầu ra",
      "source": "Nguồn",
      "note": "Tổng khối lượng: 4 điểm. Ghi chú..."
    }
  ],
  "low_confidence": false
}

LƯU Ý QUAN TRỌNG: Mảng "tasks" có thể có số lượng BẤT KỲ (từ 1 đến 5 task) cho mỗi vai trò. Hãy linh hoạt thay đổi số lượng task (ví dụ: người làm task 5 điểm chỉ cần 1 task, người làm task 2 điểm cần 2-3 task) để TỔNG ĐIỂM của mỗi người là XẤP XỈ NHAU.
"""
    messages = [{"role": "system", "content": system_prompt}]
    for msg in history:
        messages.append({"role": msg["role"], "content": msg["content"]})
        
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        if api_key.startswith("sk-") and openai_url:
            url = f"{openai_url.rstrip('/')}/chat/completions"
            data = {
                "model": "gemini-2.5-flash",
                "messages": messages,
                "temperature": 0.2
            }
            req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {api_key}',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            with urllib.request.urlopen(req, context=ctx) as response:
                result = json.loads(response.read().decode('utf-8'))
            raw_text = result['choices'][0]['message']['content']
        else:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            contents = []
            for msg in history:
                role = "user" if msg["role"] == "user" else "model"
                contents.append({"role": role, "parts": [{"text": msg["content"]}]})
            data = {
                "system_instruction": {"parts": [{"text": system_prompt}]},
                "contents": contents,
                "generationConfig": {"temperature": 0.2}
            }
            req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers={
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            with urllib.request.urlopen(req, context=ctx) as response:
                result = json.loads(response.read().decode('utf-8'))
            raw_text = result['candidates'][0]['content']['parts'][0]['text']
            
        return {"text": raw_text}
    except Exception as e:
        return {"error": str(e)}


def active_analysis():
    return RISKY_ANALYSIS if STATE["low_confidence"] else NORMAL_ANALYSIS


def role_by_id(role_id):
    return next((role for role in ROLES if role["id"] == role_id), None)


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
        <h1>Codelabs Tutor</h1>
        <p class="subtle">Trợ lý phân tích tài liệu Codelabs và điều phối công việc nhóm.</p>
      </div>
      <nav class="steps" aria-label="Các bước">{''.join(buttons)}</nav>
    </aside>
    """


def render_upload():
    if STATE.get("upload_status") == "ai_processing":
        return f"""
        <div class="panel upload-panel" style="text-align: center; padding: 50px;">
          <div class="spinner" style="border: 4px solid var(--line); border-top: 4px solid var(--green); border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin: 0 auto;"></div>
          <h3 style="margin-top: 20px;">Đang gửi tài liệu cho AI phân tích...</h3>
          <p style="color: var(--muted);">Quá trình này có thể mất vài giây. Vui lòng giữ nguyên trang.</p>
        </div>
        """
    elif STATE.get("upload_status") == "clarify":
        return f"""
        <div class="panel upload-panel" style="text-align: center; padding: 50px;">
          <h3 style="color: #d9534f; margin-bottom: 20px;">⚠️ AI cần làm rõ thông tin</h3>
          <p style="color: var(--muted); line-height: 1.6;">
            Tài liệu bạn cung cấp bị thiếu thông tin hoặc chứa yêu cầu chưa rõ ràng.<br>
            Vui lòng kiểm tra khung Chat bên phải và <strong>trả lời câu hỏi của AI</strong> để tiếp tục lập kế hoạch.
          </p>
          <form method="post" style="margin-top: 20px;">
            <input type="hidden" name="action" value="reset_upload">
            <button class="ghost">Huỷ và nạp link khác</button>
          </form>
        </div>
        """

    return f"""
    <form method="post" class="panel upload-panel" onsubmit="document.getElementById('upload-ui').style.display='none'; document.getElementById('upload-loading').style.display='block';">
      <div id="upload-ui">
        <div>
          <p class="eyebrow">Nguồn đầu vào</p>
          <h3>Nạp link Git của nhóm</h3>
          <p>CP2 dùng link mẫu để chứng minh flow. Ở CP3, nút phân tích này sẽ gọi AI thật để đọc repo và lưu trace trong repo.</p>
        </div>
        <div style="display: grid; grid-template-columns: 3fr 1fr; gap: 16px; margin-top: 16px;">
          <div class="field">
            <label for="git_link">Link Git của nhóm</label>
            <input class="link-input" id="git_link" name="git_link" value="{escape(STATE.get("git_link", ""))}" placeholder="https://github.com/..." />
          </div>
          <div class="field">
            <label for="member_count">Số lượng thành viên</label>
            <input type="number" min="1" max="15" class="link-input" id="member_count" name="member_count" value="{escape(STATE.get("member_count", "4"))}" placeholder="Ví dụ: 4" />
          </div>
        </div>
        <div class="source-box">
          <p class="eyebrow">AI sẽ phân tích gì?</p>
          <p>Repo Github để hiểu cấu trúc code, README, mục tiêu và yêu cầu của lab.</p>
        </div>
        <div class="actions">
          <button class="primary" name="action" value="analyze">Phân tích</button>
          <button class="ghost" name="action" value="load_risky">Thử link thiếu thông tin</button>
        </div>
      </div>
      <div id="upload-loading" style="display: none; text-align: center; padding: 50px;">
          <div class="spinner" style="border: 4px solid var(--line); border-top: 4px solid var(--green); border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin: 0 auto;"></div>
          <h3 style="margin-top: 20px;">Đang cào dữ liệu từ Github...</h3>
          <p style="color: var(--muted);">Vui lòng đợi khoảng 10-15 giây để tải mã nguồn. Không tải lại trang!</p>
      </div>
    </form>
    """


def render_analysis():
    data = active_analysis()
    summary = "".join(f"<li>{escape(item)}</li>" for item in data.get("summary", []))
    timeline = "".join(f"<li>{escape(item)}</li>" for item in data.get("timeline", []))
    deliverables = "".join(
        f'<div class="deliverable"><strong>{escape(title)}</strong><span>{escape(desc)}</span></div>'
        for title, desc in data.get("deliverables", [])
    )
    return f"""
    <section class="grid">
      <article class="panel wide">
        <p class="eyebrow">Tổng quan nhanh</p>
        <h3>Lab này cần làm gì?</h3>
        <div class="summary-stat">
          <div class="stat"><strong>4</strong><span>bước chính trong flow CP2</span></div>
          <div class="stat"><strong>{len(ROLES)}</strong><span>vai trò gợi ý cho nhóm</span></div>
          <div class="stat"><strong>{'Cần hỏi lại' if STATE["low_confidence"] else 'Đủ mock'}</strong><span>mức tin cậy của phân tích</span></div>
        </div>
        <div class="link-preview">
          <span><strong>Git:</strong> {escape(STATE.get("git_link", ""))}</span>
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
    if not ROLES:
        return "<div class='panel' style='text-align: center; padding: 50px;'><h3 style='color: var(--muted);'>Vui lòng yêu cầu AI phân tích để tạo danh sách công việc.</h3></div>"
        
    cards = []
    for role in ROLES:
        task_inputs = []
        for index, task in enumerate(STATE["role_tasks"].get(role["id"], [])):
            task_inputs.append(
                f"""
                <div class="task-edit">
                  <label for="{role["id"]}-task-{index}">Việc cần làm {index + 1}</label>
                  <input class="edit-input" id="{role["id"]}-task-{index}" name="task_{role["id"]}_{index}" value="{escape(task)}">
                </div>
                """
            )
        member = escape(STATE["members"].get(role["id"], ""))
        output = escape(STATE["role_outputs"].get(role["id"], ""))
        cards.append(
            f"""
            <article class="role-card">
              <div>
                <p class="eyebrow">{escape(role.get("focus", ""))}</p>
                <h3>{escape(role.get("name", ""))}</h3>
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
    if not ROLES:
        return "<div class='panel' style='text-align: center; padding: 50px;'><h3 style='color: var(--muted);'>Vui lòng yêu cầu AI phân tích để tạo danh sách công việc.</h3></div>"
        
    active_role = role_by_id(STATE.get("active_role"))
    if not active_role:
        active_role = ROLES[0]
        
    tabs = []
    total_group_tasks = 0
    total_group_done = 0
    
    for role in ROLES:
        role_task_titles = STATE["role_tasks"].get(role["id"], [])
        role_done = STATE["done"].get(role["id"], set())
        
        role_total = len(role_task_titles)
        role_done_count = len(role_done)
        
        total_group_tasks += role_total
        total_group_done += role_done_count
        
        role_percent = round((role_done_count / role_total) * 100) if role_total else 0
        
        active = " is-active" if role["id"] == STATE["active_role"] else ""
        tabs.append(
            f"""
            <form method="post">
              <input type="hidden" name="action" value="select_role">
              <input type="hidden" name="role_id" value="{role["id"]}">
              <button class="role-tab{active}" style="position: relative;">
                <strong>{escape(role.get("name", ""))}</strong>
                <span style="position: absolute; right: 12px; top: 12px; font-size: 11px; background: {'var(--green)' if role_percent == 100 else '#e9ecef'}; color: {'white' if role_percent == 100 else 'var(--muted)'}; padding: 2px 6px; border-radius: 10px; font-weight: bold;">{role_percent}%</span>
                <br>
                <span>{escape(STATE["members"].get(role["id"], ""))}</span>
              </button>
            </form>
            """
        )
        
    overall_percent = round((total_group_done / total_group_tasks) * 100) if total_group_tasks else 0
    done = STATE["done"].get(active_role["id"], set())
    task_items = []
    task_titles = STATE["role_tasks"].get(active_role["id"], [])
    for index, task in enumerate(task_titles):
        help_text = active_role["tasks"][index][1] if index < len(active_role["tasks"]) else ""
        checked = "checked" if str(index) in done else ""
        task_items.append(
            f"""
            <div class="task-item" style="display: flex; justify-content: space-between; align-items: flex-start;">
              <label style="display: flex; gap: 12px; cursor: pointer; flex: 1;">
                <input type="checkbox" name="done" value="{index}" {checked}>
                <span>
                  <strong>{escape(task)}</strong>
                  <p>{escape(help_text)}</p>
                </span>
              </label>
              <button type="button" class="ghost" style="padding: 6px 10px; min-height: 30px; font-size: 12px; flex-shrink: 0; color: var(--green);" onclick="requestTaskGuide('{escape(task)}', '{escape(help_text)}')">
                📖 Hướng dẫn
              </button>
            </div>
            """
        )
    note = (
        "Cảnh báo AI: Tài liệu đầu vào thiếu căn cứ. Các task hiện tại là khung tạm, cần xác minh checkpoint và đầu ra trước khi làm thật."
        if STATE["low_confidence"]
        else active_role.get("note", "")
    )
    base_html = f"""
    <div style="margin-bottom: 20px; background: white; padding: 15px; border-radius: 12px; border: 1px solid var(--line);">
      <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
        <strong style="color: var(--green-dark);">Tiến độ cả nhóm</strong>
        <strong style="color: var(--green);">{overall_percent}%</strong>
      </div>
      <div style="height: 8px; background: #e9ecef; border-radius: 4px; overflow: hidden;">
        <div style="height: 100%; background: var(--green); width: {overall_percent}%; transition: width 0.3s ease;"></div>
      </div>
    </div>
    <div class="progress-layout">
      <aside class="panel role-tabs" aria-label="Danh sách vai trò">{''.join(tabs)}</aside>
      <section class="panel">
        <div class="task-head">
          <div>
            <p class="eyebrow">{escape(active_role.get("focus", ""))}</p>
            <h3>{escape(active_role.get("name", ""))} - {escape(STATE["members"].get(active_role["id"], ""))}</h3>
          </div>
        </div>
        <div class="role-output">
          <p class="eyebrow">Output của vai trò</p>
          <strong>{escape(STATE["role_outputs"].get(active_role["id"], ""))}</strong>
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
          <p>{escape(active_role.get("source", ""))}</p>
        </div>
        <div class="ai-note">{escape(note)}</div>
      </section>
    </div>
    """
    
    import json
    roles_data = {}
    for r in ROLES:
        roles_data[r["id"]] = [t[1] if len(t)>1 else "" for t in r.get("tasks", [])]
    roles_json = json.dumps(roles_data)
    done_data = {k: list(v) for k, v in STATE.get("done", {}).items()}
    done_json = json.dumps(done_data)
    
    script = f"""
    <script>
    function checkDeadlines() {{
        const now = new Date();
        const rolesData = {roles_json};
        const doneData = {done_json};
        const activeRoleId = "{active_role["id"]}";
        
        let activeRoleOverdue = false;
        
        function parseTime(text) {{
            const match = text.match(/Deadline.*?(\\d{{1,2}})[:h](\\d{{2}})?/i);
            if (!match) return null;
            let hours = parseInt(match[1]);
            let mins = match[2] ? parseInt(match[2]) : 0;
            let d = new Date();
            if (text.match(/ngày 2|ngày mai|n2|tomorrow/i)) {{
                d.setDate(d.getDate() + 1);
            }} else if (text.match(/ngày 3|n3/i)) {{
                d.setDate(d.getDate() + 2);
            }}
            d.setHours(hours, mins, 0, 0);
            return d;
        }}

        document.querySelectorAll('.task-item').forEach(task => {{
            const checkbox = task.querySelector('input[type="checkbox"]');
            if (checkbox && checkbox.checked) {{
                task.style.borderColor = "";
                task.style.backgroundColor = "";
                const w = task.querySelector('.overdue-warning');
                if (w) w.remove();
                return;
            }}
            const text = task.innerText;
            const deadline = parseTime(text);
            if (deadline) {{
                const diffMins = (deadline - now) / 60000;
                if (diffMins <= 15) {{
                    task.style.borderColor = "#d9534f";
                    task.style.backgroundColor = "#fdf2f2";
                    activeRoleOverdue = true;
                    let warning = task.querySelector('.overdue-warning');
                    if (!warning) {{
                        warning = document.createElement('span');
                        warning.className = 'overdue-warning';
                        warning.style.color = '#d9534f';
                        warning.style.fontSize = '12px';
                        warning.style.fontWeight = 'bold';
                        warning.style.marginLeft = '8px';
                        task.querySelector('p').appendChild(warning);
                    }}
                    warning.innerText = (diffMins < 0) ? ' ⚠️ Quá hạn!' : ' ⚠️ Sắp đến hạn!';
                }} else {{
                    task.style.borderColor = "";
                    task.style.backgroundColor = "";
                    const w = task.querySelector('.overdue-warning');
                    if (w) w.remove();
                }}
            }}
        }});

        document.querySelectorAll('.role-tab').forEach(tab => {{
            const roleId = tab.parentElement.querySelector('input[name="role_id"]').value;
            let isOverdue = false;
            if (roleId === activeRoleId) {{
                isOverdue = activeRoleOverdue;
            }} else {{
                const tasks = rolesData[roleId] || [];
                const done = doneData[roleId] || [];
                for (let i = 0; i < tasks.length; i++) {{
                    if (done.includes(String(i))) continue;
                    const d = parseTime(tasks[i]);
                    if (d && (d - now) / 60000 <= 15) {{
                        isOverdue = true;
                        break;
                    }}
                }}
            }}
            
            if (isOverdue) {{
                tab.style.borderColor = "#d9534f";
                tab.style.backgroundColor = tab.classList.contains("is-active") ? "#fdf2f2" : "#fff5f5";
                tab.style.color = "#d9534f";
            }} else {{
                tab.style.borderColor = "";
                tab.style.backgroundColor = "";
                tab.style.color = "";
            }}
        }});
    }}
    
    checkDeadlines();
    setInterval(checkDeadlines, 30000);
    </script>
    """
    
    return base_html + script


def render_persistent_chat():
    if not STATE.get("git_link"):
        return "<aside class='chat-sidebar' style='background:#fbfcfb; padding:20px;'><h3 style='color:var(--muted)'>Codelabs Tutor</h3><p style='color:var(--muted); font-size:14px'>Hãy điền Link tài liệu ở bên trái để bắt đầu chat.</p></aside>"
        
    history_json = json.dumps(STATE.get("chat_history", []))
    ctx = f"Git: {STATE.get('git_link', '')}\\nNội dung:\\n{STATE.get('doc', '')}"
    ctx_json = json.dumps(ctx)
    
    return f'''
    <aside class="chat-sidebar" style="display:flex; flex-direction:column; background:#fff; height:100vh; border-left:1px solid var(--line);">
      <div style="padding: 20px; border-bottom: 1px solid var(--line); background:#f8faf8;">
        <h3 style="margin:0; color:var(--green-dark);">Codelabs Tutor</h3>
        <p style="margin:4px 0 0; font-size:12px; color:var(--muted);">Gõ chat để thay đổi Dashboard</p>
      </div>
      
      <div id="chat-window" style="flex:1; overflow-y:auto; padding:20px; display:flex; flex-direction:column; gap:8px; background:#fbfcfb;">
      </div>
      
      <div style="padding:20px; border-top:1px solid var(--line); background:#fff;">
        <div style="display:flex; gap:8px;">
          <input type="text" id="chat-input" class="edit-input" placeholder="Thêm tester, sửa deadline..." style="flex:1; font-size:14px;">
          <button id="chat-send" class="primary" style="padding:0 14px; min-height: 36px;">Gửi</button>
        </div>
      </div>
      
      <form id="hidden-chat-form" method="post" style="display:none;">
        <input type="hidden" name="action" id="chat-action" value="chat_update">
        <input type="hidden" name="history_json" id="history-input">
        <input type="hidden" name="ai_json" id="ai-json-input">
      </form>
      
      <script>
        const chatWindow = document.getElementById("chat-window");
        const chatInput = document.getElementById("chat-input");
        const chatSend = document.getElementById("chat-send");
        const form = document.getElementById("hidden-chat-form");
        
        const currentState = {{"upload_status": "{STATE.get('upload_status', 'idle')}"}};
        let history = {history_json};
        if(history.length === 0 && currentState.upload_status === "ai_processing") {{
            history.push({{role: "user", content: "Tôi cần chia việc cho tài liệu Lab:\\n" + {ctx_json}}});
            setTimeout(() => sendMsgInternal(""), 300);
        }} else {{
            renderHistory();
            setTimeout(() => {{ chatWindow.scrollTop = chatWindow.scrollHeight; }}, 100);
        }}
        
        function renderHistory() {{
            chatWindow.innerHTML = "";
            let visible = history.filter(m => !m.content.startsWith("Tôi cần chia việc cho tài liệu Lab:"));
            visible.forEach(m => {{
                let text = m.content;
                let hasPlan = text.includes("[FINAL_PLAN]");
                if(hasPlan) text = text.split("[FINAL_PLAN]")[0];
                if(!text.trim() && hasPlan) {{
                    text = "✅ Đã cập nhật xong Dashboard theo yêu cầu của bạn!";
                }} else if(!text.trim()) {{
                    return;
                }}
                appendMsgUI(m.role, text);
            }});
        }}
        
        function appendMsgUI(role, text) {{
            const div = document.createElement("div");
            div.style.padding = "10px 14px";
            div.style.borderRadius = "12px";
            div.style.maxWidth = "85%";
            div.style.lineHeight = "1.5";
            div.style.fontSize = "14px";
            if(role === "user") {{
                div.style.alignSelf = "flex-end";
                div.style.background = "#d9efdf";
                div.style.color = "#17211b";
                div.innerHTML = "<strong>Bạn:</strong><br>" + text.replace(/\\n/g, "<br>");
            }} else {{
                div.style.alignSelf = "flex-start";
                div.style.background = "#fff";
                div.style.color = "#24415f";
                div.style.border = "1px solid #d6e1ef";
                div.style.boxShadow = "0 2px 8px rgba(0,0,0,0.03)";
                div.innerHTML = "<strong>AI:</strong><br>" + (window.marked ? marked.parse(text) : text.replace(/\\n/g, "<br>"));
                
                // Remove margin from paragraphs inside AI message
                const paragraphs = div.getElementsByTagName("p");
                for (let p of paragraphs) p.style.marginTop = "8px", p.style.marginBottom = "8px";
            }}
            chatWindow.appendChild(div);
            chatWindow.scrollTop = chatWindow.scrollHeight;
        }}
        
        async function sendMsgInternal(text) {{
            if (text) {{
                history.push({{role: "user", content: text}});
                appendMsgUI("user", text);
                chatInput.value = "";
            }}
            chatInput.disabled = true; chatSend.disabled = true;
            
            const loading = document.createElement("div");
            loading.id = "loading-msg";
            loading.style.alignSelf = "flex-start";
            loading.style.color = "#647067";
            loading.style.fontSize = "13px";
            loading.innerText = "AI đang suy nghĩ...";
            chatWindow.appendChild(loading);
            chatWindow.scrollTop = chatWindow.scrollHeight;
            
            try {{
                const res = await fetch("/chat", {{
                    method: "POST",
                    headers: {{"Content-Type": "application/json"}},
                    body: JSON.stringify({{history: history}})
                }});
                const data = await res.json();
                chatWindow.removeChild(document.getElementById("loading-msg"));
                
                if (data.error) {{
                    appendMsgUI("ai", "Lỗi: " + data.error);
                    chatInput.disabled = false; chatSend.disabled = false; return;
                }}
                
                let aiText = data.text;
                history.push({{role: "assistant", content: aiText}});
                
                if (aiText.includes("[FINAL_PLAN]")) {{
                    const parts = aiText.split("[FINAL_PLAN]");
                    if (parts[0].trim()) appendMsgUI("ai", parts[0].trim());
                    
                    let jsonStr = parts[1].trim();
                    if (jsonStr.startsWith("```json")) jsonStr = jsonStr.substring(7);
                    if (jsonStr.startsWith("```")) jsonStr = jsonStr.substring(3);
                    if (jsonStr.endsWith("```")) jsonStr = jsonStr.substring(0, jsonStr.length - 3);
                    
                    document.getElementById("ai-json-input").value = jsonStr.trim();
                    document.getElementById("history-input").value = JSON.stringify(history);
                    document.getElementById("chat-action").value = "chat_update";
                    form.submit();
                }} else {{
                    appendMsgUI("ai", aiText);
                    await fetch("/chat_save", {{
                        method: "POST",
                        headers: {{"Content-Type": "application/json"}},
                        body: JSON.stringify({{history: history}})
                    }});
                    chatInput.disabled = false; chatSend.disabled = false; chatInput.focus();
                    
                    if (currentState.step === "upload" && currentState.upload_status === "ai_processing") {{
                        document.getElementById("chat-action").value = "chat_clarify";
                        document.getElementById("history-input").value = JSON.stringify(history);
                        form.submit();
                    }}
                }}
            }} catch(e) {{
                chatWindow.removeChild(document.getElementById("loading-msg"));
                appendMsgUI("ai", "Lỗi kết nối.");
                chatInput.disabled = false; chatSend.disabled = false;
            }}
        }}
        
        window.requestTaskGuide = function(taskName, taskDesc) {{
            const prompt = `Bạn có thể hướng dẫn tôi chi tiết từng bước để làm task này không?\\n\\nTask: ${{taskName}}\\nMô tả: ${{taskDesc}}\\n\\nYêu cầu: Hãy chia thành các bước rõ ràng, cung cấp code mẫu nếu cần thiết, và chỉ ra những điểm cần lưu ý.`;
            sendMsgInternal(prompt);
        }};
        
        chatSend.onclick = () => sendMsgInternal(chatInput.value);
        chatInput.onkeypress = (e) => {{ if (e.key === 'Enter') sendMsgInternal(chatInput.value); }};
      </script>
    </aside>
    '''

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
    <style>
      {STYLE}
      .markdown-body ul, .markdown-body ol {{ margin: 8px 0; padding-left: 20px; }}
      .markdown-body pre {{ background: #f6f8fa; padding: 10px; border-radius: 6px; overflow-x: auto; }}
      .markdown-body code {{ background: #f6f8fa; padding: 2px 4px; border-radius: 4px; }}
    </style>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <script>
      let sidebarOpen = true;
      let chatOpen = true;
      let chatWidth = 350;
      let isResizing = false;
      
      function updateGrid() {{
        const columns = [];
        if (sidebarOpen) columns.push("250px");
        columns.push("minmax(0,1fr)");
        if (chatOpen) {{
          columns.push("5px");
          columns.push(chatWidth + "px");
        }}
        
        const shell = document.getElementById('app-shell');
        if (shell) shell.style.gridTemplateColumns = columns.join(' ');
        
        const sidebar = document.querySelector('.sidebar');
        if (sidebar) sidebar.style.display = sidebarOpen ? 'flex' : 'none';
        const resizer = document.getElementById('chat-resizer');
        if (resizer) resizer.style.display = chatOpen ? 'block' : 'none';
        const chat = document.querySelector('.chat-sidebar');
        if (chat) chat.style.display = chatOpen ? 'flex' : 'none';
      }}
      function toggleSidebar() {{ sidebarOpen = !sidebarOpen; updateGrid(); }}
      function toggleChat() {{ chatOpen = !chatOpen; updateGrid(); }}
      
      document.addEventListener('DOMContentLoaded', () => {{
        const resizer = document.getElementById('chat-resizer');
        if (!resizer) return;
        resizer.addEventListener('mousedown', (e) => {{
          isResizing = true;
          document.body.style.cursor = 'ew-resize';
          document.body.style.userSelect = 'none';
        }});
        window.addEventListener('mousemove', (e) => {{
          if (!isResizing) return;
          const newWidth = window.innerWidth - e.clientX;
          if (newWidth > 250 && newWidth < 800) {{
            chatWidth = newWidth;
            updateGrid();
          }}
        }});
        window.addEventListener('mouseup', () => {{
          if (isResizing) {{
            isResizing = false;
            document.body.style.cursor = '';
            document.body.style.userSelect = '';
          }}
        }});
      }});
    </script>
  </head>
  <body>
    <main class="app-shell" id="app-shell">
      {sidebar()}
      <section class="workspace" style="border-right: 1px solid var(--line);">
        <header class="topbar">
          <div style="display: flex; gap: 12px; align-items: center;">
            <button class="ghost" onclick="toggleSidebar()" style="padding: 4px 8px; border: none; font-size: 18px;" title="Đóng/Mở thanh công cụ">☰</button>
            <div>
              <p class="eyebrow">Prototype Python Mock</p>
              <h2>{page_title()}</h2>
            </div>
          </div>
          <div style="display: flex; gap: 12px; align-items: center;">
            <div class="status-pill">{status}</div>
            <button class="ghost" onclick="toggleChat()" style="padding: 4px 8px; border: none; font-size: 18px;" title="Đóng/Mở Chat AI">💬</button>
          </div>
        </header>
        {render_body()}
      </section>
      <div id="chat-resizer" style="cursor: ew-resize; background: transparent; transition: background 0.2s; z-index: 10;" onmouseover="this.style.background='rgba(0,0,0,0.1)'" onmouseout="this.style.background='transparent'"></div>
      {render_persistent_chat()}
    </main>
  </body>
</html>"""


def handle_form(fields):
    action = fields.get("action", [""])[0]
    if action == "analyze":
        STATE["git_link"] = fields.get("git_link", [STATE.get("git_link", "")] )[0].strip()
        STATE["member_count"] = fields.get("member_count", [STATE.get("member_count", "4")] )[0].strip()
        doc_input = fields.get("doc", [STATE.get("doc", "")] )[0].strip()
        
        # Kích hoạt Auto-Scraping nếu ô nhập liệu trống hoặc chứa văn bản mặc định
        if not doc_input or "Buổi LABCODE" in doc_input:
            if STATE.get("git_link") and STATE.get("git_link") == STATE.get("last_fetched_link") and STATE.get("last_fetched_doc"):
                STATE["doc"] = STATE["last_fetched_doc"]
            else:
                scraped_text = ""
                if STATE.get("git_link"):
                    git_text = fetch_github_repo_context(STATE["git_link"])
                    if git_text:
                        scraped_text += "--- CẤU TRÚC GITHUB REPOSITORY ---\n" + git_text + "\n\n"
                        
                if scraped_text.strip():
                    STATE["doc"] = scraped_text
                    STATE["last_fetched_link"] = STATE["git_link"]
                    STATE["last_fetched_doc"] = scraped_text
                else:
                    STATE["doc"] = "Không thể cào dữ liệu tự động từ các link cung cấp. Vui lòng kiểm tra lại link hoặc paste thủ công."
        else:
            STATE["doc"] = doc_input
            
        STATE["chat_history"] = []
        STATE["step"] = "upload"
        STATE["upload_status"] = "ai_processing"
    elif action == "chat_clarify":
        STATE["chat_history"] = json.loads(fields.get("history_json", ["[]"])[0])
        STATE["upload_status"] = "clarify"
    elif action == "reset_upload":
        STATE["upload_status"] = "idle"
        STATE["chat_history"] = []
    elif action == "chat_update":
        STATE["chat_history"] = json.loads(fields.get("history_json", ["[]"])[0])
        ai_json_str = fields.get("ai_json", [""])[0]
        try:
            parsed_ai = json.loads(ai_json_str)
            global NORMAL_ANALYSIS, RISKY_ANALYSIS, ROLES
            NORMAL_ANALYSIS = parsed_ai.get("analysis", NORMAL_ANALYSIS)
            RISKY_ANALYSIS = NORMAL_ANALYSIS
            ROLES = parsed_ai.get("roles", ROLES)
            
            for i, role in enumerate(ROLES):
                role["member"] = f"Bạn {chr(65+i)}"
            
            STATE["low_confidence"] = parsed_ai.get("low_confidence", False)
            STATE["members"] = {role["id"]: role.get("member", "Chưa gán") for role in ROLES}
            STATE["role_tasks"] = {role["id"]: [task[0] if len(task) > 0 else "Task" for task in role.get("tasks", [])] for role in ROLES}
            
            for role in ROLES:
                new_tasks = []
                for t in role.get("tasks", []):
                    if len(t) >= 2:
                        new_tasks.append(t)
                    elif len(t) == 1:
                        new_tasks.append([t[0], ""])
                    else:
                        new_tasks.append(["Task", ""])
                role["tasks"] = new_tasks
                
            STATE["role_outputs"] = {role["id"]: role.get("output", "") for role in ROLES}
            STATE["active_role"] = ROLES[0]["id"] if ROLES else "pm"
            STATE["done"] = {}
            STATE["step"] = "analysis"
            STATE["upload_status"] = "idle"
        except Exception as e:
            STATE["low_confidence"] = True
            STATE["doc"] = "Lỗi parse JSON từ AI: " + str(e) + "\\n" + ai_json_str
            STATE["step"] = "upload"
            STATE["upload_status"] = "clarify"
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
        STATE["upload_status"] = "idle"
    elif action == "goto":
        target = fields.get("step", [STATE["step"]])[0]
        allowed = [step[0] for step in STEPS]
        current_index = allowed.index(STATE["step"])
        if target in allowed and allowed.index(target) <= current_index:
            STATE["step"] = target
            if target == "upload":
                STATE["upload_status"] = "idle"


class LabcodeHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.respond()

    def do_POST(self):
        if self.path == "/chat":
            length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(length).decode("utf-8")
            req = json.loads(body)
            res = call_gemini_chat(req.get("history", []))
            try:
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps(res).encode("utf-8"))
            except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError):
                pass
            return
            
        if self.path == "/chat_save":
            length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(length).decode("utf-8")
            req = json.loads(body)
            STATE["chat_history"] = req.get("history", [])
            try:
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(b"{}")
            except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError):
                pass
            return
            
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length).decode("utf-8")
        handle_form(parse_qs(body))
        self.respond()

    def respond(self):
        page = render_page().encode("utf-8")
        try:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(page)))
            self.end_headers()
            self.wfile.write(page)
        except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError):
            pass

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
