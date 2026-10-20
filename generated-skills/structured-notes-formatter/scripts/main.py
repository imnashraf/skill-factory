#!/usr/bin/env python3
"""Structured Notes Formatter (Office Productivity Pack).

Parses raw notes and transcripts into standardized markdown meeting minutes
with metadata, agenda items, key decisions, and prioritized action items.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


def parse_raw_notes(text: str) -> Dict[str, Any]:
    """Parse raw text lines into structured meeting note sections."""
    lines = [line.strip() for line in text.strip().splitlines() if line.strip()]
    
    title = "Meeting Notes"
    date_val = "Undated"
    attendees: List[str] = []
    decisions: List[str] = []
    actions: List[Dict[str, str]] = []
    discussion: List[str] = []

    for line in lines:
        lower = line.lower()
        if lower.startswith("# "):
            title = line[2:].strip()
        elif lower.startswith("date:") or lower.startswith("date -"):
            date_val = line.split(":", 1)[-1].strip() if ":" in line else line.split("-", 1)[-1].strip()
        elif lower.startswith("attendees:") or lower.startswith("participants:"):
            raw_att = line.split(":", 1)[-1].strip()
            attendees = [a.strip() for a in re.split(r"[,;]", raw_att) if a.strip()]
        elif lower.startswith("decision:") or lower.startswith("decided:"):
            decisions.append(line.split(":", 1)[-1].strip())
        elif lower.startswith("action:") or lower.startswith("todo:") or "action item:" in lower:
            raw_act = line.split(":", 1)[-1].strip()
            # check for owner pattern: "Do X (Owner: Alice)" or "@Alice: Do X"
            owner = "Unassigned"
            match_owner = re.search(r"\((?:owner|assignee):\s*([^)]+)\)", raw_act, re.IGNORECASE)
            if match_owner:
                owner = match_owner.group(1).strip()
                raw_act = re.sub(r"\((?:owner|assignee):\s*[^)]+\)", "", raw_act, flags=re.IGNORECASE).strip()
            elif "@" in raw_act:
                m_at = re.search(r"@([A-Za-z0-9_-]+)", raw_act)
                if m_at:
                    owner = m_at.group(1)
            actions.append({"task": raw_act, "owner": owner})
        else:
            discussion.append(line)

    return {
        "title": title,
        "date": date_val,
        "attendees": attendees,
        "decisions": decisions,
        "actions": actions,
        "discussion": discussion,
    }


def format_markdown(data: Dict[str, Any]) -> str:
    """Format structured notes data into clean GitHub-flavored markdown."""
    out = [f"# {data['title']}", ""]
    out.append(f"**Date:** {data['date']}")
    if data["attendees"]:
        out.append(f"**Attendees:** {', '.join(data['attendees'])}")
    else:
        out.append("**Attendees:** Unspecified")
    out.append("")

    if data["decisions"]:
        out.append("## Key Decisions")
        for d in data["decisions"]:
            out.append(f"- [x] **Decision:** {d}")
        out.append("")

    if data["actions"]:
        out.append("## Action Items")
        for a in data["actions"]:
            out.append(f"- [ ] {a['task']} *(Assignee: {a['owner']})*")
        out.append("")

    if data["discussion"]:
        out.append("## Discussion & Notes")
        for disc in data["discussion"]:
            if disc.startswith("- ") or disc.startswith("* "):
                out.append(disc)
            else:
                out.append(f"- {disc}")
        out.append("")

    return "\n".join(out)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Format raw notes into structured markdown meeting minutes.")
    parser.add_argument("file", help="Path to raw notes text file")
    parser.add_argument("--json", action="store_true", help="Output parsed structure as JSON")
    parser.add_argument("--output", help="Write output to specified file path")
    args = parser.parse_args(argv)

    path = Path(args.file)
    if not path.is_file():
        print(f"[ERROR] File not found: {path}", file=sys.stderr)
        return 1

    content = path.read_text(encoding="utf-8", errors="replace")
    data = parse_raw_notes(content)

    if args.json:
        result = json.dumps(data, indent=2)
    else:
        result = format_markdown(data)

    if args.output:
        Path(args.output).write_text(result, encoding="utf-8")
        print(f"[OK] Formatted notes written to {args.output}")
    else:
        print(result)

    return 0


if __name__ == "__main__":
    sys.exit(main())
