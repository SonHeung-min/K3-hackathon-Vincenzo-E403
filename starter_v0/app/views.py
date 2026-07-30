from html import escape
from . import state

STYLE = """
:root{--bg:#f5f7f4;--ink:#18201c;--muted:#647067;--panel:#fff;--line:#d9e1d9;--green:#2f7d52;--green-dark:#215b3d;--amber:#c77918;--shadow:0 16px 40px rgba(24,32,28,.08)}
*{box-sizing:border-box}body{margin:0;min-height:100vh;color:var(--ink);background:var(--bg);font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}button,textarea,input{font:inherit}button{cursor:pointer}.app-shell{display:grid;grid-template-columns:320px minmax(0,1fr);min-height:100vh}.sidebar{display:flex;flex-direction:column;gap:28px;padding:28px;color:#f7fbf7;background:#18201c}.sidebar h1,.topbar h2,.panel h3{margin:0;letter-spacing:0}.sidebar h1{margin-top:6px;font-size:32px;line-height:1.05}.subtle{color:#b6c6bb;line-height:1.55}.eyebrow{margin:0 0 8px;color:var(--green);font-size:12px;font-weight:750;text-transform:uppercase;letter-spacing:.08em}.sidebar .eyebrow{color:#8cd6ad}.steps{display:grid;gap:10px}.step{display:grid;grid-template-columns:34px 1fr;align-items:center;gap:12px;width:100%;padding:12px;color:#d8e5dc;background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.12);border-radius:8px;text-align:left}.step span{display:grid;place-items:center;width:34px;height:34px;border-radius:50%;color:#17211b;background:#d9efdf;font-weight:800}.step.is-active{color:#fff;border-color:#8cd6ad;background:rgba(140,214,173,.18)}.checkpoint{margin-top:auto;padding:18px;border:1px solid rgba(255,255,255,.14);border-radius:8px}.checkpoint ul{margin:0;padding-left:18px;line-height:1.7;color:#d8e5dc}.workspace{padding:28px}.topbar{display:flex;justify-content:space-between;gap:16px;align-items:center;margin-bottom:22px}.topbar h2{font-size:clamp(26px,4vw,42px)}.status-pill{min-width:112px;padding:9px 14px;border:1px solid var(--line);border-radius:999px;color:var(--green-dark);background:#edf7ef;text-align:center;font-weight:750}.panel{padding:22px;border:1px solid var(--line);border-radius:8px;background:var(--panel);box-shadow:var(--shadow)}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}.wide{grid-column:1/-1}.upload-panel{display:grid;gap:16px}.textarea-label{font-weight:750}textarea{min-height:280px;resize:vertical;width:100%;padding:16px;border:1px solid var(--line);border-radius:8px;color:#253029;background:#fbfcfb;line-height:1.55}.actions{display:flex;flex-wrap:wrap;gap:12px;margin-top:18px}.primary,.ghost{min-height:42px;padding:0 16px;border-radius:8px;font-weight:800}.primary{color:#fff;background:var(--green);border:1px solid var(--green)}.ghost{color:var(--ink);background:transparent;border:1px solid var(--line)}ul,ol{line-height:1.65}.deliverables,.roles-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}.deliverable,.role-card{padding:14px;border:1px solid var(--line);border-radius:8px;background:#f8faf8}.deliverable strong{display:block;margin-bottom:8px}.role-card{display:grid;gap:12px}.role-card label{color:var(--muted);font-size:13px;font-weight:700}.role-card input{width:100%;padding:10px 12px;border:1px solid var(--line);border-radius:8px}.role-toolbar{display:flex;align-items:center;justify-content:space-between;gap:16px;margin-bottom:16px}.progress-layout{display:grid;grid-template-columns:280px minmax(0,1fr);gap:16px}.role-tabs{display:grid;align-content:start;gap:10px}.role-tab{width:100%;padding:12px;border:1px solid var(--line);border-radius:8px;background:#f8faf8;text-align:left}.role-tab.is-active{border-color:var(--green);background:#edf7ef}.task-head{display:flex;justify-content:space-between;align-items:center;gap:16px;margin-bottom:18px}.progress-ring{display:grid;place-items:center;width:70px;height:70px;border:8px solid #d9eadd;border-top-color:var(--green);border-radius:50%;color:var(--green-dark);font-weight:850}.task-list{display:grid;gap:12px}.task-item{display:grid;grid-template-columns:auto 1fr;gap:12px;padding:14px;border:1px solid var(--line);border-radius:8px;background:#fbfcfb}.task-item input{width:18px;height:18px;margin-top:3px}.task-item strong{display:block;margin-bottom:4px}.task-item p{margin:0;color:var(--muted);line-height:1.5}.source-box,.ai-note{margin-top:16px;padding:16px;border-radius:8px;line-height:1.55}.source-box{border:1px solid #d6e1ef;background:#f2f7ff}.ai-note{border:1px solid #ead8bd;color:#6d4614;background:#fff8ed}@media(max-width:920px){.app-shell{grid-template-columns:1fr}.sidebar{min-height:auto}.grid,.roles-grid,.progress-layout,.deliverables{grid-template-columns:1fr}.topbar,.role-toolbar,.task-head{align-items:flex-start;flex-direction:column}}
.field-grid{display:grid;grid-template-columns:1fr 1fr;gap:14px}.field{display:grid;gap:8px}.field label{font-weight:750}.link-input,.edit-input,.mini-textarea{width:100%;padding:11px 12px;border:1px solid var(--line);border-radius:8px;color:#253029;background:#fbfcfb}.mini-textarea{min-height:74px}.link-preview{display:grid;gap:8px;margin-top:12px;color:var(--muted);font-size:14px}.summary-stat{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}.stat{padding:14px;border:1px solid var(--line);border-radius:8px;background:#f8faf8}.stat strong{display:block;font-size:24px;color:var(--green-dark)}.role-output{padding:12px;border:1px solid #d6e1ef;border-radius:8px;background:#f2f7ff;color:#24415f}.task-edit{display:grid;gap:8px}.task-edit label{color:var(--muted);font-size:13px;font-weight:700}@media(max-width:920px){.field-grid,.summary-stat{grid-template-columns:1fr}}
"""

