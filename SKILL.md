---
name: nutrition-infographic
description: Generate nutrition/science infographic images through a consultative workflow: first ask the human what image they need (purpose, audience, topic, language, size, style, data/text, output channel), then generate via Codex built-in imagegen or deterministic Pillow fallback.
version: 1.2.0
tags: [python, nutrition, infographic, image-generation, workflow]
---

# Nutrition Infographic Generator

This skill creates nutrition/science infographic images. The **default workflow is consultative**: ask the human what kind of image they need before generating anything, unless they already supplied enough detail or explicitly asked for a demo.

Recommended generation route in Codex environments: ask Codex CLI / Codex's built-in `imagegen` system skill to use the built-in `image_gen` tool, then copy the generated PNG into the requested project path. The deterministic Pillow renderer remains the fallback for exact chart geometry, repeatability, offline rendering, or fast drafts.

## When this applies

Use this skill for:

- balanced-plate diagrams and meal composition visuals
- macronutrient proportion charts
- nutrition education cards, posters, and article illustrations
- diet/health science explainers where numbers and labels must stay legible
- rapid drafts that should look like finished educational images
- social posts, article covers, slides, handouts, and app onboarding visuals

Do **not** use this as-is for medical diagnosis, patient-specific diet prescriptions, disease-treatment promises, photorealistic food photography, or brand-sensitive publication design without explicit human direction and review.

## First move: ask what image the human needs

If the human has not already provided the essentials, ask a short intake question before generating. Do not interrogate them with a long form; ask for the missing pieces that matter.

### Minimal intake

Ask in the human's language:

> 你想要一张什么样的营养学图片？请告诉我：用途/平台、主题、面向谁、语言、尺寸比例、风格、是否有必须出现的数据或文案。没有细节的话我可以先给你一个默认方案。

For English:

> What nutrition image do you need? Please tell me the purpose/platform, topic, audience, language, aspect ratio, style, and any required data or wording. If you do not have details, I can propose a default.

### If they are in a hurry

Ask only the 3 essentials:

1. **Topic** — what nutrition concept, food, meal, nutrient, or behavior?
2. **Use/channel** — WeChat article, poster, slide, social card, app UI, handout?
3. **Audience/language** — general adults, children, athletes, older adults, diabetes education, etc.; Chinese/English/bilingual?

Then choose sensible defaults for the rest and state them before generating.

### Intake fields to capture

- **Purpose/channel**: WeChat article, service-account reply, Xiaohongshu card, slide, poster, handout, app screen.
- **Audience**: general public, parents, students, athletes, older adults, clinicians, patients, etc.
- **Topic**: balanced meal, protein, fiber, glycemic load, hydration, sodium, pregnancy nutrition, etc.
- **Message goal**: educate, compare, warn, motivate, summarize, explain a process.
- **Language**: Chinese, English, bilingual; simplified/traditional if Chinese matters.
- **Canvas**: square `1024x1024`, vertical `1080x1920`, horizontal slide `1600x900`, print A4, etc.
- **Style**: clean medical, warm editorial, playful cartoon, premium brand, minimalist data viz, etc.
- **Required text/data**: exact title, numbers, units, source, disclaimer.
- **Brand constraints**: colors, logo, QR code, no-logo, typography.
- **Accuracy constraints**: illustrative vs sourced; whether medical/professional review is required.
- **Output path/channel**: where to save and whether to send/attach it.

## Decision tree

1. **Human provided a complete brief** → draft JSON spec or rich prompt and generate.
2. **Human provided only a topic** → ask the minimal intake question; if they say “随便/默认”, proceed with defaults.
3. **Exact numbers/charts must be correct** → use the Pillow renderer first, or use GPT image only for a decorative companion.
4. **Polished editorial visual matters more than exact geometry** → use Codex built-in imagegen.
5. **No imagegen available / offline / reproducible draft needed** → use `scripts/render_nutrition_infographic.py`.
6. **Medical personalization requested** → keep it educational, ask for professional constraints, include disclaimer; do not invent clinical advice.

## Default brief if the human says “你来定”

Use this default unless the context suggests otherwise:

- Channel: WeChat article / social card
- Canvas: square, `1024x1024`
- Language: simplified Chinese if the human is using Chinese; otherwise match human language
- Audience: general adults
- Style: clean warm health-education editorial, high contrast, readable labels
- Claims: educational / illustrative, not medical advice
- Footer: `科普示意，不替代医生或注册营养师建议`

## JSON spec schema

Prefer JSON when the content includes structured nutrition data. Supported top-level fields:

```json
{
  "title": "Main title",
  "subtitle": "Short explanatory subtitle",
  "theme": "green",
  "background": "cream",
  "canvas": {"size": "1024x1024", "aspect": "1:1"},
  "audience": "general adults",
  "style": "clean editorial health education",
  "plate": [
    {"label": "Vegetables", "value": 40, "color": "green"}
  ],
  "metrics": [
    {"label": "Protein", "value": "31", "unit": "g", "note": "Satiety", "color": "orange"}
  ],
  "bars": [
    {"label": "Carbs", "value": 45, "target": 55, "unit": "%", "color": "yellow"}
  ],
  "tips": ["Practical tip 1", "Practical tip 2"],
  "required_text": ["Exact phrase that must appear"],
  "footer": "Source / disclaimer"
}
```

