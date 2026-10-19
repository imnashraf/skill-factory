# Compatibility Matrix

> [!IMPORTANT]
> Researched on **2026-10-19** from official documentation (sources at the bottom). These products change frequently. Every row must be re-verified before each release (task T9.03), and the machine-readable copy lives in `skillfactory/data/platforms.json` (Phase 3, FR-COMPAT-01). Rows marked *unverified* must not be claimed as supported.

## Skill folder locations

`~` = user home (`%USERPROFILE%` on Windows). "Project" folders are relative to the repository / working directory.

| ID | Platform | Project scope | User (global) scope | System / managed scope | Also reads |
| :--- | :--- | :--- | :--- | :--- | :--- |
| CM-01 | **Claude Code** | `.claude/skills/<name>/` (cwd and every parent up to repo root; nested subfolders load on demand) | `~/.claude/skills/<name>/` | Managed settings dir, e.g. `/etc/claude-code/.claude/skills/` (Linux) | Plugin skills; `~/.claude/skills/synced/` (downloaded from claude.ai, read-only) |
| CM-02 | **Cursor** | `.agents/skills/` and `.cursor/skills/` (also nested anywhere in repo, scoped to that subtree) | `~/.agents/skills/`, `~/.cursor/skills/` | — | `.claude/skills/`, `.codex/skills/`, `~/.claude/skills/`, `~/.codex/skills/` (compatibility) |
| CM-03 | **OpenAI Codex** | `.agents/skills/` in cwd and every parent up to repo root | `~/.agents/skills/` | `/etc/codex/skills/`; built-in system skills | Optional `agents/openai.yaml` inside a skill for UI metadata / invocation policy |
| CM-04 | **Google Antigravity** | `.agents/skills/` (also `.agent/`, `_agents/`, `_agent/`), walking up from cwd to repo root | `~/.gemini/config/skills/` *(verified on this machine; confirm on Windows/Linux)* | Built-in skills | `skills.json` / `plugins.json` for non-standard locations |

### What this means (plain language)

- **One project folder reaches three tools.** Putting a skill in `.agents/skills/` makes it visible to Cursor, Codex, and Antigravity. Claude Code needs `.claude/skills/` instead.
- **Cursor reads almost everything**, including Claude's and Codex's folders. If you install the same skill into both `.agents/skills/` and `.claude/skills/`, Cursor may see it **twice**. Skill Factory must detect and avoid this (FR-COMPAT-05).
- **User-level folders differ for every tool** except that Cursor and Codex share `~/.agents/skills/`.

## Frontmatter field support

✅ documented support · ⚠️ partial / different meaning · ❌ not documented (ignored or unknown) · Spec = agentskills.io specification

| ID | Field | Spec | Claude Code | Cursor | Codex | Antigravity |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| CM-10 | `name` (required, must match folder) | ✅ | ✅ (optional; defaults to folder name) | ✅ | ✅ | ✅ |
| CM-11 | `description` (required, ≤ 1024) | ✅ | ✅ | ✅ | ✅ | ✅ |
| CM-12 | `license` | ✅ | ❌ | ✅ | ❌ | ❌ |
| CM-13 | `compatibility` (≤ 500) | ✅ | ❌ | ✅ | ❌ | ❌ |
| CM-14 | `metadata` (string→string) | ✅ | ❌ | ✅ | ❌ | ❌ |
| CM-15 | `allowed-tools` | ⚠️ experimental | ✅ pre-approves tools for the invoking turn | ❌ | ❌ | ❌ |
| CM-16 | `disable-model-invocation` | — | ✅ | ✅ | ⚠️ via `agents/openai.yaml` `allow_implicit_invocation: false` | ❌ |
| CM-17 | `user-invocable`, `argument-hint`, `context: fork`, `agent` | — | ✅ | ❌ | ❌ | ❌ |
| CM-18 | `paths` (file-glob scoping), `icon` | — | ❌ | ✅ | ❌ | ❌ |

"❌" means *not documented*; unknown fields are generally ignored but this must be tested per platform (task T3.06).

## Behavioural differences

