# Video Recording Script: Demo 04 — Dependency Manifest Reviewer

**Duration**: 75 seconds (1m 15s)  
**Format**: Terminal Screen Recording + Voiceover  
**Target Audience**: Application Security Engineers, DevSecOps Leads, Senior Software Engineers  

---

## Scene 1: Business Problem Hook (0:00 – 0:12)

**Visual**: Graphic of a software supply chain attack originating from unpinned dependencies and insecure repository endpoints.  
**Voiceover**:  
> "A single unpinned package or unencrypted HTTP mirror link in your requirements file can compromise your entire CI/CD pipeline. Here is how Skill Factory audits dependency configurations offline."

---

## Scene 2: Synthetic Dataset Introduction (0:12 – 0:22)

**Visual**: Terminal displays `sample-inputs/edge_case_requirements.txt`.  

```bash
cat showcase/cybersecurity/dependency-review/sample-inputs/edge_case_requirements.txt
```

**Voiceover**:  
> "Here is an edge-case manifest with plaintext HTTP endpoints, mutable git branch references, conflicting package constraints, and wildcards."

---

## Scene 3: Skill Factory Lifecycle (0:22 – 0:38)

**Visual**: Operator runs validation, tests, and security scanning.  

```bash
skillfactory validate showcase/cybersecurity/dependency-review --no-hashes
skillfactory scan showcase/cybersecurity/dependency-review
```

**Voiceover**:  
> "The skill itself is verified with Skill Factory's AST safety scanner to ensure zero dangerous shell invocations or secret leaks."

---

## Scene 4: Workflow Execution & Actual Results (0:38 – 0:58)

**Visual**: Operator runs dependency review script and displays findings table.  

```bash
python3 showcase/cybersecurity/dependency-review/scripts/main.py \
  showcase/cybersecurity/dependency-review/sample-inputs/edge_case_requirements.txt
```

**Voiceover**:  
> "The auditor flags DEP-01 Critical for insecure HTTP, DEP-02 High for unpinned VCS links, and DEP-03 for conflicting urllib3 requirements. Notice the explicit disclaimer: it audits configuration hygiene without making unverified CVE claims."

---

## Scene 5: Closing Statement & Next Steps (0:58 – 1:15)

**Visual**: Terminal displays clean installation into Claude Code and Antigravity.  

```bash
skillfactory install showcase/cybersecurity/dependency-review --target claude-code --dry-run
```

**Voiceover**:  
> "Audit your software supply chain in milliseconds before code merges. Built with Skill Factory."
