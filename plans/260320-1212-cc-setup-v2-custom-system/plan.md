# cc-setup v2: Custom Orchestration System

**Date:** 2026-03-20
**Goal:** Replace ECC, Reflexion, taches, sadd, planning-with-files with custom skills in cc-setup
**Keep:** OMC (orchestration), claude-mem (memory)
**Target:** 3 plugins total

---

## Data-Driven Prioritization

Based on 3527 session transcripts, 11GB of JSONL data:

### Phase 1: Top 5 Skills (covers 75% of replaceable usage)
| Skill | Replaces | Invocations | Priority |
|-------|----------|-------------|----------|
| plan | ECC plan + planning-with-files | 1303 | P0 |
| reflect | reflexion:reflect | 1012 | P0 |
| orchestrate | ECC orchestrate | 190 | P0 |
| functional-validation | ECC functional-validation | 45 | P0 |
| critique | reflexion:critique | 41 | P0 |

### Phase 2: Next 5 Skills (covers 90%)
| Skill | Replaces | Invocations |
|-------|----------|-------------|
| memorize | reflexion:memorize | 56 |
| create-meta-prompt | taches | 73 |
| research | taches:research | 42 |
| e2e-validate | ECC e2e | 29 |
| skill-stocktake | ECC skill-stocktake | 216 |

### Phase 3: Remaining 5 + Agents + Commands
| Skill | Replaces | Invocations |
|-------|----------|-------------|
| simplify | ECC simplify | 13 |
| whats-next | taches:whats-next | 16 |
| gate-validation | ECC gate-validation | 10 |
| create-plan | taches:create-plan | 4 |
| do-in-steps | sadd:do-in-steps | 11 |

Plus agents: verifier, plan-checker
Plus commands: cc-reflect, cc-plan, cc-research

### Phase 4: Install.sh Fixes + Remote Deploy
- Smart merge for settings.json (preserve plugins/hooks/prefs)
- Platform awareness (macOS/Linux)
- Remove global/agents/ dead weight
- Fix diff.sh false positives
- Re-deploy to remote

### Phase 5: Plugin Disablement
Disable replaced plugins one by one, verify health after each:
1. Disable reflexion (after reflect + critique + memorize built)
2. Disable planning-with-files (after plan built)
3. Disable sadd (after do-in-steps built)
4. Disable taches (after research + create-meta-prompt + whats-next built)
5. Disable ECC (after all ECC replacements built) — biggest change, do last

---

## Approach Per Skill

For each skill:
1. Read the source implementation from the plugin cache
2. Extract the core logic (strip bloat, keep what works)
3. Write custom SKILL.md tuned to Nick's workflow
4. Test in a live session
5. Compare output quality vs original

## Success Criteria

- health.sh HEALTHY on both local and remote
- All 15 skills invokable and producing quality output
- Only 3 plugins enabled: OMC, claude-mem, cc-setup
- diff.sh shows zero unexpected diffs
- Remote deployment works via git pull + install.sh
