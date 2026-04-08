# 🔧 دليل الإعداد

## 1. استنساخ الريبو

```bash
git clone https://github.com/YOUR_USERNAME/hamad-carousel-system.git
cd hamad-carousel-system
```

## 2. إعداد Python

```bash
python -m venv venv
source venv/bin/activate      # Mac/Linux
venv\Scripts\activate         # Windows

pip install requests python-dotenv
```

## 3. إعداد متغيرات البيئة

```bash
cp .env.example .env
```

عدّل ملف `.env`:
```
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxx
```

> 🔑 احصل على مفتاح API من: https://console.anthropic.com

## 4. تشغيل التطبيق

### التطبيق المرئي
```bash
open app/weekly_carousel.html
```

### سكريبت Python
```bash
# توليد تلقائي
python scripts/generate_carousel.py

# موضوع محدد
python scripts/generate_carousel.py --topic "قانون الجذب"

# معاينة فقط
python scripts/generate_carousel.py --dry-run

# حفظ + توليد
python scripts/generate_carousel.py --save
```

## 5. ربط Canva

التطبيق يتصل بـ Canva عبر Claude API تلقائياً.
تأكد من أن حساب Canva مربوط بحساب Claude.

---

## ❓ مشاكل شائعة

**خطأ: API Key غير موجود**
```
❌ ANTHROPIC_API_KEY غير موجود في .env
```
الحل: تأكد من وجود `.env` وأن المفتاح صحيح.

**خطأ: Canva لا يتصل**
الحل: تأكد من ربط Canva في claude.ai → Settings → Integrations.
