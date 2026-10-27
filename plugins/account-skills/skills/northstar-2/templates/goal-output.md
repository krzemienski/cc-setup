# Output template

Emit Phase 5 in this structure. Fill every section; keep it tight. The `/goal` line must be in its own fenced block so it is one-tap copyable.

---

**Goal**

```text
/goal <the synthesized condition: one measurable end state · stated real-command checks · constraints · bound>
```

**Why this is verifiable** *(2–4 lines)*
- End state: <the single outermost signal>
- Proven by: <the commands whose output lands in the transcript>
- Guarded by: <the key constraints that block the obvious cheats>

**Run it unattended**
- Turn on auto mode so each turn runs without per-tool approvals (auto mode approves tool calls without asking — expected for an unattended loop).
- Paste the line above into the session. Setting it starts a turn immediately.
- Watch: `/goal` (no args) shows the condition, turns, token spend, and the evaluator's last reason. Stop early: `/goal clear`.

**Or one-shot / headless**
```bash
claude -p "/goal <same condition>"
```
Runs the loop to completion in one invocation; Ctrl+C interrupts.

**Or make it repeatable** *(only when the user wants this every session)*
Since `/goal` is a session-scoped Stop hook, the same condition can live as a Stop hook in settings instead — note this edits settings and applies to every session in scope.

**Heads up**
- This spends main-turn tokens every turn until the condition holds or the bound (`<N turns / T min>`) trips — the bound is what protects you.
- The evaluator only sees the transcript, so the proving command must actually run and print its result; the condition above is written to force that.
