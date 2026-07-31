import os
import json
import urllib.request
import time
import datetime
import ssl
import hashlib

def call_ai_api(git_link, lab_link, doc_content, num_members=3):
    # Calculate cache key
    cache_input = f"{git_link}||{lab_link}||{doc_content}||{num_members}"
    cache_key = hashlib.sha256(cache_input.encode('utf-8')).hexdigest()
    
    cache_dir = os.path.join("eval", "cache")
    os.makedirs(cache_dir, exist_ok=True)
    cache_file = os.path.join(cache_dir, f"ai_cache_{cache_key}.json")
    
    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                cached_data = json.load(f)
            print(f"Loaded from cache: {cache_file}")
            return cached_data, None
        except Exception as e:
            print(f"Lỗi đọc cache: {e}")

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return None, "Lỗi: Không tìm thấy biến môi trường GEMINI_API_KEY."
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={api_key}"
    
    prompt = f"""
Bạn là một trợ lý ảo LABCODE Copilot chuyên nghiệp.
Nhiệm vụ của bạn là đọc nội dung tài liệu hướng dẫn lab và link git của nhóm để phân tích, tổng hợp và chia việc cho đúng {num_members} thành viên nhóm.

Dữ liệu đầu vào:
Link Git: {git_link}
Link Lab: {lab_link}
Nội dung lab:
{doc_content}

Dựa vào thông tin trên, hãy trả về kết quả dưới định dạng JSON với cấu trúc CHÍNH XÁC như sau (không thêm markdown code block, chỉ xuất JSON thuần tuý):
{{
  "analysis": {{
    "summary": ["Câu 1", "Câu 2", "Câu 3"],
    "timeline": ["Bước 1", "Bước 2", "Bước 3"],
    "deliverables": [
      ["Tên đầu ra 1", "Mô tả ngắn 1"],
      ["Tên đầu ra 2", "Mô tả ngắn 2"]
    ]
  }},
  "roles": [
    {{
      "id": "pm",
      "name": "Tên vai trò (VD: Product Lead)",
      "focus": "Trọng tâm công việc",
      "tasks": [
        ["Tên task 1", "Mô tả chi tiết 1"],
        ["Tên task 2", "Mô tả chi tiết 2"]
      ],
      "output": "Đầu ra cần nộp của vai trò này",
      "source": "Trích dẫn nguồn từ tài liệu",
      "note": "Ghi chú từ AI cho vai trò này"
    }}
  ],
  "low_confidence": false
}}

Lưu ý quan trọng:
1. Hãy chia việc thành đúng {num_members} vai trò (roles). Mảng "roles" trong JSON trả về bắt buộc phải có CHÍNH XÁC đúng {num_members} phần tử.
2. Với mỗi vai trò, các task cần có tên và mô tả rõ ràng.
3. Trong trường 'tasks', mỗi mô tả task không chỉ ghi "làm gì", mà phải giải thích ngắn:
   - Task này phục vụ mục tiêu lab nào.
   - Input cần lấy từ vai trò/phần việc nào.
   - Output sẽ đưa cho vai trò/phần việc nào.
   - Người làm task này cần hiểu tối thiểu điều gì về phần của teammate.
4. Nếu một task có đầu ra trao đổi dữ liệu với vai trò khác, hãy chỉ rõ định dạng Data Contract ở dạng JSON trong phần mô tả của task để tránh đứt gãy logic (ví dụ: "Đầu ra JSON contract: {{'status': string, 'results': list}}").
5. Trong trường 'note', hãy tóm tắt vai trò này đóng góp gì vào bức tranh chung của lab và người làm vai trò này cần hiểu gì về các vai trò còn lại để demo/Q&A được.
6. Nếu tài liệu cung cấp thiếu thông tin cơ bản, hãy set "low_confidence": true.
"""
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
    req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'})
    
    start_time = time.time()
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        with urllib.request.urlopen(req, context=ctx) as response:
            result = json.loads(response.read().decode('utf-8'))
            
        elapsed = time.time() - start_time
        
        raw_text = result['candidates'][0]['content']['parts'][0]['text']
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        if raw_text.startswith("```"):
            raw_text = raw_text[3:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
            
        parsed_json = json.loads(raw_text.strip())
        
        # Save traces inside eval/traces
        os.makedirs(os.path.join("eval", "traces"), exist_ok=True)
        trace_file = os.path.join("eval", "traces", f"trace_{int(time.time())}.json")
        with open(trace_file, "w", encoding="utf-8") as f:
            json.dump({
                "timestamp": datetime.datetime.now().isoformat(),
                "model": "gemini-3.5-flash",
                "elapsed_seconds": elapsed,
                "input_git": git_link,
                "input_lab": lab_link,
                "prompt": prompt,
                "raw_response": result,
                "parsed": parsed_json
            }, f, ensure_ascii=False, indent=2)
        # Save to cache
        try:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(parsed_json, f, ensure_ascii=False, indent=2)
        except Exception as cache_err:
            print(f"Lỗi ghi cache: {cache_err}")
            
        return parsed_json, None
    except Exception as e:
        return None, str(e)
