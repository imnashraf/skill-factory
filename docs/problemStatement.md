# Problem Statement

## The problem

AI coding assistants (Claude Code, Cursor, OpenAI Codex, Google Antigravity) can be extended with **Agent Skills**: folders containing a `SKILL.md` file plus optional scripts and references. A good skill turns a one-off conversation into a reusable, reliable capability.

Today, creating a good skill is harder than it should be:

1. **Format knowledge is required.** Users must know the `SKILL.md` frontmatter rules (name format, description length, folder name must match `name`), progressive disclosure, and file layout.
2. **Every platform is slightly different.** Each tool reads skills from different folders and supports different optional fields (see [compatibilityMatrix.md](compatibilityMatrix.md)). A skill that works in one tool may be invisible, duplicated, or behave differently in another.
3. **Quality is rarely verified.** Skills are often shipped without tests, without examples, and with scripts nobody reviewed. There is no simple way to check "is this skill correct, portable, and safe?"
4. **Installation is manual and risky.** Copying folders into hidden directories, updating them, and removing them cleanly is error-prone — especially on Windows.
5. **Existing helpers often require paid APIs or accounts.** Beginners and privacy-conscious users need a tool that works locally and for free.

## Who it is for

| Persona | Need |
|---|---|
| **Beginner user** | Describe a problem in plain language and get a working, installed skill without learning the format. |
| **Developer** | Scaffold, validate, test, and publish skills from the command line, scriptably. |
| **Team lead** | Share vetted skills across a team and several AI tools, with predictable updates. |
| **Privacy-conscious / offline user** | Do all of the above with no network and no AI model. |

## Goals

- Turn a problem description into a complete, portable, tested skill package.
- Work fully offline with deterministic templates; use the host assistant's AI only when available.
- Install, update, uninstall, and roll back skills safely on macOS, Windows, and Linux.
- Report honestly what was verified and what was not.

## Non-goals (v1.0)

- Skill Factory will **not** call any AI model API itself, host a cloud service, or require an account.
- It will **not** guarantee that AI-written skill logic is correct — it verifies with tests and reports results.
- It will **not** provide a true security sandbox (the Python standard library cannot); it provides isolation-lite plus review gates (see [securityAndPrivacy.md](securityAndPrivacy.md)).
- It will **not** manage AI platform accounts, subscriptions, or settings beyond skill folders.
- Non-English UI is out of scope for v1.0 (UTF-8 content is fully supported).

## Current state (end of Phase 0)

- Repository restructured, `.gitignore` added, GitHub Actions running 3 unit tests on Python 3.11 and 3.13 (passing).
- `scripts/create_skill.py` generates a minimal scaffold (stdlib only, offline, no overwrite).
- Defects found during planning review are listed in [progress.md](progress.md#defects-found-during-planning-review).

## Success looks like

A beginner on Windows, macOS, or Linux follows the quickstart, describes a problem, and within 10 minutes has a validated skill installed in at least one target AI tool — without paying for anything, and with a clear report of what was tested.
