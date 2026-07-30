import sys
import os
from pathlib import Path

# Add path for local imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from env_loader import load_lab_env
load_lab_env(Path(__file__).parent)

from app import state
from app.github import parse_github_url, fetch_github_readme
from app.ai import call_ai_api
from app.server import handle_form

def run_tests():
    print("=== CHẠY KIỂM THỬ TỰ ĐỘNG CÁC MÔ-ĐUN APP ===")
    
    # 1. Test state initialization
    print("\n[Test 1] Kiểm tra khởi tạo state:")
    print(f"Bắt đầu tại step: {state.STATE['step']}")
    print(f"Số lượng thành viên mặc định: {state.STATE['num_members']}")
    assert state.STATE["step"] == "upload"
    assert state.STATE["num_members"] == 3
    print("-> ĐẠT!")

    # 2. Test GitHub URL parsing
    print("\n[Test 2] Kiểm tra parse URL GitHub:")
    owner, repo = parse_github_url("https://github.com/octocat/Spoon-Knife")
    print(f"URL: https://github.com/octocat/Spoon-Knife => Owner: {owner}, Repo: {repo}")
    assert owner == "octocat"
    assert repo == "Spoon-Knife"
    print("-> ĐẠT!")

    # 3. Test GitHub README fetching (with API or Fallback)
    print("\n[Test 3] Kiểm tra fetch README GitHub:")
    content, err = fetch_github_readme("https://github.com/octocat/Spoon-Knife")
    if err:
        print(f"-> Lỗi fetch: {err}")
    else:
        print(f"-> Thành công! Độ dài README: {len(content)} ký tự.")
        assert len(content) > 0
        print("-> ĐẠT!")

    # 4. Test Gemini API integration with dynamic member counts (e.g., 4 members)
    print("\n[Test 4] Kiểm tra gọi Gemini API với 4 thành viên:")
    sample_text = "Bài lab yêu cầu xây dựng ứng dụng chatbot AI có 4 chức năng chính: Đăng nhập, Giao diện chat, Lưu lịch sử, và Phân tích cảm xúc."
    parsed, err = call_ai_api("https://github.com/test/repo", "https://test.com/lab", sample_text, num_members=4)
    if err:
        print(f"-> Lỗi gọi Gemini: {err}")
        print("-> BỎ QUA do thiếu API key hoặc API lỗi (nếu có).")
    else:
        print("-> Thành công! Dữ liệu trả về từ Gemini:")
        print(f"Số lượng roles tạo ra: {len(parsed.get('roles', []))}")
        print("Danh sách các vai trò:")
        for r in parsed.get("roles", []):
            print(f"  - {r['id']}: {r['name']} ({r.get('focus', '')})")
            for t in r.get("tasks", []):
                print(f"    * Task: {t[0]} - {t[1]}")
        assert len(parsed.get("roles", [])) == 4
        print("-> ĐẠT!")

    # 5. Test handle_form 'analyze' logic with fallback doc
    print("\n[Test 5] Kiểm tra handle_form xử lý fallback khi git link lỗi:")
    fields = {
        "action": ["analyze"],
        "git_link": ["https://github.com/error-user/private-repo"],
        "lab_link": ["https://vlearn.vinuni.edu.vn/labcode"],
        "num_members": ["5"]
    }
    handle_form(fields)
    print(f"Sau khi submit repo lỗi:")
    print(f"  - show_fallback: {state.STATE.get('show_fallback')}")
    print(f"  - error_msg: {state.STATE.get('error_msg')}")
    print(f"  - step: {state.STATE.get('step')}")
    assert state.STATE["show_fallback"] is True
    assert state.STATE["step"] == "upload"
    print("-> ĐẠT!")

    # 6. Test handle_form 'analyze' with pasted fallback text
    print("\n[Test 6] Kiểm tra handle_form chạy với văn bản dán thủ công (fallback):")
    fields = {
        "action": ["analyze"],
        "git_link": ["https://github.com/error-user/private-repo"],
        "lab_link": ["https://vlearn.vinuni.edu.vn/labcode"],
        "num_members": ["5"],
        "pasted_doc": ["Tài liệu bài LAB 04 yêu cầu xây dựng Research Agent và đo đạc thông số."]
    }
    handle_form(fields)
    print(f"Sau khi gửi fallback document:")
    print(f"  - show_fallback: {state.STATE.get('show_fallback')}")
    print(f"  - step: {state.STATE.get('step')}")
    print(f"  - Số lượng vai trò: {len(state.ROLES)}")
    assert state.STATE["step"] == "analysis"
    assert len(state.ROLES) == 5
    print("-> ĐẠT!")

if __name__ == "__main__":
    run_tests()
