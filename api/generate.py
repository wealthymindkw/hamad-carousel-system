from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.request
import urllib.error

# ─── قراءة ملف الأسلوب ───────────────────────────────────────
def load_style_guide() -> str:
    style_path = os.path.join(os.path.dirname(__file__), "..", "config", "style_corrections.md")
    try:
        with open(style_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""

SYSTEM_PROMPT_BASE = """أنت كاتب محتوى متخصص بأسلوب حمد الفيلكاوي (@hamad_failakawi).

{style_guide}

قواعد الكتابة الصارمة:
1. الكفر (سلايد 1): قصة شخصية قصيرة + كشف الموضوع باسمه
2. السلايدات 2-5: كل سلايد فكرة واحدة + جملة قوية بين ""
3. السلايد 6 (CTA): ينتهي دائماً بـ: اكتبلي (ارسل) بالتعليقات وراح ارسل لك رابط التحدي
4. لغة: عامية كويتية/خليجية، جمل قصيرة، نبرة مباشرة
5. لا هاشتاقات

يجب الرد بـ JSON صرف فقط."""

USER_PROMPT_TEMPLATE = """{topic_instruction}

{corrections_block}
اكتب كاروسيل من 6 سلايدات. الرد JSON فقط بهذا الشكل:
{{"topic":"العنوان","slides":[
  {{"num":1,"type":"hook","text":"..."}},
  {{"num":2,"type":"content","text":"..."}},
  {{"num":3,"type":"content","text":"..."}},
  {{"num":4,"type":"content","text":"..."}},
  {{"num":5,"type":"content","text":"..."}},
  {{"num":6,"type":"cta","text":"..."}}
]}}"""


def build_corrections_block(corrections: list) -> str:
    if not corrections:
        return ""
    lines = ["--- تصحيحات أسلوب المستخدم (تعلّم منها) ---"]
    for c in corrections:
        lines.append(f'النص الأصلي: {c.get("original", "")[:200]}')
        lines.append(f'التصحيح:    {c.get("corrected", "")[:200]}')
        lines.append("")
    lines.append("---")
    return "\n".join(lines) + "\n\n"


def generate_content(api_key: str, topic: str = None, corrections: list = None) -> dict:
    style_guide = load_style_guide()

    system_prompt = SYSTEM_PROMPT_BASE.format(
        style_guide=f"--- دليل الأسلوب ---\n{style_guide}\n---\n" if style_guide else ""
    )

    if topic:
        topic_instruction = f"الموضوع المحدد: {topic}"
    else:
        topic_instruction = (
            "اختر أقوى موضوع حالياً في: الوعي الذاتي، "
            "التطوير الشخصي، النجاح، الإنتاجية، القوانين الكونية."
        )

    corrections_block = build_corrections_block(corrections or [])

    payload = json.dumps({
        "model": "claude-sonnet-4-6",
        "max_tokens": 1800,
        "system": system_prompt,
        "messages": [
            {"role": "user", "content": USER_PROMPT_TEMPLATE.format(
                topic_instruction=topic_instruction,
                corrections_block=corrections_block,
            )}
        ],
    }, ensure_ascii=False).encode("utf-8")

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=payload,
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=60) as resp:
        result = json.loads(resp.read().decode("utf-8"))

    text = result["content"][0]["text"]
    start = text.find("{")
    end = text.rfind("}") + 1
    return json.loads(text[start:end])


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length)) if length else {}

            topic       = (body.get("topic") or "").strip() or None
            corrections = body.get("corrections") or []
            api_key     = (os.getenv("ANTHROPIC_API_KEY") or "").strip()

            if not api_key:
                self._json(400, {"error": "ANTHROPIC_API_KEY غير موجود في إعدادات الخادم"})
                return

            data = generate_content(api_key, topic, corrections)
            self._json(200, data)

        except urllib.error.HTTPError as e:
            self._json(e.code, {"error": f"خطأ من Anthropic API — تحقق من صلاحية المفتاح"})
        except Exception as e:
            self._json(500, {"error": str(e)})

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _json(self, status, data):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self._cors()
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def log_message(self, format, *args):
        pass
