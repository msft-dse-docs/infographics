#!/usr/bin/env python3
"""
Stamp changed HTML infographics with a validation date and ensure every page
shows that date in a subtle fixed label.

With file arguments, each applicable file is stamped with today's UTC date
(or --date) and its visible label is synchronized. With no file arguments,
all infographic pages are synchronized without changing an existing date.

Use --check to verify that every applicable page has matching metadata and
visible chrome without modifying files. Redirect stubs and the root index are
always skipped.
"""

from __future__ import annotations

import argparse
import datetime as dt
import os
import re
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_INDEX = os.path.join(REPO_ROOT, "index.html")

META_MARKER = "<!-- smec-accuracy v1 -->"
META_NAME = "smec:last-accuracy-check"
STYLE_MARKER = "/* smec-validation-date v1 */"
BADGE_MARKER = 'data-smec-validation-date="v1"'

VALIDATION_STYLE = """<style>/* smec-validation-date v1 */
.smec-validation-date { position: fixed; right: 16px; bottom: 16px;
  z-index: 9998; box-sizing: border-box; padding: 5px 9px;
  border: 1px solid rgba(107, 114, 128, 0.22); border-radius: 4px;
  background: rgba(255, 255, 255, 0.86) !important;
  color: #4b5563 !important; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  backdrop-filter: blur(6px); pointer-events: none;
  font: 500 11px/1.2 'Segoe UI', sans-serif !important;
  letter-spacing: 0; white-space: nowrap; }
@media (max-width: 600px) {
  .smec-validation-date { right: 12px; bottom: 12px; }
}
</style>"""

HEAD_CLOSE_RE = re.compile(r"^(?P<indent>[ \t]*)</head>", re.MULTILINE)
BODY_OPEN_RE = re.compile(r"(<body\b[^>]*>)", re.IGNORECASE)
META_REFRESH_RE = re.compile(
    r'<meta\s+http-equiv=["\']refresh["\']', re.IGNORECASE
)
ACCURACY_META_RE = re.compile(
    r'(<meta\s+[^>]*name=["\']' + re.escape(META_NAME)
    + r'["\'][^>]*content=["\'])([^"\']*)(["\'])',
    re.IGNORECASE,
)
BADGE_RE = re.compile(
    r'<time\b[^>]*\bdata-smec-validation-date\s*=\s*["\']v1["\'][^>]*>'
    r'.*?</time>',
    re.IGNORECASE | re.DOTALL,
)

SKIP_DIRS = {".git", "node_modules", ".github", "reports"}


def iter_html_files(root: str):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for filename in filenames:
            if filename.lower().endswith(".html"):
                yield os.path.join(dirpath, filename)


def _badge(date_str: str) -> str:
    return (
        f'<time class="smec-validation-date" datetime="{date_str}" '
        f'{BADGE_MARKER}>Valid as of {date_str}</time>'
    )


