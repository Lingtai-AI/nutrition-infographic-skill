# Nutrition Infographic Skill

Agent-facing skill for creating nutrition/science infographic images.

The key workflow is **consultative**: before generating, the agent asks the human what kind of image they need — purpose, audience, topic, language, size/aspect ratio, style, required data/text, and output channel. If the human says “use defaults,” the skill proceeds with a safe educational default.

## Contents

- `SKILL.md` — agent playbook and decision tree.
- `scripts/generate_gpt_image.py` — OpenAI Images API fallback for GPT image generation.
- `scripts/render_nutrition_infographic.py` — deterministic Pillow renderer for exact/reproducible charts.
- `assets/demo-balanced-plate.json` — demo structured spec.
- `assets/demo-balanced-plate.png` — deterministic demo output.

## Recommended route

In Codex-enabled environments, use Codex built-in imagegen by asking Codex CLI to invoke the system imagegen skill and copy the generated PNG from `$CODEX_HOME/generated_images/<session>/` to the requested output path.

Use the Pillow renderer when exact chart proportions or reproducibility matter.

## Safety

Nutrition visuals should be educational unless a qualified professional supplied the constraints. Avoid disease-treatment claims, one-size-fits-all medical prescriptions, and unsupported promises. Include a disclaimer when appropriate.
