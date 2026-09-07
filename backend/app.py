"""
AI-Assisted Digital Advertisement Generator — Backend
------------------------------------------------------
Flow (ab poori tarah FREE stack use karke):
  1. User se product info, target audience, aur ad requirements lete hain.
  2. Gemini (gemini-3.6-flash, free tier) se tagline + short ad copy + color palette generate karte hain.
  3. Pollinations.ai (free, no API key) se background/product visual generate karte hain.
  4. Pillow se text ko image ke upar layout ke hisaab se overlay karke final ad banate hain.
  5. Final ad (base64 PNG) + generated text/colors frontend ko return karte hain.
"""

import os
import io
import json
import base64
import textwrap
import urllib.parse
import urllib.request
from datetime import datetime

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from google import genai
from PIL import Image, ImageDraw, ImageFont

load_dotenv()

app = Flask(__name__, static_folder="../frontend", static_url_path="")
CORS(app)

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# ---- Platform-wise canvas sizes ----
PLATFORM_SIZES = {
    "instagram_post": (1080, 1080),
    "instagram_story": (1080, 1920),
    "facebook_banner": (1200, 628),
    "youtube_thumbnail": (1280, 720),
}

FONT_PATH_BOLD = os.path.join(os.path.dirname(__file__), "fonts", "DejaVuSans-Bold.ttf")
FONT_PATH_REGULAR = os.path.join(os.path.dirname(__file__), "fonts", "DejaVuSans.ttf")


def safe_truetype(path, size):
    """TTF load karo; agar file missing ho to PIL ka bitmap default font use karo (crash nahi hoga)."""
    try:
        return ImageFont.truetype(path, size)
    except (OSError, IOError):
        try:
            return ImageFont.load_default(size=size)
        except TypeError:
            return ImageFont.load_default()


def generate_ad_content(product_name, product_description, audience, mood, platform):
    """Step 1: Use an LLM to generate tagline, short copy, color palette, layout choice."""
    prompt = f"""
You are an expert advertising copywriter and art director.

Product: {product_name}
Product description: {product_description}
Target audience: {audience}
Desired mood/style: {mood}
Platform: {platform}

Return ONLY valid JSON (no markdown, no preamble) with this exact shape:
{{
  "tagline": "short punchy tagline, max 6 words",
  "subtext": "one supporting line, max 12 words",
  "cta": "a 2-3 word call to action, e.g. Shop Now",
  "palette": {{
    "primary": "#hex",
    "secondary": "#hex",
    "text_on_image": "#hex (must contrast well against a photo background, usually white or near-white)"
  }},
  "text_position": "top | bottom | center",
  "image_prompt": "a detailed prompt (30-50 words) for a product photo. It MUST start with 'A close-up professional product photograph of {product_name}' and MUST keep {product_name} as the clear, in-focus, central hero subject of the image — not just implied by a lifestyle scene. Then describe background, lighting, and mood that fits the audience and style — no text/typography in the image itself"
}}
"""
    resp = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
    )
    raw = resp.text.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    content = json.loads(raw)

    # Safety net: agar model image_prompt me product ka naam bhool jaye,
    # to hum explicitly product_name ko prompt ke shuru me force kar dete hain.
    if product_name.lower() not in content.get("image_prompt", "").lower():
        content["image_prompt"] = (
            f"A close-up professional product photograph of {product_name}, "
            f"clearly visible and in sharp focus as the main subject. "
            f"{content.get('image_prompt', '')}"
        )

    return content


def generate_background_image(image_prompt, size):
    """Step 2: Use Pollinations.ai (free, no API key) to generate the background/product visual."""
    full_prompt = image_prompt + ", no text, no words, no letters in the image"
    encoded_prompt = urllib.parse.quote(full_prompt)
    url = (
        f"https://image.pollinations.ai/prompt/{encoded_prompt}"
        f"?width={size[0]}&height={size[1]}&nologo=true"
    )
    # Pollinations bina User-Agent wali requests ko block kar deta hai (403 Forbidden),
    # isliye ek normal browser jaisa header bhejna zaroori hai.
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as response:
        img_data = response.read()
    img = Image.open(io.BytesIO(img_data)).convert("RGB")
    return img.resize(size, Image.LANCZOS)


def fit_font(draw, text, max_width, font_path, start_size, min_size=24):
    """Shrink font size until the text fits within max_width."""
    size = start_size
    while size > min_size:
        font = safe_truetype(font_path, size)
        bbox = draw.textbbox((0, 0), text, font=font)
        if bbox[2] - bbox[0] <= max_width:
            return font
        size -= 4
    return safe_truetype(font_path, min_size)


