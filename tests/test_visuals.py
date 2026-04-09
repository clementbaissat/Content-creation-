from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from content_creation.visuals import render_social_images


class VisualRenderTests(unittest.TestCase):
    def test_render_social_images_writes_square_portrait_and_landscape_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            thumbnail_path = tmp_path / "thumbnail.jpg"
            Image.new("RGB", (1280, 720), color="#154545").save(thumbnail_path)

            render_social_images(thumbnail_path, tmp_path)

            self.assertTrue((tmp_path / "social_image_1x1.jpg").exists())
            self.assertTrue((tmp_path / "social_image_4x5.jpg").exists())
            self.assertTrue((tmp_path / "social_image_16x9.jpg").exists())


if __name__ == "__main__":
    unittest.main()
