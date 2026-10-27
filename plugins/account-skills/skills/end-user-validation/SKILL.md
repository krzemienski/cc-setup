---
name: "end-user-validation"
description: "Use after building or changing anything runnable (backend, web app, iOS app, CLI, TUI, worker, full stack) to find out whether the original goal was actually achieved. Independent verifier subagents use the real system as its end users would, judge it against the original intent and report gaps. The work is then fixed and re-verified by fresh agents until the goal is met. Use when asked to verify, validate, QA or confirm a task is done, or before declaring work complete. Not for code review or writing test suites."
---

# End-User Validation

The question is never "did the steps run?" It is **"was the thing the user
asked for actually achieved?"** Answer it the only way that counts: someone
uses the real, running product the way its end users do, compares what they
experience against the original intent, and reports what matches and what
doesn't. If it falls short, keep building until it doesn't.

That "someone" should not be the agent that did the work. An implementer who
checks its own work sees what it meant to build. A fresh agent that only knows
the goal sees what was actually built. So this skill has three parts:
capture intent, dispatch independent verifiers, then remediate and
re-verify until the goal is met.

## Principles

- **The original intent is the bar.** Not the plan, not the task list, not the
  implementer's summary. If the user asked for "a settings page where I can
  change my email and get a confirmation," then a page with an email field
  that saves silently is not done, whatever the checklist says.
- **Judge by use, not by inspection.** Reading code, confirming a file exists,
  a green test suite, or "the build passed" can suggest where to look. None of
  them show the goal was met. Test suites are regression signals, never proof.
- **Each component is used through its own front door.** An API is used with
  HTTP requests. A web UI is used by clicking in a browser. A mobile app is
  used by tapping in a simulator or on a device. A CLI is used by running the
  installed or compiled binary in a terminal. See the surface guide below.
- **Real system only.** Real server, real database, real binary. When
  something doesn't work, fix the real thing. Never add mocks, stubs, canned
  data, or test-mode switches to make verification pass.
- **Watch it work, loudly.** Run things at maximum log verbosity while they're
  being used. A UI that looks right over a log full of errors, retries and
  silent fallbacks is not done.
- **Outcome over exit code.** "Did it do what was wanted?" is answered by
  effects: the record exists, the file was written, the email was queued, the
  screen shows the right data after a reload.
- **Local by default, consent for anything real.** Verify against a local or
  dev instance. Ask the user before anyone touches production, real accounts
  or real third parties: sending email/SMS/webhooks, payments, deleting shared
  data, publishing.
- **Use scripts for mechanics, judgment for verdicts.** Use the project's own
  scripts, or small throwaway ones, for repeatable chores: starting services,
  seeding an account, capturing logs. Don't build a validation harness. Keep
  evidence proportionate: enough screenshots, responses and log excerpts to
  show what was seen, saved wherever is convenient and cited in reports.

## The loop

```
1. Capture intent   → the original goal, verbatim, plus what "done" looks like to its users
2. Map surfaces     → every part of the product the goal touches, and how its users reach it
3. Bring it up      → real system running, verbose, reachable by verifiers
4. Dispatch         → independent verifier subagents, in parallel, each given the intent
5. Synthesize       → read their reports, check the evidence behind key claims, list gaps
6. Remediate        → fix the real system for each gap (you or implementer agents)
7. Re-verify        → FRESH verifiers on the fixed areas + a whole-goal pass
   ↺ repeat 5–7 until a full round finds the goal met with no open intent gaps
8. Report           → tell the user what was verified, how, and anything still open
```

### 1. Capture intent

Find the original goal in the user's words: their message, the ticket, PRD,
plan, design mockups, screenshots of what they want. Keep it **verbatim**,
because verifiers get this, not your paraphrase.

Then, for your own use, sketch what "done" looks like from each user's side.
For example: "A signed-in user opens Settings, changes their email, sees a
confirmation message, gets a verification email, and after verifying, the new
email shows on their profile on web and iOS." Note anything ambiguous. If the
ambiguity changes what gets built, ask the user now rather than guessing
through several rounds.

