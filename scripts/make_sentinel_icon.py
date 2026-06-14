"""Generate ../sentinel.ico — a multi-resolution Windows icon labeled
"Sentinel" for the Sentinel Forge / dashboard launcher.

Re-run this script if the design needs to change; the .ico itself is
committed alongside the app so users don't need Pillow at runtime.

Design notes:
- Dark rounded-square background matches the Sentinel Forge's UI palette
  (cyan accent, deep-slate fill) so the icon reads as part of the app.
- A bold "S" sits dead-center as the brand glyph — it stays legible at
  16x16 where the wordmark below would smear into noise.
- A small "SENTINEL" wordmark hugs the bottom; it disappears at tiny
  sizes (intended) and reads cleanly at 48x48 and up.
"""
from __future__ import annotations

import os
import sys
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT  = os.path.normpath(os.path.join(HERE, "..", "sentinel.ico"))

# Palette — mirrors the Sentinel Forge's dark theme.
BG_FILL     = (14, 32, 46, 255)     # deep slate, opaque
BG_BORDER   = (0, 184, 212, 255)    # cyan accent ring
FG_GLYPH    = (255, 255, 255, 255)  # white "S"
FG_WORDMARK = (180, 220, 235, 255)  # cool white for wordmark


def _load_font(candidates: list[str], size: int) -> ImageFont.FreeTypeFont:
    """Try each font path in turn; fall back to PIL's default if none
    are available so this script still runs on systems without Segoe."""
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _make_master(side: int = 256) -> Image.Image:
    """Render the icon at `side` x `side` px. Larger source = cleaner
    downscale for the 16/32/48 ICO frames."""
    img = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    d   = ImageDraw.Draw(img)

    # Rounded square background with a thin cyan ring.
    pad    = int(side * 0.04)
    radius = int(side * 0.18)
    d.rounded_rectangle(
        (pad, pad, side - pad, side - pad),
        radius=radius,
        fill=BG_FILL,
        outline=BG_BORDER,
        width=max(2, side // 64),
    )

    # Big centered "S" — the brand glyph that survives at 16x16.
    glyph_font = _load_font(
        [
            r"C:\Windows\Fonts\seguibl.ttf",   # Segoe UI Black
            r"C:\Windows\Fonts\segoeuib.ttf",  # Segoe UI Bold
            r"C:\Windows\Fonts\arialbd.ttf",   # Arial Bold
        ],
        size=int(side * 0.62),
    )
    glyph_text = "S"
    bbox = d.textbbox((0, 0), glyph_text, font=glyph_font)
    gw, gh = bbox[2] - bbox[0], bbox[3] - bbox[1]
    # textbbox includes leading whitespace; subtract bbox origin so the
    # glyph is geometrically centered, not baseline-centered.
    gx = (side - gw) // 2 - bbox[0]
    gy = (side - gh) // 2 - bbox[1] - int(side * 0.05)  # lift slightly above wordmark
    d.text((gx, gy), glyph_text, font=glyph_font, fill=FG_GLYPH)

    # "SENTINEL" wordmark across the bottom.
    word_font = _load_font(
        [
            r"C:\Windows\Fonts\segoeuib.ttf",
            r"C:\Windows\Fonts\arialbd.ttf",
        ],
        size=int(side * 0.13),
    )
    word_text = "SENTINEL"
    bbox = d.textbbox((0, 0), word_text, font=word_font)
    ww = bbox[2] - bbox[0]
    wx = (side - ww) // 2 - bbox[0]
    wy = int(side * 0.78)
    d.text((wx, wy), word_text, font=word_font, fill=FG_WORDMARK)

    return img


def main() -> int:
    master = _make_master(256)
    # Windows ICO conventions: include the sizes Explorer / taskbar /
    # title bar actually use. Pillow downscales the master for each.
    sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64),
             (128, 128), (256, 256)]
    master.save(OUT, format="ICO", sizes=sizes)
    print(f"wrote {OUT}")
    # Also dump a PNG preview alongside, useful for eyeballing.
    preview = os.path.splitext(OUT)[0] + "_preview.png"
    master.save(preview, format="PNG")
    print(f"wrote {preview}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
