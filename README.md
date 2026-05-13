# Nutrition Infographic Skill

Self-contained agent-facing skill for creating nutrition/science infographic images.

The key workflow is **consultative**: before generating, the agent asks the human what kind of image they need — purpose, audience, topic, language, size/aspect ratio, style, required data/text, and output channel. If the human says “use defaults,” the skill proceeds with a safe educational default.

## Contents

- `SKILL.md` — agent playbook and decision tree.
- `scripts/generate_gpt_image.py` — OpenAI Images API fallback for GPT image generation.
- `scripts/render_nutrition_infographic.py` — deterministic Pillow renderer for exact/reproducible charts.
- `assets/demo-balanced-plate.json` — demo structured spec.
- `assets/demo-balanced-plate.png` — deterministic demo output.

## Recommended route

In Codex-enabled environments, use command-line `codex exec` to invoke the system imagegen skill, then explicitly copy the generated PNG from `$CODEX_HOME/generated_images/...` to the requested output path. The repo is self-contained: examples use `scripts/...` and `assets/...` relative to the repo root, not a local `.library/custom/...` path.

Use the Pillow renderer when exact chart proportions or reproducibility matter.

## Safety

Nutrition visuals should be educational unless a qualified professional supplied the constraints. Avoid disease-treatment claims, one-size-fits-all medical prescriptions, and unsupported promises. Include a disclaimer when appropriate.


## Codex CLI imagegen example

```bash
cat > /tmp/nutrition-spec.json <<'JSON'
{"title":"早餐怎么搭配更稳","subtitle":"科普示意","language":"Simplified Chinese","style":"clean WeChat health card","footer":"科普示意，不替代医生或注册营养师建议"}
JSON

OUT="$PWD/generated/nutrition-breakfast.png"
mkdir -p "$(dirname "$OUT")"
codex exec --cd "$PWD" "Use the system imagegen skill. Read /tmp/nutrition-spec.json. Generate one polished nutrition infographic PNG with the built-in image_gen tool. After generation, locate the newest PNG under \$CODEX_HOME/generated_images/ and copy it to '$OUT'. Print only the final output path. Do not use the OpenAI API fallback script."
```