def sidebar():
    buttons = []
    active_index = [step[0] for step in state.STEPS].index(state.STATE["step"])
    for index, (step_id, number, label) in enumerate(state.STEPS):
        disabled = "disabled" if index > active_index else ""
        active = " is-active" if step_id == state.STATE["step"] else ""
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
    error_block = ""
    if state.STATE.get("error_msg", ""):
        error_block = f"""
        <div style="background-color: #fff1f0; color: #d8544f; border: 1px solid #fbc4c4; padding: 16px; border-radius: 8px; font-size: 14px; line-height: 1.5; margin-bottom: 12px;">
          <strong>Lỗi xảy ra:</strong> {escape(state.STATE["error_msg"])}
        </div>
        """
        
    fallback_field = ""
    if state.STATE.get("show_fallback", False):
        fallback_field = f"""
        <div class="field wide" style="margin-top: 14px; display: flex; flex-direction: column; gap: 8px;">
          <label for="pasted_doc" style="font-weight: 750;">Dán nội dung tài liệu hướng dẫn LAB (Dự phòng)</label>
          <textarea id="pasted_doc" name="pasted_doc" placeholder="Dán nội dung đề bài/README tại đây..." style="min-height: 180px;">{escape(state.STATE.get("pasted_doc", ""))}</textarea>
        </div>
        """

    return f"""
    <form method="post" class="panel upload-panel">
      <div>
        <p class="eyebrow">Nguồn đầu vào</p>
        <h3>Nạp link Git và link code lab</h3>
        <p>Hệ thống tự động đọc file README/Docs từ link GitHub và chia việc dựa trên số thành viên.</p>
      </div>
      {error_block}
      <div class="field-grid" style="grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));">
        <div class="field">
          <label for="git_link">Link Git của nhóm</label>
          <input class="link-input" id="git_link" name="git_link" value="{escape(state.STATE["git_link"])}" placeholder="https://github.com/..." />
        </div>
        <div class="field">
          <label for="lab_link">Link code/tài liệu LABCODE</label>
          <input class="link-input" id="lab_link" name="lab_link" value="{escape(state.STATE["lab_link"])}" placeholder="https://vlearn... hoặc link bài lab" />
        </div>
        <div class="field">
          <label for="num_members">Số lượng thành viên (2-6)</label>
          <input type="number" class="link-input" id="num_members" name="num_members" min="2" max="6" value="{state.STATE.get("num_members", 3)}" />
        </div>
      </div>
      {fallback_field}
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
    data = state.active_analysis()
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
          <div class="stat"><strong>{len(state.ROLES)}</strong><span>vai trò gợi ý cho nhóm</span></div>
          <div class="stat"><strong>{'Cần hỏi lại' if state.STATE["low_confidence"] else 'Đủ mock'}</strong><span>mức tin cậy của phân tích</span></div>
        </div>
        <div class="link-preview">
          <span><strong>Git:</strong> {escape(state.STATE["git_link"])}</span>
          <span><strong>Lab:</strong> {escape(state.STATE["lab_link"])}</span>
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
    for role in state.ROLES:
        task_inputs = []
        for index, task in enumerate(state.STATE["role_tasks"][role["id"]]):
            task_inputs.append(
                f"""
                <div class="task-edit">
                  <label for="{role["id"]}-task-{index}">Việc cần làm {index + 1}</label>
                  <input class="edit-input" id="{role["id"]}-task-{index}" name="task_{role["id"]}_{index}" value="{escape(task)}">
                </div>
                """
            )
        member = escape(state.STATE["members"][role["id"]])
        output = escape(state.STATE["role_outputs"][role["id"]])
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
          <p class="eyebrow">Nhóm {len(state.ROLES)} người</p>
          <h3>AI đã tạo role, nhóm có thể sửa trước khi nhận việc</h3>
        </div>
        <button class="primary" name="action" value="confirm_roles">Tạo task riêng</button>
      </div>
      <div class="roles-grid">{''.join(cards)}</div>
    </form>
    """

