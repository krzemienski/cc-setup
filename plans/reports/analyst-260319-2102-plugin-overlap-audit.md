# Plugin Overlap Audit Report — cc-setup

**Date:** 2026-03-19
**Scope:** 17 enabled plugins, 10 rules files, 3 custom skills

---

## Plugin Inventory

| Plugin | Version | Primary Purpose |
|--------|---------|----------------|
| oh-my-claudecode@omc | 4.9.0 | Multi-agent orchestration (core) |
| everything-claude-code@ecc | 1.8.0 | Comprehensive workflow (60+ skills) |
| claude-mem@thedotmack | 10.6.1 | Persistent cross-session memory |
| code-review@claude-plugins-official | latest | 4-agent parallel code review |
| reflexion@context-engineering-kit | 1.1.4 | Self-refinement + critique |
| sadd@context-engineering-kit | 1.2.0 | Sub-agent driven development patterns |
| kaizen@context-engineering-kit | 1.0.0 | Continuous improvement methodology |
| skill-judge@agent-toolkit | latest | SKILL.md quality evaluation |
| skill-creator@claude-plugins-official | latest | Skill creation with eval loop |
| taches-cc-resources | 1.0.0 | Creation templates (8 skills, 27 commands) |
| planning-with-files | 2.23.0 | Manus-style live plan tracking |
| start@the-startup | 3.2.1 | Full SDLC framework (15 skills) |
| plugin-dev@claude-plugins-official | latest | Plugin development (7 skills) |
| claude-code-setup@claude-plugins-official | 1.0.0 | Setup recommendations (read-only) |
| claude-md-management@claude-plugins-official | 1.0.0 | CLAUDE.md improvement |
| skills-search@daymade-skills | 1.1.0 | Skill marketplace (38 skills) |
| claude-skills-troubleshooting@daymade-skills | 1.0.0 | Skill marketplace superset (42 skills) |

---

## Plugins to REMOVE (3)

### 1. skills-search@daymade-skills — REMOVE (exact duplicate)
Same repo as claude-skills-troubleshooting (daymade/claude-code-skills). The 42-skill version subsumes the 38-skill version. Having both creates duplicate trigger evaluation. **Risk: Zero.**

### 2. start@the-startup — REMOVE (superseded)
15 skills, every capability covered by OMC + ECC at higher quality:
- specify → OMC ralplan + planning-with-files
- implement → OMC executor/deep-executor
- review → code-review plugin (4-agent)
- test → ECC tdd-workflow
- debug → OMC debugger agent
**Risk: Low — verify no plans reference `start:` prefixed skills.**

### 3. kaizen@context-engineering-kit — REMOVE (absorbed)
Root-cause-tracing, plan-do-check-act, cause-and-effect all covered by OMC + ECC:
- Iterative planning → OMC ralplan
- Self-referential loop → OMC ralph
- Root cause → OMC debugger + analyze shortcut
**Risk: Low — extract PDCA into custom skill if methodology valued.**

---

## Overlap Precedence Rules

### Code Review (4 plugins)
| Use Case | Winner |
|----------|--------|
| Pre-commit quality | code-review@claude-plugins-official (4-agent parallel) |
| Security-focused | ECC security-scan + OMC security-reviewer |
| Pipeline-integrated | OMC code-reviewer agent |
| Self-critique | reflexion:critique |

### Planning (5 plugins → 2 after removals)
| Use Case | Winner |
|----------|--------|
| Strategic pre-execution | OMC ralplan (Planner+Architect+Critic) |
| Live execution tracking | planning-with-files |

### Sub-agent Orchestration (3 plugins)
| Use Case | Winner |
|----------|--------|
| Production pipelines | OMC team pipeline |
| Experimental patterns | sadd (tree-of-thoughts, competitive) |
| Creation templates | taches-cc-resources |

### Skill Creation (4 plugins)
| Use Case | Winner |
|----------|--------|
| Create from scratch | skill-creator@claude-plugins-official |
| Evaluate quality | skill-judge@agent-toolkit |
| Create full plugins | plugin-dev@claude-plugins-official |

---

## cc-setup Agent Dedup (25 → ~10)

### KEEP (~10 unique agents)
brainstormer, docs-manager, fullstack-developer, git-manager, journal-writer, mcp-manager, project-manager, researcher, tester, ui-ux-designer

### REMOVE (~15 covered by OMC/ECC)
architect, build-error-resolver, code-reviewer, code-simplifier, database-reviewer, debugger, doc-updater, e2e-runner, go-build-resolver, go-reviewer, planner, python-reviewer, refactor-cleaner, security-reviewer, tdd-guide

---

## Custom Skills — All Unique, Keep All 3
- **cc-health**: Runs health.sh validation (no equivalent)
- **cc-sync**: Orchestrates backup/restore/diff (no equivalent)
- **cc-index**: Future Zoekt indexing placeholder (no equivalent)

---

## Context Budget Concern
~180+ skills evaluated per message from all plugins. After removing 3 plugins: ~110 skills. Still high — monitor for latency.

---

## Plugins to KEEP (14 after removals)
oh-my-claudecode, everything-claude-code, claude-mem, code-review, reflexion, sadd, skill-judge, skill-creator, taches-cc-resources, planning-with-files, plugin-dev, claude-code-setup, claude-md-management, claude-skills-troubleshooting