def sync_file(
    filepath: str,
    stamp_date: str | None,
    fallback_date: str,
    check_only: bool = False,
) -> str:
    """Synchronize one page and return its status."""
    if os.path.abspath(filepath) == os.path.abspath(ROOT_INDEX):
        return "skipped"

    with open(filepath, encoding="utf-8", newline="") as file_handle:
        content = file_handle.read()

    if META_REFRESH_RE.search(content):
        return "skipped"

    meta_match = ACCURACY_META_RE.search(content)
    date_str = stamp_date or (
        meta_match.group(2).strip() if meta_match else fallback_date
    )
    expected_badge = _badge(date_str)
    badge_match = BADGE_RE.search(content)
    is_current = (
        META_MARKER in content
        and meta_match is not None
        and meta_match.group(2).strip() == date_str
        and STYLE_MARKER in content
        and badge_match is not None
        and badge_match.group(0) == expected_badge
    )
    if is_current:
        return "present"
    if check_only:
        return "missing"

    head_match = HEAD_CLOSE_RE.search(content)
    if not head_match:
        return "nohead"
    body_match = BODY_OPEN_RE.search(content)
    if not body_match:
        return "nobody"

    newline = "\r\n" if "\r\n" in content else "\n"
    new_content = content

    if meta_match:
        new_content = (
            new_content[:meta_match.start()]
            + meta_match.group(1) + date_str + meta_match.group(3)
            + new_content[meta_match.end():]
        )
    else:
        head_match = HEAD_CLOSE_RE.search(new_content)
        indent = head_match.group("indent")
        meta_block = (
            f"{indent}{META_MARKER}{newline}"
            f'{indent}<meta name="{META_NAME}" content="{date_str}">{newline}'
        )
        new_content = (
            new_content[:head_match.start()]
            + meta_block
            + new_content[head_match.start():]
        )

    if STYLE_MARKER not in new_content:
        head_match = HEAD_CLOSE_RE.search(new_content)
        indent = head_match.group("indent")
        style_block = newline.join(
            indent + line if line else line
            for line in VALIDATION_STYLE.splitlines()
        ) + newline
        new_content = (
            new_content[:head_match.start()]
            + style_block
            + new_content[head_match.start():]
        )

    badge_match = BADGE_RE.search(new_content)
    if badge_match:
        new_content = (
            new_content[:badge_match.start()]
            + expected_badge
            + new_content[badge_match.end():]
        )
    else:
        body_match = BODY_OPEN_RE.search(new_content)
        new_content = (
            new_content[:body_match.end()]
            + newline + expected_badge + newline
            + new_content[body_match.end():]
        )

    with open(filepath, "w", encoding="utf-8", newline="") as file_handle:
        file_handle.write(new_content)
    return "updated" if meta_match else "inserted"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "files",
        nargs="*",
        help=(
            "HTML files to stamp. With no files, synchronize all pages while "
            "preserving existing dates."
        ),
    )
    parser.add_argument(
        "--date",
        default=None,
        help="Date to stamp (YYYY-MM-DD). Defaults to today's UTC date.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify metadata and visible labels without modifying files.",
    )
    args = parser.parse_args()

    try:
        selected_date = (
            dt.date.fromisoformat(args.date)
            if args.date
            else dt.datetime.now(dt.timezone.utc).date()
        )
    except ValueError:
        print(f"ERROR: bad --date value {args.date!r}", file=sys.stderr)
        return 2
    today = selected_date.isoformat()

    if args.files:
        candidates = []
        for raw_path in args.files:
            if not raw_path.lower().endswith(".html"):
                continue
            filepath = (
                raw_path if os.path.isabs(raw_path)
                else os.path.join(REPO_ROOT, raw_path)
            )
            candidates.append((raw_path, filepath))
        stamp_date = today
    else:
        candidates = [
            (os.path.relpath(path, REPO_ROOT), path)
            for path in sorted(iter_html_files(REPO_ROOT))
        ]
        stamp_date = None

    totals = {
        "updated": [], "inserted": [], "present": [], "missing": [],
        "skipped": [], "nohead": [], "nobody": [], "notfound": [],
    }
    for display_path, filepath in candidates:
        rel = os.path.relpath(filepath, REPO_ROOT).replace(os.sep, "/")
        if not os.path.isfile(filepath):
            totals["notfound"].append(display_path)
            continue
        status = sync_file(
            filepath, stamp_date, today, check_only=args.check
        )
        totals[status].append(rel)

    for status, label in (
        ("updated", "Updated"),
        ("inserted", "Inserted date"),
        ("present", "Already current"),
        ("missing", "Missing or mismatched"),
        ("skipped", "Skipped (redirect or root index)"),
        ("nohead", "No </head> found"),
        ("nobody", "No <body> found"),
        ("notfound", "File not found"),
    ):
        print(f"{label}: {len(totals[status])}")
        for path in totals[status]:
            print(f"  - {path}")

    failures = totals["nohead"] + totals["nobody"] + totals["notfound"]
    if args.check:
        failures += totals["missing"]
    if failures:
        print(
            "ERROR: validation-date chrome is incomplete.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
