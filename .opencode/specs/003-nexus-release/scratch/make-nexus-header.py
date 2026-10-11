#!/usr/bin/env python3
"""Generate the plain 1920x1080 Nexus header image for NoRelicSickness.

This draws text and a gradient with Pillow -- no generative model is involved and
no CD Projekt Red artwork is used. It is a plain text banner, reproducible from
this file with:

    python3 make-nexus-header.py            # writes nexus-header-sickness.png

Edit TEXT below and re-run to change the wording.
"""

from PIL import Image, ImageDraw, ImageFont

W, H = 1920, 1080

# ---- palette -------------------------------------------------------------
BG_TOP = (10, 12, 16)
BG_BOTTOM = (20, 24, 31)
FG = (242, 244, 247)
MUTED = (139, 150, 165)
ACCENT = (79, 209, 197)

# ---- copy ----------------------------------------------------------------
TEXT = {
    "kicker": "CYBERPUNK 2077",
    "title": "NoRelicSickness",
    "subtitle": "The Relic still runs. It just stops hurting you.",
    "footer": "Requires RED4ext + TweakXL   \u00b7   v1.0.0",
}

BOLD_CANDIDATES = [
    "/usr/share/fonts/noto/NotoSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/liberation/LiberationSans-Bold.ttf",
]
REG_CANDIDATES = [
    "/usr/share/fonts/noto/NotoSans-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/TTF/DejaVuSans.ttf",
    "/usr/share/fonts/liberation/LiberationSans-Regular.ttf",
]


def load(candidates, size):
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    raise SystemExit(f"no usable font in {candidates}")


def gradient():
    img = Image.new("RGB", (W, H))
    px = img.load()
    for y in range(H):
        t = y / (H - 1)
        row = tuple(round(BG_TOP[i] + (BG_BOTTOM[i] - BG_TOP[i]) * t) for i in range(3))
        for x in range(W):
            px[x, y] = row
    return img


def draw_tracked(draw, text, font, tracking, centre_x, y, fill):
    """Draw text with extra letter spacing, centred on centre_x."""
    widths = [draw.textlength(ch, font=font) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = centre_x - total / 2
    for ch, w in zip(text, widths):
        draw.text((x, y), ch, font=font, fill=fill)
        x += w + tracking


def centre(draw, text, font, centre_x, y, fill):
    w = draw.textlength(text, font=font)
    draw.text((centre_x - w / 2, y), text, font=font, fill=fill)


def main():
    img = gradient()
    draw = ImageDraw.Draw(img)
    cx = W / 2

    draw_tracked(draw, TEXT["kicker"], load(BOLD_CANDIDATES, 40), 16, cx, 352, MUTED)
    centre(draw, TEXT["title"], load(BOLD_CANDIDATES, 136), cx, 420, FG)

    rule_y = 632
    rule_w = 280
    draw.rectangle([cx - rule_w / 2, rule_y, cx + rule_w / 2, rule_y + 5], fill=ACCENT)

    centre(draw, TEXT["subtitle"], load(REG_CANDIDATES, 48), cx, 686, MUTED)
    centre(draw, TEXT["footer"], load(REG_CANDIDATES, 34), cx, 944, MUTED)

    out = "nexus-header-sickness.png"
    img.save(out)
    print(f"wrote {out} ({W}x{H})")


if __name__ == "__main__":
    main()
