# Video Recording Script: Demo 05 — Test Inventory Analyzer

**Duration**: 75 seconds (1m 15s)  
**Format**: Terminal Screen Recording + Voiceover  
**Target Audience**: QA Leads, Software Architects, Engineering Managers  

---

## Scene 1: Business Problem Hook (0:00 – 0:12)

**Visual**: Graphic of an engineer trying to figure out which modules in a repository lack tests without waiting 30 minutes for a test suite to run.  
**Voiceover**:  
> "Running runtime code coverage on large test suites takes 20 to 45 minutes. But what if you could discover untested modules, duplicate tests, and skipped suites in under 10 milliseconds?"

---

## Scene 2: Synthetic Dataset Introduction (0:12 – 0:22)

**Visual**: Tree view of `sample-inputs/edge_case_repo/` showing `src/` modules and `tests/` suites.  

```bash
ls showcase/software-engineering/test-inventory/sample-inputs/edge_case_repo/src
ls showcase/software-engineering/test-inventory/sample-inputs/edge_case_repo/tests
```

**Voiceover**:  
> "Our synthetic repository contains four source modules alongside test suites with duplicate functions and skipped integration tests."

---

## Scene 3: Skill Factory Lifecycle (0:22 – 0:38)

**Visual**: Operator runs validation and evaluation.  

```bash
skillfactory validate showcase/software-engineering/test-inventory --no-hashes
skillfactory eval showcase/software-engineering/test-inventory --no-hashes
```

**Voiceover**:  
> "Skill Factory validates the skill folder and verifies its structural test isolation. It grades Grade A 98 out of 100."

---

## Scene 4: Workflow Execution & Actual Results (0:38 – 0:58)

**Visual**: Operator executes the test inventory analyzer.  

```bash
python3 showcase/software-engineering/test-inventory/scripts/main.py \
  showcase/software-engineering/test-inventory/sample-inputs/edge_case_repo \
  --src-dir src \
  --tests-dir tests
```

**Voiceover**:  
> "In single-digit milliseconds, AST parsing catalogs four test functions across two test files, flags analytics and reporting as completely lacking test files, and isolates duplicate test definitions."

---

## Scene 5: Closing Statement & Next Steps (0:58 – 1:15)

**Visual**: Terminal displays output report and installation to Antigravity.  

```bash
skillfactory install showcase/software-engineering/test-inventory --target antigravity --dry-run
```

**Voiceover**:  
> "Fast, static, and zero runtime dependencies. Bring structural test quality visibility to your AI coding agents with Skill Factory."
