from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from content_creation.config import ChannelConfig
from content_creation.generator import build_assets
from content_creation.models import TranscriptSnippet, VideoDetails, VideoSummary


class GeneratorImageSpecTests(unittest.TestCase):
    def test_image_specs_include_square_instagram_and_brand_asset_rules(self) -> None:
        channel = ChannelConfig(
            slug="fr",
            name="HopeStage FR",
            language="fr",
            channel_id="channel",
            channel_url="https://example.com",
            output_dir=None,  # type: ignore[arg-type]
        )
        details = VideoDetails(
            summary=VideoSummary(
                video_id="video123",
                title="AAH et bipolarité : sécurité ou piège ?",
                url="https://www.youtube.com/watch?v=video123",
                published_at="2026-04-09T10:00:00Z",
            ),
            author="HopeStage",
            description="L'AAH peut protéger pendant une période difficile, mais elle peut aussi compliquer la reconstruction.",
            publish_date="2026-04-09",
            length_seconds=600,
            thumbnail_url="https://i.ytimg.com/vi/video123/hqdefault.jpg",
            thumbnail_source="youtube",
            transcript_available=True,
            transcript=[TranscriptSnippet(start=0.0, duration=10.0, text="L'AAH peut aider mais elle peut aussi devenir un piège.")],
        )

        assets = build_assets(channel, details)

        self.assertIn("Primary Instagram carousel format: 1:1 square, 1080x1080.", assets.image_specs)
        self.assertIn("Secondary feed format: 4:5 portrait, 1080x1350, for Instagram single-image posts and LinkedIn feed.", assets.image_specs)
        self.assertIn(
            "If branded graphics are used, source logos only from assets/brand/HopeStage logo home.png or assets/brand/Frame 10.png.",
            assets.image_specs,
        )
        self.assertIn("#bipolarite", assets.linkedin_hashtags)
        self.assertIn("#aah", assets.linkedin_hashtags)
        self.assertIn("#hopestage", assets.x_hashtags)
        self.assertIn("#psychoeducation", assets.instagram_hashtags)
        self.assertIn("#bipolarite", assets.instagram_post)


if __name__ == "__main__":
    unittest.main()
