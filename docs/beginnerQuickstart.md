# Skill Factory — Complete Beginner Quickstart Guide

**Target Audience:** New developers, prompt engineers, and beginners with zero prior experience with Agent Skills or Skill Factory.  
**Prerequisites:** Python 3.9 or higher. Zero paid APIs or accounts needed.

---

## 1. What is an Agent Skill?

An **Agent Skill** is an open standard folder containing instructions, scripts, tests, and documentation that an AI coding assistant (like Claude Code, Cursor, or Google Antigravity) reads to perform specialized tasks autonomously or via commands.

Skill Factory is the free, offline-first tool that creates, validates, scores, and installs these skills safely onto your computer.

---

## 2. Step 1: Check Required Software

Skill Factory requires Python 3.9 or higher and uses **only Python's built-in standard library** (zero third-party dependencies).

### On macOS

Open your Terminal (`Cmd + Space` $\rightarrow$ type `Terminal`) and run:

```bash
python3 --version
```

If missing, install Apple Command Line Tools by typing `xcode-select --install`.

### On Windows

Open Command Prompt or PowerShell (`Win + R` $\rightarrow$ type `cmd`) and run:

```cmd
py --version
```

If Python is not installed, download the official installer from [python.org](https://www.python.org/downloads/) and be sure to check **"Add Python to PATH"**.

### On Linux (Ubuntu / Debian / Fedora / Arch)

Open your terminal and run:

```bash
python3 --version
```

If missing, run `sudo apt-get update && sudo apt-get install -y python3`.

---

## 3. Step 2: Download & Launch Skill Factory

You do not need to install complex dependencies.

### Option A: Direct Git Clone (Recommended)

```bash
git clone https://github.com/imnashraf/skill-factory.git
cd skill-factory

# Launch the interactive menu
python3 -m skillfactory
```

*(On Windows, use `py -m skillfactory`)*

### Option B: Clean pip Installation

```bash
pip install .

# Launch from any directory
skillfactory
```

---

## 4. Step 3: Verify Your Environment (`doctor`)

Run the built-in diagnostic tool to see which AI coding assistants are detected on your machine:

```bash
python3 -m skillfactory doctor
```

Output will show:

- Your Python version and operating system.
- Which AI platforms are detected (Claude Code, Google Antigravity, Cursor, Codex).
- Whether skill directories are ready to receive installations.

---

## 5. Step 4: Create Your First Skill

Skill Factory provides two ways to create a skill:

### Method 1: The 5-Minute Guided Questionnaire (Beginner)

```bash
python3 -m skillfactory interview
```

Skill Factory asks 5 straightforward questions:

1. **Skill Name:** (e.g. `csv-cleaner`, lowercase kebab-case).
2. **Description:** What the skill does and when the AI should use it.
3. **Template Family:** Choose between `standard`, `api-wrapper`, `data-pipeline`, `code-analysis`, or `workflow-automation`.
4. **Primary Tools & Inputs:** Files or parameters the skill accepts.
5. **Expected Output:** What the skill outputs (e.g. a cleaned file or JSON summary).

### Method 2: Direct Single-Command Scaffolding

```bash
python3 -m skillfactory new \
  --name my-first-tool \
  --description "Parses server log files and generates summary statistics."
```

This creates a clean, standard directory at `generated-skills/my-first-tool/`.

---

## 6. Step 5: Complete the Functional Implementation

Every skill created by Skill Factory has an explicit, clean anatomy:

```text
generated-skills/my-first-tool/
├── SKILL.md                 # Instructions for AI assistants
├── README.md                # Human quickstart documentation
├── scripts/
│   └── main.py              # Executable Python script
├── tests/
│   └── test_placeholder.py  # Unit tests
└── .skillfactory/
    └── manifest.json        # Cryptographic file manifest
```

### Implementing Domain Logic

- **In Host-AI Mode (Claude, Cursor, Codex, Antigravity):**  
  Open your assistant and say:  
  *"Read generated-skills/my-first-tool/SKILL.md and implement the complete parsing logic in scripts/main.py and unit tests in tests/test_placeholder.py."*  
  Your assistant will write the logic for you!
- **In Manual / Developer Mode:**  
  Open `scripts/main.py` in your favorite editor (VS Code, Cursor, Vim) and write your Python logic.

---

## 7. Step 6: Test & Evaluate Your Skill

Before installing any skill, verify that it passes safety and quality standards:

```bash
# 1. Validate structure and YAML frontmatter
python3 -m skillfactory validate generated-skills/my-first-tool

# 2. Run automated tests in an isolated subprocess
python3 -m skillfactory test generated-skills/my-first-tool

# 3. Compute quality score (0-100) and letter grade
python3 -m skillfactory eval generated-skills/my-first-tool

# 4. Scan for dangerous code or exposed credentials
python3 -m skillfactory scan generated-skills/my-first-tool
```

Skill Factory evaluates your skill across 5 dimensions and gives you actionable recommendations to reach **Grade A** (≥ 90/100).

---

## 8. Step 7: Install into Your AI Assistant

Install your verified skill into your desired AI assistant using natural platform names:

```bash
# Install to Claude Code
python3 -m skillfactory install generated-skills/my-first-tool --platform claude

# Install to Google Antigravity
python3 -m skillfactory install generated-skills/my-first-tool --platform google

# Install to Cursor
python3 -m skillfactory install generated-skills/my-first-tool --platform cursor
```

### How the AI Assistant Activates the Skill

| Platform | Activation Method | What Happens |
| :--- | :--- | :--- |
| **Claude Code** | **Autonomous or Command** | When you ask a question matching the skill description, Claude Code autonomously invokes it. You can also type `/my-first-tool`. |
| **Google Antigravity** | **Autonomous Activation** | Antigravity registers the skill in its `<skills>` context; the model autonomously reads `SKILL.md` when your prompt matches the skill's purpose. |
| **Cursor** | **Manual Invocation** | Type `/my-first-tool` in Cursor Chat or reference `@my-first-tool` in your prompt. |
| **OpenAI Codex** | **CLI Syntax** | Type `$my-first-tool` in your terminal session. |

---

## 9. Step 8: Update, Rollback, and Uninstall

Skill Factory manages the complete lifecycle with automatic safety backups:

### Updating an Installed Skill

```bash
# Edit your skill in generated-skills/my-first-tool, then run:
python3 -m skillfactory update my-first-tool --platform claude
```

Skill Factory automatically saves a timestamped snapshot of the old version before updating!

### Rolling Back to Previous Backup

If an update broke something, restore the previous working version with a single command:

```bash
python3 -m skillfactory rollback my-first-tool --platform claude
```

### Safe Uninstallation

```bash
python3 -m skillfactory uninstall my-first-tool --platform claude
```

Skill Factory removes only tracked files, preserving your personal data files.

---

## 10. Troubleshooting & Common Issues

| Issue | Cause | Fix |
| :--- | :--- | :--- |
| `python3: command not found` on Windows | Python is installed as `py.exe` | Run `py -m skillfactory` instead of `python3`. |
| `FileExistsError: not managed by Skill Factory` | Target folder already existed with unmanaged files | Pass `--force` if you intentionally want to overwrite: `skillfactory install ... --force`. |
| `Local modifications detected` during update | You manually edited installed files | Pass `--force` to create a backup snapshot and overwrite. |
| Test execution timed out | A script ran longer than 10 seconds or had an infinite loop | Check `scripts/main.py` for long-running loops or blocking I/O calls. |
| AST CRITICAL finding | Script contains `eval()`, `exec()`, or `shell=True` | Replace dangerous dynamic execution with safe standard library alternatives. |
