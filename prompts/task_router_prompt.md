# HopeStage Task Router Prompt

The user should be able to make short, natural requests for content creation.

## Goal

Translate a plain-language request into a concrete HopeStage content workflow.

## Input Types

- latest interview
- latest video
- latest YouTube video
- podcast episode URL
- video URL
- transcript
- voice note
- idea note

## Output Types

- LinkedIn post
- Instagram post
- X post
- newsletter
- blog post
- thumbnail direction
- image prompt

## Routing Rules

1. Determine the source first.
2. If the request mentions the latest YouTube video and no direct URL is given, use:
   - French: `https://www.youtube.com/@HopeStage-FR`
   - English: `https://www.youtube.com/@clementbaissat-HopeStage`
3. If the source is a public video or podcast, inspect it directly.
4. If the source is a voice note or transcript, identify the main idea before writing.
5. If language is not specified, use the source language.
6. If the user asks for visual output, prepare thumbnail or image guidance too.
7. Keep everything aligned with:
   - `VOICE_PROFILE.md`
   - `CONTENT_SYSTEM.md`
   - `DESIGN_GUIDELINES.md`
   - `config/founder_profile.json`

## Default Deliverable Shape

- one strong hook
- one clear angle
- one practical takeaway
- one platform-appropriate call to engagement
- visual direction if requested
