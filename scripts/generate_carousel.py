#!/usr/bin/env python3
"""
🚀 Hamad Carousel Generator
نظام توليد الكاروسيل الأسبوعي — @hamad_failakawi

الاستخدام:
    python generate_carousel.py
    python generate_carousel.py --topic "قانون الجذب"
    python generate_carousel.py --dry-run   # معاينة بدون رفع لـ Canva
"""

import os
import sys
import json
import argparse
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# ─── الإعدادات ───────────────────────────────────────────────
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
CANVA_DESIGN_ID   = "DAHFiuiA1vE"   # claude Hamads Carousal

# معرفات عناصر النص في Canva (سلايد 1 → 6)
ELEMENT_IDS = {
    1: "PBg3Hsm1vXF7xZ9S-LBr1n18DqqWHCyPh",
    2: "PBcM1MSMChHvHJ1C-LB80Y8XxjfTG0sYF",
    3: "PB91b655CZQc6BJj-LBhb9yp6M4ByHKJL",
    4: "PBJPs5x3Hrn0T1cf-LBnDJDqr85wml8VB",
    5: "PBKMSDvZ7DCnZdC3-LBTWCrtqswcKnJj2",
    6: "PBJ7w6VRp10Rg8ZN-LBPSMzXx2ljCX6Ml",
}

# ─── توليد المحتوى ───────────────────────────────────────────
SYSTEM_PROMPT = """أنت كاتب محتوى متخصص بأسلوب حمد الفيلكاوي (@hamad_failakawi).

قواعد الكتابة الصارمة:
1. الكفر (سلايد 1): قصة شخصية قصيرة + كشف الموضوع باسمه
2. السلايدات 2-7: كل سلايد فكرة واحدة + جملة قوية بين ""
3. السلايد 7 (CTA): ينتهي دائماً بـ: اكتبلي (ارسل) بالتعليقات وراح ارسل لك رابط التحدي
4. لغة: عامية كويتية/خليجية، جمل قصيرة، نبرة مباشرة
5. لا هاشتاقات

يجب الرد بـ JSON صرف فقط."""

USER_PROMPT_TEMPLATE = """{topic_instruction}

اكتب كاروسيل من 6 سلايدات. الرد JSON فقط بهذا الشكل:
{{"topic":"العنوان","slides":[
  {{"num":1,"type":"hook","text":"..."}},
  {{"num":2,"type":"content","text":"..."}},
  {{"num":3,"type":"content","text":"..."}},
  {{"num":4,"type":"content","text":"..."}},
  {{"num":5,"type":"content","text":"..."}},
  {{"num":6,"type":"cta","text":"..."}}
]}}"""


def generate_content(topic: str | None = None) -> dict:
    """يولّد محتوى الكاروسيل باستخدام Claude API"""
    if not ANTHROPIC_API_KEY:
        raise ValueError("❌ ANTHROPIC_API_KEY غير موجود في .env")

    if topic:
        topic_instruction = f"الموضوع المحدد: {topic}"
    else:
        topic_instruction = (
            "اختر أقوى موضوع حالياً في: الوعي الذاتي، "
            "التطوير الشخصي، النجاح، الإنتاجية، القوانين الكونية."
        )

    response = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": "claude-sonnet-4-6",
            "max_tokens": 1500,
            "system": SYSTEM_PROMPT,
            "messages": [
                {"role": "user", "content": USER_PROMPT_TEMPLATE.format(
                    topic_instruction=topic_instruction
                )}
            ],
        },
        timeout=60,
    )
    response.raise_for_status()

    text = response.json()["content"][0]["text"]
    # استخراج JSON
    start = text.find("{")
    end   = text.rfind("}") + 1
    return json.loads(text[start:end])


# ─── Canva Integration ────────────────────────────────────────
def push_to_canva(slides: list[dict], topic: str) -> bool:
    """يدفع المحتوى إلى Claude عشان يرفعه لـ Canva"""
    print("\n📤 المحتوى جاهز للرفع إلى Canva:")
    print(f"   الموضوع: {topic}")
    print(f"   Design ID: {CANVA_DESIGN_ID}")
    print("\n💡 لرفع المحتوى تلقائياً، استخدم Claude في المحادثة:")
    print('   قل: "ولّد واحد" أو الصق المحتوى التالي:\n')

    for slide in slides:
        print(f"[سلايد {slide['num']}]")
        print(slide['text'])
        print()

    return True


# ─── عرض المحتوى ─────────────────────────────────────────────
def display_carousel(data: dict) -> None:
    """يعرض الكاروسيل بشكل منسق"""
    week_num = datetime.now().isocalendar()[1]
    year     = datetime.now().year

    print("\n" + "═" * 60)
    print(f"  🚀 كاروسيل الأسبوع {week_num} — {year}")
    print(f"  📌 الموضوع: {data['topic']}")
    print("═" * 60)

    icons = {1: "🎯", 2: "💡", 3: "💡", 4: "💡", 5: "💡", 6: "📣"}

    for slide in data["slides"]:
        icon = icons.get(slide["num"], "•")
        stype = {"hook": "كفر", "content": "محتوى", "cta": "CTA"}.get(
            slide["type"], slide["type"]
        )
        print(f"\n{icon} سلايد {slide['num']} [{stype}]")
        print("─" * 40)
        print(slide["text"])

    print("\n" + "═" * 60)


# ─── حفظ JSON ─────────────────────────────────────────────────
def save_output(data: dict) -> str:
    """يحفظ المحتوى كـ JSON"""
    os.makedirs("output", exist_ok=True)
    date_str  = datetime.now().strftime("%Y-%m-%d")
    filename  = f"output/carousel_{date_str}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\n💾 تم الحفظ: {filename}")
    return filename


# ─── Main ─────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="مولّد الكاروسيل الأسبوعي — @hamad_alfailakawi"
    )
    parser.add_argument("--topic",    type=str, help="موضوع محدد (اختياري)")
    parser.add_argument("--dry-run",  action="store_true", help="معاينة بدون رفع لـ Canva")
    parser.add_argument("--save",     action="store_true", help="احفظ المحتوى كـ JSON")
    args = parser.parse_args()

    print("🔍 جاري توليد المحتوى...")
    data = generate_content(args.topic)

    display_carousel(data)

    if args.save:
        save_output(data)

    if not args.dry_run:
        push_to_canva(data["slides"], data["topic"])
    else:
        print("\n⚠️  Dry Run — المحتوى لم يُرفع إلى Canva")


if __name__ == "__main__":
    main()
