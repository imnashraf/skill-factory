# Quickstart Guide: Windows

This guide walks you through using Skill Factory on **Windows 10 and Windows 11** using PowerShell or Command Prompt.

---

## 1. Prerequisites

Verify Python is installed on your Windows machine:

```powershell
python --version
# or
py --version
```

If Python is not installed, install it from the Microsoft Store or [python.org](https://www.python.org/downloads/). Ensure **Add Python to PATH** is checked during setup.
Skill Factory requires **Python 3.9+**. Zero external dependencies or `pip install` commands are needed!

---

## 2. Clone and Test Skill Factory

```powershell
git clone https://github.com/imnashraf/skill-factory.git
cd skill-factory

# Run the test suite to verify Windows compatibility
python -m unittest discover -s tests -v
```

---

## 3. Create Your First Skill

### Interactive Questionnaire

```powershell
python -m skillfactory interview
```

### Direct CLI Creation

```powershell
python -m skillfactory new --name "log-analyzer" --description "Parses Windows event logs and web server access logs when asked." --template "python-script" --output "my-skills"
```

---

## 4. Test and Evaluate

Skill Factory handles Windows path length limits (`MAX_PATH`) and reserved device names (`CON`, `PRN`, `AUX`, `NUL`) automatically:

```powershell
# Run tests with 10s subprocess timeout
python -m skillfactory test my-skills\log-analyzer

# Score quality across 5 dimensions (0-100)
python -m skillfactory eval my-skills\log-analyzer

# Check for secrets and AST safety
python -m skillfactory scan my-skills\log-analyzer
```

---

## 5. Install into AI Assistant

By default on Windows, Skill Factory uses **copy installation** so you don't need Administrator privileges:

```powershell
# Check detected tools
python -m skillfactory doctor

# Install into Cursor or Antigravity
python -m skillfactory install my-skills\log-analyzer --target cursor

# List installed skills
python -m skillfactory list
```

---

## 6. Self-Installation

Teach your local AI assistant to create and manage skills:

```powershell
python -m skillfactory install-self
```
