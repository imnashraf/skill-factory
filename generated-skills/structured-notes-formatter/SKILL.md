---
name: structured-notes-formatter
description: Parses unstructured meeting notes and text transcripts into standardized GitHub-flavored markdown minutes with metadata, decisions, and assigned action items.
---

# Structured Notes Formatter

Format rough meeting notes and stream-of-consciousness text into structured, action-oriented meeting summaries.

## When to Use This Skill

Activate this skill when:

- Converting rough bullet notes or interview notes into clear meeting minutes.
- Extracting decisions, owners, and action items from transcripts.
- Generating markdown documentation from team syncs.

## Workflow Instructions

1. Locate the raw notes file (e.g. `raw_notes.txt`).
2. Run the formatter:

   ```bash
   python3 scripts/main.py raw_notes.txt --output meeting_minutes.md
   ```

3. Or output JSON format:

   ```bash
   python3 scripts/main.py raw_notes.txt --json
   ```

## Limitations & Best Practices

- Does not modify source text files in-place without `--output`.
- Handles UTF-8 encoded text files safely.
- Zero external Python dependencies required.
