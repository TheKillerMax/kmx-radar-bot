from __future__ import annotations

from pathlib import Path
import logging
import tempfile
import time

import requests
from PIL import Image, ImageDraw, ImageFont

from .config import ASSETS_DIR

LOG = logging.getLogger(__name__)
W, H = 1080, 1350
SAFE = 60
BG = (5, 16, 28)
PANEL = (7, 27, 43, 232)
ACCENT = (29, 236, 198)
BLUE = (88, 166, 255)
WARM = (255, 179, 71)
WHITE = (247, 250, 252)
MUTED = (192, 207, 220)


def _hex_rgb(value: str, fallback):
    value = str(value or "").strip().lstrip("#")
    if len(value) != 6:
        return fallback
    try:
        return tuple(int(value[i:i+2], 16) for i in (0, 2, 4))
    except ValueError:
        return fallback


def _apply_theme(config: dict) -> None:
    global BG, PANEL, ACCENT, BLUE, WARM, WHITE, MUTED
    theme = config.get("theme") or {}
    BG = _hex_rgb(theme.get("background"), BG)
    ACCENT = _hex_rgb(theme.get("accent"), ACCENT)
    BLUE = _hex_rgb(theme.get("accent2"), BLUE)
    WARM = _hex_rgb(theme.get("warm"), WARM)
    WHITE = _hex_rgb(theme.get("text"), WHITE)
    MUTED = _hex_rgb(theme.get("muted"), MUTED)
    panel_rgb = _hex_rgb(theme.get("panel"), PANEL[:3])
    PANEL = (*panel_rgb, 232)


def _font(size: int, bold: bool = False):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ]
    for p in paths:
        if Path(p).exists():
            return ImageFont.truetype(p, size=size)
    return ImageFont.load_default()


def _download(url: str, dest: Path) -> None:
    headers = {"User-Agent": "KMX-RADAR/1.0 (+https://github.com/TheKillerMax/kmx-radar-bot)"}
    last = None
    for delay in (0, 2, 6, 12):
        if delay:
            time.sleep(delay)
        r = requests.get(url, timeout=60, headers=headers)
        last = r
        if r.status_code == 200 and r.content:
            dest.write_bytes(r.content)
            return
        if r.status_code not in (429, 500, 502, 503, 504):
            r.raise_for_status()
    if last is not None:
        last.raise_for_status()
    raise RuntimeError(f"Unable to download {url}")


