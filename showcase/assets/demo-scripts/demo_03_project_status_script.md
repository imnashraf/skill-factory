# Video Recording Script: Demo 03 — Project Status Reporter

**Duration**: 80 seconds (1m 20s)  
**Format**: Terminal Screen Recording + Voiceover  
**Target Audience**: Program Managers, PMO Directors, Agile Delivery Leads  

---

## Scene 1: Business Problem Hook (0:00 – 0:12)

**Visual**: Slide showing project managers arguing over whether a project is "Green" or "Amber" despite blocked dependencies.  
**Voiceover**:  
> "Project status reports are notoriously subjective. Teams mark initiatives 'Green' even when deliverables are blocked and critical risks are ignored. Here is how Skill Factory brings mathematical objectivity to PMO reporting."

---

## Scene 2: Synthetic Dataset Introduction (0:12 – 0:24)

**Visual**: Terminal displays `valid_milestones.csv` and `valid_raid.csv`.  

```bash
cat showcase/project-management/project-status/sample-inputs/edge_case_milestones.csv
cat showcase/project-management/project-status/sample-inputs/edge_case_raid.csv
```

**Voiceover**:  
> "We feed in milestone delivery dates alongside active RAID signals: risks, issues, assumptions, and dependencies."

---

## Scene 3: Skill Factory Lifecycle (0:24 – 0:40)

**Visual**: Operator runs validation and evaluation.  

```bash
skillfactory validate showcase/project-management/project-status --no-hashes
skillfactory eval showcase/project-management/project-status --no-hashes
```

**Voiceover**:  
> "Skill Factory validates the Agent Skill structure and verifies all subprocess tests pass within clean timeouts. Quality grade: 98 out of 100 Grade A."

---

## Scene 4: Workflow Execution & Actual Results (0:40 – 1:02)

**Visual**: Operator runs the status generator on the edge-case project dataset.  

```bash
python3 showcase/project-management/project-status/scripts/main.py \
  showcase/project-management/project-status/sample-inputs/edge_case_milestones.csv \
  --raid-file showcase/project-management/project-status/sample-inputs/edge_case_raid.csv \
  --as-of-date 2026-10-20
```

**Voiceover**:  
> "Applying documented governance rules, the engine objectively calculates overall health as RED. Why? One deliverable is blocked, two milestones are overdue, and a critical licensing risk is open. Look at the Action Summary—it gives leadership an immediate, owner-assigned priority checklist."

---

## Scene 5: Closing Statement & Next Steps (1:02 – 1:20)

**Visual**: Terminal displays generated markdown report and Antigravity installation.  

```bash
skillfactory install showcase/project-management/project-status --target antigravity --dry-run
```

**Voiceover**:  
> "No invented progress updates. No sugarcoated narratives. Real-world PMO governance delivered with Skill Factory."
