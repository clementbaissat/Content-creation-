# HopeStage Content Creation

Weekly dual-channel content pipeline for HopeStage.

This project checks the latest YouTube upload on the French and English channels, keeps a local processed-state file so runs are idempotent, and generates a reusable content bundle for each new video:

- video metadata
- description snapshot
- transcript export when available
- thumbnail download
- hook bank
- LinkedIn draft
- thank-you email draft for the guest
- review notes

The output is designed for speed and reliability first. It uses deterministic local generation so it still works without extra API keys.

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

Force regeneration for the current latest video:

```bash
content-pipeline --channel fr --force
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
- `thank_you_email.txt`
- `notes.txt`
- `bundle.txt`
- `thumbnail.jpg`

## Idempotency

Processed video ids are stored in `data/runtime_state.json`.

That means:

- normal runs skip a channel when the latest video was already processed
- `--force` rebuilds the output for the latest video

## Content choices

The current generator is rule-based on purpose:

- it always runs locally
- it is easy to inspect and debug
- it avoids blocking the weekly workflow on missing API keys

The code is split so an LLM-backed generator can be added later without changing the YouTube or file-writing logic.

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
