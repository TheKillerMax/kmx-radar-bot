from __future__ import annotations

from pathlib import Path
import json
import logging
import tempfile
import textwrap
import time

import requests
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import cairosvg

from .config import ASSETS_DIR

LOG = logging.getLogger(__name__)

W, H = 1080, 1350
BG = (5, 15, 25)
ACCENT = (25, 236, 198)
GOLD = (245, 195, 80)
WHITE = (245, 248, 250)
MUTED = (190, 204, 216)
PANEL = (9, 31, 47, 225)


def _font(size: int, bold: bool = False):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ]
    for p in paths:
        if Path(p).exists():
            return ImageFont.truetype(p, size=size)
    return ImageFont.load_default()


def _fit_font(draw: ImageDraw.ImageDraw, text: str, max_width: int, start_size: int, bold: bool = False, min_size: int = 10):
    size = start_size
    while size > min_size:
        font = _font(size, bold)
        box = draw.textbbox((0, 0), text, font=font)
        if (box[2] - box[0]) <= max_width:
            return font
        size -= 1
    return _font(min_size, bold)


def _draw_single_fit(draw: ImageDraw.ImageDraw, xy, text: str, max_width: int, start_size: int, fill=WHITE, bold: bool = False, min_size: int = 10):
    font = _fit_font(draw, text, max_width, start_size, bold, min_size)
    draw.text(xy, text, font=font, fill=fill)
    return font


