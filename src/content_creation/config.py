from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List


ROOT_DIR = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT_DIR / "config" / "channels.json"
FOUNDER_PROFILE_PATH = ROOT_DIR / "config" / "founder_profile.json"
STATE_PATH = ROOT_DIR / "data" / "runtime_state.json"
THUMBNAIL_OVERRIDE_DIR = ROOT_DIR / "thumbnail_overrides"
BRAND_ASSET_DIR = ROOT_DIR / "assets" / "brand"
CANONICAL_BRAND_ASSETS = {
    "pale_background_lockup": BRAND_ASSET_DIR / "Frame 10.png",
    "horizontal_wordmark": BRAND_ASSET_DIR / "HopeStage logo home.png",
    "square_dark_lockup": BRAND_ASSET_DIR / "HopeStage google logo.png",
    "icon_mark": BRAND_ASSET_DIR / "hopestage 256.png",
}


@dataclass(frozen=True)
class ChannelConfig:
    slug: str
    name: str
    language: str
    channel_id: str
    channel_url: str
    output_dir: Path


@dataclass(frozen=True)
class FounderProfile:
    founder_name: str
    organization: str
    intro: str
    age: int
    stable_years: int
    lived_experience: List[str]
    expertise: List[str]
    worldview: List[str]
    references: Dict[str, List[str]]
    voice_traits: List[str]
    trust_builders: List[str]
    avoid: List[str]
    required_terms: List[str]
    blocked_terms: List[str]
    signature_angles: List[str]
    default_structure: List[str]
    visual_direction: str
    design_palette: Dict[str, str]
    imagery_rules: List[str]


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


def load_founder_profile() -> FounderProfile:
    raw = json.loads(FOUNDER_PROFILE_PATH.read_text())
    identity = raw["identity"]
    voice = raw["voice"]
    content = raw["content"]
    design = raw["design"]
    return FounderProfile(
        founder_name=identity["founder_name"],
        organization=identity["organization"],
        intro=identity["intro"],
        age=identity["age"],
        stable_years=identity["stable_years"],
        lived_experience=raw["lived_experience"],
        expertise=raw["expertise"],
        worldview=raw["worldview"],
        references=raw["references"],
        voice_traits=voice["core_traits"],
        trust_builders=voice["trust_builders"],
        avoid=voice["avoid"],
        required_terms=voice["required_terms"],
        blocked_terms=voice["blocked_terms"],
        signature_angles=content["signature_angles"],
        default_structure=content["default_structure"],
        visual_direction=design["visual_direction"],
        design_palette=design["palette"],
        imagery_rules=design["imagery_rules"],
    )
