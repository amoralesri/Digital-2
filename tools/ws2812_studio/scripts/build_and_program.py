#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys


def main() -> int:
    repo_root = Path(__file__).resolve().parents[3]
    package_root = repo_root / "tools" / "ws2812_studio"
    sys.path.insert(0, str(package_root))

    from ws2812_studio.services.build_program import build_and_program, program_existing_bitstream

    parser = argparse.ArgumentParser(description="Build and program WS2812 Studio animations.")
    parser.add_argument("--project", help="Path to .ws2812project")
    parser.add_argument("--repo-root", default=str(repo_root), help="Repository root")
    parser.add_argument("--no-program", action="store_true", help="Build bitstream but do not program FPGA")
    parser.add_argument("--program-only", action="store_true", help="Program the existing bitstream")
    args = parser.parse_args()

    if args.program_only:
        return program_existing_bitstream(args.repo_root)
    if not args.project:
        parser.error("--project is required unless --program-only is used")
    return build_and_program(args.project, args.repo_root, program=not args.no_program)


if __name__ == "__main__":
    raise SystemExit(main())
