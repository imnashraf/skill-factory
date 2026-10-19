# Security Policy

The Skill Factory maintainers and community take software security seriously. This policy describes how security vulnerabilities in Skill Factory are handled, how to report them responsibly, and the built-in defenses protecting users from untrusted code.

---

## 1. Supported Versions

Security updates and patches are actively maintained for the following versions:

| Version | Supported | Minimum Python |
| --- | --- | --- |
| `1.0.1` | :white_check_mark: Yes (Current) | Python 3.9+ |
| `1.0.0` | :white_check_mark: Yes | Python 3.9+ |
| `< 1.0.0` | :x: No (Legacy / Alpha) | Python 3.9+ |

---

## 2. Reporting a Vulnerability

If you discover a security vulnerability in Skill Factory, please report it responsibly so we can resolve the issue before details become public.

**Please DO NOT open a public GitHub issue for security vulnerabilities.**

Instead, please report vulnerabilities using one of these methods:

1. **GitHub Security Advisory**: Open a private draft security advisory under the repository's **Security** -> **Advisories** tab on GitHub.
2. **Direct Contact**: If GitHub advisories are unavailable, email `security@skillfactory.dev` (or the repository maintainer) with:
   - A clear description of the vulnerability and attack vector.
   - Proof-of-concept steps or reproduction scripts.
   - The affected Skill Factory version and operating system.

### Response SLA & Turnaround

- **Acknowledgment**: Within **48 hours** of report receipt.
- **Triage & Assessment**: Within **5 business days**, confirming severity and affected platforms.
- **Patch & Advisory**: Critical vulnerabilities will be patched and released with an advisory within **14 business days**.
- **Credit**: Reporters who practice responsible disclosure will be acknowledged in the release notes and advisory.

---

## 3. Threat Model and Security Guarantees

Skill Factory generates and manages code intended to run within developer workstations and AI coding assistants. Because generated code or imported third-party skills could be malicious or flawed, Skill Factory enforces the following structural safeguards:

### 1. Isolated Subprocess Test Execution

Skill Factory never executes test suites in the host Python process. All test runs (`skillfactory test`) are spawned inside an isolated subprocess with a strict **10-second execution timeout** (`timeout=10.0`). Runaway scripts or infinite loops are terminated automatically (`SIGKILL`).

### 2. Zip-Slip Path Traversal Protection

When importing `.zip` packages (`skillfactory import`), Skill Factory inspects every entry header before extraction. Any archive member containing `../`, leading slashes, drive letters, or resolving outside the target destination folder is rejected immediately, preventing file overwrite attacks.

### 3. Static AST Safety Scanner

The built-in safety scanner (`skillfactory scan`) uses Python's Abstract Syntax Tree (`ast`) to analyze scripts without executing them. It flags dangerous constructs including:

- Arbitrary code execution: `eval()`, `exec()`, `__import__()`.
- Shell execution: `os.system()`, `os.popen()`, `subprocess(..., shell=True)`.
- Destructive operations: `os.remove('/')`, `shutil.rmtree('/')`.

### 4. Credential and Secret Detection

Files are automatically scanned for hardcoded credentials prior to publishing or archiving. The detector catches:

- AWS Access Keys (`AKIA...`)
- GitHub Personal Access Tokens (`ghp_...`, `gho_...`)
- OpenAI API Keys (`sk-proj-...`)
- Private Cryptographic Keys (`BEGIN RSA PRIVATE KEY`)
- High-entropy password and secret assignments.

### 5. Atomic File Operations and Rollback Snapshots

All file generation uses a temporary staging folder (`.tmp-*`) and atomic rename. If any error occurs during generation, staging is rolled back and zero partial or corrupted files remain. Before updating or uninstalling skills, timestamped backup snapshots are preserved in `.skillfactory/backups/`.

---

## 4. Third-Party Dependencies

Skill Factory has **zero third-party runtime dependencies** (`pip`). The entire codebase is implemented using standard Python 3.9+ libraries, eliminating supply-chain exposure from external PyPI package compromises. All GitHub Actions workflows are strictly pinned to full 40-character commit hashes.
