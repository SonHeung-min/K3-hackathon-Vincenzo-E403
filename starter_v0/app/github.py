import urllib.request
import urllib.error
import json
import re
import os

def parse_github_url(url):
    """
    Parses a GitHub URL to extract owner and repository name.
    Supports formats like:
    - https://github.com/owner/repo
    - https://github.com/owner/repo.git
    - github.com/owner/repo
    """
    url = url.strip()
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url
        
    pattern = r"github\.com/([^/]+)/([^/]+?)(?:\.git|/)?$"
    match = re.search(pattern, url)
    if match:
        return match.group(1), match.group(2)
    return None, None

def fetch_github_readme(repo_url):
    """
    Fetches the README file content from a GitHub repository.
    First tries the official GitHub API. If it fails or is private/unauthorized,
    falls back to fetching the raw content directly from raw.githubusercontent.com.
    """
    owner, repo = parse_github_url(repo_url)
    if not owner or not repo:
        return None, f"Định dạng URL GitHub không hợp lệ: {repo_url}"
        
    # Get GITHUB_TOKEN if available to avoid API limits
    token = os.environ.get("GITHUB_TOKEN")
    
    # 1. Try GitHub API
    api_url = f"https://api.github.com/repos/{owner}/{repo}/readme"
    req = urllib.request.Request(api_url)
    req.add_header("User-Agent", "LabSplitter-App")
    req.add_header("Accept", "application/vnd.github.raw+json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
        
    try:
        with urllib.request.urlopen(req) as response:
            content = response.read().decode("utf-8")
            return content, None
    except urllib.error.HTTPError as e:
        # If API rate limits or not found, try the raw content URL fallback (useful for public/main branch repos)
        print(f"GitHub API call failed: {e.code}. Trying raw content URL fallback...")
    except Exception as e:
        print(f"GitHub API connection failed: {str(e)}. Trying raw content URL fallback...")
        
    # 2. Raw URL Fallback (try main branch first, then master)
    for branch in ["main", "master"]:
        raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/README.md"
        raw_req = urllib.request.Request(raw_url)
        raw_req.add_header("User-Agent", "LabSplitter-App")
        if token:
            raw_req.add_header("Authorization", f"Bearer {token}")
        try:
            with urllib.request.urlopen(raw_req) as response:
                content = response.read().decode("utf-8")
                return content, None
        except Exception:
            continue
            
    return None, f"Không thể tải tài liệu tự động từ repository '{owner}/{repo}'. Hãy kiểm tra lại link hoặc sử dụng khung nhập tài liệu dự phòng bên dưới."
