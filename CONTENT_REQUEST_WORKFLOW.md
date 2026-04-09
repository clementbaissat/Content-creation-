# HopeStage Simple Content Request Workflow

This file defines the simplest way to ask for content work in plain language.

The goal is that Clement can talk naturally and still get a clean deliverable.

## Default Request Style

You should be able to ask things like:

- `Prepare me a LinkedIn post for the latest interview I did in English.`
- `Fais-moi un post LinkedIn en français pour ma dernière interview, avec la miniature.`
- `Prepare me a LinkedIn post for the latest YouTube video in English.`
- `Fais-moi un post LinkedIn pour la dernière vidéo YouTube en français.`
- `Use this video and prepare an Instagram post plus thumbnail: <url>`
- `I recorded a voice note with an idea. Turn it into a LinkedIn post.`
- `Take this transcript and create a post for LinkedIn and Instagram.`

## Supported Inputs

- latest interview
- latest video
- latest YouTube video
- podcast episode URL
- YouTube or video URL
- transcript
- voice recording or voice note
- rough text idea

## Official YouTube Sources

When a request mentions the `latest YouTube video` and no direct URL is provided, use these official channels:

- French: `https://www.youtube.com/@HopeStage-FR`
- English: `https://www.youtube.com/@clementbaissat-HopeStage`

## Supported Outputs

- LinkedIn post
- LinkedIn hashtags
- Instagram post
- Instagram hashtags
- X post
- X hashtags
- blog article
- newsletter draft
- thumbnail direction
- image prompt

## Default Behavior

- If language is not specified, default to the source language.
- If the request mentions the latest interview or latest video, fetch the newest relevant source first.
- If the request mentions the latest YouTube video, use the official HopeStage YouTube channels unless the user gives a direct URL.
- If the request is based on a voice note, extract the core idea before drafting.
- If the request asks for a thumbnail or image, also prepare a visual direction or image prompt.
- Keep all outputs aligned with HopeStage voice and brand guidance.
- If the request is for an Instagram carousel, default to square `1080x1080` slides unless another format is explicitly requested.
- Social post deliverables should include hashtags by default.
- Unless stated otherwise, assume the audience is people living with bipolarity.
- For podcast and YouTube content, optimize first for views, comments, and full-video watching.
- Use an expert founder angle by default, not only personal testimony.
- Include the video URL when the goal is to drive viewing.

## Core Workflow

1. Find the source.
2. Understand the main idea and emotional angle.
3. Identify the practical takeaway.
4. Draft the requested content in the right language.
5. Add visual direction when needed.

## Voice Expectations

- Scientific but human
- Direct but kind
- Friendly but respectful
- Inspiring, not preachy
- Clear, practical, and useful
- Emotional when useful
- Expert founder, not just lived-experience storytelling

## Quick Examples

### English

`Prepare me a LinkedIn post for my latest interview in English and give me the thumbnail.`

### French

`Prépare-moi un post LinkedIn pour ma dernière interview en français, avec une miniature.`

### Latest YouTube

`Prepare me a LinkedIn post for the latest YouTube video in English and give me the thumbnail.`

### Voice Note

`I have a voice recording with a content idea. Turn it into a LinkedIn post and an Instagram caption.`
