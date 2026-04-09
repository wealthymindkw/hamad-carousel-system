from http.server import BaseHTTPRequestHandler
import json
import os
import base64
import urllib.request
import urllib.error

REPO       = "wealthymindkw/hamad-carousel-system"
FILE_PATH  = "config/corrections.json"
API_BASE   = "https://api.github.com"
MAX_ITEMS  = 30


def _github_headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "Content-Type": "application/json",
        "User-Agent": "hamad-carousel-system",
    }


def _get_file(token: str) -> tuple[list, str]:
    """Returns (corrections_list, sha). sha needed to update the file."""
    url = f"{API_BASE}/repos/{REPO}/contents/{FILE_PATH}"
    req = urllib.request.Request(url, headers=_github_headers(token))
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
        content = base64.b64decode(data["content"]).decode("utf-8")
        sha = data["sha"]
        corrections = json.loads(content)
        return corrections, sha
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return [], ""
        raise


def _put_file(token: str, corrections: list, sha: str, message: str):
    """Commit updated corrections list to GitHub."""
    url = f"{API_BASE}/repos/{REPO}/contents/{FILE_PATH}"
    content_b64 = base64.b64encode(
        json.dumps(corrections, ensure_ascii=False, indent=2).encode("utf-8")
    ).decode("ascii")

    payload: dict = {
        "message": message,
        "content": content_b64,
    }
    if sha:
        payload["sha"] = sha

    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=_github_headers(token), method="PUT")
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    def do_GET(self):
        token = (os.getenv("GITHUB_TOKEN") or "").strip()
        if not token:
            self._json(200, [])   # بدون token نرجع قائمة فارغة بدل خطأ
            return
        try:
            corrections, _ = _get_file(token)
            self._json(200, corrections)
        except Exception as e:
            self._json(500, {"error": str(e)})

    def do_POST(self):
        token = (os.getenv("GITHUB_TOKEN") or "").strip()
        if not token:
            self._json(503, {"error": "GITHUB_TOKEN غير موجود في إعدادات الخادم"})
            return
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length)) if length else {}

            original  = (body.get("original") or "").strip()
            corrected = (body.get("corrected") or "").strip()

            if not original or not corrected:
                self._json(400, {"error": "original و corrected مطلوبان"})
                return

            corrections, sha = _get_file(token)

            # استبدل لو نفس النص موجود مسبقاً
            corrections = [c for c in corrections if c.get("original") != original]
            corrections.append({"original": original, "corrected": corrected, "ts": body.get("ts", 0)})

            # احتفظ بآخر MAX_ITEMS فقط
            corrections = corrections[-MAX_ITEMS:]

            _put_file(token, corrections, sha, f"style: save correction ({len(corrections)} total)")
            self._json(200, {"ok": True, "total": len(corrections)})

        except Exception as e:
            self._json(500, {"error": str(e)})

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _json(self, status, data):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self._cors()
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def log_message(self, format, *args):
        pass
