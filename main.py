#!/usr/bin/env python3
"""Entry point for the make.fun news-image-20261118 v3 entry.

Copies the pre-rendered front page (entry.png, produced by draw.py)
into the directory the harness asks for. Standard library only.
"""
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    out = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if not out:
        print("MAKEFUN_OUTPUT_DIR is not set", file=sys.stderr)
        return 1
    os.makedirs(out, exist_ok=True)
    shutil.copyfile(os.path.join(HERE, "entry.png"),
                    os.path.join(out, "entry.png"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
