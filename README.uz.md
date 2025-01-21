# Bitiruv malakaviy ishi generatori 📚

*Boshqa tillarda o'qing: [English](README.md), [Русский](README.ru.md)*

Ushbu avtomatlashtirilgan vosita manba kod fayllarini tahlil qiladi va API integratsiyasi orqali Katta Til Modellari (LLM) yordamida tuzilgan bitiruv malakaviy ishi hujjatini yaratadi.

## Old shartlar ✅

- Python 3.8 yoki undan yuqori versiyasi
- OpenAI-ga mos keluvchi API'ga kirish imkoniyati (Google, Anthropic yoki OpenAI)
- **Tahlil qilish uchun loyiha manba kod fayllari**

## O'rnatish 🛠️

1. Repozitoriyni klonlang:
```bash
git clone https://github.com/sukhrobyangibaev/bmi_first_draft.git
cd bmi_first_draft
```

2. Kerakli bog'liqliklarni o'rnating:
```bash
pip install -r requirements.txt
```

3. Atrof-muhit konfiguratsiyasini yarating:
```bash
cp .env.example .env
```

4. `.env` faylingizni tegishli sozlamalar bilan konfiguratsiya qiling:
```env
API_KEY=your_api_key_here
BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
LOW_RATE_LIMITS=true
MODEL=gemini-exp-1206
PROJECT_FILES_DIR=project_files
TRANSLATE=true
TRANSLATION_LANG=UZ
```

Muhim konfiguratsiya eslatmalari:

- **API_KEY**: [Google AI Studio](https://aistudio.google.com/app/apikey) dan bepul Gemini API kalitingizni oling
- **BASE_URL**: Gemini API'dan foydalanayotganda standart qiymatni saqlang
- **LOW_RATE_LIMITS**: Bepul Gemini API kalitidan foydalanayotganda `true` qiymatida qoldiring (kerakli so'rov kechikishlarini qo'shadi)
- **MODEL**: Mavjud modellarni [Gemini API hujjatlari](https://ai.google.dev/gemini-api/docs/models/gemini)da topish mumkin. Hozirda `gemini-exp-1206` eng yaxshi natijalarni beradi
- **PROJECT_FILES_DIR**: Manba kod fayllaringizni saqlash uchun ushbu nom bilan papka yarating
- **TRANSLATE**: Agar tarjima kerak bo'lsa `true` ga, faqat ingliz tili kerak bo'lsa `false` ga o'rnating
- **TRANSLATION_LANG**: Ruscha tarjima uchun `RU` yoki O'zbekcha tarjima uchun `UZ` dan foydalaning

## Foydalanish 🚀

1. Loyihangizning asosiy manba kod fayllarini `project_files` katalogiga joylashtiring:
   - Faqat asosiy loyiha fayllaringizni kiriting
   - Tashqi kutubxonalar, virtual muhitlar yoki bog'liqlik fayllarini kiritmang
   - Misol: Agar sizda Python loyihasi bo'lsa, `.py` fayllaringizni kiriting, lekin `venv/` yoki `site-packages/` papkalarini kiritmang

2. Bitiruv malakaviy ishi generatorini ishga tushiring:
```bash
python first_draft.py
```

3. Skript `draft` katalogida ikkita asosiy fayl yaratadi:
   - `draft/EN/THESIS_PLAN_EN.txt`: Bitiruv malakaviy ishi tuzilmasi va rejasi
   - `draft/EN/THESIS_MAIN_TEXT_EN.txt`: Bitiruv malakaviy ishining to'liq matni

4. Agar tarjima yoqilgan bo'lsa, qo'shimcha fayllar quyidagi kataloglarda yaratiladi:
   - `draft/RU/` ruscha tarjima uchun
   - `draft/UZ/` o'zbekcha tarjima uchun

> **Eslatma:** Yaratilgan matn birinchi qoralama hisoblanadi va uni diqqat bilan ko'rib chiqish va tahrirlash kerak. Bu ayniqsa tarjima qilingan versiyalar uchun muhim.

## Chiqish tuzilmasi 📋

Yaratilgan bitiruv malakaviy ishi quyidagi tuzilmaga ega:

1. Kirish
   - Dolzarbligi
   - Maqsadi
   - Ob'ekti
   - Predmeti

2. I Qism: Tizimli tahlil
   - Umumiy tahlil (§1.1)
   - Prinsiplar (§1.2)
   - Muammoning qo'yilishi (§1.3)

3. II Qism: Ishlab chiqish
   - Loyihalash va yaratish (§2.1)
   - Ishlab chiqish ketma-ketligi (§2.2)
   - Foydalanish bo'yicha ko'rsatmalar (§2.3)

4. Xulosa

5. Foydalanilgan adabiyotlar

6. Ilova

## Hissa qo'shish 🤝

Hissa qo'shish xush kelibsiz! Iltimos, Pull Request yuborishdan tortinmang.

## Yordam ❓

Muammolar va funksiya so'rovlari uchun, iltimos, repozitoriyda issue yarating.

## Minnatdorchilik 🙏

Gemini API'ga bepul kirish imkoniyatini taqdim etgani uchun Google'ga alohida minnatdorchilik bildiramiz.
