#!/usr/bin/env python3
"""
Find HTML infographics whose documented "last accuracy check" date is
missing or older than the configured threshold, and emit one markdown
issue body per stale page into reports/accuracy-review-issues/.

Each page is expected to carry a meta tag of the form:

    <!-- smec-accuracy v1 -->
    <meta name="smec:last-accuracy-check" content="YYYY-MM-DD">

Pages without the marker are treated as "never reviewed" and become
immediately eligible — that is intentional so legacy pages roll
through the review cycle naturally without a separate bootstrap step.
The per-run cap (--max-issues) throttles the initial wave.

This script does not modify any HTML and does not call any LLM. The
companion workflow `.github/workflows/accuracy-review.yml` reads the
generated `index.json`, opens GitHub issues, and assigns the Copilot
coding agent. Mirrors the structure of
`scripts/open-copilot-review-issues.py`.

Stdlib only.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
from typing import Any

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_INDEX = os.path.join(REPO_ROOT, "index.html")
REPORTS_DIR = os.path.join(REPO_ROOT, "reports")
OUT_DIR = os.path.join(REPORTS_DIR, "accuracy-review-issues")

# Hidden marker embedded in each issue body so the workflow can dedup
# reliably (issue-title search is tokenized and misses backticks). The
# workflow searches open issues by label and checks the body for this
# marker + the file path before creating a duplicate.
ISSUE_MARKER = "<!-- copilot-accuracy-review v1 -->"

META_NAME = "smec:last-accuracy-check"
SUBMITTER_NAME = "smec:submitter"
META_BLOCK_MARKER = "<!-- smec-accuracy v1 -->"
    
ACCURACY_META_RE = re.compile(
    r'<meta\s+[^>]*name=["\']' + re.escape(META_NAME)
    + r'["\'][^>]*content=["\']([^"\']*)["\']',
    re.IGNORECASE,
)
SUBMITTER_META_RE = re.compile(
    r'<meta\s+[^>]*name=["\']' + re.escape(SUBMITTER_NAME)
    + r'["\'][^>]*content=["\']([^"\']*)["\']',
    re.IGNORECASE,
)
TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)
META_REFRESH_RE = re.compile(
    r'<meta\s+http-equiv=["\']refresh["\']', re.IGNORECASE
)

SKIP_DIRS = {".git", "node_modules", ".github", "reports"}

# GitHub issue body hard limit is 65536 chars; stay well below.
MAX_BODY_CHARS = 60000


def iter_html_files(root: str):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fname in filenames:
            if fname.lower().endswith(".html"):
                yield os.path.join(dirpath, fname)


def _extract_title(content: str, fallback: str) -> str:
    m = TITLE_RE.search(content)
    if not m:
        return fallback
    raw = re.sub(r"\s+", " ", m.group(1)).strip()
    return raw or fallback


def _extract_submitter(content: str) -> str | None:
    m = SUBMITTER_META_RE.search(content)
    if not m:
        return None
    return m.group(1).strip() or None


def _sanitize_title(title: str) -> str:
    # Strip characters that could terminate a markdown code span or
    # inject markdown structure so the title renders as literal text.
    return re.sub(r"[`<>]", "", title).strip() or "(untitled)"


def _parse_date(value: str) -> dt.date | None:
    value = (value or "").strip()
    if not value:
        return None
    try:
        return dt.date.fromisoformat(value[:10])
    except ValueError:
        return None


def _classify(filepath: str, today: dt.date,
              max_age_days: int) -> tuple[str, dt.date | None, int | None]:
    """Return (status, last_check_date, age_days).

    status is one of:
      - "missing"   : no marker / no parseable date
      - "stale"     : last check older than max_age_days
      - "fresh"     : within the threshold
      - "skipped"   : redirect stub / root index
    """
    if os.path.abspath(filepath) == os.path.abspath(ROOT_INDEX):
        return "skipped", None, None
    with open(filepath, encoding="utf-8") as fh:
        content = fh.read()
    if META_REFRESH_RE.search(content):
        return "skipped", None, None
    m = ACCURACY_META_RE.search(content)
    if not m:
        return "missing", None, None
    last = _parse_date(m.group(1))
    if last is None:
        return "missing", None, None
    age = (today - last).days
    if age > max_age_days:
        return "stale", last, age
    return "fresh", last, age


def _render(rel: str, title: str, last_check: dt.date | None,
            age_days: int | None, max_age_days: int,
            submitter: str | None) -> str:
    safe_title = _sanitize_title(title)
    if last_check is None:
        freshness_line = (
            "**Last accuracy check:** _no record on file — this is the "
            "page's first scheduled review._"
        )
    else:
        freshness_line = (
            f"**Last accuracy check:** `{last_check.isoformat()}` "
            f"({age_days} days ago, threshold {max_age_days})."
        )

    parts: list[str] = []
    parts.append(ISSUE_MARKER)
    parts.append(f"<!-- page: {rel} -->")
    parts.append("")
    parts.append(f"# Accuracy review: `{rel}`")
    parts.append("")
    parts.append(
        "_This issue was opened automatically by the weekly accuracy-"
        "review workflow because this page has not been verified "
        f"against Microsoft Learn within the last {max_age_days} days. "
        "It is assigned to the Copilot coding agent, which will open a "
        "draft PR. A human reviewer merges or closes._"
    )
    parts.append("")
    parts.append(f"**Page title:** {safe_title}")
    parts.append(f"**File:** `{rel}`")
    parts.append(freshness_line)
    if submitter:
        parts.append(f"**Original submitter:** `@{submitter}`")
        parts.append(f"**Reviewer to add on the draft PR:** `@{submitter}`")
    else:
        parts.append("**Original submitter:** _not recorded on page metadata._")
    parts.append("")
    parts.append("## What to do")
    parts.append("")
    parts.append(
        "Re-read this page end to end and verify every factual claim "
        "against the **current** documentation on "
        "[learn.microsoft.com](https://learn.microsoft.com/). Focus on:"
    )
    parts.append("")
    parts.append(
        "- Service names, SKU names, and tier names (Microsoft renames "
        "products frequently)."
    )
    parts.append(
        "- Quotas, limits, retention windows, region availability, and "
        "any other numeric claim."
    )
    parts.append(
        "- Feature availability (GA vs preview vs deprecated) and any "
        "guidance that has been superseded."
    )
    parts.append(
        "- Recommended patterns and Microsoft-prescribed best "
        "practices that may have shifted."
    )
    parts.append(
        "- External links — broken or redirected `learn.microsoft.com` "
        "URLs should be updated to the current canonical page."
    )
    parts.append("")
    parts.append("## Deliverable")
    parts.append("")
    parts.append(
        "Open a **draft pull request** linked to this issue. Apply the "
        "`accuracy-review` label to the PR — a post-merge workflow uses "
        "that label to stamp the page's `smec:last-accuracy-check` meta "
        "tag with the merge date."
    )
    parts.append("")
    parts.append("**If corrections are needed:**")
    parts.append("")
    parts.append(
        "- Edit the HTML file in place. Each substantive change must "
        "cite a current `learn.microsoft.com` URL **in the PR "
        "description** under a `## Sources` section, paired with the "
        "claim it supports. Example:"
    )
    parts.append("")
    parts.append("  ```")
    parts.append("  ## Sources")
    parts.append("  - Renamed \"Synapse Data Engineering\" to \"Fabric Data Engineering\":")
    parts.append("    https://learn.microsoft.com/fabric/data-engineering/")
    parts.append("  - Updated retention default from 7 to 30 days:")
    parts.append("    https://learn.microsoft.com/azure/.../retention")
    parts.append("  ```")
    parts.append("")
    parts.append(
        "- Do not invent facts. If a claim cannot be verified against "
        "Microsoft Learn, leave the original wording and note "
        "`needs human verification` in the PR description rather than "
        "guessing."
    )
    parts.append("")
    parts.append("**If the page is already accurate:**")
    parts.append("")
    parts.append(
        "- Open a metadata-only PR that adds (or refreshes) the "
        "accuracy-check meta block in the page's `<head>`:"
    )
    parts.append("")
    parts.append("  ```html")
    parts.append(f"  {META_BLOCK_MARKER}")
    parts.append(
        f'  <meta name="{META_NAME}" content="YYYY-MM-DD">'
    )
    parts.append("  ```")
    parts.append("")
    parts.append(
        "  Use today's UTC date as a placeholder; the post-merge "
        "stamper will overwrite it with the actual merge date. State "
        "in the PR description that the review found no corrections "
        "and list the Microsoft Learn pages you cross-checked under "
        "`## Sources`."
    )
    parts.append("")
    parts.append("## Guardrails")
    parts.append("")
    parts.append(
        "- The PR must modify **exactly one file**, the HTML page "
        "named above. Do not touch any other `.html` page, any script "
        "under `scripts/`, any workflow under `.github/`, "
        "`manifest.json`, or `README.md`."
    )
    parts.append(
        "- Do not refactor site chrome (tracking, back button, meta, "
        "favicon) — those are owned by the `ensure-*` scripts and run "
        "post-merge. Only the `smec-accuracy` block is in scope here."
    )
    parts.append(
        "- Preserve all idempotency markers verbatim: "
        "`data-website-id=...`, `data-smec-back-button=\"v2\"`, "
        "`<!-- smec-meta v1 -->`, `<!-- smec-favicon v1 -->`, "
        "`<!-- smec-tmpl:<id> -->`."
    )
    parts.append(
        "- Keep the PR as a **draft** and apply the `accuracy-review` "
        "label so the post-merge stamper picks it up."
    )
    parts.append("")
    parts.append("## How to verify locally")
    parts.append("")
    parts.append("```bash")
    parts.append("python3 scripts/audit-pages.py")
    parts.append("python3 scripts/check-accuracy-staleness.py")
    parts.append("```")
    parts.append("")
    body = "\n".join(parts)
    if len(body) > MAX_BODY_CHARS:
        body = body[:MAX_BODY_CHARS] + "\n\n_…body truncated to fit GitHub issue size limit._\n"
    return body


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--only",
        default=None,
        help="Restrict to files whose repo-relative path starts with PREFIX.",
    )
    parser.add_argument(
        "--max-age-days",
        type=int,
        default=28,
        help=(
            "Pages whose recorded last-accuracy-check date is older "
            "than this many days (default 28) are flagged. Pages "
            "without any recorded date are always flagged."
        ),
    )
    parser.add_argument(
        "--max-issues",
        type=int,
        default=10,
        help=(
            "Cap on number of page bodies emitted per run. Throttles "
            "the initial wave of legacy pages without markers. Pages "
            "beyond the cap are reported on stderr and dropped."
        ),
    )
    parser.add_argument(
        "--today",
        default=None,
        help="Override today's date (YYYY-MM-DD); for tests.",
    )
    args = parser.parse_args()

    if args.max_issues <= 0:
        print("ERROR: --max-issues must be positive.", file=sys.stderr)
        return 2
    if args.max_age_days < 0:
        print("ERROR: --max-age-days must be non-negative.", file=sys.stderr)
        return 2

    today = dt.date.today()
    if args.today:
        try:
            today = dt.date.fromisoformat(args.today)
        except ValueError:
            print(f"ERROR: bad --today value {args.today!r}", file=sys.stderr)
            return 2

    only_prefix = args.only.rstrip("/") + "/" if args.only else None

    eligible: list[tuple[str, str, dt.date | None, int | None, str | None]] = []
    fresh_count = 0
    skipped_count = 0
    
    for filepath in sorted(iter_html_files(REPO_ROOT)):
        rel = os.path.relpath(filepath, REPO_ROOT).replace(os.sep, "/")
        if only_prefix and not (rel + "/").startswith(only_prefix) and rel != args.only:
            continue
        status, last, age = _classify(filepath, today, args.max_age_days)
        if status == "skipped":
            skipped_count += 1
            continue
        if status == "fresh":
            fresh_count += 1
            continue
        # status == "stale" or "missing"
        with open(filepath, encoding="utf-8") as fh:
            content = fh.read()
        title = _extract_title(
            content, os.path.splitext(os.path.basename(filepath))[0]
        )
        submitter = _extract_submitter(content)
        eligible.append((rel, title, last, age, submitter))

    os.makedirs(OUT_DIR, exist_ok=True)
    # Clean previous run so the index always matches what's on disk.
    for existing in os.listdir(OUT_DIR):
        if existing.endswith(".md") or existing == "index.json":
            try:
                os.remove(os.path.join(OUT_DIR, existing))
            except OSError:
                pass

    index: list[dict[str, Any]] = []
    dropped_over_cap: list[str] = []
    for rel, title, last, age, submitter in eligible:
        if len(index) >= args.max_issues:
            dropped_over_cap.append(rel)
            continue
        body = _render(rel, title, last, age, args.max_age_days, submitter)
        slug = rel.replace("/", "__").replace(".html", "")
        out_path = os.path.join(OUT_DIR, f"{slug}.md")
        with open(out_path, "w", encoding="utf-8") as fh:
            fh.write(body)
        index.append({
            "path": rel,
            "title": title,
            "body_file": os.path.basename(out_path),
            "last_check": last.isoformat() if last else None,
            "age_days": age,
        })

    with open(os.path.join(OUT_DIR, "index.json"), "w", encoding="utf-8") as fh:
        json.dump({
            "today": today.isoformat(),
            "max_age_days": args.max_age_days,
            "max_issues": args.max_issues,
            "issues": index,
            "dropped_over_cap": dropped_over_cap,
        }, fh, indent=2)

    print(f"Eligible pages: {len(eligible)}")
    print(f"  emitted:     {len(index)}")
    print(f"  over cap:    {len(dropped_over_cap)}")
    print(f"Fresh pages:   {fresh_count}")
    print(f"Skipped pages: {skipped_count}")
    if dropped_over_cap:
        print("Dropped (over cap):", file=sys.stderr)
        for r in dropped_over_cap:
            print(f"  - {r}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