def _draw_pill(draw: ImageDraw.ImageDraw, x: int, y: int, text: str, *,
               max_width: int = 500, height: int = 46, start_size: int = 21,
               fill=(7, 36, 48, 235), outline=ACCENT, text_fill=ACCENT,
               pad_x: int = 22, bold: bool = True):
    """Draw a pill that always contains its text with explicit horizontal padding."""
    inner_max = max_width - (pad_x * 2)
    font = _fit_font(draw, text, inner_max, start_size, bold, 12)
    box = draw.textbbox((0, 0), text, font=font)
    text_w = box[2] - box[0]
    text_h = box[3] - box[1]
    width = min(max_width, text_w + (pad_x * 2))
    y2 = y + height
    draw.rounded_rectangle((x, y, x + width, y2), height // 2, fill=fill, outline=outline, width=2)
    text_y = y + max(0, (height - text_h) // 2 - box[1])
    draw.text((x + pad_x, text_y), text, font=font, fill=text_fill)
    return (x, y, x + width, y2)


def _fit_title(draw: ImageDraw.ImageDraw, xy, text: str, max_width: int, start_size: int, fill=WHITE):
    return _draw_single_fit(draw, xy, text, max_width, start_size, fill=fill, bold=True, min_size=34)


def _download(url: str, dest: Path) -> None:
    headers = {
        "User-Agent": "KMX-RADAR/1.0 (news graphics; contact via github.com/TheKillerMax/kmx-radar-bot)",
        "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
    }
    last = None
    for delay in (0, 3, 8, 15):
        if delay:
            time.sleep(delay)
        r = requests.get(url, timeout=60, headers=headers)
        if r.status_code == 200:
            dest.write_bytes(r.content)
            return
        last = r
        if r.status_code not in (429, 502, 503, 504):
            r.raise_for_status()
    if last is not None:
        last.raise_for_status()
    raise RuntimeError(f"Unable to download {url}")


def _cover(im: Image.Image, size=(W, H)) -> Image.Image:
    im = im.convert("RGB")
    sw, sh = size
    scale = max(sw / im.width, sh / im.height)
    nw, nh = int(im.width * scale), int(im.height * scale)
    im = im.resize((nw, nh), Image.Resampling.LANCZOS)
    x = max(0, (nw - sw) // 2)
    y = max(0, (nh - sh) // 2)
    return im.crop((x, y, x + sw, y + sh))


def _darken(im: Image.Image, alpha: int = 145) -> Image.Image:
    base = im.convert("RGBA")
    base.alpha_composite(Image.new("RGBA", base.size, (3, 12, 22, alpha)))
    return base


def _split(a: Image.Image, b: Image.Image) -> Image.Image:
    left = _cover(a, (W // 2, H))
    right = _cover(b, (W - W // 2, H))
    out = Image.new("RGB", (W, H), BG)
    out.paste(left, (0, 0))
    out.paste(right, (W // 2, 0))
    return out


def _logo_png(tmp: Path) -> Image.Image | None:
    svg = ASSETS_DIR / "logo.svg"
    png = ASSETS_DIR / "logo.png"
    try:
        if png.exists():
            return Image.open(png).convert("RGBA")
        if svg.exists():
            out = tmp / "logo.png"
            cairosvg.svg2png(url=str(svg), write_to=str(out), output_width=180, output_height=180)
            return Image.open(out).convert("RGBA")
    except Exception as exc:
        LOG.warning("Logo render failed: %s", exc)
    return None


def _header(img: Image.Image, draw: ImageDraw.ImageDraw, logo: Image.Image | None, n: int, total: int = 8, archive=True):
    if logo:
        lg = logo.copy()
        lg.thumbnail((108, 108), Image.Resampling.LANCZOS)
        img.alpha_composite(lg, (58, 45))
        tx = 178
    else:
        tx = 60
    draw.text((tx, 65), "KMX RADAR", font=_font(34, True), fill=WHITE)
    draw.text((tx, 108), "DETECTAMOS LO QUE IMPORTA", font=_font(16, True), fill=ACCENT)
    draw.text((930, 65), f"{n}/{total}", font=_font(28, True), fill=WHITE)
    if archive:
        label = "ARCHIVO"
        font = _font(14, True)
        tb = draw.textbbox((0, 0), label, font=font)
        tw = tb[2] - tb[0]
        pad_x = 18
        x2 = 1010
        x1 = x2 - tw - (pad_x * 2)
        y1, y2 = 112, 151
        draw.rounded_rectangle((x1, y1, x2, y2), 18, fill=(0, 0, 0, 165), outline=GOLD, width=2)
        draw.text((x1 + pad_x, 121), label, font=font, fill=GOLD)


def _wrap(draw, text, font, maxw):
    words = text.split()
    lines, cur = [], ""
    for word in words:
        test = (cur + " " + word).strip()
        if draw.textbbox((0,0), test, font=font)[2] <= maxw:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def _text_block(draw, text, xy, maxw, size, fill=WHITE, bold=False, line_gap=10, max_lines=None):
    font = _font(size, bold)
    lines = _wrap(draw, text, font, maxw)
    if max_lines:
        lines = lines[:max_lines]
    x, y = xy
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        bbox = draw.textbbox((x,y), line, font=font)
        y = bbox[3] + line_gap
    return y


def _panel(draw, box, fill=PANEL, outline=(36, 105, 129, 230), radius=26, width=2):
    draw.rounded_rectangle(box, radius, fill=fill, outline=outline, width=width)


def _footer(draw, cta: str, credit: str | None = None):
    draw.line((60, 1275, 1020, 1275), fill=(30, 100, 120), width=2)
    draw.text((60, 1293), "@kmxradar", font=_font(22, True), fill=ACCENT)
    if cta:
        _draw_single_fit(draw, (230, 1294), cta, 760, 20, fill=WHITE, bold=True, min_size=15)
    if credit:
        _draw_single_fit(draw, (60, 1242), credit, 950, 13, fill=MUTED, bold=False, min_size=10)


def _base(bg: Image.Image) -> Image.Image:
    im = _darken(bg, 120)
    # stronger lower gradient for text safety
    grad = Image.new("RGBA", (W, H), (0,0,0,0))
    gd = ImageDraw.Draw(grad)
    for y in range(H):
        a = max(0, min(180, int((y/H)*175)))
        gd.line((0,y,W,y), fill=(2,9,18,a))
    im.alpha_composite(grad)
    return im


def build_real_visuals(package_dir: Path, config: dict) -> None:
    sources = config.get("sources", {})
    slides = config.get("slides", [])
    if not sources or not slides:
        return

    with tempfile.TemporaryDirectory(prefix="kmx-real-visuals-") as td:
        tmp = Path(td)
        images = {}
        for key, src in sources.items():
            p = tmp / f"{key}.jpg"
            _download(src["direct_url"], p)
            images[key] = Image.open(p).convert("RGB")
        logo = _logo_png(tmp)

        for spec in slides:
            mode = spec.get("background")
            if isinstance(mode, list) and len(mode) == 2:
                bg = _split(images[mode[0]], images[mode[1]])
            else:
                bg = _cover(images[mode])
            canvas = _base(bg)
            draw = ImageDraw.Draw(canvas)
            _header(canvas, draw, logo, int(spec["n"]))

            # content layouts
            layout = spec.get("layout", "standard")
            if layout == "cover":
                _draw_pill(draw, 60, 205, spec["kicker"], max_width=430)
                y = 330
                y = _text_block(draw, spec["title"][0], (60,y), 960, 68, WHITE, True, 5)
                y = _text_block(draw, spec["title"][1], (60,y+5), 960, 78, ACCENT, True, 5)
                y = _text_block(draw, spec["title"][2], (60,y+5), 960, 78, WHITE, True, 5)
                y = _text_block(draw, spec["subtitle"], (60,y+35), 890, 32, WHITE, False, 12)
                _panel(draw, (60, y+28, 795, y+185), fill=(5,18,28,230), outline=GOLD, width=3)
                draw.text((90, y+55), "CLAVE", font=_font(25, True), fill=GOLD)
                _text_block(draw, spec["highlight"], (90,y+95), 650, 30, WHITE, True, 8)
            elif layout == "facts":
                _draw_pill(draw, 60, 205, spec["kicker"], max_width=430)
                _fit_title(draw, (60, 290), spec["title"], 960, 66, WHITE)
                y=390
                for fact in spec["facts"]:
                    _panel(draw,(60,y,1020,y+185))
                    draw.text((92,y+28), fact["label"], font=_font(24,True), fill=ACCENT)
                    _text_block(draw,fact["text"],(92,y+70),860,30,WHITE,True,8,3)
                    y+=205
                _panel(draw,(60,y+5,1020,y+140),fill=(20,17,8,225),outline=GOLD,width=2)
                draw.text((92,y+28),"OJO",font=_font(24,True),fill=GOLD)
                _text_block(draw,spec["note"],(175,y+25),800,24,WHITE,False,7,3)
            elif layout == "timeline":
                _fit_title(draw, (60, 220), spec["title"], 960, 58, WHITE)
                draw.text((60, 285), spec["subtitle"], font=_font(30, True), fill=ACCENT)
                y=470
                xs=[175,540,895]
                draw.line((xs[0],y,xs[-1],y),fill=ACCENT,width=6)
                for x,item in zip(xs,spec["timeline"]):
                    draw.ellipse((x-28,y-28,x+28,y+28),fill=(5,25,38),outline=GOLD,width=4)
                    draw.text((x-46,y+45),item["date"],font=_font(22,True),fill=GOLD)
                    _text_block(draw,item["text"],(x-95,y+85),190,20,WHITE,True,5,3)
                _panel(draw,(60,760,1020,1115),fill=(5,18,28,235),outline=GOLD,width=2)
                draw.text((90,800),spec["box_title"],font=_font(30,True),fill=GOLD)
                _text_block(draw,spec["box_text"],(90,855),870,27,WHITE,False,9,7)
            elif layout == "changes":
                draw.text((60, 220), spec["title"], font=_font(58, True), fill=WHITE)
                y=335
                for item in spec["items"]:
                    _panel(draw,(60,y,1020,y+205))
                    draw.text((90,y+30),item["label"],font=_font(25,True),fill=ACCENT)
                    _text_block(draw,item["text"],(90,y+80),850,30,WHITE,True,8,3)
                    y+=225
                _panel(draw,(60,y+5,1020,y+145),fill=(5,18,28,230),outline=GOLD,width=2)
                _text_block(draw,spec["note"],(90,y+35),850,24,GOLD,True,7,3)
            elif layout == "money":
                _fit_title(draw, (60, 220), spec["title"], 960, 56, WHITE)
                _panel(draw,(60,340,1020,570),fill=(5,18,28,235),outline=ACCENT,width=3)
                draw.text((90,375),spec["big"],font=_font(86,True),fill=ACCENT)
                draw.text((90,480),spec["big_label"],font=_font(30,True),fill=WHITE)
                _panel(draw,(60,600,1020,805))
                draw.text((90,635),spec["small"],font=_font(48,True),fill=GOLD)
                _text_block(draw,spec["small_label"],(90,700),850,26,WHITE,False,8,3)
                _panel(draw,(60,840,1020,1045),fill=(20,17,8,230),outline=GOLD,width=2)
                explain_title = spec.get("explain_title", "LO QUE DEBES SABER")
                _draw_single_fit(draw, (90,875), explain_title, 850, 25, fill=GOLD, bold=True, min_size=18)
                _text_block(draw,spec["explain"],(90,925),850,25,WHITE,False,8,4)
                _text_block(draw,spec["disclaimer"],(60,1090),900,19,MUTED,False,6,2)
            elif layout == "brands":
                draw.text((60, 220), spec["title"], font=_font(56, True), fill=WHITE)
                _text_block(draw,spec["subtitle"],(60,290),920,28,ACCENT,True,8,2)
                _panel(draw,(60,380,1020,960),fill=(5,18,28,235),outline=ACCENT,width=2)
                draw.text((90,420),spec["box_title"],font=_font(30,True),fill=ACCENT)
                y=485
                for brand in spec["brands"]:
                    draw.ellipse((95,y+8,111,y+24),fill=ACCENT)
                    _draw_single_fit(draw, (135,y), brand, 820, 29, fill=WHITE, bold=True, min_size=20)
                    y+=70
                _panel(draw,(60,990,1020,1175),fill=(5,18,28,235),outline=GOLD,width=2)
                explain_title = spec.get("explain_title", "QUÉ SIGNIFICA")
                _draw_single_fit(draw, (90,1020), explain_title, 850, 24, fill=GOLD, bold=True, min_size=18)
                _text_block(draw,spec["explain"],(90,1070),850,24,WHITE,False,7,4)
            elif layout == "streaming":
                draw.text((60, 220), spec["title"], font=_font(56, True), fill=WHITE)
                _panel(draw,(60,335,1020,525),fill=(20,17,8,235),outline=GOLD,width=3)
                _text_block(draw,spec["statement"],(90,370),850,31,GOLD,True,9,4)
                y=560
                for item in spec["items"]:
                    _panel(draw,(60,y,1020,y+165))
                    draw.text((90,y+28),item["label"],font=_font(24,True),fill=ACCENT)
                    _text_block(draw,item["text"],(90,y+72),850,25,WHITE,False,7,3)
                    y+=185
            elif layout == "sources":
                draw.text((60, 220), spec["title"], font=_font(56, True), fill=WHITE)
                y=335
                for item in spec["watch"]:
                    _panel(draw,(60,y,1020,y+110))
                    draw.ellipse((90,y+42,106,y+58),fill=ACCENT)
                    _text_block(draw,item,(135,y+29),820,24,WHITE,True,6,2)
                    y+=125
                _panel(draw,(60,850,1020,1110),fill=(5,18,28,235),outline=GOLD,width=2)
                draw.text((90,880),"FUENTES",font=_font(25,True),fill=GOLD)
                sy=925
                for s in spec["sources"]:
                    _draw_single_fit(draw, (90,sy), "• "+s, 870, 22, fill=WHITE, bold=True, min_size=16)
                    sy+=42
                draw.text((60,1165),"CRÉDITOS VISUALES",font=_font(16,True),fill=ACCENT)
                _text_block(draw,spec["credits"],(60,1192),930,14,MUTED,False,4,4)

            _footer(draw, spec.get("cta",""), spec.get("credit"))
            out = package_dir / spec["file"]
            final = canvas.convert("RGB")
            if final.size != (W, H):
                raise RuntimeError(f"Unexpected output size for {out.name}: {final.size}")
            final.save(out, "PNG", optimize=True)
            LOG.info("Built real-visual slide %s", out.name)
