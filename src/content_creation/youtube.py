from __future__ import annotations

import html
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List

import requests
from youtube_transcript_api import YouTubeTranscriptApi

from .config import ChannelConfig, THUMBNAIL_OVERRIDE_DIR
from .models import TranscriptSnippet, VideoDetails, VideoSummary


RSS_NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "yt": "http://www.youtube.com/xml/schemas/2015",
}


class YouTubeClient:
    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Mozilla/5.0"})
        self.transcript_api = YouTubeTranscriptApi()

    def latest_videos(self, channel: ChannelConfig, limit: int = 1) -> List[VideoSummary]:
        response = self.session.get(
            f"https://www.youtube.com/feeds/videos.xml?channel_id={channel.channel_id}",
            timeout=30,
        )
        response.raise_for_status()
        root = ET.fromstring(response.text)
        entries = root.findall("atom:entry", RSS_NS)
        if not entries:
            raise RuntimeError(f"No videos found for {channel.name}")
        videos: List[VideoSummary] = []
        for entry in entries[:limit]:
            video_id = entry.findtext("yt:videoId", namespaces=RSS_NS)
            title = entry.findtext("atom:title", namespaces=RSS_NS)
            link = entry.find("atom:link", RSS_NS)
            published = entry.findtext("atom:published", namespaces=RSS_NS)
            if not video_id or not title or link is None:
                continue
            videos.append(
                VideoSummary(
                    video_id=video_id,
                    title=title,
                    url=link.attrib["href"],
                    published_at=published or "",
                )
            )
        if not videos:
            raise RuntimeError(f"Incomplete RSS data for {channel.name}")
        return videos

    def latest_video(self, channel: ChannelConfig) -> VideoSummary:
        return self.latest_videos(channel, limit=1)[0]

    def video_details(self, summary: VideoSummary, language: str) -> VideoDetails:
        response = self.session.get(summary.url, timeout=30)
        response.raise_for_status()
        page = response.text
        description = self._extract_json_string(page, "shortDescription")
        author = self._extract_json_string(page, "author")
        publish_date = self._extract_json_string(page, "publishDate")
        length_seconds_raw = self._extract_json_string(page, "lengthSeconds")
        thumbnail_url, thumbnail_source = self._resolve_thumbnail(summary.video_id, page)
        transcript = self._fetch_transcript(summary.video_id, language)
        return VideoDetails(
            summary=summary,
            author=author,
            description=description,
            publish_date=publish_date,
            length_seconds=int(length_seconds_raw or "0"),
            thumbnail_url=thumbnail_url,
            thumbnail_source=thumbnail_source,
            transcript_available=bool(transcript),
            transcript=transcript,
        )

    def download_thumbnail(self, url: str, output_path) -> None:
        source_path = Path(url)
        if source_path.exists():
            output_path.write_bytes(source_path.read_bytes())
            return

        response = self.session.get(url, timeout=30)
        response.raise_for_status()
        output_path.write_bytes(response.content)

    def _resolve_thumbnail(self, video_id: str, page: str) -> tuple[str, str]:
        override = self._thumbnail_override(video_id)
        if override is not None:
            return str(override), "manual_override"

        og_image = self._extract_og_image(page)
        if og_image:
            return og_image, "youtube_og_image"

        candidates = [
            f"https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg",
            f"https://i.ytimg.com/vi/{video_id}/sddefault.jpg",
            f"https://i.ytimg.com/vi/{video_id}/hq720.jpg",
            f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg",
            f"https://i.ytimg.com/vi/{video_id}/mqdefault.jpg",
        ]
        for candidate in candidates:
            if self._thumbnail_available(candidate):
                return candidate, "youtube_fallback"
        return f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg", "youtube_default"

    def _fetch_transcript(self, video_id: str, language: str) -> List[TranscriptSnippet]:
        preferred_languages = [language, "en", "fr"]
        try:
            transcript = self.transcript_api.fetch(video_id, languages=preferred_languages)
        except Exception:
            return []
        return [
            TranscriptSnippet(
                start=float(snippet.start),
                duration=float(snippet.duration),
                text=snippet.text.strip(),
            )
            for snippet in transcript.snippets
            if snippet.text.strip()
        ]

    @staticmethod
    def _extract_og_image(page: str) -> str:
        match = re.search(r'<meta property="og:image" content="([^"]+)"', page)
        if not match:
            return ""
        return html.unescape(match.group(1))

    def _thumbnail_available(self, url: str) -> bool:
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
        except Exception:
            return False
        content_type = response.headers.get("Content-Type", "")
        return content_type.startswith("image/")

    @staticmethod
    def _thumbnail_override(video_id: str) -> Path | None:
        for suffix in (".png", ".jpg", ".jpeg", ".webp"):
            candidate = THUMBNAIL_OVERRIDE_DIR / f"{video_id}{suffix}"
            if candidate.exists():
                return candidate
        return None

    @staticmethod
    def _extract_json_string(page: str, key: str) -> str:
        match = re.search(rf'"{re.escape(key)}":"((?:\\.|[^"])*)"', page)
        if not match:
            return ""
        raw = match.group(1)
        try:
            decoded = __import__("json").loads(f'"{raw}"')
        except Exception:
            decoded = raw
        return html.unescape(decoded)
