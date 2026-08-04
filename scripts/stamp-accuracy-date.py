#!/usr/bin/env python3
"""
Stamp the `smec:last-accuracy-check` meta tag on one or more HTML
infographics with today's UTC date (or a date passed via --date).

Used by the post-merge workflow `.github/workflows/accuracy-review-merge.yml`
so that the recorded review date reflects the **merge time**, not the
time the Copilot coding agent first opened the PR. This avoids
shortening the next review cycle when a PR sits in review for days.

Behavior per file:
  - If the `<!-- smec-accuracy v1 -->` marker block already exists,
    the tag's `content="..."` attribute is updated in place.
  - Otherwise a new marker block + meta tag is injected just before
    `</head>`.
  - Files with no `</head>` and redirect stubs (`<meta http-equiv="refresh">`)
    are skipped.

Idempotent on the date value: re-running with the same date is a no-op
because the regex match returns the same content.

Stdlib only.
"""

from __future__ import annotations

import argparse
import datetime as dt
import os
import re
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MARKER = "<!-- smec-accuracy v1 -->"
META_NAME = "smec:last-accuracy-check"

HEAD_CLOSE_RE = re.compile(r"^(?P<indent>[ \t]*)</head>", re.MULTILINE)
META_REFRESH_RE = re.compile(
    r'<meta\s+http-equiv=["\']refresh["\']', re.IGNORECASE
)
ACCURACY_META_RE = re.compile(
    r'(<meta\s+[^>]*name=["\']' + re.escape(META_NAME)
    + r'["\'][^>]*content=["\'])([^"\']*)(["\'])',
    re.IGNORECASE,
)


def stamp_file(filepath: str, date_str: str) -> str:
    """Return 'updated', 'inserted', 'unchanged', 'skipped', or 'nohead'."""
    with open(filepath, encoding="utf-8", newline="") as fh:
        content = fh.read()

    if META_REFRESH_RE.search(content):
        return "skipped"

    m = ACCURACY_META_RE.search(content)
    if m:
        if m.group(2) == date_str:
            return "unchanged"
        new_content = (
            content[:m.start()]
            + m.group(1) + date_str + m.group(3)
            + content[m.end():]
        )
        with open(filepath, "w", encoding="utf-8", newline="") as fh:
            fh.write(new_content)
        return "updated"

    head_match = HEAD_CLOSE_RE.search(content)
    if not head_match:
        return "nohead"

    nl = "\r\n" if "\r\n" in content else "\n"
    indent = head_match.group("indent")
    block = (
        f"{indent}{MARKER}{nl}"
        f'{indent}<meta name="{META_NAME}" content="{date_str}">{nl}'
    )
    new_content = (
        content[:head_match.start()] + block + content[head_match.start():]
    )
    with open(filepath, "w", encoding="utf-8", newline="") as fh:
        fh.write(new_content)
    return "inserted"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "files",
        nargs="*",
        help=(
            "HTML files (repo-relative or absolute) to stamp. Non-HTML "
            "paths are silently ignored so the workflow can pass the "
            "raw list of changed files from a PR."
        ),
    )
    parser.add_argument(
        "--date",
        default=None,
        help=(
            "Date to stamp (YYYY-MM-DD). Defaults to today's UTC date."
        ),
    )
    args = parser.parse_args()

    if args.date:
        try:
            date_obj = dt.date.fromisoformat(args.date)
        except ValueError:
            print(f"ERROR: bad --date value {args.date!r}", file=sys.stderr)
            return 2
    else:
        date_obj = dt.datetime.now(dt.timezone.utc).date()
    date_str = date_obj.isoformat()

    if not args.files:
        print("No files passed; nothing to do.")
        return 0

    totals = {
        "updated": [], "inserted": [], "unchanged": [],
        "skipped": [], "nohead": [], "missing": [],
    }
    for raw in args.files:
        if not raw.lower().endswith(".html"):
            continue
        path = raw if os.path.isabs(raw) else os.path.join(REPO_ROOT, raw)
        if not os.path.isfile(path):
            totals["missing"].append(raw)
            continue
        status = stamp_file(path, date_str)
        totals[status].append(
            os.path.relpath(path, REPO_ROOT).replace(os.sep, "/")
        )

    print(f"Stamp date: {date_str}")
    for status, label in (
        ("updated", "Updated existing tag"),
        ("inserted", "Inserted new tag"),
        ("unchanged", "Already up to date"),
        ("skipped", "Skipped (redirect stub)"),
        ("nohead", "No </head> found"),
        ("missing", "File not found"),
    ):
        files = totals[status]
        print(f"{label}: {len(files)}")
        for f in files:
            print(f"  - {f}")

    if totals["nohead"]:
        print(
            "ERROR: one or more HTML files have no </head> tag.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
