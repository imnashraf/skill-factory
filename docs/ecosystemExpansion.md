# Skill Factory — Ecosystem Expansion Assessment (Phase 14, AC14.05)

**Document Status:** Formal Architecture & Platform Expansion Assessment  
**Date:** 2026-10-19  
**Scope:** Evaluation of candidate AI coding assistants for future Agent Skills support.  

---

## 1. Executive Summary

As the Agent Skills open standard ([agentskills.io](https://agentskills.io/specification)) gains broader industry adoption, new AI developer assistants are emerging. This assessment systematically evaluates 5 candidate platforms across:

1. **Standard Alignment:** Compatibility with `SKILL.md` frontmatter and subdirectory structure (`scripts/`, `references/`).
2. **Discovery Mechanism:** Whether the platform automatically discovers workspace skills or requires manual configuration.
3. **Technical Feasibility:** Engineering effort required to build and maintain an adapter within Skill Factory.
4. **Maintenance Cost & Risk:** API stability, documentation maturity, and breaking change risks.

---

## 2. Platform Evaluation Matrix

| Candidate Platform | Architecture & Skill Convention | Standard Alignment | Technical Feasibility | Maintenance Cost | Recommendation |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **Windsurf (Codeium Cascade)** | Investigating `.windsurf/skills/` and shared `.agents/skills/` workspace conventions. | **Medium** | **High** | **Low** | **Tier 1 Candidate for v1.1.0.** If Cascade adopts `.agents/skills/`, zero code changes needed; alias adapter can be added once vendor docs stabilize. |
| **Continue.dev** | Open-source extension using `.continue/prompts` and `config.json` custom slash-command extensions. | **Low** (Custom JSON/prompts) | **Medium** | **Medium** | **Deferred.** Requires synthetic markdown-to-prompt conversion layer; maintain as community plugin. |
| **Cline / Roo-Code** | Autonomous agent using workspace `.clinerules` and `.roomodes`. | **Medium** | **Medium** | **Low** | **Monitor.** Instructions can reference `SKILL.md`, but lack native folder-based progressive disclosure. |
| **GitHub Copilot** | Single-file configuration (`.github/copilot-instructions.md`). | **Low** | **Low** | **High** | **Not Recommended.** Monolithic file architecture conflicts with modular progressive disclosure. |
| **OpenCodeInterpreter** | Open-weights execution engine with experimental command hooks. | **Low** | **Low** | **High** | **Research Only.** High API volatility; defer until multi-agent protocol standardizes. |

---

## 3. Recommended Roadmap & Criteria for Adding New Platforms

To preserve Skill Factory's high reliability and zero-regression guarantee, any newly added platform adapter must fulfill the following mandatory criteria:

1. **Official Vendor Specification:** The assistant vendor must publish official documentation specifying skill discovery locations and supported frontmatter fields.
2. **Directory-Based Isolation:** The assistant must support directory-level encapsulation rather than forcing monolithic configuration files.
3. **Automated Testability:** The installation directory must be reproducible in headless CI environments without requiring paid subscriptions or proprietary UI interaction.
4. **Zero Proprietary SDKs:** The integration must operate strictly using file-based discovery and standard shell utilities.

---

## 4. Immediate Action Plan

- **v1.0.x Maintenance:** Keep the verified core focused on Claude Code, Cursor, OpenAI Codex, and Google Antigravity.
- **Future v1.1.0 Milestone:** Re-evaluate Windsurf (Codeium) upon formal vendor release of folder-based skill loading.