### 2. Map the surfaces

List every part of the product the goal touches and who uses each. Typical
surfaces: backend API, web frontend, mobile app, CLI/TUI, background workers,
data store, third-party integrations, and the journey that crosses them. Also
map the connections: which button calls which endpoint, which command writes
which file, which job sends which email. Gaps hide most often in those
connections.

### 3. Bring the real system up

Start everything the verifiers will need, the way a user would get it:
built binaries, the installed CLI entry point, the running dev server, the
app installed on a booted simulator, databases migrated. Rebuild from clean
project caches (`.next`, `dist`, `__pycache__`, the project's DerivedData)
when stale builds could hide the change. Turn logging to
debug everywhere (`LOG_LEVEL=debug`, `RUST_LOG=debug`, `DEBUG=*`, `-vv`,
`--verbose`, and so on). Run long-lived processes somewhere their output is
captured and watchable, such as tmux sessions or log files, so verifiers can
read them.

Write down how to reach everything: URLs and ports, the simulator UDID, test
account credentials (by env var or file, never pasted into reports), log
locations, and how to restart a service. If the system won't start, that is
the first gap. Fix it before dispatching anyone.

**Pin the version under test.** Note the commit hash, build number or a
checksum of the changed files before each round. Don't change the code while
verifiers are working. If anything changes mid-round, from you, a teammate or
another process, that round's verdicts describe a version that no longer
exists. Discard them and run the round again.

### 4. Dispatch independent verifiers

Launch verifier subagents **in parallel** (multiple Agent calls in one
message). Each gets a lens and a fresh context. Shape the team to the task:

| Task size | Verifiers |
|---|---|
| Small (one surface, one behavior) | 1 verifier using it end to end, plus optionally an intent-gap skeptic |
| Medium (a feature across 2–3 surfaces) | one per surface + one full-journey verifier |
| Large (multi-surface product work) | one per surface, one per major journey, a visual/design-fidelity verifier, an intent-gap skeptic |

Useful lenses:
- **Surface verifier:** uses one component through its front door (API, web
  UI, iOS app, CLI) and judges it against the intent.
- **Journey verifier:** does the whole thing as a real user would across
  every surface, e.g. sign up on iOS → create item → see it on web → it's
  in the database.
- **Fidelity verifier:** compares what users see against the intended look
  and feel (mockups, design system, the user's description, or the platform's
  conventions) and says plainly whether it looks like it's supposed to.
- **Intent-gap skeptic:** reads the original intent and hunts for anything
  asked for that isn't there at all, is half there, or was quietly swapped for
  something easier.
- **Resilience verifier** (when it matters): tries empty/huge/invalid input,
  logged-out access, double submits, network loss, service restarts.

**What verifiers receive:** the original intent verbatim, their lens and
scope, how to reach and restart the running system, where logs are, which
test accounts or data they own, and which actions need user approval.

**What verifiers must NOT receive:** your summary of what you built, the task
checklist marked done, "I fixed X, please confirm", or expected answers. Those
anchor them to your view. They may read code to learn how to run or reach
something. Their verdict must come from using it.

**Tool fit:** a verifier can only drive what its tools can reach. Before
dispatching, make sure each one has what its surface needs: a browser tool
for web UIs, simulator control for iOS, a shell with tmux for CLIs. Choose an
agent type that has those tools. If none can reach a surface, drive that
surface yourself and say so in the final report.

**Isolation:** parallel verifiers must not trample each other. Give each its
own test account or recognizable data (e.g. a title prefix per verifier), its
own browser context, and its own simulator (or run the iOS verifiers one after
another). Don't let two of them restart the same service mid-run. Verifiers
never edit the product. They verify, and you fix. When verifiers running at
the same time expose a race in the product (lost writes, duplicate ids), that
is a real finding, not test noise: real users run concurrently too.

**Verifier prompt shape** (adapt freely; this is guidance, not a form):

```
You are verifying whether this goal was actually achieved. Judge only by
using the running product as its real users would. You did not build it and
must not fix it: don't edit any project files; write only in your own
evidence folder.

ORIGINAL INTENT (verbatim):
<user's words / ticket / design reference>

YOUR LENS: <e.g. "the web frontend, as a signed-in user" | "full journey
across iOS app, API and web" | "does the UI look as intended" | "what did the
intent ask for that's missing">

HOW TO REACH IT: <URLs, ports, simulator UDID, CLI path, how to restart,
where logs are, test account env vars you own>
NEEDS APPROVAL FIRST: <sending real email, payments, deleting shared data...>

Use it for real: <API: HTTP requests against the live server | web: click
through in a browser as a user | iOS: tap through on the simulator | CLI: run
the installed binary, in a terminal/tmux for long-running or interactive
tools>. Keep logs at debug and read them while you act. Check that actions
had their real effect (data saved, files written, requests reached the
backend), not just that screens changed.

Report:
- For each part of the intent in your lens: MET / PARTLY MET / NOT MET /
  COULD NOT VERIFY (and why)
- What you did, step by step, and what you observed (quote responses and log
  lines; describe what screenshots show; give paths to anything you saved)
- Intent gaps: what the intent wanted vs what actually happens, how serious,
  how to reproduce
- Beyond the intent: things that work as asked but would still bother a real
  user or break under realistic use; list these separately
Be blunt. "Mostly works" is a gap report, not a pass.
```

### 5. Synthesize

Read every report. For any NOT MET, and for MET claims on the parts of the
goal that matter most, look at the evidence yourself: open the screenshot,
read the quoted log, rerun the one request. Trust verifiers, but check their
work, and never let a claim with no observations behind it count.

When verifiers disagree, one says the save works and another says it
doesn't, reproduce it yourself or send a tie-breaker verifier with just that
question. Disagreement often means intermittent behavior, state leaking
between tests, or a race, and each of those is itself a gap.

Consolidate everything into one gap list, ordered by what blocks the goal
most, and sort each item into one of two buckets:
- **Intent gaps** drive the loop. These are anything the goal asked for that
  isn't achieved. They also include anything that quietly undermines it under
  normal use: data loss, a crash on ordinary input, a false success message,
  or a security hole in the new feature.
- **Beyond-intent findings** do not drive the loop. They are polish and
  hardening the goal didn't ask for (length limits, live updates, favicons).
  Fix the cheap, obvious ones if you like, but the rest go to the user as
  follow-ups. Fresh verifiers will always find something. Chasing every
  observation turns the loop into an endless audit.

For each intent gap, localize the layer: if the UI is wrong, call the API
directly. If the API is wrong, check the data and the server log. Fix at the
lowest layer that's actually broken.

### 6. Remediate

Keep writing code until each gap is closed in the real system: the actual
root cause, not a workaround that makes a verifier's check pass. Fix blocking
gaps first, since a broken API makes UI verification meaningless. Independent
gaps can go to implementer subagents in parallel, each with the gap report,
the intent, and the files involved.

After each fix, do a quick check yourself that the specific gap is gone:
repeat the verifier's reproduction steps. That is only a sanity check. The
verdict still comes from the next verification round.

Never close a gap by lowering the bar: editing the intent to match what was
built, deleting the feature that fails, or reclassifying a requirement as
"out of scope" without the user agreeing.

### 7. Re-verify with fresh eyes

Dispatch **new** verifier agents, not the same ones continued. They should
cover each area that was fixed, plus at least one whole-goal pass (journey or
skeptic), because fixes break neighbors. Give them the same original intent,
still without your list of fixes. Repeat synthesize → remediate → re-verify.

**Done** when a full round of fresh verifiers finds every part of the intent
MET, with evidence you've checked, and no open intent gaps. Beyond-intent
findings don't block done. They go into the report.

**Stop and bring the user in** when:
- the intent is ambiguous and the verifiers' findings hinge on which
  reading is right
- something external blocks you: credentials, a paid service, a physical
  device, a third party that's down
- the same gap survives three rounds (step back: the approach, not the
  patch, is probably wrong; say what you've tried)
- meeting the intent would require a trade-off the user should choose
  (breaking change, cost, data migration)

### 8. Report

Tell the user in plain terms:
- The goal as they stated it, and whether it's met.
- Per part of the goal: what was verified, by which lens, how it was used
  (e.g. "clicked through on Chrome", "tapped through on iPhone 16 simulator",
  "ran `mytool sync` for 6 min in tmux"), and what was seen.
- How many rounds it took and what was fixed along the way.
- Anything still unverified or open, and why.
- Beyond-intent findings worth doing next, briefly, so the user can choose.
- Regression suite results if run, labeled as regression, not proof.

## Surface guide: how an end user reaches each part

| Surface | Use it like its user does | Watch while doing it | Gaps that hide here |
|---|---|---|---|
| **Backend / JSON API** | Real HTTP requests (`curl -i`, httpie) against the running server with real payloads; auth and no-auth; create then read back | Server log at debug; the database after writes | Right status, wrong body; 200 with a swallowed exception; missing auth checks; pagination/ordering wrong |
| **Web frontend** | A real browser (connected browser MCP such as Claude in Chrome or Playwright, or a Playwright script), clicking and typing via visible labels; reload; back button; narrow viewport | Network requests each click fires; console errors; the server log for that click; the data after | Button fires no request or the wrong one; says "Saved" on a 4xx; stale or optimistic UI; layout differs from the design |
| **iOS / Android app** | Simulator or emulator: install the fresh build, launch, tap through via accessibility-identified elements or deep links; background and foreground; kill and relaunch | Device log stream at debug; backend log; crash reports | Works on first launch only; state lost on relaunch; wrong screen on deep link; backend errors shown as blank screens |
| **CLI (short-lived)** | The installed/compiled binary with real arguments, the way users invoke it (not `python script.py`) | stdout/stderr at `-v`/`--debug`; exit code; files and records it claims to produce | Exit 0 with partial work; misleading success message; wrong output on edge input |
| **CLI (long-running, interactive, TUI)** | Run it in a real terminal session (tmux) so it has a real TTY; send keys like a user; let it run as long as users would | Its log over the whole run, not just the end; the screen; side effects accumulating | Hangs; retries/backoff loops; silently skipped items; different behavior when not on a TTY (never pipe it to judge it) |
| **Workers / queues / cron** | Trigger a real job through the real entry point (the UI action or API call that enqueues it) | Worker log; queue depth; the output store | Job never picked up; retried forever; succeeded but wrote nothing |
| **Data layer** | Query it after user actions | Migrations applied; constraints | UI and API agree but the data is wrong or duplicated |
| **Integrations** (email, payments, webhooks, OAuth) | Sandbox or test-mode accounts of the real provider; ask before touching anything live | Provider dashboards and logs; your outbound request log | Request never sent; sent to the wrong environment; failure not surfaced to the user |
| **AI / agent features** | Real model calls with realistic inputs | Transcripts, tool calls, token use | Plausible-looking but wrong outputs; tool calls failing silently; judge quality against the intent, not just "it responded" |
| **Desktop apps** | Computer-use tools operating the real app | App log files | Same as mobile |
| **Cross-surface journey** | One user path through every surface the goal touches | All of the above | Each part works alone but the handoff between them doesn't |

## Red flags

| If you catch yourself thinking… | Instead |
|---|---|
| "I built it, I know it works, I'll verify it myself" | Dispatch someone who didn't build it. |
| "I'll tell the verifier what I changed so it knows where to look" | Give it the intent. Let it find where to look. |
| "The verifier said MET, done" | Look at the evidence behind the claims that matter. |
| "Tests pass / it compiled / the endpoint returns 200" | Those are hints. Use the product. |
| "It's close enough; the user can polish it" | Close is a gap. Fix it or tell the user explicitly. |
| "This requirement is hard; it was probably optional" | Ask the user. Don't quietly drop it. |
| "Mock this dependency so verification passes" | Fix the real system, or report it as blocked. |
| "Same verifiers can re-check my fix" | Fresh ones. The old ones are anchored. |