#!/usr/bin/env python3
"""
Ensures each HTML infographic has a favicon <link> tag pointing at the
shared site favicon at /favicon.svg.

Pattern mirrors the other ensure-* scripts:
  - idempotent via marker comment (<!-- smec-favicon v1 -->)
  - skips redirect stubs (<meta http-equiv="refresh">)
  - skips the root index.html library landing page
  - supports --check

The favicon link uses an absolute path (/favicon.svg) so it resolves
from the site root regardless of the infographic's folder depth.

Usage:
    python3 scripts/ensure-favicon.py
    python3 scripts/ensure-favicon.py --check
"""

from __future__ import annotations

import argparse
import os
import re
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_INDEX = os.path.join(REPO_ROOT, "index.html")

MARKER = "<!-- smec-favicon v1 -->"
FAVICON_LINK = '<link rel="icon" type="image/svg+xml" href="/favicon.svg">'

HEAD_CLOSE_RE = re.compile(r"^(?P<indent>[ \t]*)</head>", re.MULTILINE)
META_REFRESH_RE = re.compile(
    r'<meta\s+http-equiv=["\']refresh["\']', re.IGNORECASE
)
EXISTING_FAVICON_RE = re.compile(
    r'<link\s+[^>]*rel=["\'](?:shortcut\s+)?icon["\']', re.IGNORECASE
)

SKIP_DIRS = {".git", "node_modules", ".github", "reports"}


def iter_html_files(root: str):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fname in filenames:
            if fname.lower().endswith(".html"):
                yield os.path.join(dirpath, fname)


def ensure_favicon(filepath: str, check_only: bool = False) -> str:
    with open(filepath, encoding="utf-8", newline="") as fh:
        content = fh.read()

    if META_REFRESH_RE.search(content):
        return "skipped"
    if MARKER in content or EXISTING_FAVICON_RE.search(content):
        # If the page already carries a <link rel=icon>, respect it and
        # just stamp the marker on a future run — but don't rewrite an
        # existing one. We simply treat "present" == done.
        return "present"

    match = HEAD_CLOSE_RE.search(content)
    if not match:
        return "nohead"
    if check_only:
        return "missing"

    nl = "\r\n" if "\r\n" in content else "\n"
    indent = match.group("indent")
    insertion = f"{indent}{MARKER}{nl}{indent}{FAVICON_LINK}{nl}"
    new_content = content[: match.start()] + insertion + content[match.start():]

    with open(filepath, "w", encoding="utf-8", newline="") as fh:
        fh.write(new_content)
    return "added"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    totals: dict[str, list[str]] = {
        "added": [],
        "missing": [],
        "present": [],
        "skipped": [],
        "nohead": [],
    }
    for filepath in sorted(iter_html_files(REPO_ROOT)):
        if os.path.abspath(filepath) == os.path.abspath(ROOT_INDEX):
            totals["skipped"].append(
                os.path.relpath(filepath, REPO_ROOT).replace(os.sep, "/")
            )
            continue
        rel = os.path.relpath(filepath, REPO_ROOT).replace(os.sep, "/")
        status = ensure_favicon(filepath, check_only=args.check)
        totals[status].append(rel)

    for status, label in (
        ("added", "Added favicon link"),
        ("missing", "Missing favicon link"),
        ("present", "Already present"),
        ("skipped", "Skipped"),
        ("nohead", "No </head> found"),
    ):
        files = totals[status]
        print(f"{label}: {len(files)}")
        for f in files:
            print(f"  - {f}")

    exit_code = 0
    if totals["nohead"]:
        print(
            "ERROR: one or more HTML files have no </head> tag.",
            file=sys.stderr,
        )
        exit_code = 1
    if args.check and totals["missing"]:
        print(
            "ERROR: one or more HTML files are missing the favicon link. "
            "Run `python3 scripts/ensure-favicon.py` to add it.",
            file=sys.stderr,
        )
        exit_code = 1
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
