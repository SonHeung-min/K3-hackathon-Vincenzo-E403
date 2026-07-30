from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs
import os
import sys
from . import state
from .ai import call_ai_api
from .github import fetch_github_readme
from .views import render_body, render_shell

def handle_form(fields):
    action = fields.get("action", [""])[0]
    if action == "analyze":
        state.STATE["git_link"] = fields.get("git_link", [state.STATE["git_link"]])[0].strip()
        state.STATE["lab_link"] = fields.get("lab_link", [state.STATE["lab_link"]])[0].strip()
        
        num_members_str = fields.get("num_members", ["3"])[0].strip()
        try:
            state.STATE["num_members"] = int(num_members_str)
        except ValueError:
            state.STATE["num_members"] = 3
        state.STATE["num_members"] = max(2, min(6, state.STATE["num_members"]))
        
        # Check if we should use pasted document (fallback)
        pasted = fields.get("pasted_doc", [""])[0].strip()
        if state.STATE.get("show_fallback", False) and pasted:
            state.STATE["pasted_doc"] = pasted
            doc_content = pasted
            state.STATE["doc"] = pasted
            state.STATE["error_msg"] = ""
        else:
            # Try to fetch from GitHub
            fetched_content, fetch_err = fetch_github_readme(state.STATE["git_link"])
            if fetch_err:
                # Show error, activate fallback, and stay on upload page
                state.STATE["error_msg"] = fetch_err
                state.STATE["show_fallback"] = True
                state.STATE["step"] = "upload"
                return
            else:
                doc_content = fetched_content
                state.STATE["doc"] = fetched_content
                state.STATE["pasted_doc"] = fetched_content
                state.STATE["error_msg"] = ""
                state.STATE["show_fallback"] = False
                
        parsed_ai, err = call_ai_api(state.STATE["git_link"], state.STATE["lab_link"], doc_content, num_members=state.STATE["num_members"])
        
        if err:
            state.STATE["error_msg"] = f"Lỗi gọi Gemini API: {err}"
            state.STATE["low_confidence"] = True
            state.STATE["step"] = "upload"
            return
        else:
            state.NORMAL_ANALYSIS = parsed_ai.get("analysis", state.NORMAL_ANALYSIS)
            state.RISKY_ANALYSIS = state.NORMAL_ANALYSIS
            state.ROLES = parsed_ai.get("roles", state.ROLES)
            
            for i, role in enumerate(state.ROLES):
                role["member"] = f"Bạn {chr(65+i)}"
            
            state.STATE["low_confidence"] = parsed_ai.get("low_confidence", False)
            state.STATE["members"] = {role["id"]: role.get("member", "Chưa gán") for role in state.ROLES}
            state.STATE["role_tasks"] = {role["id"]: [task[0] if len(task) > 0 else "Task" for task in role.get("tasks", [])] for role in state.ROLES}
            
            # Cập nhật tasks vào trong ROLES luôn để giao diện render help_text đúng (tránh list index out of range)
            for role in state.ROLES:
                new_tasks = []
                for t in role.get("tasks", []):
                    if len(t) >= 2:
                        new_tasks.append(t)
                    elif len(t) == 1:
                        new_tasks.append([t[0], ""])
                    else:
                        new_tasks.append(["Task", ""])
                role["tasks"] = new_tasks
                
            state.STATE["role_outputs"] = {role["id"]: role.get("output", "") for role in state.ROLES}
            state.STATE["active_role"] = state.ROLES[0]["id"] if state.ROLES else "pm"
            state.STATE["done"] = {}
        state.STATE["step"] = "analysis"
    elif action == "load_risky":
        state.STATE["git_link"] = "https://github.com/nhom-demo/labcode-cp2"
        state.STATE["lab_link"] = "link lab bị thiếu yêu cầu đầu ra"
        state.STATE["doc"] = state.RISKY_DOC
        state.STATE["low_confidence"] = True
        state.STATE["error_msg"] = "Tài liệu bị thiếu thông tin cần thiết. Vui lòng bổ sung."
        state.STATE["show_fallback"] = True
        state.STATE["pasted_doc"] = state.RISKY_DOC
        state.STATE["step"] = "upload"
    elif action == "assign_roles":
        state.STATE["step"] = "roles"
    elif action == "confirm_roles":
        for role in state.ROLES:
            key = f"member_{role['id']}"
            if fields.get(key, [""])[0].strip():
                state.STATE["members"][role["id"]] = fields[key][0].strip()
            output_key = f"output_{role['id']}"
            if fields.get(output_key, [""])[0].strip():
                state.STATE["role_outputs"][role["id"]] = fields[output_key][0].strip()
            for index in range(len(role["tasks"])):
                task_key = f"task_{role['id']}_{index}"
                if fields.get(task_key, [""])[0].strip():
                    state.STATE["role_tasks"][role["id"]][index] = fields[task_key][0].strip()
        state.STATE["step"] = "progress"
    elif action == "select_role":
        state.STATE["active_role"] = fields.get("role_id", [state.STATE["active_role"]])[0]
        state.STATE["step"] = "progress"
    elif action == "update_progress":
        role_id = fields.get("role_id", [state.STATE["active_role"]])[0]
        state.STATE["active_role"] = role_id
        state.STATE["done"][role_id] = set(fields.get("done", []))
        state.STATE["step"] = "progress"
    elif action == "back_upload":
        state.STATE["step"] = "upload"
    elif action == "goto":
        target = fields.get("step", [state.STATE["step"]])[0]
        allowed = [step[0] for step in state.STEPS]
        current_index = allowed.index(state.STATE["step"])
        if target in allowed and allowed.index(target) <= current_index:
            state.STATE["step"] = target

class LabcodeHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.respond()

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length).decode("utf-8")
        handle_form(parse_qs(body))
        self.respond()

    def respond(self):
        page = render_shell(render_body()).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(page)))
        self.end_headers()
        self.wfile.write(page)

    def log_message(self, format, *args):
        return

def run_server():
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
