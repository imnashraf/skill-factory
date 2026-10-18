#!/usr/bin/env python3
"""Offline, standard-library-only Agent Skill scaffold generator."""
import argparse
import re
from pathlib import Path


def create(name: str, description: str, destination: Path) -> Path:
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', name) or len(name) > 64:
        raise ValueError('Name must be lowercase kebab-case and at most 64 characters')
    if not description.strip() or len(description) > 1024 or '\n' in description:
        raise ValueError('Description must be one nonempty line of at most 1024 characters')
    root = destination.resolve()
    root.mkdir(parents=True, exist_ok=True)
    target = root / name
    target.mkdir(exist_ok=False)
    (target / 'scripts').mkdir()
    (target / 'tests').mkdir()
    (target / 'references').mkdir()
    (target / 'SKILL.md').write_text(f'''---\nname: {name}\ndescription: {description.strip()}\n---\n\n# {name}\n\n## When to use\nUse this skill when the user needs: {description.strip()}\n\n## Workflow\n1. Clarify the expected input and output.\n2. Inspect available files without modifying them.\n3. Explain the plan and obtain approval before destructive actions.\n4. Run the implementation after verifying dependencies.\n5. Validate the output and report any limitations.\n\n## Safety\n- Do not delete or overwrite user data without explicit permission.\n- Never send private files to external services.\n- Do not claim success without verification.\n\n## Implementation status\nScaffold only. Add working scripts and task-specific tests before publishing as functional.\n''', encoding='utf-8')
    (target / 'README.md').write_text(f'# {name}\n\n{description.strip()}\n\nThis is an unimplemented starter scaffold.\n', encoding='utf-8')
    (target / 'tests' / 'test_placeholder.py').write_text('import unittest\n\nclass ScaffoldTests(unittest.TestCase):\n    def test_scaffold_only(self):\n        self.skipTest("Implement task-specific behavior before release")\n', encoding='utf-8')
    return target


def main():
    parser = argparse.ArgumentParser(description='Create a free offline Agent Skill scaffold')
    parser.add_argument('--name', required=True)
    parser.add_argument('--description', required=True)
    parser.add_argument('--output', default='generated-skills')
    args = parser.parse_args()
    print('Created scaffold:', create(args.name, args.description, Path(args.output)))

if __name__ == '__main__':
    main()