The Pillow fallback uses the original subset: `title`, `subtitle`, `theme`, `background`, `plate`, `metrics`, `bars`, `tips`, and `footer`. Extra fields are for prompt-building and should be reflected in GPT image prompts.

## Procedure

1. **Clarify the brief.** Ask for missing essentials. If the human says to proceed, write down the assumptions.
2. **Choose route.** Use Codex built-in imagegen for polished visuals; Pillow for exact/reproducible charts; OpenAI API fallback only when explicitly needed.
3. **Draft a spec/prompt.** Preserve exact numbers and wording. Keep claims conservative. Add source/disclaimer text when appropriate.
4. **Generate.** Save the PNG to a stable output path under the project or requested destination.
5. **Inspect.** Check legibility, label overlap, text language, numerical consistency, and whether unsupported medical claims slipped in.
6. **Iterate.** If text or numbers are wrong in GPT image output, simplify the prompt/spec or switch to Pillow for the data layer.
7. **Deliver.** Send or attach the image on the same channel where the request arrived if possible, and mention assumptions used.

## Codex built-in imagegen route

From the agent workdir, write a JSON spec or prompt file and use Codex CLI as the default GPT image route:

```bash
OUT=/tmp/nutrition-infographic.png
codex exec --cd "$PWD" "Use the system imagegen skill. Read /tmp/nutrition-spec.json, generate a polished nutrition infographic with the built-in image_gen tool, then copy the generated PNG from \$CODEX_HOME/generated_images/<session>/ to $OUT ; do not use the OpenAI API fallback script."
```

If the human did not provide data, create a draft spec with reasonable placeholder values and clearly mark it as educational/illustrative. If they provide exact values, preserve them.

## OpenAI API fallback

Use only when an explicit API path is desired and credentials are available:

```bash
python3 .library/custom/nutrition-infographic/scripts/generate_gpt_image.py \
  --spec /tmp/spec.json \
  --out /tmp/nutrition-gpt.png
```

or:

```bash
python3 .library/custom/nutrition-infographic/scripts/generate_gpt_image.py \
  --prompt-file /tmp/nutrition-prompt.txt \
  --out /tmp/nutrition-poster.png \
  --model gpt-image-1 \
  --size 1024x1024 \
  --quality high
```

## Pillow fallback

Use the deterministic renderer when exact chart proportions, repeatable output, no API call, or a fast draft matters:

```bash
# Render demo directly with Pillow
python3 .library/custom/nutrition-infographic/scripts/render_nutrition_infographic.py \
  --out /tmp/demo-nutrition.png

# Render a custom spec with fixed canvas size
python3 .library/custom/nutrition-infographic/scripts/render_nutrition_infographic.py \
  --spec /tmp/spec.json \
  --out /tmp/card.png \
  --width 1400 --height 1000

# Write a starter spec
python3 .library/custom/nutrition-infographic/scripts/render_nutrition_infographic.py \
  --write-demo-spec /tmp/demo-nutrition.json
```

## Prompt template for GPT image

Use this structure when generating through imagegen:

```text
Create a polished nutrition science infographic.

Purpose/channel: <...>
Audience: <...>
Language: <...>
Canvas/aspect: <...>
Style: <...>

Main message: <...>
Title: <exact title>
Subtitle: <exact subtitle>
Required text/numbers: <list exact phrases, values, units>
Visual structure: <plate / metric cards / comparison bars / tips / footer>
Data/source status: <sourced or illustrative>
Disclaimer/footer: <...>

Design constraints:
- Make all labels crisp, high contrast, and readable.
- Preserve all provided numbers, units, and wording exactly.
- Avoid disease-treatment promises, miracle claims, or unsupported medical advice.
- Prefer clean information design over photorealistic food photography unless requested.
```

## Content safety and accuracy checklist

Before sending a nutrition infographic:

- Are values explicitly sourced or clearly marked as illustrative?
- Does the output avoid disease-treatment promises and one-size-fits-all prescriptions?
- Does the footer warn that special groups should consult clinicians/dietitians?
- Are units correct (`g`, `mg`, `kcal`, `%`, `g/kg`, etc.)?
- Is the target audience clear?
- Is the language exactly what the human requested?
- If the human asks for medical personalization, ask for permission to keep it general or request professional constraints; do not invent clinical advice.

## Files

- `scripts/generate_gpt_image.py` — OpenAI API fallback / explicit API path using the OpenAI Python SDK; not the default Codex built-in imagegen route.
- `scripts/render_nutrition_infographic.py` — deterministic PNG renderer built with Pillow.
- `assets/demo-balanced-plate.json` — Chinese demo spec for a balanced-plate infographic.
- `assets/demo-balanced-plate.png` — deterministic demo output.

## Publishing notes

When publishing this skill outside one agent:

- Include `SKILL.md`, `README.md`, `scripts/`, `assets/demo-balanced-plate.json`, and at least one small demo output.
- Do not include transient `__pycache__` folders.
- Generated examples are optional; keep repo size reasonable.
- After copying into a LingTai `.library/custom/` or `.library_shared/`, run the skills validator and refresh the agent.
