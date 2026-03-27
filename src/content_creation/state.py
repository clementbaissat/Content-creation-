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

    def mark_processed(self, channel_slug: str, video_id: str, output_dir: str) -> None:
        self.data[channel_slug] = {
            "last_video_id": video_id,
            "last_output_dir": output_dir,
        }

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.data, indent=2))
