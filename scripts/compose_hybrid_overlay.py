#!/usr/bin/env python3
"""Compose deterministic Chinese text over an AI-generated no-text background.

Use this after generating a MiniMax/Codex/OpenAI background that intentionally
contains no text. The script renders the nutrition copy, numbers, and disclaimer
with local fonts so publication-critical wording stays exact.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Iterable, Tuple

from PIL import Image, ImageDraw, ImageFont

Color = Tuple[int, int, int, int]

DEFAULT_SPEC: Dict[str, Any] = {
    "title": "早餐怎么搭配更稳？",
    "subtitle": "高纤维蔬果 + 优质蛋白 + 慢碳水",
    "cards": [
        {"number": "01", "title": "先吃蔬果", "body": "增加膳食纤维，延缓餐后血糖波动"},
        {"number": "02", "title": "配足蛋白", "body": "鸡蛋、奶、豆制品或瘦肉提升饱腹感"},
        {"number": "03", "title": "主食选慢碳水", "body": "优先燕麦、全麦、杂豆、薯类"},
    ],
    "footer": "科普示意，不替代医生或注册营养师建议。特殊人群请咨询专业人士。",
    "palette": {
        "title": [39, 82, 55, 255],
        "subtitle": [87, 101, 79, 255],
        "body": [67, 77, 70, 255],
        "accent": [87, 155, 99, 255],
        "panel": [255, 255, 255, 226],
    },
}


def rgba(value: Any, default: Color) -> Color:
    if isinstance(value, str):
        s = value.strip().lstrip("#")
        if len(s) in (6, 8):
            try:
                vals = [int(s[i : i + 2], 16) for i in range(0, len(s), 2)]
                if len(vals) == 3:
                    vals.append(255)
                return tuple(vals)  # type: ignore[return-value]
            except ValueError:
                return default
    if isinstance(value, (list, tuple)) and len(value) in (3, 4):
        vals = [max(0, min(255, int(x))) for x in value]
        if len(vals) == 3:
            vals.append(255)
        return tuple(vals)  # type: ignore[return-value]
    return default


def find_font(candidates: Iterable[str], size: int) -> ImageFont.ImageFont:
    for path in candidates:
        if path and Path(path).exists():
            try:
                return ImageFont.truetype(path, size=size)
            except Exception:
                pass
    return ImageFont.load_default()


def font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    return find_font(
        [
            "/System/Library/Fonts/STHeiti Medium.ttc" if bold else "/System/Library/Fonts/STHeiti Light.ttc",
            "/System/Library/Fonts/Hiragino Sans GB.ttc",
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc" if bold else "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ],
        size,
    )


def text_width(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.ImageFont) -> int:
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[2] - box[0]


def draw_centered_wrapped(
    draw: ImageDraw.ImageDraw,
    text: str,
    y: int,
    fnt: ImageFont.ImageFont,
    fill: Color,
    canvas_w: int,
    max_width: int,
    line_gap: int = 8,
) -> int:
    lines = []
    cur = ""
    for ch in text:
        trial = cur + ch
        if text_width(draw, trial, fnt) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = ch
    if cur:
        lines.append(cur)

    for line in lines:
        box = draw.textbbox((0, 0), line, font=fnt)
        w = box[2] - box[0]
        h = box[3] - box[1]
        draw.text(((canvas_w - w) // 2, y), line, font=fnt, fill=fill)
        y += h + line_gap
    return y


def panel(draw: ImageDraw.ImageDraw, box: Tuple[int, int, int, int], fill: Color, outline: Color, radius: int = 28) -> None:
    x1, y1, x2, y2 = box
    draw.rounded_rectangle((x1 + 5, y1 + 9, x2 + 5, y2 + 9), radius=radius, fill=(0, 0, 0, 35))
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=2)


def load_spec(path: Path | None) -> Dict[str, Any]:
    if path is None:
        return dict(DEFAULT_SPEC)
    with path.open("r", encoding="utf-8") as f:
        spec = json.load(f)
    merged = dict(DEFAULT_SPEC)
    merged.update(spec)
    if "palette" in spec:
        pal = dict(DEFAULT_SPEC["palette"])
        pal.update(spec.get("palette") or {})
        merged["palette"] = pal
    return merged


def compose(spec: Dict[str, Any], background: Path | None, out: Path, width: int, height: int) -> None:
    if background:
        base = Image.open(background).convert("RGBA").resize((width, height))
    else:
        base = Image.new("RGBA", (width, height), (255, 249, 239, 255))
    draw = ImageDraw.Draw(base, "RGBA")

    pal = spec.get("palette") or {}
    title_color = rgba(pal.get("title"), (39, 82, 55, 255))
    subtitle_color = rgba(pal.get("subtitle"), (87, 101, 79, 255))
    body_color = rgba(pal.get("body"), (67, 77, 70, 255))
    accent = rgba(pal.get("accent"), (87, 155, 99, 255))
    panel_fill = rgba(pal.get("panel"), (255, 255, 255, 226))
    outline = rgba(pal.get("outline"), (73, 126, 88, 175))

    # Layout ratios are tuned for a square social card but scale to any canvas.
    margin_x = int(width * 0.09)
    top = int(height * 0.075)
    panel((draw), (margin_x, top, width - margin_x, int(height * 0.285)), panel_fill, outline, radius=int(width * 0.032))

    y = top + int(height * 0.032)
    y = draw_centered_wrapped(draw, str(spec.get("title", "")), y, font(int(width * 0.056), True), title_color, width, int(width * 0.74))
    y = draw_centered_wrapped(draw, str(spec.get("subtitle", "")), y + int(height * 0.012), font(int(width * 0.029), True), subtitle_color, width, int(width * 0.74))

    cards = list(spec.get("cards") or [])[:4]
    card_x = int(width * 0.12)
    card_w = int(width * 0.765)
    card_h = int(height * 0.11)
    card_gap = int(height * 0.024)
    card_y = int(height * 0.36)
    for i, card in enumerate(cards):
        yy = card_y + i * (card_h + card_gap)
        panel(draw, (card_x, yy, card_x + card_w, yy + card_h), panel_fill, outline, radius=int(width * 0.024))
        bubble = (card_x + int(width * 0.027), yy + int(card_h * 0.25), card_x + int(width * 0.082), yy + int(card_h * 0.75))
        draw.ellipse(bubble, fill=accent)
        draw.text((bubble[0] + int(width * 0.014), bubble[1] + int(height * 0.008)), str(card.get("number", i + 1)), font=font(int(width * 0.022), True), fill=(255, 255, 255, 255))
        tx = card_x + int(width * 0.105)
        draw.text((tx, yy + int(card_h * 0.18)), str(card.get("title", "")), font=font(int(width * 0.033), True), fill=title_color)
        draw.text((tx, yy + int(card_h * 0.60)), str(card.get("body", "")), font=font(int(width * 0.023)), fill=body_color)

    footer = str(spec.get("footer", ""))
    if footer:
        foot_y1 = int(height * 0.875)
        panel(draw, (int(width * 0.115), foot_y1, int(width * 0.885), int(height * 0.94)), rgba(pal.get("footer_panel"), (255, 255, 255, 210)), outline, radius=int(width * 0.02))
        draw.text((int(width * 0.145), foot_y1 + int(height * 0.022)), footer, font=font(int(width * 0.021)), fill=body_color)

    out.parent.mkdir(parents=True, exist_ok=True)
    base.convert("RGB").save(out, quality=95)


def main() -> None:
    ap = argparse.ArgumentParser(description="Compose deterministic text over a no-text AI background.")
    ap.add_argument("--background", type=Path, help="No-text background image from MiniMax/Codex/OpenAI")
    ap.add_argument("--spec", type=Path, help="JSON text overlay spec")
    ap.add_argument("--out", type=Path, required=True, help="Output PNG/JPEG path")
    ap.add_argument("--width", type=int, default=1024)
    ap.add_argument("--height", type=int, default=1024)
    ap.add_argument("--write-demo-spec", type=Path, help="Write a starter hybrid overlay JSON spec and exit")
    args = ap.parse_args()

    if args.write_demo_spec:
        args.write_demo_spec.parent.mkdir(parents=True, exist_ok=True)
        args.write_demo_spec.write_text(json.dumps(DEFAULT_SPEC, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Wrote demo spec: {args.write_demo_spec}")
        return

    spec = load_spec(args.spec)
    compose(spec, args.background, args.out, args.width, args.height)
    print(f"Wrote hybrid image: {args.out}")


if __name__ == "__main__":
    main()
