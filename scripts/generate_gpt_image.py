#!/usr/bin/env python3
"""OpenAI API fallback for generating a nutrition infographic image.

The default Codex workflow should use the built-in imagegen/image_gen tool and
copy the generated PNG from $CODEX_HOME/generated_images/<session>/ to the
project path. Use this script only when an explicit OpenAI API path is desired.
It calls the Images API and saves the returned PNG. The API key is read from
OPENAI_API_KEY first, then from ~/.codex/auth.json as a fallback. The key is
never printed.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import urllib.request
from pathlib import Path
from typing import Any, Iterable


DEFAULT_MODEL = "gpt-image-1"
DEFAULT_SIZE = "1024x1024"
DEFAULT_QUALITY = "auto"


def find_auth_key(value: Any) -> str | None:
    """Recursively find an OPENAI_API_KEY value in auth.json-like data."""
    if isinstance(value, dict):
        for key, child in value.items():
            if key.upper() == "OPENAI_API_KEY" and isinstance(child, str) and child.strip():
                return child.strip()
        for child in value.values():
            found = find_auth_key(child)
            if found:
                return found
    elif isinstance(value, list):
        for child in value:
            found = find_auth_key(child)
            if found:
                return found
    return None


def load_api_key() -> str:
    key = os.environ.get("OPENAI_API_KEY")
    if key:
        return key

    auth_path = Path.home() / ".codex" / "auth.json"
    if auth_path.exists():
        try:
            data = json.loads(auth_path.read_text(encoding="utf-8"))
        except Exception as exc:
            raise RuntimeError(f"Could not parse {auth_path}: {exc}") from exc
        key = find_auth_key(data)
        if key:
            return key

    raise RuntimeError(
        "OPENAI_API_KEY was not found in the environment or ~/.codex/auth.json."
    )


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise RuntimeError(f"Could not read JSON spec {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise RuntimeError(f"Spec must be a JSON object: {path}")
    return data


def format_items(items: Any, fields: Iterable[str]) -> str:
    if not isinstance(items, list) or not items:
        return "None provided."

    lines: list[str] = []
    for idx, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            lines.append(f"{idx}. {item}")
            continue
        parts = []
        for field in fields:
            if field in item and item[field] not in (None, ""):
                parts.append(f"{field}: {item[field]}")
        lines.append(f"{idx}. " + "; ".join(parts))
    return "\n".join(lines)


def build_prompt_from_spec(spec: dict[str, Any]) -> str:
    title = spec.get("title", "Nutrition infographic")
    subtitle = spec.get("subtitle", "")
    footer = spec.get("footer", "Educational infographic; not medical advice.")

    return f"""Create a polished nutrition science infographic PNG.

Design requirements:
- Clean editorial information design, suitable for a health education handout or article illustration.
- Make all text crisp, high contrast, and easy to read.
- Preserve all numbers, units, labels, and wording exactly as provided below.
- Use a balanced layout with a plate/proportion visual, metric cards, bar/progress comparisons, practical tips, and a small footer.
- Avoid photorealistic food photography unless it supports the infographic; prioritize readable data visualization.
- Do not add disease-treatment claims, weight-loss promises, or unsupported medical advice.

Content:
Title: {title}
Subtitle: {subtitle}
Theme: {spec.get("theme", "fresh green / health education")}
Background: {spec.get("background", "warm neutral")}

Plate/proportion sections:
{format_items(spec.get("plate"), ("label", "value", "color"))}

Metric cards:
{format_items(spec.get("metrics"), ("label", "value", "unit", "note", "color"))}

Bar/progress comparisons:
{format_items(spec.get("bars"), ("label", "value", "target", "unit", "color"))}

Practical tips:
{format_items(spec.get("tips"), ())}

Footer/disclaimer:
{footer}
"""


def read_prompt(args: argparse.Namespace) -> str:
    pieces: list[str] = []

    if args.spec:
        pieces.append(build_prompt_from_spec(load_json(Path(args.spec))))
    if args.prompt_file:
        pieces.append(Path(args.prompt_file).read_text(encoding="utf-8").strip())
    if args.prompt:
        pieces.append(args.prompt.strip())

    prompt = "\n\nAdditional instruction:\n".join(piece for piece in pieces if piece)
    if not prompt:
        raise RuntimeError("Provide --spec, --prompt-file, or --prompt.")
    return prompt


def save_image_response(image_data: Any, out_path: Path) -> None:
    b64_json = getattr(image_data, "b64_json", None)
    url = getattr(image_data, "url", None)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    if b64_json:
        out_path.write_bytes(base64.b64decode(b64_json))
        return
    if url:
        with urllib.request.urlopen(url, timeout=120) as response:
            out_path.write_bytes(response.read())
        return

    raise RuntimeError("Image response did not contain b64_json or url data.")


def generate_image(args: argparse.Namespace) -> Path:
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError(
            "OpenAI Python SDK is not installed. Install with: python3 -m pip install openai"
        ) from exc

    prompt = read_prompt(args)
    client = OpenAI(api_key=load_api_key())

    request: dict[str, Any] = {
        "model": args.model,
        "prompt": prompt,
        "size": args.size,
    }
    if args.quality:
        request["quality"] = args.quality

    result = client.images.generate(**request)
    if not getattr(result, "data", None):
        raise RuntimeError("Image API returned no image data.")

    out_path = Path(args.out)
    save_image_response(result.data[0], out_path)
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a nutrition infographic using OpenAI GPT image."
    )
    parser.add_argument("--prompt", help="Direct image prompt text.")
    parser.add_argument("--prompt-file", help="UTF-8 text file containing an image prompt.")
    parser.add_argument("--spec", help="JSON nutrition infographic spec.")
    parser.add_argument("--out", default="nutrition-gpt-image.png", help="Output image path.")
    parser.add_argument("--size", default=DEFAULT_SIZE, help="Image size, e.g. 1024x1024.")
    parser.add_argument("--quality", default=DEFAULT_QUALITY, help="Image quality, e.g. auto/high/medium/low.")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="OpenAI image model.")
    args = parser.parse_args()

    try:
        out_path = generate_image(args)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)

    print(out_path)


if __name__ == "__main__":
    main()
