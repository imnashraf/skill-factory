# Quickstart Guide: macOS

This guide walks you through using Skill Factory on **macOS** (Apple Silicon M1/M2/M3/M4 or Intel).

---

## 1. Prerequisites

macOS includes Python 3 out of the box with the Xcode Command Line Tools.
Open **Terminal** (`Command + Space`, type `Terminal`) and check your Python version:

```bash
python3 --version
```

Skill Factory supports **Python 3.9+** (Python 3.9.6 or newer). Zero additional packages (`pip`) are required!

---

## 2. Clone and Test Skill Factory

```bash
git clone https://github.com/imnashraf/skill-factory.git
cd skill-factory

# Run the test suite to verify everything is working
python3 -m unittest discover -s tests -v
```

---

## 3. Create Your First Skill

### Interactive Terminal Mode (No AI needed)

```bash
python3 -m skillfactory interview
```

Follow the prompts to name your skill, describe what it does, and choose a starter template.

### One-Command Creation

```bash
python3 -m skillfactory new \
  --name "csv-to-sqlite" \
  --description "Converts CSV data files into an indexed SQLite database when instructed by user." \
  --template "file-transform" \
  --output "my-skills"
```

---

## 4. Test and Evaluate Your Skill

```bash
# Run isolated unit tests
python3 -m skillfactory test my-skills/csv-to-sqlite

# Evaluate quality score (0–100)
python3 -m skillfactory eval my-skills/csv-to-sqlite

# Perform AST safety and secret scan
python3 -m skillfactory scan my-skills/csv-to-sqlite
```

---

## 5. Install into Your AI Coding Tool

Check which AI coding assistants you have installed:

```bash
python3 -m skillfactory doctor
```

Install into your platform (project workspace or user profile):

```bash
# Install into Claude Code
python3 -m skillfactory install my-skills/csv-to-sqlite --target claude-code

# Install into Cursor / Codex / Antigravity
python3 -m skillfactory install my-skills/csv-to-sqlite --target cursor

# List installed skills
python3 -m skillfactory list
```

---

## 6. Self-Installation (Teach Your AI Assistant to Build Skills)

```bash
python3 -m skillfactory install-self --target claude-code
```

Now, whenever you ask your AI assistant *"Build me a skill for X"*, it will use Skill Factory directly!
