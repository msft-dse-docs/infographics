#!/usr/bin/env python3
"""
Ensures each HTML infographic has basic SEO / social metadata in its
<head>: description, Open Graph tags, and Twitter card tags. The page
title is used to derive a default description and og:title.

Pattern mirrors ensure-tracking.py / ensure-back-button.py:
  - idempotent via a marker comment (<!-- smec-meta v1 -->)
  - skips redirect stubs (<meta http-equiv="refresh">)
  - skips the root index.html library landing page
  - supports --check (exit 1 if any page is missing the marker; no writes)

Only the marker block is injected. Existing <meta name="description">,
Open Graph, or Twitter tags on the page are left untouched; on subsequent
runs the marker's presence makes the script a no-op.

Usage:
    python3 scripts/ensure-meta.py          # add where missing
    python3 scripts/ensure-meta.py --check  # fail if any page is missing
"""

from __future__ import annotations

import argparse
import html
import os
import re
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_INDEX = os.path.join(REPO_ROOT, "index.html")

MARKER = "<!-- smec-meta v1 -->"
SITE_BASE_URL = "https://sme-c-infographics.github.io"

TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)
HEAD_CLOSE_RE = re.compile(r"^(?P<indent>[ \t]*)</head>", re.MULTILINE)
META_REFRESH_RE = re.compile(
    r'<meta\s+http-equiv=["\']refresh["\']', re.IGNORECASE
)
META_DESC_RE = re.compile(
    r'<meta\s+[^>]*name=["\']description["\']', re.IGNORECASE
)
OG_TITLE_RE = re.compile(
    r'<meta\s+[^>]*property=["\']og:title["\']', re.IGNORECASE
)
OG_DESC_RE = re.compile(
    r'<meta\s+[^>]*property=["\']og:description["\']', re.IGNORECASE
)
OG_TYPE_RE = re.compile(
    r'<meta\s+[^>]*property=["\']og:type["\']', re.IGNORECASE
)
OG_URL_RE = re.compile(
    r'<meta\s+[^>]*property=["\']og:url["\']', re.IGNORECASE
)
TWITTER_CARD_RE = re.compile(
    r'<meta\s+[^>]*name=["\']twitter:card["\']', re.IGNORECASE
)

SKIP_DIRS = {".git", "node_modules", ".github", "reports"}


def iter_html_files(root: str):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fname in filenames:
            if fname.lower().endswith(".html"):
                yield os.path.join(dirpath, fname)


def extract_title(content: str, fallback: str) -> str:
    match = TITLE_RE.search(content)
    if not match:
        return fallback
    title = html.unescape(match.group(1))
    return re.sub(r"\s+", " ", title).strip() or fallback


def derive_description(title: str) -> str:
    # The authored infographics don't currently carry a prose abstract we
    # can reliably extract, so use the title as a safe, stable description
    # fallback. Human editors can always add a bespoke <meta name=description>
    # above the marker — the script will then leave it alone.
    return (
        f"{title} — an interactive infographic from the SME&C Infographic Hub."
    )


def canonical_url(rel_path: str) -> str:
    return f"{SITE_BASE_URL}/{rel_path.replace(os.sep, '/')}"


def build_block(
    content: str, title: str, description: str, page_url: str, indent: str
) -> str:
    """Build the meta block, skipping tags the page already has."""
    nl = "\r\n" if "\r\n" in content else "\n"
    lines: list[str] = [f"{indent}{MARKER}"]

    # Escape quotes/HTML specials in content values.
    esc_title = html.escape(title, quote=True)
    esc_desc = html.escape(description, quote=True)
    esc_url = html.escape(page_url, quote=True)

    if not META_DESC_RE.search(content):
        lines.append(
            f'{indent}<meta name="description" content="{esc_desc}">'
        )
    if not OG_TITLE_RE.search(content):
        lines.append(
            f'{indent}<meta property="og:title" content="{esc_title}">'
        )
    if not OG_DESC_RE.search(content):
        lines.append(
            f'{indent}<meta property="og:description" content="{esc_desc}">'
        )
    if not OG_TYPE_RE.search(content):
        lines.append(f'{indent}<meta property="og:type" content="website">')
    if not OG_URL_RE.search(content):
        lines.append(
            f'{indent}<meta property="og:url" content="{esc_url}">'
        )
    if not TWITTER_CARD_RE.search(content):
        lines.append(
            f'{indent}<meta name="twitter:card" content="summary_large_image">'
        )
        lines.append(
            f'{indent}<meta name="twitter:title" content="{esc_title}">'
        )
        lines.append(
            f'{indent}<meta name="twitter:description" content="{esc_desc}">'
        )

    # Even when every tag already exists we still emit the marker so
    # subsequent runs are O(1).
    return nl.join(lines) + nl


def ensure_meta(filepath: str, check_only: bool = False) -> str:
    """Return 'added', 'missing', 'present', 'skipped', or 'nohead'."""
    with open(filepath, encoding="utf-8", newline="") as fh:
        content = fh.read()

    if META_REFRESH_RE.search(content):
        return "skipped"
    if MARKER in content:
        return "present"

    match = HEAD_CLOSE_RE.search(content)
    if not match:
        return "nohead"
    if check_only:
        return "missing"

    rel = os.path.relpath(filepath, REPO_ROOT).replace(os.sep, "/")
    title = extract_title(
        content, os.path.splitext(os.path.basename(filepath))[0]
    )
    description = derive_description(title)
    page_url = canonical_url(rel)

    indent = match.group("indent")
    block = build_block(content, title, description, page_url, indent)
    new_content = content[: match.start()] + block + content[match.start():]

    with open(filepath, "w", encoding="utf-8", newline="") as fh:
        fh.write(new_content)
    return "added"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Do not modify files; exit 1 if any page is missing the marker.",
    )
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
        status = ensure_meta(filepath, check_only=args.check)
        totals[status].append(rel)

    for status, label in (
        ("added", "Added meta block"),
        ("missing", "Missing meta block"),
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
            "ERROR: one or more HTML files are missing the SEO meta marker. "
            "Run `python3 scripts/ensure-meta.py` to add it.",
            file=sys.stderr,
        )
        exit_code = 1
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