def compose_ad(image, content, canvas_size):
    """Step 3: Overlay tagline/subtext/CTA on the image using the chosen layout."""
    w, h = canvas_size
    img = image.copy()
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    text_color = content["palette"].get("text_on_image", "#FFFFFF")
    accent = content["palette"].get("primary", "#FF8A5B")
    position = content.get("text_position", "bottom")

    padding = int(w * 0.06)
    max_text_width = w - 2 * padding

    tagline_font = fit_font(draw, content["tagline"], max_text_width, FONT_PATH_BOLD, start_size=int(h * 0.09))
    subtext_font = safe_truetype(FONT_PATH_REGULAR, max(18, int(h * 0.028)))
    cta_font = safe_truetype(FONT_PATH_BOLD, max(20, int(h * 0.03)))

    # Gradient scrim so text stays readable over any photo
    scrim = Image.new("L", img.size, 0)
    scrim_draw = ImageDraw.Draw(scrim)
    band_h = int(h * 0.42)
    if position == "top":
        for y in range(band_h):
            alpha = int(190 * (1 - y / band_h))
            scrim_draw.line([(0, y), (w, y)], fill=alpha)
    elif position == "center":
        for y in range(h):
            dist = abs(y - h / 2) / (h / 2)
            alpha = int(150 * max(0, 1 - dist * 1.6))
            scrim_draw.line([(0, y), (w, y)], fill=alpha)
    else:  # bottom
        for y in range(h - band_h, h):
            alpha = int(190 * ((y - (h - band_h)) / band_h))
            scrim_draw.line([(0, y), (w, y)], fill=alpha)

    black_layer = Image.new("RGBA", img.size, (10, 10, 15, 255))
    img = Image.composite(black_layer, img.convert("RGBA"), scrim.point(lambda a: int(a * 0.75)))

    draw = ImageDraw.Draw(overlay)

    if position == "top":
        y = padding
    elif position == "center":
        tb = draw.textbbox((0, 0), content["tagline"], font=tagline_font)
        y = h / 2 - (tb[3] - tb[1]) / 2 - int(h * 0.04)
    else:
        y = h - padding - int(h * 0.20)

    draw.text((padding, y), content["tagline"], font=tagline_font, fill=text_color)
    y += tagline_font.size + int(h * 0.015)
    draw.multiline_text((padding, y), textwrap.fill(content["subtext"], width=40), font=subtext_font, fill=text_color)
    y += subtext_font.size * 2 + int(h * 0.02)

    # CTA pill
    cta_text = content["cta"]
    cta_bbox = draw.textbbox((0, 0), cta_text, font=cta_font)
    cta_w = cta_bbox[2] - cta_bbox[0] + int(w * 0.06)
    cta_h = cta_bbox[3] - cta_bbox[1] + int(h * 0.025)
    draw.rounded_rectangle([padding, y, padding + cta_w, y + cta_h], radius=cta_h // 2, fill=accent)
    draw.text((padding + int(w * 0.03), y + int(h * 0.008)), cta_text, font=cta_font, fill="#0B0B0F")

    final = Image.alpha_composite(img, overlay).convert("RGB")
    return final


@app.route("/api/generate-ad", methods=["POST"])
def generate_ad():
    data = request.get_json(force=True)
    product_name = data.get("product_name", "").strip()
    product_description = data.get("product_description", "").strip()
    audience = data.get("audience", "").strip()
    mood = data.get("mood", "modern and clean").strip()
    platform = data.get("platform", "instagram_post")

    if not product_name or not product_description or not audience:
        return jsonify({"error": "product_name, product_description aur audience zaroori hain."}), 400

    if platform not in PLATFORM_SIZES:
        platform = "instagram_post"
    size = PLATFORM_SIZES[platform]

    try:
        content = generate_ad_content(product_name, product_description, audience, mood, platform)
        bg_image = generate_background_image(content["image_prompt"], size)
        final_ad = compose_ad(bg_image, content, size)

        buf = io.BytesIO()
        final_ad.save(buf, format="PNG")
        b64_image = base64.b64encode(buf.getvalue()).decode("utf-8")

        return jsonify({
            "image_base64": f"data:image/png;base64,{b64_image}",
            "tagline": content["tagline"],
            "subtext": content["subtext"],
            "cta": content["cta"],
            "palette": content["palette"],
            "text_position": content["text_position"],
            "platform": platform,
            "generated_at": datetime.utcnow().isoformat(),
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


if __name__ == "__main__":
    app.run(debug=True, port=5000)