def render_progress():
    active_role = state.role_by_id(state.STATE["active_role"])
    tabs = []
    for role in state.ROLES:
        active = " is-active" if role["id"] == state.STATE["active_role"] else ""
        tabs.append(
            f"""
            <form method="post">
              <input type="hidden" name="action" value="select_role">
              <input type="hidden" name="role_id" value="{role["id"]}">
              <button class="role-tab{active}">
                <strong>{escape(role["name"])}</strong><br>
                <span>{escape(state.STATE["members"][role["id"]])}</span>
              </button>
            </form>
            """
        )
    done = state.STATE["done"].get(active_role["id"], set())
    task_items = []
    task_titles = state.STATE["role_tasks"][active_role["id"]]
    for index, task in enumerate(task_titles):
        help_text = active_role["tasks"][index][1] if index < len(active_role["tasks"]) else ""
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
    percent = round(len(done) / len(active_role["tasks"]) * 100) if active_role["tasks"] else 0
    note = (
        "Cảnh báo AI: Tài liệu đầu vào thiếu căn cứ. Các task hiện tại là khung tạm, cần xác minh checkpoint và đầu ra trước khi làm thật."
        if state.STATE["low_confidence"]
        else active_role.get("note", "")
    )
    return f"""
    <div class="progress-layout">
      <aside class="panel role-tabs" aria-label="Danh sách vai trò">{''.join(tabs)}</aside>
      <section class="panel">
        <div class="task-head">
          <div>
            <p class="eyebrow">{escape(active_role["focus"])}</p>
            <h3>{escape(active_role["name"])} - {escape(state.STATE["members"][active_role["id"]])}</h3>
          </div>
          <div class="progress-ring">{percent}%</div>
        </div>
        <div class="role-output">
          <p class="eyebrow">Output của vai trò</p>
          <strong>{escape(state.STATE["role_outputs"][active_role["id"]])}</strong>
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
    }[state.STATE["step"]]()

def render_shell(body_content):
    status = "Cần xác minh" if state.STATE["low_confidence"] else "Sẵn sàng"
    return f"""<!DOCTYPE html>
<html lang="vi">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LABCODE Copilot - {escape(state.page_title())}</title>
    <style>{STYLE}</style>
  </head>
  <body>
    <main class="app-shell">
      {sidebar()}
      <section class="workspace">
        <header class="topbar">
          <div>
            <p class="eyebrow">Prototype Python Mock</p>
            <h2>{state.page_title()}</h2>
          </div>
          <div class="status-pill">{status}</div>
        </header>
        {body_content}
      </section>
    </main>
  </body>
</html>"""
