#!/usr/bin/env python3
"""Copy the finished front page to the make.fun output directory.

Standard library only. No network, no clock, no randomness.

Usage:
    MAKEFUN_OUTPUT_DIR=/output python3 main.py

Writes $MAKEFUN_OUTPUT_DIR/entry.png (default /output).
"""
import os
import shutil
from pathlib import Path

BASE = Path(__file__).resolve().parent
SRC = BASE / "entry.png"


def main():
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    dst = out_dir / "entry.png"
    shutil.copyfile(SRC, dst)
    print(f"wrote {dst} ({dst.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
