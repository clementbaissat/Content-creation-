from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import List


ROOT_DIR = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT_DIR / "config" / "channels.json"
STATE_PATH = ROOT_DIR / "data" / "runtime_state.json"


@dataclass(frozen=True)
class ChannelConfig:
    slug: str
    name: str
    language: str
    channel_id: str
    channel_url: str
    output_dir: Path


def load_channels() -> List[ChannelConfig]:
    raw = json.loads(CONFIG_PATH.read_text())
    return [
        ChannelConfig(
            slug=item["slug"],
            name=item["name"],
            language=item["language"],
            channel_id=item["channel_id"],
            channel_url=item["channel_url"],
            output_dir=ROOT_DIR / item["output_dir"],
        )
        for item in raw
    ]
