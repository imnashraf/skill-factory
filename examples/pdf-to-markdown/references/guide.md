# pdf-to-markdown — Format Specifications & Schema Guide

Detailed format mapping rules, options, and troubleshooting for pdf-to-markdown.

## Transformation Parameters

- Input Requirements: Ensure valid encoding (default UTF-8).
- Output Format: Specify structure, delimiters, or schema definitions.

## Error Handling

1. Missing File: Clean exit code 1 with path error.
2. Malformed Input: Logs problematic record/line number.
3. Encoding Issues: Automatic fallback or strict UTF-8 enforcement.