def _cover(im: Image.Image) -> Image.Image:
    im = im.convert("RGB")
    scale = max(W / im.width, H / im.height)
    nw, nh = int(im.width * scale), int(im.height * scale)
    im = im.resize((nw, nh), Image.Resampling.LANCZOS)
    left = max(0, (nw - W) // 2)
    top = max(0, (nh - H) // 2)
    return im.crop((left, top, left + W, top + H))


def _fit_font(draw, text: str, max_width: int, start_size: int,
              bold: bool = False, min_size: int = 12):
    for size in range(start_size, min_size - 1, -1):
        font = _font(size, bold)
        box = draw.textbbox((0, 0), text, font=font)
        if (box[2] - box[0]) <= max_width:
            return font
    raise RuntimeError(f"Text does not fit safely in one line: {text!r}")


def _wrap(draw, text: str, font, maxw: int):
    words = text.split()
    lines, cur = [], ""
    for word in words:
        test = (cur + " " + word).strip()
        if draw.textbbox((0, 0), test, font=font)[2] <= maxw:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def _fit_wrapped(draw, text: str, maxw: int, maxh: int, start: int, *,
                 bold: bool = False, min_size: int = 16, line_gap: int = 8,
                 max_lines: int | None = None):
    for size in range(start, min_size - 1, -1):
        font = _font(size, bold)
        lines = _wrap(draw, text, font, maxw)
        if max_lines is not None and len(lines) > max_lines:
            continue
        heights = []
        for line in lines:
            b = draw.textbbox((0, 0), line, font=font)
            heights.append(b[3] - b[1])
        total = sum(heights) + max(0, len(lines) - 1) * line_gap
        if total <= maxh:
            return font, lines, heights, total
    raise RuntimeError(f"Text does not fit safely: {text!r}")


def _draw_wrapped(draw, text: str, x: int, y: int, maxw: int, maxh: int,
                  start: int, *, fill=WHITE, bold=False, min_size=16,
                  line_gap=8, max_lines=None):
    font, lines, heights, total = _fit_wrapped(
        draw, text, maxw, maxh, start, bold=bold, min_size=min_size,
        line_gap=line_gap, max_lines=max_lines
    )
    cy = y
    for line, lh in zip(lines, heights):
        draw.text((x, cy), line, font=font, fill=fill)
        cy += lh + line_gap
    return cy, total


def _pill(draw, x: int, y: int, text: str, *, outline=ACCENT, text_fill=ACCENT,
          maxw=520, font_size=22):
    font = _font(font_size, True)
    while font_size >= 14:
        font = _font(font_size, True)
        b = draw.textbbox((0, 0), text, font=font)
        tw, th = b[2] - b[0], b[3] - b[1]
        width = tw + 44
        if width <= maxw:
            break
        font_size -= 1
    if width > maxw:
        raise RuntimeError(f"Pill text too wide: {text}")
    height = max(46, th + 20)
    draw.rounded_rectangle((x, y, x + width, y + height), height // 2,
                           fill=(4, 20, 34, 225), outline=outline, width=2)
    draw.text((x + 22, y + (height - th)//2 - b[1]), text, font=font, fill=text_fill)
    return width, height


def _logo(canvas: Image.Image):
    path = ASSETS_DIR / "logo.png"
    if not path.exists():
        raise FileNotFoundError("Official KMX RADAR logo missing at assets/logo.png")
    lg = Image.open(path).convert("RGBA")
    lg.thumbnail((112, 112), Image.Resampling.LANCZOS)
    canvas.alpha_composite(lg, (SAFE, 34))


def _base(photo: Image.Image):
    canvas = _cover(photo).convert("RGBA")
    # Full dark tint for readability.
    canvas.alpha_composite(Image.new("RGBA", (W, H), (3, 10, 19, 105)))
    # Strong bottom gradient.
    grad = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(grad)
    for y in range(H):
        if y < 340:
            a = 20
        else:
            a = min(235, int(20 + (y - 340) / (H - 340) * 230))
        gd.line((0, y, W, y), fill=(3, 11, 20, a))
    canvas.alpha_composite(grad)
    return canvas


def _panel(draw, box, *, outline=(31, 100, 130, 220), fill=PANEL, width=2, radius=24):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def _header(canvas, draw, slide_n: int, total: int, archive: bool):
    _logo(canvas)
    draw.text((190, 60), "KMX RADAR", font=_font(31, True), fill=WHITE)
    draw.text((190, 101), "DETECTAMOS LO QUE IMPORTA", font=_font(15, True), fill=ACCENT)
    draw.text((936, 60), f"{slide_n}/{total}", font=_font(27, True), fill=WHITE)
    if archive:
        _pill(draw, 858, 112, "ARCHIVO", outline=WARM, text_fill=WARM, maxw=160, font_size=14)


def _footer(draw, credit: str, footer: str):
    draw.line((SAFE, 1260, W-SAFE, 1260), fill=(35, 94, 115), width=2)
    # Credits are context, always small but readable.
    _draw_wrapped(draw, credit, SAFE, 1217, W-2*SAFE, 34, 14, fill=MUTED,
                  min_size=11, line_gap=3, max_lines=2)
    draw.text((SAFE, 1282), "@kmxradar", font=_font(20, True), fill=ACCENT)
    _draw_wrapped(draw, footer, 220, 1282, 790, 42, 18, fill=WHITE,
                  bold=True, min_size=14, line_gap=3, max_lines=2)


def _render_slide(package_dir: Path, spec: dict, photo: Image.Image, credit: str, total: int):
    canvas = _base(photo)
    draw = ImageDraw.Draw(canvas)
    _header(canvas, draw, int(spec["n"]), total, bool(spec.get("archive", False)))

    _pill(draw, SAFE, 176, str(spec["kicker"]), maxw=560, font_size=21)

    # Title gets a large reserved block.
    title_bottom, _ = _draw_wrapped(
        draw, str(spec["title"]), SAFE, 250, W-2*SAFE, 245, 54,
        bold=True, min_size=34, line_gap=8, max_lines=4
    )
    y = max(500, title_bottom + 22)

    if spec.get("stat"):
        # Stack the large number and its explanation vertically. A side-by-side
        # layout can overlap when the number is wider than expected (for
        # example "7 h 55 min"). Both elements are measured before drawing.
        stat_text = str(spec["stat"])
        stat_label = str(spec.get("stat_label", ""))
        stat_box = (SAFE, y, W-SAFE, y+205)
        _panel(draw, stat_box, outline=ACCENT, width=3)
        stat_font = _fit_font(draw, stat_text, W - 2*SAFE - 56, 64, True, 38)
        draw.text((SAFE+28, y+20), stat_text, font=stat_font, fill=ACCENT)
        _draw_wrapped(
            draw, stat_label, SAFE+28, y+105, W-2*SAFE-56, 72, 24,
            fill=WHITE, bold=True, min_size=18, line_gap=5, max_lines=2
        )
        y += 235

    if spec.get("body"):
        body = str(spec["body"])
        # Dynamic panel height from fitted text.
        font, lines, heights, total_h = _fit_wrapped(draw, body, W-2*SAFE-56, 240, 28,
                                                      min_size=19, line_gap=8, max_lines=5)
        ph = total_h + 56
        _panel(draw, (SAFE, y, W-SAFE, y+ph))
        cy = y + 28
        for line, lh in zip(lines, heights):
            draw.text((SAFE+28, cy), line, font=font, fill=WHITE)
            cy += lh + 8
        y += ph + 22

    if spec.get("people"):
        people = list(spec["people"])
        line_h = 58
        ph = 36 + line_h * len(people)
        _panel(draw, (SAFE, y, W-SAFE, y+ph), outline=BLUE)
        cy = y + 28
        for person in people:
            draw.ellipse((SAFE+26, cy+9, SAFE+40, cy+23), fill=BLUE)
            _draw_wrapped(draw, person, SAFE+58, cy, W-2*SAFE-90, 42, 25,
                          fill=WHITE, bold=True, min_size=19, max_lines=1)
            cy += line_h
        y += ph + 20

    if spec.get("bullets"):
        bullets = list(spec["bullets"])
        # Give each bullet its own measured row.
        for item in bullets:
            font, lines, heights, total_h = _fit_wrapped(draw, item, W-2*SAFE-95, 72, 23,
                                                          min_size=17, line_gap=5, max_lines=2)
            ph = max(76, total_h + 32)
            if y + ph > 1145:
                raise RuntimeError(f"Slide {spec['n']} bullet content exceeds safe area")
            _panel(draw, (SAFE, y, W-SAFE, y+ph))
            draw.ellipse((SAFE+26, y+30, SAFE+40, y+44), fill=ACCENT)
            cy = y + 16
            for line, lh in zip(lines, heights):
                draw.text((SAFE+58, cy), line, font=font, fill=WHITE)
                cy += lh + 5
            y += ph + 12

    if spec.get("callout"):
        callout = str(spec["callout"])
        font, lines, heights, total_h = _fit_wrapped(draw, callout, W-2*SAFE-56, 160, 24,
                                                      bold=True, min_size=18, line_gap=6, max_lines=4)
        ph = total_h + 50
        if y + ph > 1170:
            y = 1170 - ph
        _panel(draw, (SAFE, y, W-SAFE, y+ph), outline=WARM,
               fill=(28, 22, 10, 230), width=2)
        cy = y + 25
        for line, lh in zip(lines, heights):
            draw.text((SAFE+28, cy), line, font=font, fill=WARM)
            cy += lh + 6
        y += ph + 14

    if spec.get("sources"):
        src = "Fuentes: " + " · ".join(spec["sources"])
        if y < 1130:
            _draw_wrapped(draw, src, SAFE, y, W-2*SAFE, 46, 18, fill=MUTED,
                          bold=True, min_size=15, max_lines=2)

    _footer(draw, f"{'ARCHIVO · ' if spec.get('archive') else ''}{credit}", str(spec["footer"]))
    out = package_dir / str(spec["file"])
    final = canvas.convert("RGB")
    if final.size != (W, H):
        raise RuntimeError(f"Wrong output size for {out.name}: {final.size}")
    final.save(out, "PNG", optimize=True)
    LOG.info("Rendered %s", out.name)


def build_space_visuals(package_dir: Path, config: dict) -> list[Path]:
    _apply_theme(config)
    sources = config.get("sources", {})
    slides = config.get("slides", [])
    if not sources or not slides:
        raise RuntimeError("visuals.json must contain sources and slides")

    with tempfile.TemporaryDirectory(prefix="kmx-space-") as td:
        tmp = Path(td)
        photos: dict[str, Image.Image] = {}
        for key, meta in sources.items():
            path = tmp / f"{key}.jpg"
            _download(str(meta["direct_url"]), path)
            photos[key] = Image.open(path).convert("RGB")

        outputs = []
        total = len(slides)
        for spec in slides:
            key = str(spec["photo"])
            if key not in photos:
                raise RuntimeError(f"Unknown photo source {key}")
            credit = str(sources[key].get("credit") or "NASA")
            _render_slide(package_dir, spec, photos[key], credit, total)
            outputs.append(package_dir / str(spec["file"]))

        return outputs
