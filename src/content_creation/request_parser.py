from __future__ import annotations

import json
import re
from typing import List, Optional

from .models import ContentRequest
from .utils import compact_whitespace


URL_PATTERN = re.compile(r"https?://\S+")


def parse_content_request(request_text: str) -> ContentRequest:
    text = compact_whitespace(request_text)
    lower = text.lower()
    source_url = extract_url(text)
    source_kind = detect_source_kind(lower, source_url)
    content_kind = detect_content_kind(lower, source_kind)
    language = detect_language(lower)
    outputs = detect_outputs(lower)
    latest_only = contains_any(lower, ["latest", "dernier", "derniere", "dernière", "newest", "most recent"])
    needs_thumbnail = "thumbnail" in outputs
    needs_visual = needs_thumbnail or "image_prompt" in outputs or "social_visual" in outputs
    needs_transcript = source_kind in {"latest_content", "video_url", "podcast_url"} or contains_any(
        lower, ["transcript", "audio", "voice recording", "voice note", "vocal", "interview"]
    )
    workflow_steps = build_workflow_steps(source_kind, outputs, needs_transcript, needs_visual)
    notes = build_notes(source_kind, language, outputs, source_url)
    return ContentRequest(
        request_text=text,
        source_kind=source_kind,
        source_url=source_url,
        content_kind=content_kind,
        language=language,
        outputs=outputs,
        latest_only=latest_only,
        needs_visual=needs_visual,
        needs_thumbnail=needs_thumbnail,
        needs_transcript=needs_transcript,
        workflow_steps=workflow_steps,
        notes=notes,
    )


def extract_url(text: str) -> Optional[str]:
    match = URL_PATTERN.search(text)
    if not match:
        return None
    return match.group(0).rstrip(").,]")


def detect_source_kind(lower: str, source_url: Optional[str]) -> str:
    if source_url:
        if any(host in source_url for host in ["youtube.com", "youtu.be", "video.hopestage.com"]):
            return "video_url"
        if "podcast.hopestage.com" in source_url or "spotify.com" in source_url or "podcasts.apple.com" in source_url:
            return "podcast_url"
        return "url"
    if contains_any(lower, ["voice recording", "voice note", "audio note", "vocal", "memo vocal"]):
        return "voice_note"
    if contains_any(lower, ["latest interview", "latest video", "latest episode", "derniere interview", "dernière interview"]):
        return "latest_content"
    if contains_any(lower, ["interview", "podcast", "video", "episode"]):
        return "content_reference"
    return "idea_note"


def detect_content_kind(lower: str, source_kind: str) -> str:
    if contains_any(lower, ["interview", "entretien"]):
        return "interview"
    if contains_any(lower, ["podcast", "episode"]):
        return "podcast_episode"
    if contains_any(lower, ["video", "youtube"]):
        return "video"
    if source_kind == "voice_note":
        return "voice_idea"
    return "general_content"


def detect_language(lower: str) -> str:
    if contains_any(lower, [" in french", " en francais", " en français", "french", "francais", "français"]):
        return "fr"
    if contains_any(lower, [" in english", "english", "anglais"]):
        return "en"
    return "source_default"


def detect_outputs(lower: str) -> List[str]:
    outputs: List[str] = []
    if "linkedin" in lower:
        outputs.append("linkedin_post")
    if "instagram" in lower:
        outputs.append("instagram_post")
    if re.search(r"\bx\b|twitter", lower):
        outputs.append("x_post")
    if contains_any(lower, ["newsletter", "email"]):
        outputs.append("newsletter")
    if contains_any(lower, ["blog", "article"]):
        outputs.append("blog_post")
    if contains_any(lower, ["thumbnail", "miniature"]):
        outputs.append("thumbnail")
    if contains_any(lower, ["image", "visual", "visuel", "illustration"]):
        outputs.append("image_prompt")
        outputs.append("social_visual")
    if not outputs:
        outputs.append("linkedin_post")
    return dedupe(outputs)


def build_workflow_steps(
    source_kind: str,
    outputs: List[str],
    needs_transcript: bool,
    needs_visual: bool,
) -> List[str]:
    steps: List[str] = []
    if source_kind in {"latest_content", "video_url", "podcast_url", "content_reference"}:
        steps.append("Find the source content.")
    if needs_transcript:
        steps.append("Extract or review the transcript, description, or notes.")
    steps.append("Identify the main idea, emotional angle, and practical takeaway.")
    steps.append("Draft the requested social copy in the right HopeStage voice.")
    if needs_visual:
        steps.append("Prepare the visual direction, thumbnail guidance, or image prompt.")
    steps.append("Return a clean deliverable set ready to publish or review.")
    return steps


def build_notes(source_kind: str, language: str, outputs: List[str], source_url: Optional[str]) -> List[str]:
    notes: List[str] = []
    if language == "source_default":
        notes.append("If language is not specified, default to the source language.")
    if source_kind == "voice_note":
        notes.append("Voice notes should be turned into a clarified content angle before drafting.")
    if "linkedin_post" in outputs:
        notes.append("LinkedIn should favor clarity, credibility, and practical insight over hype.")
    if "instagram_post" in outputs:
        notes.append("Instagram should be more concise and visually legible.")
    if source_url:
        notes.append("A source URL is available and should be used directly.")
    return notes


def contains_any(text: str, needles: List[str]) -> bool:
    return any(needle in text for needle in needles)


def dedupe(items: List[str]) -> List[str]:
    seen = set()
    result = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        result.append(item)
    return result


def request_to_json(request: ContentRequest) -> str:
    return json.dumps(
        {
            "request_text": request.request_text,
            "source_kind": request.source_kind,
            "source_url": request.source_url,
            "content_kind": request.content_kind,
            "language": request.language,
            "outputs": request.outputs,
            "latest_only": request.latest_only,
            "needs_visual": request.needs_visual,
            "needs_thumbnail": request.needs_thumbnail,
            "needs_transcript": request.needs_transcript,
            "workflow_steps": request.workflow_steps,
            "notes": request.notes,
        },
        indent=2,
    )
