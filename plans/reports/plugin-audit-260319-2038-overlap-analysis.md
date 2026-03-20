# Plugin Overlap Audit Report

## 17 Enabled Plugins

| # | Plugin | Primary Purpose |
|---|--------|----------------|
| 1 | `oh-my-claudecode@omc` | **Core orchestrator**: ralph, team, autopilot, ultrawork, planning, agents |
| 2 | `everything-claude-code@everything-claude-code` | **Mega skill pack**: 80+ skills (plan, tdd, security, reviews, patterns, frameworks) |
| 3 | `code-review@claude-plugins-official` | PR code review with 4 parallel agents |
| 4 | `claude-mem@thedotmack` | Persistent cross-session memory + smart code search |
| 5 | `reflexion@context-engineering-kit` | Self-refinement: reflect, critique, memorize |
| 6 | `sadd@context-engineering-kit` | Sub-agent driven development: parallel agents, judging, debate |
| 7 | `kaizen@context-engineering-kit` | Problem analysis: 5-whys, fishbone, PDCA, root cause |
| 8 | `planning-with-files@planning-with-files` | Manus-style file-based planning (task_plan.md, progress.md) |
| 9 | `skill-creator@claude-plugins-official` | Create and test skills with eval-driven feedback |
| 10 | `skill-judge@agent-toolkit` | Evaluate skill quality against best practices |
| 11 | `skills-search@daymade-skills` | Search/discover/install skills from CCPM registry |
| 12 | `claude-skills-troubleshooting@daymade-skills` | Diagnose plugin/skill loading issues |
| 13 | `taches-cc-resources@taches-cc-resources` | Meta-tools: create skills/hooks/commands/subagents/plans/prompts |
| 14 | `start@the-startup` | Specification-driven development: specify → plan → implement → test |
| 15 | `plugin-dev@claude-plugins-official` | Plugin development: create plugins, hooks, agents, skills |
| 16 | `claude-code-setup@claude-plugins-official` | Automation recommender for hooks/agents/skills |
| 17 | `claude-md-management@claude-plugins-official` | CLAUDE.md audit and improvement |

## Overlap Map

### Planning (3-way overlap)
| Capability | OMC | ECC | planning-with-files |
|-----------|-----|-----|---------------------|
| Strategic planning | `ralplan`, `omc-plan` | `plan` | `plan` |
| File-based tracking | `.omc/plans/` | — | `task_plan.md`, `progress.md` |
| Consensus loop | Yes (Planner/Architect/Critic) | No | No |
| **Verdict** | **Keep** (most sophisticated) | **Keep** (lightweight alternative) | **Consider removing** (subset of OMC) |

### Code Review (3-way overlap)
| Capability | code-review plugin | OMC agents | ECC |
|-----------|-------------------|------------|-----|
| PR review | 4 parallel agents + confidence scoring | `code-reviewer` agent | `code-review` skill |
| Security review | Agent #3 (bugs) | `security-reviewer` agent | `security-review` skill |
| **Verdict** | **Keep** (specialized PR workflow) | **Keep** (on-demand agent) | **Keep** (lightweight wrapper) |

### Skill/Plugin Creation (3-way overlap)
| Capability | skill-creator | plugin-dev | taches-cc-resources |
|-----------|--------------|------------|---------------------|
| Create skills | Yes | Yes (skill-development) | Yes (create-agent-skills) |
| Create hooks | No | Yes (hook-development) | Yes (create-hooks) |
| Create plugins | No | Yes (full plugin lifecycle) | No |
| Create subagents | No | Yes (agent-development) | Yes (create-subagents) |
| **Verdict** | **Redundant** (subset of plugin-dev) | **Keep** (most complete) | **Keep** (different approach: expert guidance) |

### Sub-agent Orchestration (2-way overlap)
| Capability | OMC | sadd |
|-----------|-----|------|
| Parallel agents | `team`, `ultrawork` | `do-in-parallel` |
| Sequential agents | `ralph` | `do-in-steps` |
| Agent judging | `verifier` | `judge`, `judge-with-debate` |
| **Verdict** | **Keep both** — OMC is team-level orchestration, sadd is task-level composition |

### Problem Analysis (2-way overlap)
| Capability | kaizen | taches-cc-resources |
|-----------|--------|---------------------|
| Root cause | `why` (5-whys), `root-cause-tracing` | `consider:5-whys` |
| Fishbone | `cause-and-effect` | — |
| PDCA | `plan-do-check-act` | — |
| **Verdict** | **Keep both** — kaizen is deeper, taches is lighter/broader |

### Debugging (2-way overlap)
| Capability | OMC | taches-cc-resources |
|-----------|-----|---------------------|
| Debug skill | `analyze` → debugger agent | `debug` (expert methodology) |
| **Verdict** | **Keep both** — different depths |

## Hook vs Plugin Overlap

| Custom Hook | Overlapping Plugin Skill | Verdict |
|------------|------------------------|---------|
| `block-test-files.js` | ECC `tdd-workflow` (enforces test-first) | **Keep hook** — hook blocks at tool level, skill is guidance |
| `plan-before-execute.js` | ECC `plan` skill trigger | **Keep hook** — hook is enforcement, skill is invocation |
| `evidence-gate-reminder.js` | ECC `verification-loop` | **Keep hook** — hook reminds on TaskUpdate, skill is workflow |
| `skill-activation-forced-eval.js` | — | **Keep** — unique, no overlap |
| `validation-not-compilation.js` | — | **Keep** — unique, no overlap |

## Recommendations

### Remove (3 candidates)
1. **`planning-with-files@planning-with-files`** — OMC's `ralplan` and `omc-plan` are strictly superior (consensus loop, staged pipeline). File-based tracking is handled by `.omc/plans/`.
2. **`skill-creator@claude-plugins-official`** — `plugin-dev` already includes skill creation plus hooks, agents, and full plugin lifecycle. Redundant.
3. **`claude-code-setup@claude-plugins-official`** — One-time automation recommender. Already used; value diminishes after initial setup.

### Keep (14 essential)
All others provide unique, non-overlapping value or complementary approaches.

### Context Budget Impact
Removing 3 plugins saves ~200-400 tokens per message from reduced skill catalog injection. Marginal but compounds over long sessions.
