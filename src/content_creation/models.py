from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class VideoSummary:
    video_id: str
    title: str
    url: str
    published_at: str


@dataclass(frozen=True)
class TranscriptSnippet:
    start: float
    duration: float
    text: str


@dataclass(frozen=True)
class VideoDetails:
    summary: VideoSummary
    author: str
    description: str
    publish_date: str
    length_seconds: int
    thumbnail_url: str
    thumbnail_source: str
    transcript_available: bool
    transcript: List[TranscriptSnippet]


@dataclass(frozen=True)
class GuestProfile:
    name: Optional[str]
    detected_from: str


@dataclass(frozen=True)
class GeneratedAssets:
    summary_text: str
    hook_bank: List[str]
    linkedin_post: str
    linkedin_hashtags: List[str]
    x_post: str
    x_hashtags: List[str]
    instagram_post: str
    instagram_hashtags: List[str]
    image_prompt: str
    image_specs: List[str]
    thank_you_subject: str
    thank_you_email: str
    notes: List[str]


@dataclass(frozen=True)
class ContentRequest:
    request_text: str
    source_kind: str
    source_url: Optional[str]
    content_kind: str
    language: str
    outputs: List[str]
    latest_only: bool
    needs_visual: bool
    needs_thumbnail: bool
    needs_transcript: bool
    workflow_steps: List[str]
    notes: List[str]
