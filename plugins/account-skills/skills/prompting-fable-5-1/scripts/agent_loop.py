#!/usr/bin/env python3
"""agent_loop.py (Anthropic Messages API): an unattended tool-use loop that applies the harness
guidance for the Claude model described in ./models/.

What the loop does, and why:
- thinking {"type": "adaptive", "display": "updates"}; depth comes from output_config.effort.
  With "updates", text the model writes between tool calls arrives as readable thinking blocks.
- The vendor's autonomy text sits at the END of the system prompt from the first request, because
  changing the prefix mid-run invalidates earlier thinking blocks.
- Append-only history: assistant turns are replayed exactly as returned. The loop checks that each
  request's messages are a byte-identical prefix of the next request's and counts any edit.
- Per-turn nudges go in turn-scoped system messages (clear_at: next_user_message), so they leave
  no trace in the cached prefix. Models whose data file sets a batching nudge get it after every
  round of tool results; every model gets the silent-stretch reminder after N silent tool steps.
- A text-only end of turn with open todo items is treated as a report: the loop answers with up
  to K continuation messages naming the open items, then stops as waiting-for-user.
- Destructive commands are refused unless --allow-destructive is passed.
- Optional time signal ("elapsed Ns / Bs") appended to each message sent back.

Standard library only. Needs ANTHROPIC_API_KEY (KIT_ANTHROPIC_BASE_URL overrides the host).
Each request is logged to --log-dir with the key shown as ${ANTHROPIC_API_KEY}; summary.json is
written at the end. Exit 0 when done, 1 otherwise, 2 on a usage or environment problem.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kit  # noqa: E402
from workspace import Workspace, anthropic_tools  # noqa: E402

BASE_ROLE = ("You are an autonomous engineer working in the directory that list_dir('.') shows. Track every part "
             "of the task with the todo tool and mark an item completed only after checking it.")


def anthropic_models() -> list[str]:
    return [i for i in kit.available_models()
            if json.loads((kit.MODELS_DIR / f"{i}.json").read_text("utf-8"))["vendor"] == "anthropic"]


def post(url: str, body: dict, headers: dict, timeout: int) -> dict:
    req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"), headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def main(argv: list[str] | None = None) -> int:
    ids = anthropic_models()
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--model", choices=ids, default=ids[0] if len(ids) == 1 else None, required=len(ids) != 1)
    p.add_argument("--task", required=True, help="task text, or @FILE to read it from a file")
    p.add_argument("--system", help="file with extra system instructions (skill body, project rules)")
    p.add_argument("--cwd", default=".", help="working directory the tools are confined to")
    p.add_argument("--effort", help="defaults to the model's recommended starting effort")
    p.add_argument("--max-tokens", type=int, help="defaults to the model's agent default")
    p.add_argument("--max-turns", type=int, default=200)
    p.add_argument("--max-continuations", type=int, default=2)
    p.add_argument("--silent-threshold", type=int, default=5, help="tool steps with nothing readable before a reminder")
    p.add_argument("--max-reminders", type=int, default=3)
    p.add_argument("--budget-seconds", type=int, default=0, help="advisory time budget; 0 turns the time signal off")
    p.add_argument("--allow-destructive", action="store_true")
    p.add_argument("--log-dir", default="agent-logs")
    p.add_argument("--timeout", type=int, default=kit.DEFAULT_TIMEOUT_S)
    p.add_argument("--dry-run", action="store_true", help="write and audit the first request, then exit")
    a = p.parse_args(argv)

    m = kit.load_model(a.model)
    effort = a.effort or m["effort_guidance"]["start"]
    if effort not in m["efforts"]:
        kit.fail(f"{m['id']} does not accept effort {effort!r}; use one of {m['efforts']}")
    max_tokens = a.max_tokens or m["max_tokens_defaults"]["agent"]
    task = Path(a.task[1:]).read_text("utf-8") if a.task.startswith("@") else a.task
    extra = Path(a.system).read_text("utf-8").strip() if a.system else ""
    b = m["blocks"]
    system_text = "\n\n".join(x for x in [BASE_ROLE, extra, *kit.blocks(b["system_agent_before_tail"]),
                                          *kit.blocks(m["blocks_tail_agent"])] if x)
    batch_nudge = kit.block(b["harness_batch_nudge"]) if b.get("harness_batch_nudge") else ""
    silent_reminder = kit.block(b["harness_silent_reminder"])
    continuation = kit.block(b["harness_continuation"])

    key_env = m["auth"]["env"]
    key = os.environ.get(key_env, "")
    if not a.dry_run and not key:
        kit.fail(f"{key_env} is not set")
    base = os.environ.get(m["auth"]["base_url_env"])
    url = base.rstrip("/") + "/v1/messages" if base else m["endpoint"]
    beta = ",".join([m["betas"]["display_updates"], m["betas"]["turn_scoped_system"]])
    headers = {m["auth"]["header"]: key, **m["fixed_headers"], "anthropic-beta": beta}
    logged_headers = {**headers, m["auth"]["header"]: "${" + key_env + "}"}

    ws = Workspace(Path(a.cwd), a.allow_destructive)
    logs = Path(a.log_dir)
    logs.mkdir(parents=True, exist_ok=True)
    messages: list[dict] = [{"role": "user", "content": task}]
    prev: list[str] = []
    stats = {"model": m["id"], "effort": effort, "turns": 0, "tool_calls": 0, "continuations": 0, "reminders": 0,
             "prefix_edits": 0, "input_tokens": 0, "output_tokens": 0, "cache_read_input_tokens": 0,
             "cache_creation_input_tokens": 0, "status": "running"}
    silent = 0
    t0 = time.time()

    def time_line() -> str:
        return f"elapsed {int(time.time() - t0)}s / {a.budget_seconds}s" if a.budget_seconds else ""

    for turn in range(a.max_turns):
        body = {"model": m["id"], "max_tokens": max_tokens,
                "system": [{"type": "text", "text": system_text, "cache_control": {"type": "ephemeral"}}],
                "tools": anthropic_tools(), "messages": messages,
                "thinking": {**m["thinking"]["send"], "display": "updates"}, "output_config": {"effort": effort}}
        # Turn-scoped system messages stay in the history; the API clears their effect at the next
        # user message. So the whole message list must be append-only.
        serialized = [json.dumps(x, sort_keys=True) for x in messages]
        if serialized[:len(prev)] != prev:
            stats["prefix_edits"] += 1
        prev = serialized
        logged = {"vendor": "anthropic", "model": m["id"], "url": url, "headers": logged_headers, "body": body}
        (logs / f"request-{turn:03d}.json").write_text(json.dumps(logged, indent=2), "utf-8")
        if a.dry_run:
            findings = kit.audit_anthropic(logged, m)
            for lvl, msg in findings:
                print(f"{lvl:5} {msg}")
            print(f"dry run: wrote {logs / 'request-000.json'} ({len(findings)} finding(s))")
            return 1 if any(f[0] == "ERROR" for f in findings) else 0

        try:
            resp = post(url, body, headers, a.timeout)
        except urllib.error.HTTPError as e:
            stats["status"] = f"http_{e.code}"
            print(e.read().decode("utf-8", "replace"), file=sys.stderr)
            break
        except urllib.error.URLError as e:
            stats["status"] = f"network_error: {e.reason}"
            break
        stats["turns"] += 1
        u = resp.get("usage") or {}
        for k in ("input_tokens", "output_tokens", "cache_read_input_tokens", "cache_creation_input_tokens"):
            stats[k] += int(u.get(k) or 0)

        content = resp.get("content", [])
        messages.append({"role": "assistant", "content": content})  # exactly as returned
        readable = False
        for bl in content:
            if bl.get("type") == "thinking" and bl.get("thinking"):
                print(f"[update] {bl['thinking']}", flush=True)
                readable = True
            elif bl.get("type") == "text" and bl.get("text"):
                print(bl["text"], flush=True)
                readable = True
        silent = 0 if readable else silent + 1
        stop = resp.get("stop_reason")

        if stop == "tool_use":
            results: list[dict] = []
            for bl in content:
                if bl.get("type") == "tool_use":
                    stats["tool_calls"] += 1
                    out, err = ws.call(bl["name"], bl.get("input") or {})
                    print(f"[tool] {bl['name']} -> {'error' if err else 'ok'}", flush=True)
                    results.append({"type": "tool_result", "tool_use_id": bl["id"], "content": out, "is_error": err})
            tl = time_line()
            if tl:
                results.append({"type": "text", "text": tl})
            messages.append({"role": "user", "content": results})
            nudges = [batch_nudge] if batch_nudge else []
            if silent >= a.silent_threshold and stats["reminders"] < a.max_reminders:
                nudges.append(silent_reminder)
                stats["reminders"] += 1
                silent = 0
            if nudges:
                messages.append({"role": "system", "content": "\n\n".join(nudges), "clear_at": "next_user_message"})
            continue

        if stop == "refusal":
            stats["status"] = "refused"
            stats["stop_details"] = resp.get("stop_details")
            if m.get("refusal_fallback_targets"):
                stats["fallback_targets"] = m["refusal_fallback_targets"]
            break
        if stop == "max_tokens":
            stats["status"] = "max_tokens"
            break

        open_items = ws.open_items()
        if open_items and stats["continuations"] < a.max_continuations:
            stats["continuations"] += 1
            text = continuation.format(items="; ".join(open_items))
            tl = time_line()
            messages.append({"role": "user", "content": text + (f"\n\n{tl}" if tl else "")})
            continue
        stats["status"] = "waiting-for-user" if open_items else "done"
        break
    else:
        stats["status"] = "max_turns"

    stats["open_items"] = ws.open_items()
    stats["elapsed_seconds"] = int(time.time() - t0)
    c = kit.cost_usd(m, stats)
    stats["cost_usd"] = round(c, 6) if c is not None else None
    (logs / "summary.json").write_text(json.dumps(stats, indent=2), "utf-8")
    print("\n--- summary ---\n" + json.dumps(stats, indent=2), file=sys.stderr)
    return 0 if stats["status"] == "done" else 1


if __name__ == "__main__":
    sys.exit(main())
