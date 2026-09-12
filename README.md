# Adcraft — AI-Assisted Digital Advertisement Generator

Adcraft is an AI-powered tool that turns basic product information into a ready-to-use digital
advertisement. Given a product name, description, target audience, and desired mood/format, the
system generates ad copy, a color palette, and an AI-generated visual, then composes them into a
single downloadable ad concept — ready for further refinement in Canva or Photoshop.

Built entirely on **free-tier APIs**, so it can be run and demoed without any paid subscription.

---

## Features

- **AI copywriting** — generates a tagline, supporting subtext, and a call-to-action tailored to the product and audience
- **AI image generation** — produces a relevant background/product visual based on an auto-generated image prompt
- **Automated layout composition** — overlays text, a color-matched CTA button, and a readability scrim onto the generated image using Pillow
- **Multiple ad formats** — Instagram post (1:1), Instagram story (9:16), Facebook banner, YouTube thumbnail
- **One-click export** — download the final composed ad as a PNG

---

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Frontend | HTML, CSS, JavaScript | Form UI and result display |
| Backend | Python (Flask) | REST API, orchestrates AI calls and image processing |
| Text generation | Google Gemini API (`gemini-3.6-flash`, free tier) | Generates tagline, subtext, CTA, color palette, and image prompt as structured JSON |
| Image generation | Pollinations.ai (free, no API key) | Generates the background/product visual from a text prompt |
| Image compositing | Pillow (PIL) | Overlays text and CTA button onto the generated image |
| Config | python-dotenv | Loads the Gemini API key from a local `.env` file |

---

## Architecture

┌─────────────────────┐
│ Frontend (browser) │
│ index.html / .js │
└──────────┬───────────┘
│ POST /api/generate-ad
│ { product_name, product_description, audience, mood, platform }
▼
┌─────────────────────────────────────────────┐
│ Backend — Flask (app.py) │
│ │
│ 1. generate_ad_content() │
│ → calls Gemini, returns JSON: │
│ tagline, subtext, cta, palette, │
│ text_position, image_prompt │
│ │
│ 2. generate_background_image() │
│ → calls Pollinations.ai with image_prompt│
│ returns a PIL Image │
│ │
│ 3. compose_ad() │
│ → overlays tagline/subtext/CTA + scrim │
│ onto the image using Pillow │
└──────────────────┬────────────────────────────┘
│ { image_base64, tagline, subtext, cta, palette, ... }
▼
┌─────────────────────┐
│ Frontend renders │
│ the final ad + a │
│ "Download PNG" button│
└─────────────────────┘


---

## Project Structure

ad-generator/
├── README.md
├── .gitignore
├── backend/
│ ├── app.py # Flask app: routes, Gemini + Pollinations calls, image composition
│ ├── requirements.txt # Python dependencies
│ ├── .env.example # Template for the Gemini API key
│ └── fonts/
│ ├── DejaVuSans.ttf
│ └── DejaVuSans-Bold.ttf
└── frontend/
├── index.html
├── style.css
└── script.js


---

## Getting Started

### Prerequisites
- Python 3.10+
- A free Gemini API key

### 1. Get a Gemini API key (free)

Go to [aistudio.google.com/apikey](https://aistudio.google.com/apikey), sign in with a Google
account, and click **Create API key**. No billing or credit card is required for the free tier.

Image generation uses Pollinations.ai, which requires no API key at all.

### 2. Set up the backend

```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# open .env and set: GEMINI_API_KEY=your_key_here

python app.py
```

The backend runs at `http://localhost:5000`.

### 3. Run the frontend

Open `frontend/index.html` directly in a browser (double-click it, or right-click →
Open with Browser), fill in the form, and click **Generate ad concept**.

> If the backend runs on a different host/port, update the `API_BASE` constant at the
> top of `frontend/script.js`.

---

## API Reference

### `POST /api/generate-ad`

**Request body:**

```json
{
  "product_name": "Bloomleaf Organic Face Cream",
  "product_description": "Lightweight daily moisturizer made with cold-pressed aloe and no synthetic fragrance",
  "audience": "Women 20–35 who prefer clean, minimal skincare",
  "mood": "luxury and minimal",
  "platform": "instagram_post"
}
```

`platform` accepts: `instagram_post`, `instagram_story`, `facebook_banner`, `youtube_thumbnail`

**Response (200):**

```json
{
  "image_base64": "data:image/png;base64,...",
  "tagline": "Glow Naturally, Every Day",
  "subtext": "Lightweight hydration made from cold-pressed aloe.",
  "cta": "Shop Now",
  "palette": { "primary": "#...", "secondary": "#...", "text_on_image": "#..." },
  "text_position": "bottom",
  "platform": "instagram_post",
  "generated_at": "2026-09-13T10:00:00.000000"
}
```

**Error (400/500):**

```json
{ "error": "description of what went wrong" }
```

---

## Example Input

| Field | Example value |
|---|---|
| Product name | Bloomleaf Organic Face Cream |
| Description | Lightweight daily moisturizer, cold-pressed aloe, no synthetic fragrance |
| Audience | Women 20–35 who prefer clean, minimal skincare |
| Mood | Luxury & minimal |
| Format | Instagram post (1:1) |

Output: a fully composed ad — background visual, tagline, supporting line, and CTA button, all
in a single downloadable PNG.

---

## Roadmap

- [ ] User authentication (login/signup) with saved ad history
- [ ] Multiple layout variations generated per request, with user selection
- [ ] Custom brand color and logo upload
- [ ] Optional Stable Diffusion / Stability AI backend for higher image quality
- [ ] Persistent storage (SQLite) for generated ads

---

## License

This project was built for academic purposes as part of a coursework assignment.
