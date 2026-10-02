#!/usr/bin/env python3
"""
Ensures every HTML infographic ends with the standard educational-summary
notice and a link to Microsoft Learn.

The notice is site chrome, not contributor-authored content. Its CSS is
injected before </head> and its footer-style <aside> is injected before
</body>. Redirect stubs and the root index.html landing page are skipped.

Usage:
    python3 scripts/ensure-disclaimer.py
    python3 scripts/ensure-disclaimer.py --check
"""

from __future__ import annotations

import argparse
import os
import re
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_INDEX = os.path.join(REPO_ROOT, "index.html")

MARKER = "<!-- smec-disclaimer v1 -->"
STYLE_MARKER = "/* smec-disclaimer v1 */"
NOTICE_ATTRIBUTE = 'data-smec-disclaimer="v1"'

DISCLAIMER_STYLE = (
    "<style>" + STYLE_MARKER + """
.smec-disclaimer {
  box-sizing: border-box !important;
  width: 100% !important;
  margin: 0 !important;
  padding: 18px 72px 72px !important;
  border: 0 !important;
  border-top: 1px solid rgba(255, 255, 255, 0.14) !important;
  background: #0b1f33 !important;
  color: #dbe7f3 !important;
  text-align: center !important;
  font: 400 13px/1.55 'Segoe UI', -apple-system, BlinkMacSystemFont,
    sans-serif !important;
}
.smec-disclaimer p {
  max-width: 1100px !important;
  margin: 0 auto !important;
  padding: 0 !important;
  color: inherit !important;
  font: inherit !important;
}
.smec-disclaimer a {
  color: #78c7ff !important;
  text-decoration: underline !important;
  text-underline-offset: 2px !important;
}
.smec-disclaimer a:hover,
.smec-disclaimer a:focus-visible {
  color: #b9e3ff !important;
}
.smec-disclaimer a:focus-visible {
  outline: 2px solid #fff !important;
  outline-offset: 2px !important;
}
@media (max-width: 600px) {
  .smec-disclaimer { padding: 16px 16px 68px !important; }
}
</style>"""
)

DISCLAIMER_NOTICE = f"""{MARKER}
<aside class="smec-disclaimer" {NOTICE_ATTRIBUTE} role="note"
  aria-label="Infographic disclaimer">
  <p>This infographic is an educational summary and is not official product
  documentation. For current features, availability, limits, and guidance,
  refer to <a href="https://learn.microsoft.com/" target="_blank"
  rel="noopener">Microsoft Learn</a> and the official sources linked on this
  page.</p>
</aside>"""

HEAD_CLOSE_RE = re.compile(r"^(?P<indent>[ \t]*)</head>", re.MULTILINE)
BODY_CLOSE_RE = re.compile(
    r"^(?P<indent>[ \t]*)</body\s*>", re.IGNORECASE | re.MULTILINE
)
META_REFRESH_RE = re.compile(
    r'<meta\s+http-equiv=["\']refresh["\']', re.IGNORECASE
)
NOTICE_RE = re.compile(
    r'<aside\b[^>]*\bdata-smec-disclaimer\s*=\s*["\']v1["\']',
    re.IGNORECASE,
)

SKIP_DIRS = {".git", "node_modules", ".github", "reports"}


def iter_html_files(root: str):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fname in filenames:
            if fname.lower().endswith(".html"):
                yield os.path.join(dirpath, fname)


def ensure_disclaimer(filepath: str, check_only: bool = False) -> str:
    """Return added, missing, present, skipped, nohead, or nobody."""
    if os.path.abspath(filepath) == os.path.abspath(ROOT_INDEX):
        return "skipped"

    with open(filepath, encoding="utf-8", newline="") as fh:
        content = fh.read()

    if META_REFRESH_RE.search(content):
        return "skipped"

    has_notice = MARKER in content and bool(NOTICE_RE.search(content))
    has_style = STYLE_MARKER in content
    if has_notice and has_style:
        return "present"

    head_match = HEAD_CLOSE_RE.search(content)
    if not head_match:
        return "nohead"
    body_match = BODY_CLOSE_RE.search(content)
    if not body_match:
        return "nobody"
    if check_only:
        return "missing"

    nl = "\r\n" if "\r\n" in content else "\n"
    new_content = content

    if not has_style:
        indent = head_match.group("indent")
        style_block = nl.join(
            indent + line if line else line
            for line in DISCLAIMER_STYLE.splitlines()
        ) + nl
        new_content = (
            new_content[: head_match.start()]
            + style_block
            + new_content[head_match.start() :]
        )

    if not has_notice:
        body_match = BODY_CLOSE_RE.search(new_content)
        if not body_match:
            return "nobody"
        indent = body_match.group("indent")
        notice_block = nl.join(
            indent + line if line else line
            for line in DISCLAIMER_NOTICE.splitlines()
        ) + nl
        new_content = (
            new_content[: body_match.start()]
            + notice_block
            + new_content[body_match.start() :]
        )

    with open(filepath, "w", encoding="utf-8", newline="") as fh:
        fh.write(new_content)
    return "added"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Do not modify files; exit 1 if any page is missing the notice.",
    )
    args = parser.parse_args()

    totals: dict[str, list[str]] = {
        "added": [],
        "missing": [],
        "present": [],
        "skipped": [],
        "nohead": [],
        "nobody": [],
    }
    for filepath in sorted(iter_html_files(REPO_ROOT)):
        rel = os.path.relpath(filepath, REPO_ROOT).replace(os.sep, "/")
        status = ensure_disclaimer(filepath, check_only=args.check)
        totals[status].append(rel)

    for status, label in (
        ("added", "Added disclaimer"),
        ("missing", "Missing disclaimer"),
        ("present", "Already present"),
        ("skipped", "Skipped (redirect or root index)"),
        ("nohead", "No </head> found"),
        ("nobody", "No </body> found"),
    ):
        files = totals[status]
        print(f"{label}: {len(files)}")
        for rel in files:
            print(f"  - {rel}")

    exit_code = 0
    if totals["nohead"] or totals["nobody"]:
        print(
            "ERROR: one or more HTML files are missing <head> or <body> tags.",
            file=sys.stderr,
        )
        exit_code = 1
    if args.check and totals["missing"]:
        print(
            "ERROR: one or more HTML files are missing the standard "
            "disclaimer. Run `python3 scripts/ensure-disclaimer.py` to add it.",
            file=sys.stderr,
        )
        exit_code = 1
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