| ID | Topic | Claude Code | Cursor | Codex | Antigravity |
| :--- | :--- | :--- | :--- | :--- | :--- |
| CM-20 | Manual invocation | `/skill-name` | `/skill-name` | `$skill-name` | By name in chat (model decides) |
| CM-21 | Hot reload | Watches skill folders; changes apply in-session | *unverified* | *unverified* | *unverified* |
| CM-22 | Duplicate names | Enterprise > personal > project | *unverified* | Both shown, not merged | Workspace > declared > global > built-in |
| CM-23 | Symlinked skill folders | ✅ supported | *unverified* | ✅ supported | *unverified* |
| CM-24 | Reserved names | `synced` | — | — | — |
| CM-25 | Skill-dir variable in instructions | `${CLAUDE_SKILL_DIR}` | — | — | — |
| CM-26 | Cloud/remote sessions | Cloud sessions don't read `~/.claude/skills/`; commit to repo instead | Only `~/.cursor/skills/` syncs to Cloud Agents (opt-in) | *unverified* | *unverified* |

## Portability rules derived for generated skills

| Rule | Reason |
| :--- | :--- |
| Use only `name`, `description`, and optionally `license`, `compatibility`, `metadata` by default. | Supported or safely ignored everywhere. |
| Reference files with **relative paths from the skill root** (`scripts/run.py`), never `${CLAUDE_SKILL_DIR}` or absolute paths. | Only Claude Code expands that variable. |
| Tell the agent to run scripts with `python3` *or* `py` (Windows) — or ship a tiny instruction "use the Python interpreter available". | `python3` is often missing on Windows. |
| Never name a skill `synced` or a Windows reserved device name. | CM-24, EC-03. |
| Add platform-specific fields only when the user selects that target, and report it. | FR-COMPAT-03. |
| Keep `SKILL.md` < 500 lines; move detail to `references/`. | Spec progressive-disclosure guidance. |

## OS differences that affect skills

| Topic | macOS | Linux | Windows |
| :--- | :--- | :--- | :--- |
| Python command | `python3` (Xcode CLT ships 3.9) | `python3` | `py` launcher or `python`; `python3` may open the Store stub |
| Home folder | `/Users/<u>` | `/home/<u>` | `C:\Users\<u>` |
| Hidden folders | dot-prefix | dot-prefix | dot-prefix folders are *not* hidden by default but work |
| Symlinks | allowed | allowed | need Developer Mode or admin → default to copy |
| Max path | 1024 | 4096 | 260 unless long paths enabled → keep generated paths short |
| Case sensitivity | insensitive (default) | sensitive | insensitive |
| Line endings | LF | LF | CRLF default → force LF on write |
| Executable bit | needed for `./script` | needed | not used → always invoke via interpreter |

## Real-World Activation Verification Status (Phase 14 Audit)

To prevent misleading claims, Skill Factory strictly distinguishes between four levels of platform compatibility:

| Level | Definition |
| :--- | :--- |
| **Tier 1: Verified Autonomous Activation** | Agent autonomously detects the skill in its workspace, reads `SKILL.md`, and invokes its instructions or scripts without manual user slash-commands. |
| **Tier 2: Verified Manual Activation** | Skill is discovered by the assistant and successfully invoked via an explicit user slash command (e.g. `/skill-name` or `$skill-name`). |
| **Tier 3: Verified Directory Discovery** | The platform officially monitors and indexes the folder target; skill files appear in the agent context or tool list. |
| **Tier 4: Simulated / Documentation-Only** | Integration paths and schema conventions are documented by the vendor, but live autonomous behavior has not been directly tested on that specific assistant. |

### Verification Audit by Platform

| Platform | Verification Level | Project Directory | User Directory | Notes & Activation Behavior |
| :--- | :--- | :--- | :--- | :--- |
| **Google Antigravity** | **Tier 1: Verified Autonomous** | `.agents/skills/<name>/` | `~/.gemini/config/skills/` | Verified live in Antigravity development environment. Agent autonomously loads skills upon task relevance. |
| **Claude Code** | **Tier 2: Verified Manual** | `.claude/skills/<name>/` | `~/.claude/skills/<name>/` | Supports `/skill-name` manual invocation. Autonomous activation requires trigger match in user prompt. |
| **Cursor** | **Tier 2: Verified Manual** | `.agents/skills/`, `.cursor/skills/` | `~/.agents/skills/` | Supports `/skill-name` manual trigger and prompt indexing. |
| **OpenAI Codex** | **Tier 3: Verified Discovery** | `.agents/skills/<name>/` | `~/.agents/skills/` | Follows standard `.agents/skills/` convention with optional `agents/openai.yaml` policy. |

## Sources

- [Agent Skills specification](https://agentskills.io/specification)
- [Claude Code skills](https://code.claude.com/docs/en/skills)
- [Cursor skills](https://cursor.com/docs/context/skills)
- [OpenAI Codex skills](https://developers.openai.com/codex/skills)
- Google Antigravity — built-in customization guide (`agy-customizations` skill, read locally on 2026-10-19)
