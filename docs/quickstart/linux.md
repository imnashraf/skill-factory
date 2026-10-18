# Quickstart Guide: Linux

This guide walks you through using Skill Factory on **Linux** (Ubuntu, Debian, Fedora, Arch, Alpine, etc.) and in containerized/headless environments.

---

## 1. Prerequisites

Check your Python 3 version:

```bash
python3 --version
```

Skill Factory runs on **Python 3.9+** (including Ubuntu 20.04 LTS / 22.04 LTS / 24.04 LTS). Standard library only; no `pip` or virtual environment activation required!

---

## 2. Clone and Test Skill Factory

```bash
git clone https://github.com/imnashraf/skill-factory.git
cd skill-factory

# Run test suite
python3 -m unittest discover -s tests -v
```

---

## 3. Create Your First Skill

### Interactive Terminal

```bash
python3 -m skillfactory interview
```

### Scripted / CI Batch Creation

```bash
python3 -m skillfactory new \
  --name "systemd-service-linter" \
  --description "Validates systemd unit files for security hardening and restart policies." \
  --template "checklist-review" \
  --output "my-skills"
```

---

## 4. Test, Evaluate, and Scan

```bash
# Isolated subprocess test runner
python3 -m skillfactory test my-skills/systemd-service-linter

# Objective 0-100 quality scoring
python3 -m skillfactory eval my-skills/systemd-service-linter

# AST safety and credential scanner
python3 -m skillfactory scan my-skills/systemd-service-linter
```

---

## 5. Install into AI Assistant

```bash
# Platform health doctor
python3 -m skillfactory doctor

# Install into Claude Code or Codex workspace
python3 -m skillfactory install my-skills/systemd-service-linter --target claude-code

# List installed skills
python3 -m skillfactory list
```

---

## 6. Export and Share

Package your skill into a secure, portable `.zip` with SHA-256 checksum:

```bash
python3 -m skillfactory export my-skills/systemd-service-linter
```

Import third-party skills safely (with built-in Zip-Slip defense):

```bash
python3 -m skillfactory import systemd-service-linter.zip --dest ~/.agents/skills
```
