# Video Recording Script: Demo 01 — Financial Variance Analyzer

**Duration**: 75 seconds (1m 15s)  
**Format**: Terminal Screen Recording + Voiceover  
**Target Audience**: Finance Directors, FP&A Analysts, CFOs  

---

## Scene 1: Business Problem Hook (0:00 – 0:12)

**Visual**: Camera focuses on a chaotic spreadsheet with dozens of tabs, red `#DIV/0!` errors, and messy variance formulas.  
**Voiceover**:  
> "Every month-end, finance teams spend hours reconciling budgets against actuals in spreadsheets. Formula drift, division-by-zero on unbudgeted items, and floating-point rounding errors delay executive reporting. Here is how Skill Factory solves it in seconds."

---

## Scene 2: Synthetic Dataset Introduction (0:12 – 0:22)

**Visual**: Terminal displays head of `sample-inputs/valid_budget.csv` and `valid_actuals.csv`.  

```bash
head -n 5 showcase/finance/financial-variance/sample-inputs/valid_budget.csv
head -n 5 showcase/finance/financial-variance/sample-inputs/valid_actuals.csv
```

**Voiceover**:  
> "We start with standard departmental spend CSVs: engineering, marketing, sales, and IT broken down by cost centers and GL accounts."

---

## Scene 3: Skill Factory Lifecycle (0:22 – 0:38)

**Visual**: Operator validates and evaluates the skill using Skill Factory CLI.  

```bash
skillfactory validate showcase/finance/financial-variance --no-hashes
skillfactory eval showcase/finance/financial-variance --no-hashes
```

**Voiceover**:  
> "With Skill Factory, we validate the Agent Skill against open specifications, test its code in a secure sandbox, and evaluate its quality. It scores a perfect 98 out of 100 Grade A—production ready."

---

## Scene 4: Workflow Execution & Actual Results (0:38 – 0:58)

**Visual**: Operator runs the variance analysis command and views the generated executive markdown report.  

```bash
python3 showcase/finance/financial-variance/scripts/main.py \
  showcase/finance/financial-variance/sample-inputs/valid_budget.csv \
  showcase/finance/financial-variance/sample-inputs/valid_actuals.csv \
  --threshold-pct 10.0 \
  --threshold-abs 1000.0
```

**Voiceover**:  
> "In under five milliseconds, the analyzer performs exact Python Decimal arithmetic. It reconciles $445,000 in budget against $475,950 in actuals, flags the six material exceptions exceeding our threshold, and traces every finding directly to source CSV rows."

---

## Scene 5: Closing Statement & Next Steps (0:58 – 1:15)

**Visual**: Terminal displays dry-run installation into Google Antigravity and Claude Code.  

```bash
skillfactory install showcase/finance/financial-variance --target antigravity --dry-run
```

**Voiceover**:  
> "Zero floating-point errors. Zero division-by-zero crashes. Install it into Antigravity or Claude Code with a single command. Build deterministic financial agents with Skill Factory."
