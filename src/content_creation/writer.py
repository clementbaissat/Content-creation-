from __future__ import annotations

import json
from pathlib import Path

from .config import ChannelConfig
from .models import GeneratedAssets, VideoDetails
from .utils import ensure_dir, slugify, timestamp_label


def write_output_bundle(channel: ChannelConfig, details: VideoDetails, assets: GeneratedAssets) -> Path:
    folder_name = f"{details.publish_date[:10] or details.summary.published_at[:10]}_{slugify(details.summary.title)}"
    output_dir = ensure_dir(channel.output_dir / folder_name)
    transcript_text = "\n".join(
        f"[{timestamp_label(snippet.start)}] {snippet.text}" for snippet in details.transcript
    )
    (output_dir / "metadata.json").write_text(
        json.dumps(
            {
                "channel": channel.slug,
                "title": details.summary.title,
                "video_id": details.summary.video_id,
                "url": details.summary.url,
                "published_at": details.summary.published_at,
                "publish_date": details.publish_date,
                "author": details.author,
                "length_seconds": details.length_seconds,
                "thumbnail_url": details.thumbnail_url,
            },
            indent=2,
        )
    )
    (output_dir / "description.txt").write_text(details.description.strip() + "\n")
    (output_dir / "transcript.txt").write_text(transcript_text or "Transcript unavailable.\n")
    (output_dir / "summary.txt").write_text(assets.summary_text + "\n")
    (output_dir / "hooks.txt").write_text("\n\n".join(assets.hook_bank) + "\n")
    (output_dir / "linkedin_post.txt").write_text(assets.linkedin_post + "\n")
    (output_dir / "thank_you_email.txt").write_text(
        f"Subject: {assets.thank_you_subject}\n\n{assets.thank_you_email}\n"
    )
    (output_dir / "notes.txt").write_text("\n".join(assets.notes) + "\n")
    (output_dir / "bundle.txt").write_text(build_bundle(channel, details, assets))
    return output_dir


def build_bundle(channel: ChannelConfig, details: VideoDetails, assets: GeneratedAssets) -> str:
    return "\n".join(
        [
            f"Channel: {channel.name}",
            f"Language: {channel.language}",
            f"Title: {details.summary.title}",
            f"URL: {details.summary.url}",
            f"Published: {details.publish_date or details.summary.published_at}",
            f"Thumbnail: {details.thumbnail_url}",
            "",
            "SUMMARY",
            assets.summary_text,
            "",
            "HOOK OPTIONS",
            *[f"{index + 1}. {hook}" for index, hook in enumerate(assets.hook_bank)],
            "",
            "LINKEDIN POST",
            assets.linkedin_post,
            "",
            "THANK-YOU EMAIL",
            f"Subject: {assets.thank_you_subject}",
            assets.thank_you_email,
            "",
            "NOTES",
            *[f"- {note}" for note in assets.notes],
            "",
        ]
    )
