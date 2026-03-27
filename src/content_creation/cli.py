from __future__ import annotations

import argparse
from pathlib import Path

from .config import STATE_PATH, ChannelConfig, load_channels
from .generator import build_assets
from .state import RuntimeState
from .utils import ensure_dir
from .writer import write_output_bundle
from .youtube import YouTubeClient


def main() -> None:
    parser = argparse.ArgumentParser(description="HopeStage weekly YouTube content pipeline")
    parser.add_argument("--channel", choices=["fr", "en", "all"], default="all")
    parser.add_argument("--force", action="store_true", help="Process latest video even if already processed")
    parser.add_argument("--check-only", action="store_true", help="Print latest video ids without generating outputs")
    args = parser.parse_args()

    channels = load_channels()
    if args.channel != "all":
        channels = [channel for channel in channels if channel.slug == args.channel]

    state = RuntimeState(STATE_PATH)
    youtube = YouTubeClient()

    for channel in channels:
        run_channel(channel, youtube, state, force=args.force, check_only=args.check_only)

    if not args.check_only:
        state.save()


def run_channel(
    channel: ChannelConfig,
    youtube: YouTubeClient,
    state: RuntimeState,
    *,
    force: bool,
    check_only: bool,
) -> None:
    latest = youtube.latest_video(channel)
    print(f"[{channel.slug}] latest={latest.video_id} title={latest.title}")
    if check_only:
        return

    if not force and state.last_video_id(channel.slug) == latest.video_id:
        print(f"[{channel.slug}] already processed, skipping")
        return

    details = youtube.video_details(latest, channel.language)
    assets = build_assets(channel, details)
    output_dir = write_output_bundle(channel, details, assets)
    thumbnail_path = output_dir / "thumbnail.jpg"
    youtube.download_thumbnail(details.thumbnail_url, thumbnail_path)
    state.mark_processed(channel.slug, latest.video_id, str(output_dir))
    print(f"[{channel.slug}] wrote {output_dir}")


if __name__ == "__main__":
    main()
