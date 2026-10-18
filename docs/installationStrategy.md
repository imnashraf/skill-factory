# Installation, Update, and Rollback Strategy

Installing and managing agent skills manually by copying files into hidden folders is error-prone. A beginner might overwrite custom work, leave orphaned files, or fail to understand why an agent cannot find a newly added skill.

Skill Factory provides a **safe, reversible, and multi-agent installation engine** built into the CLI (`skillfactory install`, `update`, `uninstall`, `rollback`, `list`).

---

## 1. Core Principles

1. **Safety First:** Never silently overwrite existing files. If a destination already contains an unmanaged skill with the same name, stop, explain the situation, and require explicit user action.
2. **Reversibility:** Every install and update takes an automatic backup of the previous version. If anything goes wrong, a single command (`skillfactory rollback`) restores the previous state.
3. **Allow-List Copying:** Only files that belong in a skill (`SKILL.md`, `README.md`, `scripts/`, `references/`, `assets/`, `tests/`, `LICENSE`, `.skillfactory/`) are installed. Temporary files, `.git/`, `.DS_Store`, virtual environments, and personal editor settings are automatically excluded.
4. **Clean Uninstallation:** Skill Factory tracks exactly which files it copied using a manifest. Uninstalling removes only those tracked files and never deletes uncommitted personal files or folders created by the user.
5. **No Admin Privileges Required:** All installation targets are in user space (`~` or within the current repository). No `sudo` or administrator privileges are ever required.

---

## 2. Platform Discovery Paths

Skill Factory maps installation targets based on the platform and scope:

| Target Platform | User (Global) Scope Target | Project (Local) Scope Target |
|---|---|---|
| **Claude Code** | `~/.claude/skills/<name>/` | `.claude/skills/<name>/` |
| **Cursor** | `~/.cursor/skills/<name>/` *(or `~/.agents/skills/<name>/`)* | `.cursor/skills/<name>/` *(or `.agents/skills/<name>/`)* |
| **OpenAI Codex** | `~/.agents/skills/<name>/` | `.agents/skills/<name>/` |
| **Google Antigravity** | `~/.gemini/config/skills/<name>/` | `.agents/skills/<name>/` |

*Note: On Windows, `~` resolves to `C:\Users\<Username>`.*

### Multi-Agent Awareness
Notice that **Cursor, Codex, and Antigravity all support `.agents/skills/` at the project level**. 
When installing with `--scope project`, Skill Factory can target `.agents/skills/` once, making the skill available to Cursor, Codex, and Antigravity simultaneously without duplicating files.

---

## 3. Workflows

### 3.1 Installation (`skillfactory install <skill-path> --target <platform> [--scope user|project]`)

```
[ User runs install command ]
              |
              v
[ Validate source skill ] -----> (Fails validation? Stop and report error)
              |
              v
[ Check destination path ]
              |
      +-------+-----------------------------+
      |                                     |
(Already exists?)                   (Does not exist)
      |                                     |
      +---> Is it managed in registry?      |
               |                            |
          (Yes) -> Run 'update' flow        |
          (No)  -> STOP: Collision alert!  |
                   Require manual review    |
                                            |
                                            v
                            [ Display planned copy actions ]
                                            |
                                            v
                            [ User confirms (or --yes passed) ]
                                            |
                                            v
                            [ Copy allow-listed files ]
                                            |
                                            v
                            [ Record entry in registry.json ]
                                            |
                                            v
                            [ Output success & invocation instructions ]
```

### 3.2 Update (`skillfactory update <name> --target <platform>`)
1. **Hash Verification:** Check whether files at the destination have been modified by the user since the last install (by comparing SHA-256 hashes against `manifest.json`).
2. **Warning on Local Edits:** If the user made manual edits in the destination folder, Skill Factory warns: *"Files in the installed skill have been modified locally. Overwriting will erase these changes."*
3. **Backup Snapshot:** Before replacing anything, the existing folder is zipped or copied into `<backup_dir>/<name>-<timestamp>.bak/`.
4. **Atomic Replacement:** The new version is written to a temporary staging path and moved into place.
5. **Registry Update:** The registry is updated with new version numbers, timestamps, and hashes.

### 3.3 Rollback (`skillfactory rollback <name> --target <platform>`)
1. Skill Factory locates the most recent backup in the local registry backup store.
2. Displays the version being restored and asks for confirmation.
3. Swaps the backup back into the platform directory.
4. Updates the registry to point back to the restored version.
5. Keeps at least the last 3 versions in reserve.

### 3.4 Uninstallation (`skillfactory uninstall <name> --target <platform>`)
1. Checks the destination folder against the recorded manifest.
2. If unknown files (not in manifest) are found, pauses and asks the user whether to delete them or preserve them.
3. Removes the tracked files and the empty parent skill directory.
4. Removes the entry from `registry.json`.

---

## 4. Install Methods: Copy vs. Symlink

- **Copy (Default):** Files are physically copied. This is the safest and most compatible method across all operating systems, especially Windows (where creating symlinks may require Developer Mode or elevated privileges).
- **Symlink (`--link`, Optional):** Creates a filesystem symbolic link pointing to the development folder. Ideal for active development of a skill.
  - Before creating a symlink, Skill Factory tests if the OS and user permissions support symlinks. If not, it falls back to copying with a clear explanation.
  - Platforms that officially support symlinked skill folders: Claude Code, OpenAI Codex.

---

## 5. The Local Registry (`registry.json`)

Stored in user data space (`~/.config/skillfactory/registry.json` on Linux/macOS, `%APPDATA%\skillfactory\registry.json` on Windows):

```json
{
  "version": 1,
  "skills": {
    "excel-comparison": [
      {
        "platform": "claude-code",
        "scope": "user",
        "install_path": "/Users/mna/.claude/skills/excel-comparison",
        "installed_at": "2026-10-19T12:00:00Z",
        "skill_version": "0.1.0",
        "method": "copy",
        "manifest_hash": "a1b2c3d4...",
        "backups": [
          "/Users/mna/.config/skillfactory/backups/excel-comparison-20261019-110000"
        ]
      }
    ]
  }
}
```

---

## 6. Self-Installation (Skill Factory as an Agent Skill)

Skill Factory is itself packaged as a skill (`SKILL.md` at repository root). 
Running:
```bash
python3 -m skillfactory install-self --target claude-code --scope user
```
installs Skill Factory into the chosen host assistant so the user can interactively say:
> *"Use skill-factory to create a new skill for analyzing SQLite databases."*
The assistant will read the root `SKILL.md` and use the built-in CLI to guide the user.
