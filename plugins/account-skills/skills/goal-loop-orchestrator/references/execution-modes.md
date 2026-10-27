# Execution modes

`/goal` runs the same loop in three contexts. Pick by how much you want to watch and how trusted the condition is.

## Interactive (default for a new condition)

Set the goal in a normal Claude Code session. Setting it starts a turn immediately; the `◎ /goal active` indicator shows elapsed time. After each turn you can run `/goal` (no argument) to read the evaluator's latest reason.

Use when: it's the first run of a freshly written condition, the work is high-stakes, or you want to catch a bad condition early by watching the reasons. You can `/goal clear` the instant you see it going sideways.

## Auto mode pairing (makes turns unattended)

Auto mode auto-approves tool calls within a turn but does not start a new turn on its own. `/goal` starts the next turn. Run a goal **under auto mode** and the whole loop is hands-off: no per-tool prompts (auto mode) and no per-turn prompts (`/goal`).

Use when: the condition is trustworthy and you want the loop to proceed without babysitting. Confirm with the user that auto-approving tools in this workspace is acceptable before a long run — the loop will execute commands unattended. For first runs of a risky condition, consider leaving auto mode off so you approve tools and can interrupt cleanly.

## Headless / non-interactive (`-p`)

Set the goal with `-p` to run the loop to completion in a single invocation:

```bash
claude -p "/goal CHANGELOG.md has an entry for every PR merged this week"
```

Interrupt with Ctrl+C to stop before the condition is met. Useful for CI steps, scripted runs, or kicking a goal off from a terminal and walking away. Pair with a firm turn/time bound in the condition so a headless run can't go unbounded.

Use when: the condition is well-shaped and proven, and you want it to run start-to-finish without an interactive session.

## Remote Control

`/goal` also works through Remote Control, so you can start or watch a goal-driven run from a remote client. Same loop, same evaluator; the orchestration discipline (provable condition, bound, evidence surfacing) is identical.

## Resume behavior

A goal still active when a session ends is restored when you resume with `--resume` or `--continue`. The condition carries over, but the turn count, timer, and token-spend baseline **reset** on resume. A goal already achieved or cleared is not restored. So if you plan to resume, remember the bound's turn count starts over — a `stop after 20 turns` clause gives a fresh 20 after resume.

## Choosing quickly

| Situation | Mode |
| --- | --- |
| First run of a new condition | interactive, auto mode off, watch the reasons |
| Trusted condition, want it hands-off | interactive or headless under auto mode |
| Scripted / CI / fire-and-forget | headless `-p` with a firm bound |
| Driving from a remote client | Remote Control |
| Continuing after a session ended | `--resume` (bound counter resets) |
