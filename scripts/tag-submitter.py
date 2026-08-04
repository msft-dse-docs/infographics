#!/usr/bin/env python3
"""
Stamp the original submitter on one or more HTML infographics.

Each page gets an idempotent metadata block that records the GitHub login
of the original contributor who added the page. The marker is injected just
before `</head>` and the existing `smec:submitter` meta value is updated in
place on subsequent runs.

Stdlib only.
"""

from __future__ import annotations

import argparse
import html
import os
import re
import subprocess
import sys
from urllib.parse import quote

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_INDEX = os.path.join(REPO_ROOT, "index.html")

MARKER = "<!-- smec-submitter v1 -->"
META_NAME = "smec:submitter"

HEAD_CLOSE_RE = re.compile(r"(?P<indent>[ \t]*)</head>", re.IGNORECASE)
META_REFRESH_RE = re.compile(
    r'<meta\s+http-equiv=["\']refresh["\']', re.IGNORECASE
)
SUBMITTER_META_RE = re.compile(
    r'(<meta\s+[^>]*name=["\']' + re.escape(META_NAME)
    + r'["\'][^>]*content=["\'])([^"\']*)(["\'])',
    re.IGNORECASE,
)


def stamp_file(filepath: str, submitter: str, rewrite_existing: bool = False) -> str:
    """Return 'updated', 'inserted', 'unchanged', 'skipped', or 'nohead'.

    Existing submitter tags are preserved by default so later PRs do not
    retag the page. Set rewrite_existing=True to migrate historical tags
    to the resolved GitHub login.
    """
    with open(filepath, encoding="utf-8", newline="") as fh:
        content = fh.read()

    if os.path.abspath(filepath) == os.path.abspath(ROOT_INDEX):
        return "skipped"

    if META_REFRESH_RE.search(content):
        return "skipped"

    normalized_submitter = submitter.strip()
    if not normalized_submitter:
        return "missing"

    m = SUBMITTER_META_RE.search(content)
    escaped = html.escape(normalized_submitter, quote=True)
    if m:
        existing = m.group(2).strip()
        if existing == normalized_submitter:
            return "unchanged"
        if not rewrite_existing:
            return "unchanged"
        new_content = (
            content[:m.start()]
            + m.group(1) + escaped + m.group(3)
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
        f'{indent}<meta name="{META_NAME}" content="{escaped}">{nl}'
    )
    new_content = content[:head_match.start()] + block + content[head_match.start():]
    with open(filepath, "w", encoding="utf-8", newline="") as fh:
        fh.write(new_content)
    return "inserted"


def infer_submitter(filepath: str) -> str | None:
    rel = os.path.relpath(filepath, REPO_ROOT).replace(os.sep, "/")
    result = subprocess.run(
        ["git", "log", "--reverse", "--format=%ae%n%an", "--", rel],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return None

    lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    if len(lines) < 2:
        return None

    email = lines[0]
    name = lines[1]

    login = resolve_github_login(email)
    if login:
        return login
    return resolve_github_login(name)


def resolve_github_login(query: str) -> str | None:
    encoded = quote(query, safe="")
    result = subprocess.run(
        ["gh", "api", f"search/users?q={encoded}", "--jq", ".items[0].login"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    login = result.stdout.strip()
    if not login or login == "null":
        return None
    return login


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "files",
        nargs="*",
        help=(
            "HTML files (repo-relative or absolute) to tag. Non-HTML "
            "paths are silently ignored so workflows can pass the raw "
            "changed-file list."
        ),
    )
    parser.add_argument(
        "--submitter",
        default=None,
        help="GitHub login of the original submitter to record on each page.",
    )
    parser.add_argument(
        "--infer-from-git",
        action="store_true",
        help=(
            "Infer the submitter from git history for each tracked HTML file. "
            "Resolves the earliest commit email to a GitHub login, then falls back "
            "to the author name if no login is found."
        ),
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Do not modify files; report pages missing the submitter tag.",
    )
    parser.add_argument(
        "--rewrite-existing",
        action="store_true",
        help=(
            "Rewrite existing submitter tags to the resolved GitHub login. "
            "Useful for one-time historical backfills."
        ),
    )
    args = parser.parse_args()

    if args.infer_from_git:
        result = subprocess.run(
            ["git", "ls-files", "--", "*.html"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            print(f"ERROR: git ls-files failed: {result.stderr.strip()}", file=sys.stderr)
            return 2
        files = [line for line in result.stdout.splitlines() if line]
    else:
        files = list(args.files)

    if not args.infer_from_git:
        submitter = (args.submitter or "").strip()
        if not submitter:
            print("ERROR: --submitter must be non-empty.", file=sys.stderr)
            return 2
    else:
        submitter = None

    totals = {
        "updated": [],
        "inserted": [],
        "unchanged": [],
        "skipped": [],
        "nohead": [],
        "missing": [],
    }

    for raw in files:
        if not raw.lower().endswith(".html"):
            continue
        path = raw if os.path.isabs(raw) else os.path.join(REPO_ROOT, raw)
        if not os.path.isfile(path):
            totals["missing"].append(raw)
            continue

        if args.check:
            with open(path, encoding="utf-8") as fh:
                content = fh.read()
            if os.path.abspath(path) == os.path.abspath(ROOT_INDEX):
                totals["skipped"].append(os.path.relpath(path, REPO_ROOT).replace(os.sep, "/"))
                continue
            if META_REFRESH_RE.search(content):
                totals["skipped"].append(os.path.relpath(path, REPO_ROOT).replace(os.sep, "/"))
                continue
            if SUBMITTER_META_RE.search(content):
                totals["unchanged"].append(os.path.relpath(path, REPO_ROOT).replace(os.sep, "/"))
            else:
                totals["missing"].append(os.path.relpath(path, REPO_ROOT).replace(os.sep, "/"))
            continue

        if args.infer_from_git:
            inferred = infer_submitter(path)
            if not inferred:
                totals["missing"].append(os.path.relpath(path, REPO_ROOT).replace(os.sep, "/"))
                continue
            submitter = inferred

        status = stamp_file(path, submitter, rewrite_existing=args.rewrite_existing)
        totals[status].append(os.path.relpath(path, REPO_ROOT).replace(os.sep, "/"))

    if args.infer_from_git:
        print("Original submitter: inferred from git history and GitHub login lookup")
    else:
        print(f"Original submitter: {submitter}")
    for status, label in (
        ("updated", "Updated existing tag"),
        ("inserted", "Inserted new tag"),
        ("unchanged", "Already tagged"),
        ("skipped", "Skipped (redirect stub or root index)"),
        ("nohead", "No </head> found"),
        ("missing", "File not found"),
    ):
        files = totals[status]
        print(f"{label}: {len(files)}")
        for f in files:
            print(f"  - {f}")

    if totals["nohead"]:
        print("ERROR: one or more HTML files have no </head> tag.", file=sys.stderr)
        return 1
    if args.check and totals["missing"]:
        print(
            "ERROR: one or more HTML files are missing the submitter tag. "
            "Run `python3 scripts/tag-submitter.py --submitter <login> <files>` to add it.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
