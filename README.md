# Nutrition Infographic Skill

Self-contained agent-facing skill for creating nutrition/science infographic images.

The key workflow is **consultative**: before generating, the agent asks the human what kind of image they need — purpose, audience, topic, language, size/aspect ratio, style, required data/text, and output channel. If the human says “use defaults,” the skill proceeds with a safe educational default.

## Contents

- `SKILL.md` — agent playbook and decision tree.
- `scripts/generate_gpt_image.py` — OpenAI Images API fallback for GPT image generation.
- `scripts/render_nutrition_infographic.py` — deterministic Pillow renderer for exact/reproducible charts.
- `scripts/compose_hybrid_overlay.py` — overlay exact Chinese text/cards on a no-text AI-generated background.
- `assets/demo-balanced-plate.json` — demo structured spec.
- `assets/demo-balanced-plate.png` — deterministic demo output.

## Recommended route

Use whichever image backend is available in the current environment:

- MiniMax CLI: `mmx image generate` when MiniMax key/quota is available.
- Codex CLI: `codex exec` to invoke the system imagegen skill, then explicitly copy the generated PNG from `$CODEX_HOME/generated_images/...` to the requested output path.
- Pillow renderer: deterministic fallback when exact chart proportions or reproducibility matter.

The repo is self-contained: examples use `scripts/...` and `assets/...` relative to the repo root, not a local `.library/custom/...` path.

## Install on a fresh LingTai project

```bash
git clone https://github.com/huangzesen/nutrition-infographic-skill.git
mkdir -p .library/custom
cp -R nutrition-infographic-skill .library/custom/nutrition-infographic
# or: ln -s "$PWD/nutrition-infographic-skill" .library/custom/nutrition-infographic
```

Then refresh the agent so the skill catalog is rescanned. The new agent can read `SKILL.md` and follow the workflow without access to the original authoring chat history.

For a polished AI-image route, the new machine needs at least one working backend: MiniMax CLI (`mmx`) with key/quota, command-line `codex` with the system imagegen skill / built-in `image_gen` capability, or OpenAI Images API credentials. Without those, use the deterministic Pillow renderer.

## Safety

Nutrition visuals should be educational unless a qualified professional supplied the constraints. Avoid disease-treatment claims, one-size-fits-all medical prescriptions, and unsupported promises. Include a disclaimer when appropriate.


## MiniMax CLI imagegen example

```bash
# Prefer mmx's own config/auth. Do not blindly reuse a LingTai LLM preset key.
mmx config show --output json
mmx auth status --output json
mmx quota show --output json

mkdir -p generated
mmx image generate \
  --prompt '一张方形中文营养学科普信息图，主题：早餐怎么搭配更稳。干净温暖的微信健康科普卡片风格，高对比度，可读中文标题。包含三块：高纤维蔬果、优质蛋白、慢碳水。页脚：科普示意，不替代医生或注册营养师建议。' \
  --width 1024 --height 1024 \
  --out generated/minimax-nutrition.png \
  --non-interactive --output json --timeout 300
```

Only pass `--api-key`/`--region` when you know the key belongs to the MiniMax image API and which region it uses. If MiniMax reports `invalid api key`, check backend/region first. If it reports `usage limit exceeded` or `no active token plan subscription` after auth is verified, switch to Codex/OpenAI/Pillow rather than retrying. MiniMax layouts can look good, but exact Chinese text may be garbled; use Pillow/SVG/HTML for the final text layer when accuracy matters.

## Hybrid MiniMax background + deterministic Chinese text

Best publication workflow when MiniMax is available:

1. Ask MiniMax for a **no-text** background/layout only: blank cards, food illustration, no letters, no numbers, no logo, no watermark.
2. Render exact Chinese copy/data/disclaimer with the local overlay script.

```bash
mmx image generate \
  --prompt 'Square nutrition poster background only. Warm cream and fresh green palette. Healthy breakfast plate illustration. Blank rounded white cards. No text, no letters, no numbers, no logo, no watermark, lots of empty space for later typography overlay.' \
  --width 1024 --height 1024 \
  --prompt-optimizer \
  --out generated/minimax-layout-no-text.png \
  --non-interactive --output json --timeout 300

python3 scripts/compose_hybrid_overlay.py \
  --background generated/minimax-layout-no-text.png \
  --out generated/hybrid-minimax-text-overlay.png
```

## Codex CLI imagegen example

```bash
cat > /tmp/nutrition-spec.json <<'JSON'
{"title":"早餐怎么搭配更稳","subtitle":"科普示意","language":"Simplified Chinese","style":"clean WeChat health card","footer":"科普示意，不替代医生或注册营养师建议"}
JSON

OUT="$PWD/generated/nutrition-breakfast.png"
mkdir -p "$(dirname "$OUT")"
codex exec --cd "$PWD" "Use the system imagegen skill. Read /tmp/nutrition-spec.json. Generate one polished nutrition infographic PNG with the built-in image_gen tool. After generation, locate the newest PNG under \$CODEX_HOME/generated_images/ and copy it to '$OUT'. Print only the final output path. Do not use the OpenAI API fallback script."
```
