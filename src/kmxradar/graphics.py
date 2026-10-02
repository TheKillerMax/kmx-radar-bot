from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from .config import ASSETS_DIR, DOCS_DIR, editorial_config
from .models import Cluster
from .utils import stable_hash


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()


def _wrap(draw: ImageDraw.ImageDraw, text: str, font, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        proposal = f"{current} {word}".strip()
        if draw.textbbox((0, 0), proposal, font=font)[2] <= max_width:
            current = proposal
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def _draw_brand_mark(image: Image.Image, draw: ImageDraw.ImageDraw, accent: str) -> None:
    logo_path = ASSETS_DIR / "logo.png"
    if logo_path.exists():
        logo = Image.open(logo_path).convert("RGBA")
        logo.thumbnail((190, 190), Image.Resampling.LANCZOS)
        image.paste(logo, (55, 45), logo)
        return

    # Fallback keeps every generated post branded even if the binary logo asset is unavailable.
    cx, cy = 135, 125
    for radius in (35, 55, 75):
        draw.ellipse((cx-radius, cy-radius, cx+radius, cy+radius), outline=accent, width=3)
    draw.line((cx, cy, cx+68, cy-46), fill=accent, width=7)
    draw.text((225, 65), "KMX", font=_font(60, bold=True), fill="#f6f9fb")
    draw.text((225, 132), "RADAR", font=_font(28, bold=True), fill=accent)


def render_news_card(cluster: Cluster, editorial: dict) -> Path:
    cfg = editorial_config()
    visual = cfg["visual"]
    width, height = int(visual["width"]), int(visual["height"])
    image = Image.new("RGB", (width, height), visual["background"])
    draw = ImageDraw.Draw(image)

    cx, cy = width - 125, 135
    accent = visual["accent"]
    for radius in (70, 110, 150, 190):
        draw.ellipse((cx-radius, cy-radius, cx+radius, cy+radius), outline=accent, width=2)
    draw.line((cx-195, cy, cx+195, cy), fill=accent, width=2)
    draw.line((cx, cy-195, cx, cy+195), fill=accent, width=2)

    _draw_brand_mark(image, draw, accent)

    category_font = _font(31, bold=True)
    status_font = _font(28, bold=True)
    title_font = _font(64, bold=True)
    body_font = _font(30)
    tiny_font = _font(22)

    draw.rounded_rectangle((55, 270, 370, 330), radius=22, fill=visual["panel"], outline=accent, width=2)
    draw.text((78, 284), f"RADAR / {cluster.category}", font=category_font, fill=visual["text"])

    status_color = visual["danger"] if cluster.status == "SIN CONFIRMAR" else accent
    status_text = cluster.status.upper()
    box = draw.textbbox((0, 0), status_text, font=status_font)
    sw = box[2] - box[0]
    draw.rounded_rectangle((width-55-sw-50, 270, width-55, 330), radius=22, fill=status_color)
    draw.text((width-55-sw-25, 285), status_text, font=status_font, fill="#041016")

    headline = str(editorial.get("headline") or cluster.canonical_title).strip()
    y = 405
    for line in _wrap(draw, headline, title_font, width - 110)[:5]:
        draw.text((55, y), line, font=title_font, fill=visual["text"])
        y += 78

    y += 30
    summary = str(editorial.get("summary") or "").strip()
    for line in _wrap(draw, summary, body_font, width - 110)[:6]:
        draw.text((58, y), line, font=body_font, fill=visual["muted"])
        y += 42

    draw.line((55, height-180, width-55, height-180), fill=visual["panel"], width=3)
    domains = " · ".join((editorial.get("source_domains") or cluster.independent_domains)[:4])
    source_line = f"FUENTES: {domains}" if domains else "FUENTES CONTRASTADAS"
    for i, line in enumerate(_wrap(draw, source_line, tiny_font, width - 110)[:2]):
        draw.text((55, height-145 + i*28), line, font=tiny_font, fill=visual["muted"])
    draw.text((55, height-65), "@kmxradar", font=_font(25, bold=True), fill=accent)
    draw.text((width-360, height-65), "Detectamos lo que importa", font=tiny_font, fill=visual["muted"])

    event_id = stable_hash(cluster.key, headline, length=12)
    out_dir = DOCS_DIR / "media"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{event_id}.jpg"
    image.save(path, "JPEG", quality=93, optimize=True)
    return path
