---
name: skill-factory
description: Create and validate reusable Agent Skills from user requirements, with offline scaffolding, clear safety rules, and tests. Use when a user wants to create a new skill or SKILL.md package.
---

# Skill Factory

1. Ask the user for the problem to solve and the expected input/output if not supplied.
2. Derive a short lowercase hyphenated skill name and one-line description.
3. Run `python3 scripts/create_skill.py --name NAME --description DESCRIPTION` from the Skill Factory root.
4. Add actual implementation scripts, examples, edge-case tests, and documentation for the requested skill. The generated scaffold is not a completed implementation.
5. Run `python3 -m unittest discover -s tests -v` in the Skill Factory root and run the generated skill's task-specific tests.
6. Verify the generated SKILL.md follows the Agent Skills specification. Use `skills-ref validate` if installed.
7. Ask before installing into any agent directory, overwriting files, running untrusted code, or publishing to GitHub.
8. Report exactly which compatibility targets were tested and any remaining limitations.

No paid API is required by the generator. The AI assistant used to interpret requests may have separate costs.
