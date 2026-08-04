#!/usr/bin/env python3
"""
Read-only accessibility check for HTML infographics.

Checks:
  - <html> tag has a lang attribute
  - every <img> tag has an alt attribute (empty alt="" is allowed;
    purely-decorative images should use alt="")
  - every <a> tag has either visible text content or an aria-label
  - every <button> tag has either visible text content or an aria-label

Does NOT modify files. Alt text, link text, and button labels are
editorial decisions; a script cannot write them meaningfully. This
script surfaces issues for humans.

Usage:
    python3 scripts/ensure-a11y.py
        # report only; exits 0. Writes reports/a11y.json.

    python3 scripts/ensure-a11y.py --check
        # exits 1 if any issues are found. Suitable for warn-only CI.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from typing import Any

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_INDEX = os.path.join(REPO_ROOT, "index.html")

META_REFRESH_RE = re.compile(
    r'<meta\s+http-equiv=["\']refresh["\']', re.IGNORECASE
)
HTML_OPEN_RE = re.compile(r"<html\b([^>]*)>", re.IGNORECASE)
IMG_RE = re.compile(r"<img\b([^>]*)>", re.IGNORECASE)
# Capture <a ...>inner</a> for inner-text inspection.
A_RE = re.compile(r"<a\b([^>]*)>(.*?)</a>", re.IGNORECASE | re.DOTALL)
BUTTON_RE = re.compile(
    r"<button\b([^>]*)>(.*?)</button>", re.IGNORECASE | re.DOTALL
)
ATTR_RE = re.compile(r'(\w[\w-]*)\s*=\s*"([^"]*)"|(\w[\w-]*)\s*=\s*\'([^\']*)\'')
INNER_STRIP_RE = re.compile(r"<[^>]+>")

SKIP_DIRS = {".git", "node_modules", ".github", "reports"}


def iter_html_files(root: str):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fname in filenames:
            if fname.lower().endswith(".html"):
                yield os.path.join(dirpath, fname)


def parse_attrs(attr_str: str) -> dict[str, str]:
    attrs: dict[str, str] = {}
    # First pass: key="value" or key='value'.
    consumed_spans: list[tuple[int, int]] = []
    for m in ATTR_RE.finditer(attr_str):
        key = (m.group(1) or m.group(3) or "").lower()
        val = m.group(2) if m.group(2) is not None else m.group(4) or ""
        if key:
            attrs[key] = val
            consumed_spans.append((m.start(), m.end()))
    # Second pass: boolean attributes (no value) in the *gaps* between
    # consumed key="value" spans. Scanning the whole string would pull
    # value fragments (e.g. 'png' from src="x.png") into the attrs dict.
    cursor = 0
    remaining_segments: list[str] = []
    for start, end in consumed_spans:
        remaining_segments.append(attr_str[cursor:start])
        cursor = end
    remaining_segments.append(attr_str[cursor:])
    for segment in remaining_segments:
        for token in re.findall(r"\b([A-Za-z][\w-]*)\b", segment):
            token = token.lower()
            if token not in attrs:
                attrs[token] = ""
    return attrs


def line_of(content: str, offset: int) -> int:
    return content.count("\n", 0, offset) + 1


def scan_file(path: str) -> list[dict[str, Any]]:
    with open(path, encoding="utf-8", errors="replace") as fh:
        content = fh.read()
    if META_REFRESH_RE.search(content):
        return []

    issues: list[dict[str, Any]] = []
    rel = os.path.relpath(path, REPO_ROOT).replace(os.sep, "/")

    html_match = HTML_OPEN_RE.search(content)
    if html_match:
        attrs = parse_attrs(html_match.group(1))
        if "lang" not in attrs or not attrs["lang"].strip():
            issues.append(
                {
                    "rule": "html-lang",
                    "severity": "high",
                    "line": line_of(content, html_match.start()),
                    "snippet": html_match.group(0)[:120],
                }
            )

    for m in IMG_RE.finditer(content):
        attrs = parse_attrs(m.group(1))
        if "alt" not in attrs:
            issues.append(
                {
                    "rule": "img-missing-alt",
                    "severity": "high",
                    "line": line_of(content, m.start()),
                    "snippet": m.group(0)[:120],
                }
            )

    for m in A_RE.finditer(content):
        attrs = parse_attrs(m.group(1))
        inner_text = INNER_STRIP_RE.sub("", m.group(2)).strip()
        aria = attrs.get("aria-label", "").strip()
        title_attr = attrs.get("title", "").strip()
        # Links with images inside are accessible if the image has alt.
        has_image_with_alt = bool(
            re.search(r"<img\b[^>]*\balt\s*=", m.group(2), re.IGNORECASE)
        )
        if not inner_text and not aria and not title_attr and not has_image_with_alt:
            issues.append(
                {
                    "rule": "a-missing-accessible-name",
                    "severity": "medium",
                    "line": line_of(content, m.start()),
                    "snippet": m.group(0)[:120].replace("\n", " "),
                }
            )

    for m in BUTTON_RE.finditer(content):
        attrs = parse_attrs(m.group(1))
        inner_text = INNER_STRIP_RE.sub("", m.group(2)).strip()
        aria = attrs.get("aria-label", "").strip()
        if not inner_text and not aria:
            issues.append(
                {
                    "rule": "button-missing-accessible-name",
                    "severity": "medium",
                    "line": line_of(content, m.start()),
                    "snippet": m.group(0)[:120].replace("\n", " "),
                }
            )

    for issue in issues:
        issue["file"] = rel
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument(
        "--report",
        default=os.path.join("reports", "a11y.json"),
        help="Where to write the JSON report (relative to repo root).",
    )
    args = parser.parse_args()

    all_issues: list[dict[str, Any]] = []
    file_count = 0
    for path in sorted(iter_html_files(REPO_ROOT)):
        # Root index.html is scanned too: the landing page benefits from
        # the same accessibility guarantees as every infographic.
        file_count += 1
        all_issues.extend(scan_file(path))

    by_rule: dict[str, int] = {}
    for issue in all_issues:
        by_rule[issue["rule"]] = by_rule.get(issue["rule"], 0) + 1

    report = {
        "summary": {
            "files_scanned": file_count,
            "total_issues": len(all_issues),
            "by_rule": by_rule,
        },
        "issues": all_issues,
    }

    out_path = args.report
    if not os.path.isabs(out_path):
        out_path = os.path.join(REPO_ROOT, out_path)
    out_dir = os.path.dirname(out_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    print(
        f"a11y: {len(all_issues)} issue(s) across {file_count} file(s). "
        f"report={out_path}"
    )
    for rule, count in sorted(by_rule.items()):
        print(f"  {rule}: {count}")

    if args.check and all_issues:
        print("::warning::Accessibility issues found. See report.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
