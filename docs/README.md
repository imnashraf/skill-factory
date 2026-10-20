# Skill Factory — Planning Documentation

Status: **Draft for owner review** · Last updated: 2026-10-19 · Applies to: Phases 1–9

This folder is the single source of truth for *what* Skill Factory must do, *why*, and *how we will build and verify it*. Each document has one job; they reference each other by ID instead of repeating content.

## Reading order for beginners

1. [problemStatement.md](problemStatement.md) — why the project exists
2. [productRequirements.md](productRequirements.md) — what the product must achieve (PR-xx)
3. [phase.md](phase.md) — the 10 phases at a glance
4. [implementationPlan.md](implementationPlan.md) — order of work, dependencies, risks
5. [decisions.md](decisions.md) — choices that need your approval
6. [progress.md](progress.md) — where we are now

## Document map

| Document | Purpose | IDs defined |
| --- | --- | --- |
| [problemStatement.md](problemStatement.md) | Problem, users, goals, non-goals | — |
| [productRequirements.md](productRequirements.md) | Product-level requirements and identified gaps | `PR-xx` |
| [functionalRequirements.md](functionalRequirements.md) | Specific behaviours, grouped by area | `FR-<AREA>-xx` |
| [nonFunctionalRequirements.md](nonFunctionalRequirements.md) | Quality attributes (speed, portability, accessibility…) | `NFR-xx` |
| [securityAndPrivacy.md](securityAndPrivacy.md) | Threat model, trust boundaries, privacy, legal | `SEC-xx`, `LEG-xx` |
| [architecture.md](architecture.md) | Recommended system design | — |
| [compatibilityMatrix.md](compatibilityMatrix.md) | Researched platform differences | `CM-xx` |
| [installationStrategy.md](installationStrategy.md) | Install / update / uninstall / rollback | — |
| [phase.md](phase.md) | Phase goals, scope, entry/exit gates | `P0`–`P9` |
| [implementationPlan.md](implementationPlan.md) | Sequencing, dependency graph, risks | `R-xx` |
| [tasks.md](tasks.md) | Every task, with dependencies | `T<phase>.<nn>` |
| [testStrategy.md](testStrategy.md) | How code is tested | `TS-xx` |
| [eval.md](eval.md) | How generated-skill quality is scored | `EV-xx` |
| [edgeCases.md](edgeCases.md) | Catalogue of tricky inputs and situations | `EC-xx` |
| [acceptanceCriteria.md](acceptanceCriteria.md) | Measurable "done" per phase | `AC<phase>.<nn>` |
| [requirementsTraceability.md](requirementsTraceability.md) | Requirement → task → test → acceptance mapping | — |
| [deploymentAndRelease.md](deploymentAndRelease.md) | Versioning, CI/CD, releases | — |
| [decisions.md](decisions.md) | Architecture decision log | `D-xx` |
| [progress.md](progress.md) | Progress tracker, defects, blockers | `DEF-xx`, `B-xx` |

## Change control

- Approved requirements are never edited silently. Any change goes through a `D-xx` entry in [decisions.md](decisions.md) with status, reason and date, then the affected documents are updated in the same commit.
- Status vocabulary used everywhere: **Approved** (from your product vision or explicitly approved), **Proposed** (needs your approval), **Rejected**, **Superseded**.
