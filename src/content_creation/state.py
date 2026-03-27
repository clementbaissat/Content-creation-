from __future__ import annotations

import json
from pathlib import Path
from typing import Dict


class RuntimeState:
    def __init__(self, path: Path) -> None:
        self.path = path
        if path.exists():
            self.data: Dict[str, Dict[str, str]] = json.loads(path.read_text())
        else:
            self.data = {}

    def last_video_id(self, channel_slug: str) -> str | None:
        channel = self.data.get(channel_slug, {})
        return channel.get("last_video_id")

    def has_processed(self, channel_slug: str, video_id: str) -> bool:
        channel = self.data.get(channel_slug, {})
        processed_videos = channel.get("processed_videos", {})
        if isinstance(processed_videos, dict) and video_id in processed_videos:
            return True
        return channel.get("last_video_id") == video_id

    def mark_processed(self, channel_slug: str, video_id: str, output_dir: str) -> None:
        channel = self.data.get(channel_slug, {})
        processed_videos = channel.get("processed_videos", {})
        if not isinstance(processed_videos, dict):
            processed_videos = {}
        processed_videos[video_id] = output_dir
        channel["processed_videos"] = processed_videos
        channel["last_video_id"] = video_id
        channel["last_output_dir"] = output_dir
        self.data[channel_slug] = channel

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.data, indent=2))
