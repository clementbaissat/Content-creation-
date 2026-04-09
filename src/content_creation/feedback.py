from __future__ import annotations

from .config import CANONICAL_BRAND_ASSETS


def social_visual_feedback_specs() -> list[str]:
    return [
        "Primary Instagram carousel format: 1:1 square, 1080x1080.",
        "Secondary feed format: 4:5 portrait, 1080x1350, for Instagram single-image posts and LinkedIn feed.",
        "Third format: 16:9 landscape, 1600x900, for X and wider social previews.",
        "Keep logos, kicker text, and CTA bars inside a generous square safe zone.",
        (
            "If branded graphics are used, source logos only from "
            f"{CANONICAL_BRAND_ASSETS['horizontal_wordmark'].relative_to(CANONICAL_BRAND_ASSETS['horizontal_wordmark'].parents[2])} "
            f"or {CANONICAL_BRAND_ASSETS['pale_background_lockup'].relative_to(CANONICAL_BRAND_ASSETS['pale_background_lockup'].parents[2])}."
        ),
        "Do not rely on ad hoc desktop logo exports when canonical repo brand assets exist.",
        "No text baked into photographic images unless the deliverable is explicitly a text-led graphic.",
    ]
