---
name: building-speakwright
description: Builds, resumes, or validates the Speakwright voice-capture app from PRD.md and the .planning/ validation plan, phase by phase, advancing only when blocking gates pass against the real running system. Use when asked to build Speakwright, continue or resume its build, run a phase or gate, check build status, or write a plan's SUMMARY or a phase's VALIDATION file in this repository.
argument-hint: "[status | next | phase NN | gate ID]"
allowed-tools: Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/phase_status.py *) Bash(${CLAUDE_SKILL_DIR}/scripts/mock_scan.sh *) Bash(${CLAUDE_SKILL_DIR}/scripts/gate_evidence.sh *) Read
compatibility: Node 22+, pnpm, Python 3.9+, Playwright with Chromium; Phase 6 needs macOS with Xcode and an iOS Simulator. Keys come from environment variables.
metadata:
  verified: "2026-09-28"
---

# Building Speakwright

Build Speakwright from `PRD.md` and `.planning/`, advancing only on evidence. Each plan is an execution prompt: tasks interleaved with blocking validation gates. Nothing moves to the next plan until its gates pass against the real system.

## Iron Rule

If the real system doesn't work, fix the real system. Never create mocks, stubs, fakes, test doubles, in-memory substitutes, unit-test files, or TEST_MODE switches. Evidence comes from the running app driven the way a user drives it: Playwright against the built web app with real provider keys and a real speech recording, Maestro and `xcrun simctl` on the iOS Simulator, `curl` against the runner. `${CLAUDE_SKILL_DIR}/scripts/mock_scan.sh` must print `mock_scan: clean` before any gate verdict.

## Loop

```
- [ ] 1. phase_status.py names the next plan
- [ ] 2. Plan, BRIEF, ROADMAP entry, previous VALIDATION, and cited PRD sections read
- [ ] 3. VG-REGRESS passed (Phase 2 onward)
- [ ] 4. Each task implemented, then its gate run, evidence captured and read
- [ ] 5. SUMMARY written; phase gate and VALIDATION written after the last plan
- [ ] 6. Committed
```

1. `python3 ${CLAUDE_SKILL_DIR}/scripts/phase_status.py` prints each phase's state and the next plan.
2. Read the next `PLAN.md` fully, plus `.planning/BRIEF.md`, the ROADMAP phase entry, the previous phase's VALIDATION.md, and the PRD sections the plan cites.
3. Run the plan's `VG-REGRESS` gate first. A regression is fixed before new work.
4. For each task: implement exactly what its Action says in the named files; then run its gate: prerequisites → execute → capture evidence into `.planning/phases/<phase>/evidence/` → `${CLAUDE_SKILL_DIR}/scripts/gate_evidence.sh <evidence-dir> <files…>` → read every evidence file against the pass criteria → record the verdict. On FAIL, fix the real system and re-run the whole gate. Pass criteria are fixed in the plan; never loosen them during execution.
5. After the last task of a plan, write `<plan>-SUMMARY.md`. After the last plan of a phase, run `VG-PHASE-NN` and write `<NN>-VALIDATION.md` (templates in [reference/execution-protocol.md](reference/execution-protocol.md)).
6. Commit after each passed plan: `phase NN plan MM: <title> — gates PASS`.

Repeat until `phase_status.py` exits 0.

## Where the model skills apply

- Anthropic request code (`packages/core/providers/anthropic.ts`, `services/runner`): `prompting-opus-5-5` and `prompting-fable-5-1`. Adaptive thinking only, `output_config.effort`, no forced tool use, no prefill, no sampling parameters on Fable, `display: "updates"` with its beta header, append-only history, turn-scoped nudges.
- OpenAI request code (`packages/core/providers/openaiResponses.ts`): `prompting-gpt-6-astra`, `prompting-gpt-6-sol`, `prompting-gpt-6-luna`. Responses API, `reasoning.effort`, sampling parameters only at effort `none` on Sol and Luna, `prompt_cache_options.ttl: "30m"`.
- Prompt builder and profiles (`packages/core/prompt/`, `packages/core/profiles/<model>.yaml`): `optimizing-prompts`, whose `kit.py` audits a snapshot for any of the five models: `python3 .claude/skills/optimizing-prompts/scripts/kit.py audit snapshot.json` (the model is read from the snapshot). Every snapshot the app produces must audit with 0 errors; the Phase 4 gate depends on it.
- `services/runner` ports the behavior of `prompting-fable-5-1/scripts/agent_loop.py` (Anthropic) and `prompting-gpt-6-astra/scripts/agent_loop.py` (OpenAI): continuations, reminders, batching, append-only history, destructive guard. The Phase 7 gate audits the runner's request log the same way.
- Built-in outputs live in `packages/skills/` (14 Output Skills); keep their frontmatter as PRD §3.5 defines it.

## Secrets and hardware the gates need

Keys come from environment variables and are never committed or logged: `SPEAKWRIGHT_ANTHROPIC_KEY`, `SPEAKWRIGHT_OPENAI_KEY`, and `E2B_API_KEY` (or a Vercel Sandbox token) for Phase 7. Phase 6 needs macOS with Xcode and an iOS Simulator. When a gate needs something only the user can supply (a key, a Mac, a speech recording), finish every task that does not depend on it, record the gate as BLOCKED with the exact missing item, and stop; that is a stop the user wants.

## Stop conditions

Stop only when every phase gate has passed, or when nothing can move without the user: a missing secret or device, or a destructive or irreversible action (publishing an app build, force-pushing, deleting user data). Before stopping, write `.planning/STATE.md`: phase, plan, last gate, verdict, and the exact blocker.

## References

- [reference/execution-protocol.md](reference/execution-protocol.md): SUMMARY, VALIDATION, and STATE templates; evidence naming; commit convention; handling a failed gate.
- `scripts/phase_status.py`, `scripts/mock_scan.sh`, `scripts/gate_evidence.sh`.
- `evals/evaluations.json`: scenarios for testing this skill.
