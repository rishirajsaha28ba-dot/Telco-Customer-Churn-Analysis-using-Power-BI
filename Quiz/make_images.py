"""Render each question (without options) from questions.json as a JPEG."""
import json
import os
import textwrap

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "images")
FONT_DIR = "/usr/share/fonts/truetype/dejavu"

W, PAD = 1200, 70
BG, ACCENT, TEXT, CODE_BG = "#FFFFFF", "#1A7F37", "#1F2328", "#F2F4F7"
f_head = ImageFont.truetype(f"{FONT_DIR}/DejaVuSans-Bold.ttf", 40)
f_body = ImageFont.truetype(f"{FONT_DIR}/DejaVuSans.ttf", 34)
f_code = ImageFont.truetype(f"{FONT_DIR}/DejaVuSansMono-Bold.ttf", 32)
LINE = 50


def layout(text):
    """Return list of (kind, line) where kind is body/code/blank."""
    rows = []
    for para in text.split("\n"):
        if not para.strip():
            rows.append(("blank", ""))
        elif para.startswith("    "):
            rows.append(("code", para.strip()))
        else:
            rows.extend(("body", ln) for ln in textwrap.wrap(para, 54))
    return rows


def render(n, text):
    rows = layout(text)
    h = PAD + 60 + 30 + sum(LINE // 2 if k == "blank" else LINE for k, _ in rows) + PAD
    h = max(h, 420)
    img = Image.new("RGB", (W, h), BG)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 14, h], fill=ACCENT)
    d.text((PAD, PAD), f"Question {n}", font=f_head, fill=ACCENT)
    y = PAD + 60 + 30
    for kind, line in rows:
        if kind == "blank":
            y += LINE // 2
            continue
        if kind == "code":
            d.rounded_rectangle([PAD, y - 4, W - PAD, y + LINE - 8], 8, fill=CODE_BG)
            d.text((PAD + 20, y + 2), line, font=f_code, fill=TEXT)
        else:
            d.text((PAD, y), line, font=f_body, fill=TEXT)
        y += LINE
    img.save(os.path.join(OUT, f"Q{n:02d}.jpg"), "JPEG", quality=92)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(HERE, "questions.json"), encoding="utf-8") as f:
        qs = json.load(f)
    for i, q in enumerate(qs, 1):
        render(i, q["q"])
    print(f"Wrote {len(qs)} images to {OUT}")
