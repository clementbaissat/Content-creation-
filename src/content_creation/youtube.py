from __future__ import annotations

import html
import re
import xml.etree.ElementTree as ET
from typing import List

import requests
from youtube_transcript_api import YouTubeTranscriptApi

from .config import ChannelConfig
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

    def latest_video(self, channel: ChannelConfig) -> VideoSummary:
        response = self.session.get(
            f"https://www.youtube.com/feeds/videos.xml?channel_id={channel.channel_id}",
            timeout=30,
        )
        response.raise_for_status()
        root = ET.fromstring(response.text)
        entry = root.find("atom:entry", RSS_NS)
        if entry is None:
            raise RuntimeError(f"No videos found for {channel.name}")
        video_id = entry.findtext("yt:videoId", namespaces=RSS_NS)
        title = entry.findtext("atom:title", namespaces=RSS_NS)
        link = entry.find("atom:link", RSS_NS)
        published = entry.findtext("atom:published", namespaces=RSS_NS)
        if not video_id or not title or link is None:
            raise RuntimeError(f"Incomplete RSS data for {channel.name}")
        return VideoSummary(
            video_id=video_id,
            title=title,
            url=link.attrib["href"],
            published_at=published or "",
        )

    def video_details(self, summary: VideoSummary, language: str) -> VideoDetails:
        response = self.session.get(summary.url, timeout=30)
        response.raise_for_status()
        page = response.text
        description = self._extract_json_string(page, "shortDescription")
        author = self._extract_json_string(page, "author")
        publish_date = self._extract_json_string(page, "publishDate")
        length_seconds_raw = self._extract_json_string(page, "lengthSeconds")
        transcript = self._fetch_transcript(summary.video_id, language)
        return VideoDetails(
            summary=summary,
            author=author,
            description=description,
            publish_date=publish_date,
            length_seconds=int(length_seconds_raw or "0"),
            thumbnail_url=f"https://i.ytimg.com/vi/{summary.video_id}/hqdefault.jpg",
            transcript_available=bool(transcript),
            transcript=transcript,
        )

    def download_thumbnail(self, url: str, output_path) -> None:
        response = self.session.get(url, timeout=30)
        response.raise_for_status()
        output_path.write_bytes(response.content)

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
