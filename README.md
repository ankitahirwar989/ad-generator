# Adcraft — AI-Assisted Digital Advertisement Generator

Yeh project user se **product info + target audience + ad requirements** leta hai, aur AI se
**tagline, ad copy, color palette, aur ek generated visual** bana ke ek ready ad concept deta hai
(jise aage Canva/Photoshop me edit kiya ja sakta hai).

Yeh version **poori tarah free stack** use karta hai — koi paid API key nahi chahiye.

## Kaise kaam karta hai (architecture)

```
Frontend form (index.html)
        │  product info, audience, mood, platform
        ▼
Backend /api/generate-ad (Flask, app.py)
        │
        ├─► Google Gemini (gemini-2.5-flash, FREE)  → tagline, subtext, CTA, color palette, image prompt
        │
        ├─► Pollinations.ai (FREE, no API key)      → background/product visual
        │
        └─► Pillow                                  → text + colors ko image ke upar overlay karke
                                                          final ad compose karta hai
        ▼
Frontend: final ad image dikhata hai + "Download PNG" button
```

## Folder structure

```
ad-generator/
├── backend/
│   ├── app.py              ← Flask server + AI calls + image composition
│   ├── requirements.txt
│   ├── .env.example        ← isse .env banao aur API key daalo
│   └── fonts/               ← DejaVu Sans (bundled, so text overlay hamesha kaam kare)
└── frontend/
    ├── index.html
    ├── style.css
    └── script.js
```

## Setup — Step by Step

### 1. Gemini API key lo (FREE)
[aistudio.google.com/apikey](https://aistudio.google.com/apikey) pe jaake Google account se login karo,
"Create API key" click karo. Koi credit card ya billing nahi chahiye — free tier turant milta hai.

Image generation ke liye **Pollinations.ai** use ho raha hai — usme koi API key hi nahi chahiye.

### 2. Backend setup

```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows par: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# .env file kholo aur GEMINI_API_KEY=your_key_here me apni real key daalo

python app.py
```

Backend `http://localhost:5000` pe chalega.

### 3. Frontend kholo

`frontend/index.html` file ko directly browser me open karo (double-click karo, ya
right-click → Open with Browser). Form fill karo aur "Generate ad concept" click karo.

> Agar tum backend ko kisi doosre port/host pe chala rahe ho, to `frontend/script.js`
> ke top pe `API_BASE` variable update kar dena.

## Kaise use karo (example)

| Field | Example value |
|---|---|
| Product name | Bloomleaf Organic Face Cream |
| Description | Lightweight daily moisturizer, cold-pressed aloe, no synthetic fragrance |
| Audience | Women 20–35 jo clean, minimal skincare pasand karti hain |
| Mood | Luxury & minimal |
| Format | Instagram post (1:1) |

Result: ek complete ad — background visual + tagline + supporting line + CTA button, sab
generated aur ek hi PNG me composed. "Download PNG" se save karke Canva/Photoshop me
aage edit kar sakte ho.

## Aage kya improve kar sakte ho (project report ke liye extra points)

- Multiple layout variations ek saath generate karna (user 3 options me se choose kare)
- User ko apna brand color/logo upload karne dena
- Generated ad history save karna (SQLite database)
- Agar image quality aur better chahiye to Stability AI ka free trial credit try kar sakte ho
