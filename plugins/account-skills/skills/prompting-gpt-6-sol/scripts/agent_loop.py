#!/usr/bin/env python3
"""agent_loop.py (OpenAI Responses API): an unattended tool-use loop for the GPT-6 model described
in ./models/, applying OpenAI's GPT-6 prompting and reasoning guidance.

What the loop does, and why:
- POST /v1/responses with reasoning.effort (and reasoning.summary "auto" so progress is readable),
  function tools with strict: true, and prompt_cache_options.ttl "30m" for the instruction prefix.
- Reasoning carries across tool calls. Default: previous_response_id (stored responses), sending
  only the new function_call_output items each turn. With --stateless: store false, include
  "reasoning.encrypted_content", and replay every output item untouched; the loop checks that the
  replayed input is append-only and counts any edit.
- Instructions: the role, the project's extra rules, then the initiative, act-on-requests,
  reviewable-result, instruction-precedence, skill-debug, testing, and technical-communication
  blocks from assets/blocks. The delegation block is left out because this loop has no agents to
  delegate to.
- A turn that ends without function calls while todo items are open is treated as a report: the
  loop answers with up to K continuation messages naming the open items, then stops as
  waiting-for-user.
- status "incomplete" with reason max_output_tokens stops the run and says so; a refusal content
  item stops it as refused.
- Destructive commands are refused unless --allow-destructive is passed.

Standard library only. Needs OPENAI_API_KEY (KIT_OPENAI_BASE_URL overrides the base, e.g.
https://host/v1). Each request is logged to --log-dir with the key shown as ${OPENAI_API_KEY};
summary.json is written at the end. Exit 0 when done, 1 otherwise, 2 on a usage or environment problem.
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
from workspace import Workspace, openai_tools  # noqa: E402

BASE_ROLE = ("You are an autonomous engineer working in the directory that list_dir('.') shows. Track every part "
             "of the task with the todo tool and mark an item completed only after checking it.")
# Blocks that assume collaboration tools this loop does not provide.
SKIP_IN_LOOP = {"gpt6-delegation"}


def openai_models() -> list[str]:
    return [i for i in kit.available_models()
            if json.loads((kit.MODELS_DIR / f"{i}.json").read_text("utf-8"))["vendor"] == "openai"]


def post(url: str, body: dict, headers: dict, timeout: int) -> dict:
    req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"), headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def main(argv: list[str] | None = None) -> int:
    ids = openai_models()
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--model", choices=ids, default=ids[0] if len(ids) == 1 else None, required=len(ids) != 1)
    p.add_argument("--task", required=True, help="task text, or @FILE to read it from a file")
    p.add_argument("--system", help="file with extra instructions (skill body, project rules)")
    p.add_argument("--cwd", default=".", help="working directory the tools are confined to")
    p.add_argument("--effort", help="defaults to the model's recommended starting effort")
    p.add_argument("--max-output-tokens", type=int, help="defaults to the model's agent default")
    p.add_argument("--max-turns", type=int, default=200)
    p.add_argument("--max-continuations", type=int, default=2)
    p.add_argument("--budget-seconds", type=int, default=0, help="advisory time budget; 0 turns the time signal off")
    p.add_argument("--stateless", action="store_true", help="store false + encrypted reasoning, full replay")
    p.add_argument("--allow-destructive", action="store_true")
    p.add_argument("--log-dir", default="agent-logs")
    p.add_argument("--timeout", type=int, default=kit.DEFAULT_TIMEOUT_S)
    p.add_argument("--dry-run", action="store_true", help="write and audit the first request, then exit")
    a = p.parse_args(argv)

    m = kit.load_model(a.model)
    effort = a.effort or m["effort_guidance"]["start"]
    if effort not in m["efforts"]:
        kit.fail(f"{m['id']} does not accept effort {effort!r}; use one of {m['efforts']}")
    if effort == "none":
        kit.fail("reasoning effort 'none' turns reasoning off; agent runs need at least 'low'")
    max_out = a.max_output_tokens or m["max_output_defaults"]["agent"]
    task = Path(a.task[1:]).read_text("utf-8") if a.task.startswith("@") else a.task
    extra = Path(a.system).read_text("utf-8").strip() if a.system else ""
    b = m["blocks"]
    working = [n for n in b["working_action"] + b["working_agent_extra"] if n not in SKIP_IN_LOOP]
    sections = [f"# Role\n{BASE_ROLE}" + (f"\n\n{extra}" if extra else ""),
                "# Working style\n" + "\n\n".join(kit.blocks(working)),
                "# Writing style\n" + "\n\n".join(kit.blocks(b["writing_technical"]))]
    instructions = "\n\n".join(sections)
    continuation = kit.block(b["harness_continuation"])

    key_env = m["auth"]["env"]
    key = os.environ.get(key_env, "")
    if not a.dry_run and not key:
        kit.fail(f"{key_env} is not set")
    base = os.environ.get(m["auth"]["base_url_env"])
    url = base.rstrip("/") + "/responses" if base else m["endpoint"]
    headers = {m["auth"]["header"]: f"{m['auth']['scheme']} {key}", **m["fixed_headers"]}
    logged_headers = {**headers, m["auth"]["header"]: f"{m['auth']['scheme']} ${{{key_env}}}"}

    ws = Workspace(Path(a.cwd), a.allow_destructive)
    logs = Path(a.log_dir)
    logs.mkdir(parents=True, exist_ok=True)
    history: list[dict] = [{"role": "user", "content": task}]  # full replay (stateless mode)
    pending: list[dict] = list(history)                          # new items only (stateful mode)
    previous_id: str | None = None
    prev: list[str] = []
    stats = {"model": m["id"], "effort": effort, "mode": "stateless" if a.stateless else "previous_response_id",
             "turns": 0, "tool_calls": 0, "continuations": 0, "prefix_edits": 0, "input_tokens": 0,
             "output_tokens": 0, "cached_tokens": 0, "reasoning_tokens": 0, "cost_usd": 0.0, "status": "running"}
    t0 = time.time()

    def time_line() -> str:
        return f"elapsed {int(time.time() - t0)}s / {a.budget_seconds}s" if a.budget_seconds else ""

    for turn in range(a.max_turns):
        body: dict = {"model": m["id"], "instructions": instructions, "tools": openai_tools(),
                      "reasoning": {"effort": effort, "summary": "auto"}, "max_output_tokens": max_out,
                      m["cache"]["param"]: m["cache"]["value"]}
        if a.stateless:
            body.update({"store": False, "include": ["reasoning.encrypted_content"], "input": history})
            serialized = [json.dumps(x, sort_keys=True) for x in history]
            if serialized[:len(prev)] != prev:
                stats["prefix_edits"] += 1
            prev = serialized
        else:
            body["input"] = pending
            if previous_id:
                body["previous_response_id"] = previous_id
        logged = {"vendor": "openai", "model": m["id"], "url": url, "headers": logged_headers, "body": body}
        (logs / f"request-{turn:03d}.json").write_text(json.dumps(logged, indent=2), "utf-8")
        if a.dry_run:
            findings = kit.audit_openai(logged, m)
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
        previous_id = resp.get("id")
        u = resp.get("usage") or {}
        stats["input_tokens"] += int(u.get("input_tokens") or 0)
        stats["output_tokens"] += int(u.get("output_tokens") or 0)
        stats["cached_tokens"] += int((u.get("input_tokens_details") or {}).get("cached_tokens") or 0)
        stats["reasoning_tokens"] += int((u.get("output_tokens_details") or {}).get("reasoning_tokens") or 0)
        stats["cost_usd"] += kit.cost_usd(m, u) or 0.0  # per request: the long-context surcharge is per request

        output = resp.get("output") or []
        history.extend(output)  # replayed untouched in stateless mode
        calls, refused = [], False
        for it in output:
            t = it.get("type")
            if t == "reasoning":
                for s in it.get("summary") or []:
                    if s.get("text"):
                        print(f"[update] {s['text']}", flush=True)
            elif t == "message":
                for c in it.get("content") or []:
                    if c.get("type") == "output_text" and c.get("text"):
                        print(c["text"], flush=True)
                    elif c.get("type") == "refusal":
                        refused = True
                        stats["refusal"] = c.get("refusal")
            elif t == "function_call":
                calls.append(it)

        if resp.get("status") == "incomplete":
            stats["status"] = "incomplete: " + str((resp.get("incomplete_details") or {}).get("reason"))
            break
        if refused:
            stats["status"] = "refused"
            break

        if calls:
            outputs = []
            for it in calls:
                stats["tool_calls"] += 1
                try:
                    args = json.loads(it.get("arguments") or "{}")
                except json.JSONDecodeError as e:
                    out, err = f"arguments are not valid JSON: {e}", True
                else:
                    out, err = ws.call(it["name"], args)
                print(f"[tool] {it['name']} -> {'error' if err else 'ok'}", flush=True)
                outputs.append({"type": "function_call_output", "call_id": it["call_id"],
                                "output": ("ERROR: " if err else "") + out})
            tl = time_line()
            if tl:
                outputs[-1]["output"] += f"\n\n{tl}"
            history.extend(outputs)
            pending = outputs
            continue

        open_items = ws.open_items()
        if open_items and stats["continuations"] < a.max_continuations:
            stats["continuations"] += 1
            tl = time_line()
            msg = {"role": "user", "content": continuation.format(items="; ".join(open_items)) + (f"\n\n{tl}" if tl else "")}
            history.append(msg)
            pending = [msg]
            continue
        stats["status"] = "waiting-for-user" if open_items else "done"
        break
    else:
        stats["status"] = "max_turns"

    stats["open_items"] = ws.open_items()
    stats["elapsed_seconds"] = int(time.time() - t0)
    stats["cost_usd"] = round(stats["cost_usd"], 6)
    (logs / "summary.json").write_text(json.dumps(stats, indent=2), "utf-8")
    print("\n--- summary ---\n" + json.dumps(stats, indent=2), file=sys.stderr)
    return 0 if stats["status"] == "done" else 1


if __name__ == "__main__":
    sys.exit(main())
