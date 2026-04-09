from __future__ import annotations

import argparse
import sys

from .request_parser import parse_content_request, request_to_json


def main() -> None:
    parser = argparse.ArgumentParser(description="Parse a simple HopeStage content request.")
    parser.add_argument("--request", help="Natural-language content request. If omitted, stdin is used.")
    args = parser.parse_args()

    request_text = args.request or sys.stdin.read().strip()
    if not request_text:
        raise SystemExit("A request is required via --request or stdin.")

    parsed = parse_content_request(request_text)
    print(request_to_json(parsed))


if __name__ == "__main__":
    main()
