# HopeStage Content Creation

Weekly dual-channel content pipeline for HopeStage.

This project checks the latest YouTube uploads on the French and English channels, keeps a local processed-state file so runs are idempotent, and generates a reusable content bundle for each new video:

- video metadata
- description snapshot
- transcript export when available
- thumbnail download
- hook bank
- LinkedIn draft
- X draft
- Instagram draft
- image prompt and format specs
- thank-you email draft for the guest
- review notes
- social-ready image crops from the thumbnail, including Instagram carousel square exports

The output is designed for speed and reliability first. It uses deterministic local generation so it still works without extra API keys.

## Voice, founder, and design context

The repository now includes a reusable HopeStage content system:

- `VOICE_PROFILE.md` for plain-language voice guidance
- `CONTENT_SYSTEM.md` for content strategy and usage
- `CONTENT_REQUEST_WORKFLOW.md` for simple natural-language request handling
- `DESIGN_GUIDELINES.md` for the working visual direction
- `config/founder_profile.json` for machine-readable founder and brand context
- `prompts/post_creation_prompt.md` for future prompting and drafting
- `prompts/task_router_prompt.md` for routing short content requests

The generator reads `config/founder_profile.json` so new drafts can reflect Clement's lived experience, expertise, and HopeStage's positioning more consistently.
The design layer is now aligned with the official Notion brand page: [HopeStage Brand Guidelines (EN)](https://www.notion.so/hopestage/HopeStage-Brand-Guidelines-EN-24239dda6d2880ed93d4e25c0675564d).

## Channels

- French: `https://www.youtube.com/@HopeStage-FR/videos`
- English: `https://www.youtube.com/@clementbaissat-HopeStage/videos`

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Usage

Check the latest video on both channels without generating files:

```bash
content-pipeline --check-only
```

Run the weekly pipeline for both channels:

```bash
content-pipeline
```

or directly from the repo without installing the CLI entrypoint:

```bash
bash scripts/run_weekly.sh
```

Run just one channel:

```bash
content-pipeline --channel fr
content-pipeline --channel en
```

Process the latest 5 videos on each channel:

```bash
content-pipeline --limit 5
```

Force regeneration for the current latest video:

```bash
content-pipeline --channel fr --force
```

Force regeneration for the latest 5 videos on both channels:

```bash
content-pipeline --limit 5 --force
```

Parse a simple natural-language request into a structured content workflow:

```bash
content-intake --request "Prepare me a LinkedIn post for my latest interview in French and give me the thumbnail."
```

## Output structure

Each processed video gets its own folder under:

- `outputs/fr/`
- `outputs/en/`

Each folder contains:

- `metadata.json`
- `description.txt`
- `transcript.txt`
- `summary.txt`
- `hooks.txt`
- `linkedin_post.txt`
- `x_post.txt`
- `instagram_post.txt`
- `image_prompt.txt`
- `image_specs.txt`
- `thank_you_email.txt`
- `notes.txt`
- `bundle.txt`
- `thumbnail.jpg`
- `social_image_1x1.jpg`
- `social_image_4x5.jpg`
- `social_image_16x9.jpg`

## Idempotency

Processed video ids are stored in `data/runtime_state.json`.

That means:

- normal runs skip a video when it was already processed
- `--force` rebuilds the output for the requested recent videos

## Content choices

The current generator is rule-based on purpose:

- it always runs locally
- it is easy to inspect and debug
- it avoids blocking the weekly workflow on missing API keys

The code is split so an LLM-backed generator can be added later without changing the YouTube or file-writing logic.

Visual assets also have a local fallback:

- the pipeline creates a square `1:1` crop for Instagram carousel slides
- it also creates a portrait `4:5` crop for Instagram single-image posts and LinkedIn
- it also creates a landscape `16:9` crop for X and wider previews
- this works from the YouTube thumbnail, so the repo stays runnable without extra services

## Feedback memory

The repo now includes [`FEEDBACK_MEMORY.md`](FEEDBACK_MEMORY.md) for recurring editorial and visual corrections.

Current reusable learnings include:

- use canonical HopeStage logos from `assets/brand/`, not older desktop exports
- default Instagram carousel slides to `1:1` square, not generic `4:5`
- keep brand and CTA elements inside a generous square safe zone

## Thumbnail system

Thumbnail resolution now follows this order:

1. `thumbnail_overrides/<video_id>.*`
2. YouTube `og:image` from the watch page
3. Standard YouTube thumbnail fallbacks like `maxresdefault`, `sddefault`, `hq720`, and `hqdefault`

If YouTube serves the wrong public thumbnail for a specific video, add the correct file under:

- `thumbnail_overrides/<video_id>.jpg`
- `thumbnail_overrides/<video_id>.png`

Then rerun the pipeline with `--force` and that manual file will win automatically.

## Current limitations

- thank-you emails are generated even when the guest name cannot be detected, so the greeting may need a manual edit
- guest detection is currently title-based
- the generator is optimized for practical weekly drafts, not final publishing-quality copy

## Suggested weekly automation

Run every Tuesday after both videos are expected to be live:

```bash
cd /Users/clement/Documents/GitHub/Content-creation-
bash scripts/run_weekly.sh
```
