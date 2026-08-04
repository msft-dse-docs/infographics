#!/usr/bin/env python3
"""
Generic, idempotent, marker-based bulk edit helper for site-wide HTML
changes.

This script exists so one-off site-wide edits (a new footer, a shared
disclaimer, a nav refresh) don't require writing a dedicated new script
each time. Define the change declaratively in a JSON spec and apply it.

Spec file format (JSON):
    {
        "id": "shared-footer-v1",
        "description": "Add a shared footer before </body>.",
        "target": "before-body-close" | "before-head-close" | "regex-replace",
        "glob": "**/*.html",        // repo-relative glob; default **/*.html
        "block": "<footer>...</footer>",   // HTML to insert (target != regex-replace)
        "regex": {                          // only for target=regex-replace
            "pattern": "<div class=\\"old-cta\\">.*?</div>",
            "flags": "s",
            "replacement": "<div class=\\"new-cta\\">Click me</div>"
        },
        "skip_redirect_stubs": true,
        "skip_index": true
    }

The script stamps a marker comment derived from "id" into every file it
touches (<!-- smec-tmpl:<id> -->), so re-running on the same spec is a
no-op. Changing the HTML of a spec and bumping "id" (e.g. -v1 → -v2)
re-applies cleanly; it will NOT rewrite the v1 block — you should write
a new spec that first removes the v1 block (regex-replace) and then
inserts v2.

Usage:
    python3 scripts/apply-template-change.py specs/shared-footer-v1.json
    python3 scripts/apply-template-change.py specs/shared-footer-v1.json --dry-run
    python3 scripts/apply-template-change.py specs/shared-footer-v1.json --check
"""

from __future__ import annotations

import argparse
import fnmatch
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
HEAD_CLOSE_RE = re.compile(r"^(?P<indent>[ \t]*)</head>", re.MULTILINE)
BODY_CLOSE_RE = re.compile(r"^(?P<indent>[ \t]*)</body>", re.MULTILINE)

SKIP_DIRS = {".git", "node_modules", ".github", "reports"}


def iter_html_files_by_glob(pattern: str) -> list[str]:
    """Return HTML files in the repo matching a repo-relative glob."""
    results: list[str] = []
    for dirpath, dirnames, filenames in os.walk(REPO_ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fname in filenames:
            if not fname.lower().endswith(".html"):
                continue
            full = os.path.join(dirpath, fname)
            rel = os.path.relpath(full, REPO_ROOT).replace(os.sep, "/")
            if fnmatch.fnmatch(rel, pattern):
                results.append(full)
    return sorted(results)


def load_spec(path: str) -> dict[str, Any]:
    with open(path, encoding="utf-8") as fh:
        spec = json.load(fh)
    if "id" not in spec:
        raise ValueError("spec must have an 'id' field")
    if "target" not in spec:
        raise ValueError("spec must have a 'target' field")
    spec.setdefault("glob", "**/*.html")
    spec.setdefault("skip_redirect_stubs", True)
    spec.setdefault("skip_index", True)
    return spec


def _regex_flags(flag_str: str) -> int:
    flags = 0
    for ch in flag_str:
        if ch == "i":
            flags |= re.IGNORECASE
        elif ch == "m":
            flags |= re.MULTILINE
        elif ch == "s":
            flags |= re.DOTALL
    return flags


def apply_to_file(
    path: str, spec: dict[str, Any], dry_run: bool
) -> tuple[str, str | None]:
    """Returns (status, diff_summary).

    Status is one of: 'added', 'present', 'skipped', 'would-add',
    'missing-anchor', 'regex-nomatch'."""
    with open(path, encoding="utf-8", newline="") as fh:
        content = fh.read()

    if spec["skip_redirect_stubs"] and META_REFRESH_RE.search(content):
        return "skipped", None

    marker = f"<!-- smec-tmpl:{spec['id']} -->"
    if marker in content:
        return "present", None

    target = spec["target"]
    new_content: str
    if target == "before-head-close":
        match = HEAD_CLOSE_RE.search(content)
        if not match:
            return "missing-anchor", None
        new_content = _insert_block(content, match, marker, spec["block"])
    elif target == "before-body-close":
        match = BODY_CLOSE_RE.search(content)
        if not match:
            return "missing-anchor", None
        new_content = _insert_block(content, match, marker, spec["block"])
    elif target == "regex-replace":
        rx = spec.get("regex") or {}
        pattern = rx.get("pattern")
        replacement = rx.get("replacement", "")
        flags = _regex_flags(rx.get("flags", ""))
        if not pattern:
            return "missing-anchor", None
        new_body, n = re.subn(pattern, replacement, content, flags=flags)
        if n == 0:
            return "regex-nomatch", None
        # Tack the marker onto the end of <head> so future runs can detect.
        head_match = HEAD_CLOSE_RE.search(new_body)
        if head_match:
            nl = "\r\n" if "\r\n" in new_body else "\n"
            indent = head_match.group("indent")
            insertion = f"{indent}{marker}{nl}"
            new_content = (
                new_body[: head_match.start()]
                + insertion
                + new_body[head_match.start():]
            )
        else:
            new_content = new_body + marker
    else:
        raise ValueError(f"unknown target: {target}")

    if dry_run:
        return "would-add", f"+{len(new_content) - len(content)} bytes"

    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(new_content)
    return "added", f"+{len(new_content) - len(content)} bytes"


def _insert_block(
    content: str,
    match: re.Match,
    marker: str,
    block: str,
) -> str:
    nl = "\r\n" if "\r\n" in content else "\n"
    indent = match.group("indent")
    block_lines = block.splitlines()
    indented_block = nl.join(f"{indent}{line}" for line in block_lines)
    insertion = f"{indent}{marker}{nl}{indented_block}{nl}"
    return content[: match.start()] + insertion + content[match.start():]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec", help="Path to the JSON spec file.")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit 1 if the spec is not yet applied to every target file.",
    )
    args = parser.parse_args()

    spec = load_spec(args.spec)
    files = iter_html_files_by_glob(spec["glob"])
    if spec["skip_index"]:
        files = [f for f in files if os.path.abspath(f) != os.path.abspath(ROOT_INDEX)]

    print(f"Spec {spec['id']} -> {len(files)} candidate file(s).")
    counts: dict[str, int] = {}
    for path in files:
        status, summary = apply_to_file(
            path, spec, dry_run=args.dry_run or args.check
        )
        counts[status] = counts.get(status, 0) + 1
        if status in ("added", "would-add", "missing-anchor", "regex-nomatch"):
            rel = os.path.relpath(path, REPO_ROOT).replace(os.sep, "/")
            print(f"  {status:16s} {rel}  {summary or ''}")
    print("summary:", counts)

    if args.check:
        pending = counts.get("would-add", 0) + counts.get(
            "missing-anchor", 0
        ) + counts.get("regex-nomatch", 0)
        if pending:
            print("::warning::Template change not fully applied.")
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
