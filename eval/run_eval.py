import os
import csv
import json
import time
import urllib.request
import urllib.error
import ssl

try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path="../.env")
except ImportError:
    pass

# Hỗ trợ cả key Gemini thật (Google) và key qua Proxy OpenAI (ví dụ WokuShop)
API_KEY = os.environ.get("GEMINI_API_KEY")
OPENAI_BASE_URL = os.environ.get("OPENAI_BASE_URL")

def call_ai_api(doc_content):
    if not API_KEY:
        return None, "Missing API_KEY in .env"
    
    prompt = f"""
Bạn là một trợ lý ảo LABCODE Copilot chuyên nghiệp.
Nhiệm vụ của bạn là đọc nội dung tài liệu hướng dẫn lab và link git của nhóm để phân tích, tổng hợp và chia việc.

Dữ liệu đầu vào:
Link Git: https://github.com/demo/repo
Link Lab: https://vlearn.vinuni.edu.vn/lab
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

Lưu ý:
- Nếu tài liệu cung cấp thiếu thông tin cơ bản (không có yêu cầu đầu ra, không rõ số lượng thành viên), hãy set "low_confidence": true và giải thích trong "summary" và "roles" (gắn nhãn cần xác minh).
- Cần tạo ít nhất 2 đến 3 role. Mỗi role có từ 2-3 task.
"""

    try:
        # Nếu API Key bắt đầu bằng sk- (OpenAI format proxy)
        if API_KEY.startswith("sk-") and OPENAI_BASE_URL:
            url = f"{OPENAI_BASE_URL.rstrip('/')}/chat/completions"
            data = {
                "model": "gemini-2.5-flash", # Hoặc thay bằng tên model proxy hỗ trợ
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2
            }
            req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {API_KEY}',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            
            with urllib.request.urlopen(req, context=ctx) as response:
                result = json.loads(response.read().decode('utf-8'))
            raw_text = result['choices'][0]['message']['content']

        # Dùng Google Gemini API chuẩn
        else:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
            data = {"contents": [{"parts": [{"text": prompt}]}]}
            req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers={
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0'
            })
            
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            
            with urllib.request.urlopen(req, context=ctx) as response:
                result = json.loads(response.read().decode('utf-8'))
            raw_text = result['candidates'][0]['content']['parts'][0]['text']

        # Parse JSON output
        if raw_text.startswith("```json"): raw_text = raw_text[7:]
        if raw_text.startswith("```"): raw_text = raw_text[3:]
        if raw_text.endswith("```"): raw_text = raw_text[:-3]
            
        return json.loads(raw_text.strip()), None

    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        return None, f"HTTP {e.code}: {error_body}"
    except Exception as e:
        return None, str(e)

def run_eval():
    if not API_KEY:
        print("LỖI: Chưa cấu hình GEMINI_API_KEY trong file .env")
        return

    input_file = "golden_set.csv"
    output_file = "results_run1.csv"
    
    print(f"Bắt đầu chạy đánh giá trên file {input_file}...")
    
    with open(input_file, encoding='utf-8') as f_in:
        reader = csv.DictReader(f_in)
        fieldnames = reader.fieldnames + ['actual_low_confidence', 'actual_summary', 'manual_pass_fail']
        
        with open(output_file, 'w', encoding='utf-8', newline='') as f_out:
            writer = csv.DictWriter(f_out, fieldnames=fieldnames)
            writer.writeheader()
            
            for row in reader:
                case_id = row.get('case_id', 'Unknown')
                print(f"Đang xử lý {case_id}...")
                
                if None in row:
                    del row[None]
                
                ai_res, err = call_ai_api(row.get('doc_content', ''))
                
                actual_low_confidence = ""
                actual_summary = ""
                if err:
                    actual_low_confidence = "ERROR"
                    actual_summary = err
                elif ai_res:
                    actual_low_confidence = str(ai_res.get("low_confidence", False))
                    actual_summary = str(ai_res.get("analysis", {}).get("summary", []))
                
                row['actual_low_confidence'] = actual_low_confidence
                row['actual_summary'] = actual_summary
                row['manual_pass_fail'] = "" 
                
                writer.writerow(row)
                f_out.flush()
                
                time.sleep(4)
                
    print(f"✅ Đã chạy xong! Vui lòng mở file {output_file} để chấm điểm (Pass/Fail).")

if __name__ == "__main__":
    run_eval()
