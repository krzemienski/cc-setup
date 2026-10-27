#!/usr/bin/env python3
"""kit.py: build, audit, lint, and send requests for the model(s) described in ./models/*.json,
using the vendor prompt blocks in ../assets/blocks/. Standard library only (Python 3.9+).

Commands
  facts                      print the model's facts, effort guidance, and prices
  mark   --input FILE        wrap text as pasted content with a random 4-character id
  build  --task TEXT [...]   write a vendor request (url, headers, body) as JSON
  audit  REQUEST.json        check a request against the model's rules; exit 1 on any ERROR
  lint   PROMPT.md           check prompt text against the model's rules; exit 1 on any ERROR
  render REQUEST.json        print the request as a copy-paste prompt and a settings table
  send   REQUEST.json        send the request; print text; report usage and cost
  blocks                     list the vendor prompt blocks this skill ships

Pass --model ID when the models/ folder holds more than one model.
Exit codes: 0 ok, 1 findings with errors, 2 usage or environment problem, 3 model refusal.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import secrets
import string
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
MODELS_DIR = HERE / "models"
# Installed skill layout: scripts/kit.py + assets/blocks/. Source layout (tools/skill-source): blocks/ beside kit.py.
BLOCKS_DIR = next((d for d in (HERE.parent / "assets" / "blocks", HERE / "blocks") if d.is_dir()),
                  HERE.parent / "assets" / "blocks")

# Characters per token for rough size estimates. English prose averages about 4 characters per
# token; the estimate is only used to warn about long-context pricing thresholds.
CHARS_PER_TOKEN = 4
# Network timeout for send. Long agentic or xhigh/max turns can take several minutes.
DEFAULT_TIMEOUT_S = 600


def fail(msg: str, code: int = 2) -> None:
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(code)


# ----------------------------------------------------------------------------- loading

def available_models() -> list[str]:
    return sorted(p.stem for p in MODELS_DIR.glob("*.json"))


def load_model(model_id: str | None) -> dict[str, Any]:
    ids = available_models()
    if not ids:
        fail(f"no model files in {MODELS_DIR}")
    if model_id is None:
        if len(ids) == 1:
            model_id = ids[0]
        else:
            fail(f"several models available; pass --model with one of: {', '.join(ids)}")
    if model_id not in ids:
        fail(f"model {model_id!r} is not described here; available: {', '.join(ids)}")
    return json.loads((MODELS_DIR / f"{model_id}.json").read_text("utf-8"))


def block(name: str) -> str:
    path = BLOCKS_DIR / f"{name}.txt"
    if not path.exists():
        have = ", ".join(sorted(p.stem for p in BLOCKS_DIR.glob("*.txt")))
        fail(f"prompt block {name!r} not found in {BLOCKS_DIR}. Available: {have}")
    return path.read_text("utf-8").strip()


def blocks(names: list[str] | None) -> list[str]:
    return [block(n) for n in (names or [])]


def read_text(value: str | None) -> str:
    if not value:
        return ""
    if value == "-":
        return sys.stdin.read()
    path = Path(value)
    if not path.exists():
        fail(f"file not found: {value}")
    return path.read_text("utf-8")


def pasted_id() -> str:
    alphabet = string.ascii_lowercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(4))


def wrap_pasted(text: str) -> str:
    i = pasted_id()
    return f'<pasted_content id="{i}">\n{text.rstrip()}\n</pasted_content id="{i}">'


def input_for(a: argparse.Namespace) -> str:
    """The text to wrap as pasted content: a file's contents, or a {{SLOT}} placeholder for a reusable
    prompt template that the caller fills at run time."""
    if a.input and a.input_slot:
        fail("use --input or --input-slot, not both")
    if a.input_slot:
        if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", a.input_slot):
            fail("--input-slot takes a name like INPUT or TRANSCRIPT")
        return "{{" + a.input_slot + "}}"
    return read_text(a.input)


def load_examples(directory: str | None) -> list[dict[str, str]]:
    """Pairs NAME.input.md and NAME.output.md in a directory."""
    if not directory:
        return []
    d = Path(directory)
    if not d.is_dir():
        fail(f"examples directory not found: {directory}")
    pairs = []
    for inp in sorted(d.glob("*.input.md")):
        out = inp.with_name(inp.name.replace(".input.md", ".output.md"))
        if out.exists():
            pairs.append({"input": inp.read_text("utf-8").strip(), "output": out.read_text("utf-8").strip()})
        else:
            print(f"warning: {inp.name} has no matching .output.md; skipped", file=sys.stderr)
    return pairs


# ------------------------------------------------------------------------------- build

def build_anthropic(m: dict[str, Any], a: argparse.Namespace) -> dict[str, Any]:
    effort = a.effort or m["effort_guidance"]["start"]
    size = "agent" if a.mode == "agent" else ("long" if a.long else "chat")
    max_tokens = a.max_tokens or m["max_tokens_defaults"][size]
    input_text = input_for(a)
    b = m["blocks"]

    system = [read_text(a.system).strip() or "You are a careful assistant."]
    if input_text:
        system += blocks(b["system_when_input"])
    if a.mode == "chat":
        system += blocks(b["system_chat"])
    if a.mode == "agent" and a.progress:
        system += blocks(b["system_agent_before_tail"])
    system += blocks(a.add_block)
    if a.mode == "agent":
        # Anthropic: add the autonomy text at the END of the system prompt from the first request;
        # adding it mid-run changes the prefix and invalidates earlier thinking blocks.
        system += blocks(m["blocks_tail_agent"])
    system_text = "\n\n".join(s for s in system if s)

    user: list[str] = []
    docs = [Path(p) for p in (a.document or [])]
    if docs:
        parts = []
        for i, p in enumerate(docs, 1):
            if not p.exists():
                fail(f"document not found: {p}")
            parts.append(f'<document index="{i}">\n<source>{p.name}</source>\n<document_content>\n'
                         f'{p.read_text("utf-8").rstrip()}\n</document_content>\n</document>')
        user.append("<documents>\n" + "\n".join(parts) + "\n</documents>")
    if input_text:
        user.append(wrap_pasted(input_text))
    ex = load_examples(a.examples)
    if ex:
        user.append("<examples>\n" + "\n".join(
            f"<example>\n<input>\n{e['input']}\n</input>\n<output>\n{e['output']}\n</output>\n</example>" for e in ex
        ) + "\n</examples>")
    user.append(f"<instructions>\n{a.task.strip()}\n</instructions>")
    if a.prose:
        user += blocks(b["user_prose"])
    if effort in ("xhigh", "max"):
        user += [t.format(max_tokens=f"{max_tokens:,}") for t in blocks(b["user_long_effort"])]
    user_text = "\n\n".join(user)

    betas: list[str] = []
    thinking: dict[str, Any] = dict(m["thinking"]["send"])
    if a.display != "omitted":
        thinking["display"] = a.display
        if a.display == "updates":
            betas.append(m["betas"]["display_updates"])
    output_config: dict[str, Any] = {"effort": effort}
    if a.schema:
        output_config["format"] = {"type": "json_schema", "schema": json.loads(read_text(a.schema))}
    if a.mode == "agent":
        betas.append(m["betas"]["turn_scoped_system"])

    body: dict[str, Any] = {
        "model": m["id"],
        "max_tokens": max_tokens,
        "system": [{"type": "text", "text": system_text, "cache_control": {"type": "ephemeral"}}],
        "messages": [{"role": "user", "content": user_text}],
        "thinking": thinking,
        "output_config": output_config,
    }
    if a.stream:
        body["stream"] = True
    headers = {m["auth"]["header"]: "${" + m["auth"]["env"] + "}", **m["fixed_headers"]}
    if betas:
        headers["anthropic-beta"] = ",".join(dict.fromkeys(betas))
    return {"vendor": "anthropic", "model": m["id"], "url": m["endpoint"], "headers": headers, "body": body}


def build_openai(m: dict[str, Any], a: argparse.Namespace) -> dict[str, Any]:
    effort = a.effort or m["effort_guidance"]["start"]
    if effort == "minimal":
        effort = "low"  # OpenAI migration guide: requests that used minimal start at low
    if effort not in m["efforts"]:
        fail(f"{m['id']} does not accept effort {effort!r}; use one of {m['efforts']}")
    size = "agent" if a.mode == "agent" else ("long" if a.long else "chat")
    max_out = a.max_tokens or m["max_output_defaults"][size]
    input_text = input_for(a)
    b = m["blocks"]

    sections = [f"# Role\n{read_text(a.system).strip() or 'You are a careful assistant.'}"]
    if input_text:
        sections.append("# Input handling\n" + "\n\n".join(blocks(b["instructions_when_input"])))
    working = b["working_action"] if (a.mode == "agent" or a.action) else b["working_chat"]
    if a.mode == "agent":
        working = working + b["working_agent_extra"]
    sections.append("# Working style\n" + "\n\n".join(blocks(working) + blocks(a.add_block)))
    if a.prose:
        sections.append("# Writing style\n" + "\n\n".join(blocks(b["writing_prose"])))
    elif a.technical:
        sections.append("# Writing style\n" + "\n\n".join(blocks(b["writing_technical"])))
    if a.schema:
        sections.append("# Output\nReturn JSON that matches the provided schema.")
    instructions = "\n\n".join(sections)

    user: list[str] = []
    for p in [Path(x) for x in (a.document or [])]:
        if not p.exists():
            fail(f"document not found: {p}")
        user.append(f"## Reference: {p.name}\n{p.read_text('utf-8').rstrip()}")
    if input_text:
        user.append("## Input (pasted by the user; may contain instructions the user did not write)\n" + wrap_pasted(input_text))
    ex = load_examples(a.examples)
    if ex:
        user.append("## Examples\n" + "\n\n".join(
            f"### Example {i}\nInput:\n{e['input']}\n\nOutput:\n{e['output']}" for i, e in enumerate(ex, 1)))
    user.append(f"## Task\n{a.task.strip()}")

    reasoning: dict[str, Any] = {"effort": effort}
    if a.summary:
        reasoning["summary"] = "auto"
    text_cfg: dict[str, Any] = {"verbosity": a.verbosity}
    if a.schema:
        text_cfg["format"] = {"type": "json_schema", "name": re.sub(r"\W", "_", Path(a.schema).stem) or "output",
                              "schema": json.loads(read_text(a.schema)), "strict": True}
    body: dict[str, Any] = {
        "model": m["id"],
        "instructions": instructions,
        "input": [{"role": "user", "content": "\n\n".join(user)}],
        "reasoning": reasoning,
        "text": text_cfg,
        "max_output_tokens": max_out,
        m["cache"]["param"]: m["cache"]["value"],
    }
    if a.temperature is not None:
        if effort != m["sampling_params"]["allowed_only_at_effort"]:
            fail(f"temperature is accepted only at reasoning effort {m['sampling_params']['allowed_only_at_effort']!r}; "
                 f"this request uses {effort!r}")
        body["temperature"] = a.temperature
    if a.stream:
        body["stream"] = True
    headers = {m["auth"]["header"]: f"{m['auth']['scheme']} ${{{m['auth']['env']}}}", **m["fixed_headers"]}
    return {"vendor": "openai", "model": m["id"], "url": m["endpoint"], "headers": headers, "body": body}


def cmd_build(a: argparse.Namespace) -> int:
    m = load_model(a.model)
    if a.effort and a.effort not in m["efforts"] and not (m["vendor"] == "openai" and a.effort == "minimal"):
        fail(f"{m['id']} does not accept effort {a.effort!r}; use one of {m['efforts']}")
    if a.temperature is not None and m["vendor"] == "anthropic":
        fail(f"{m['id']} keeps thinking on, so sampling parameters are not sent; remove --temperature")
    req = build_anthropic(m, a) if m["vendor"] == "anthropic" else build_openai(m, a)
    text = json.dumps(req, indent=2, ensure_ascii=False)
    if a.out:
        Path(a.out).write_text(text + "\n", encoding="utf-8")
        print(f"wrote {a.out} ({m['id']}, effort {req['body'].get('output_config', req['body'].get('reasoning', {})).get('effort')})")
    else:
        print(text)
    return 0


# ------------------------------------------------------------------------------- audit

REASONING_EXTRACTION = re.compile(
    r"(show|write out|explain|include|output|print)\s+(all\s+of\s+)?(your|the)\s+(full\s+|internal\s+|step[- ]by[- ]step\s+)?"
    r"(reasoning|chain[- ]of[- ]thought|thinking|thought process)", re.I)
THINK_CAREFULLY = re.compile(r"\bthink (carefully|step[- ]by[- ]step|hard)\b|\blet'?s think\b", re.I)
EMPHATIC = re.compile(r"\b(CRITICAL|IMPORTANT)\b[^.\n]{0,40}\bMUST\b")
ANTI_FORMAT = re.compile(r"avoid_excessive_markdown|(never|don'?t|do not)\b[^.\n]{0,30}\b(markdown|bullet|lists?)\b", re.I)
COMPILE_CHECK = re.compile(r"\b(does|will|would|can) (this|the|it)\b[^.?\n]{0,40}\bcompile\b", re.I)
PASTED_OPEN = re.compile(r'<pasted_content id="([a-z0-9]+)">')
PASTED_CLOSE = re.compile(r'</pasted_content id="([a-z0-9]+)">')


def strip_pasted(text: str) -> str:
    return re.sub(r'<pasted_content id="([a-z0-9]+)">.*?</pasted_content id="\1">', "", text, flags=re.S)


def texts(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(b.get("text", "") or b.get("output", "") or "" for b in content if isinstance(b, dict))
    return ""


def common_text_findings(prompt_text: str, m: dict[str, Any]) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    opens, closes = PASTED_OPEN.findall(prompt_text), PASTED_CLOSE.findall(prompt_text)
    if sorted(opens) != sorted(closes):
        out.append(("ERROR", "pasted_content opening and closing ids do not match; each block needs the same id on both tags."))
    outside = strip_pasted(prompt_text)
    if REASONING_EXTRACTION.search(outside):
        if m["vendor"] == "anthropic":
            out.append(("WARN", "the prompt asks the model to write out its reasoning; Claude can decline this with the "
                                "reasoning_extraction refusal category. Ask for the conclusion and its justification, and "
                                "read summarized thinking (thinking.display 'summarized') if you need the reasoning."))
        else:
            out.append(("WARN", "the prompt asks the model to write out its reasoning; GPT-6 reasons internally. Request "
                                "reasoning.summary 'auto' instead of reasoning in the answer."))
    if THINK_CAREFULLY.search(outside):
        out.append(("WARN", "'think step by step / carefully' adds latency without a reliable gain on this reasoning "
                            "model; control depth with effort instead."))
    if m.get("lint", {}).get("compile_check_warn") and COMPILE_CHECK.search(outside):
        out.append(("WARN", "compile-check phrasing raises safeguard false positives on this model; ask "
                            "'Are there any bugs in this program?' instead (Anthropic, Reduce safeguard false positives)."))
    if EMPHATIC.search(outside):
        out.append(("WARN", "emphatic trigger language (CRITICAL ... MUST) causes tool overtriggering on current models; "
                            "write 'Use <tool> when <condition>, because <reason>.'"))
    return out


def audit_anthropic(req: dict[str, Any], m: dict[str, Any]) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    b = req.get("body", {})
    h = {k.lower(): v for k, v in req.get("headers", {}).items()}
    betas = {x.strip() for x in h.get("anthropic-beta", "").split(",") if x.strip()}
    if b.get("model") != m["id"]:
        out.append(("ERROR", f"body.model is {b.get('model')!r}; this skill audits {m['id']!r}."))
    th = b.get("thinking") or {}
    if th.get("type") in m["thinking"]["forbidden_types"] or any(k in th for k in m["thinking"]["forbidden_keys"]):
        out.append(("ERROR", f"thinking {th} returns 400: {m['display']} always thinks. Send {{\"type\": \"adaptive\"}} "
                             "(or omit thinking) and control depth with output_config.effort."))
    effort = (b.get("output_config") or {}).get("effort")
    if effort is None:
        out.append(("WARN", f"output_config.effort is not set, so the default {m['default_effort']!r} applies. Set it explicitly."))
    elif effort not in m["efforts"]:
        out.append(("ERROR", f"effort {effort!r} is not valid; use one of {m['efforts']}. ('adaptive' is a thinking mode, not an effort.)"))
    tc = (b.get("tool_choice") or {}).get("type")
    if tc in m["forbidden_tool_choice"]:
        out.append(("ERROR", f"tool_choice {tc!r} returns 400 on {m['display']}. Keep 'auto', set strict: true on the tool, "
                             "and say in the prompt when to use it; or move the schema to output_config.format."))
    for t in b.get("tools") or []:
        if isinstance(t, dict) and t.get("type") in m.get("forbidden_tool_types", []):
            out.append(("ERROR", f"tool type {t['type']!r} is rejected on the Claude API for {m['display']}; use "
                                 "computer_toolset_20260801."))
    if "output_format" in b:
        out.append(("WARN", "output_format is deprecated; move the schema to output_config.format."))
    for k in m["sampling_params"]["keys"]:
        if k in b:
            out.append((m["sampling_params"]["level"], f"remove {k}: {m['sampling_params']['why']}"))
    msgs = b.get("messages") or []
    if msgs and msgs[-1].get("role") == "assistant":
        out.append(("ERROR", "the last message is an assistant prefill, which returns 400. Put continuation text in a user "
                             "message ('Your previous response ended with …; continue from there.') or use output_config.format."))
    mt = b.get("max_tokens", 0)
    if mt > m["max_output_tokens"]:
        out.append(("ERROR", f"max_tokens {mt:,} exceeds the {m['max_output_tokens']:,} maximum."))
    elif mt < m["max_tokens_warn_below"]:
        out.append(("WARN", f"max_tokens {mt:,} is below {m['max_tokens_warn_below']:,}; thinking counts toward it and "
                            "can cut the reply off. " + m["max_tokens_defaults"]["_why"]))
    if th.get("display") == "updates" and m["betas"]["display_updates"] not in betas:
        out.append(("ERROR", f"thinking.display 'updates' needs the anthropic-beta header {m['betas']['display_updates']}."))
    if any(x.get("clear_at") for x in msgs) and m["betas"]["turn_scoped_system"] not in betas:
        out.append(("ERROR", f"clear_at on a system message needs the anthropic-beta header {m['betas']['turn_scoped_system']}."))
    if any(x.get("role") == "system" and "output_config" in x for x in msgs) and m["betas"]["per_message_effort"] not in betas:
        out.append(("ERROR", f"a per-message effort change needs the anthropic-beta header {m['betas']['per_message_effort']}."))
    if "block_binding" in th and m["betas"]["thinking_binding"] not in betas:
        out.append(("ERROR", f"thinking.block_binding needs the anthropic-beta header {m['betas']['thinking_binding']}."))

    system_text = texts(b.get("system"))
    user_text = "\n".join(texts(x.get("content")) for x in msgs if x.get("role") == "user")
    out += common_text_findings(system_text + "\n" + user_text, m)
    if PASTED_OPEN.search(user_text) and "<pasted_content> tags was pasted" not in system_text:
        out.append(("WARN", "pasted content is present but the system prompt lacks the pasted-content note; add "
                            "assets/blocks/pasted-content-note.txt."))
    if m["lint"]["anti_formatting_block_warn"] and ANTI_FORMAT.search(strip_pasted(system_text)):
        out.append(("WARN", f"{m['display']} already formats less than earlier models; an anti-formatting rule can remove "
                            "structure the content needs. Use assets/blocks/fable-formatting-in-chat.txt instead."))
    if effort in ("xhigh", "max") and "counts toward a single limit" not in user_text:
        out.append(("WARN", "xhigh/max effort without the one-limit note at the end of the user message; long deliverables "
                            "may be drafted twice. Add assets/blocks/one-limit-note.txt with the real max_tokens."))
    sysblocks = b.get("system") if isinstance(b.get("system"), list) else []
    if not any(isinstance(x, dict) and x.get("cache_control") for x in sysblocks):
        out.append(("INFO", "no cache_control on the system block, so the stable prefix will not be cached."))
    return out


def audit_openai(req: dict[str, Any], m: dict[str, Any]) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    b = req.get("body", {})
    url = req.get("url", "")
    chat = url.endswith("/chat/completions")
    if b.get("model") != m["id"]:
        out.append(("ERROR", f"body.model is {b.get('model')!r}; this skill audits {m['id']!r}."))
    effort = b.get("reasoning_effort") if chat else (b.get("reasoning") or {}).get("effort")
    if not chat and "reasoning_effort" in b:
        out.append(("ERROR", "reasoning_effort is the Chat Completions name; the Responses API uses reasoning.effort."))
    if effort is None:
        out.append(("WARN", f"reasoning effort is not set; set it explicitly (this skill starts at {m['effort_guidance']['start']!r})."))
    elif effort == "minimal":
        out.append(("ERROR", f"{m['display']} does not list 'minimal'; OpenAI's migration guide says to start with 'low'."))
    elif effort not in m["efforts"]:
        out.append(("ERROR", f"effort {effort!r} is not accepted by {m['display']}; use one of {m['efforts']}."))
    allowed_at = m["sampling_params"]["allowed_only_at_effort"]
    if effort not in (None, allowed_at):
        for k in m["sampling_params"]["keys"]:
            if k in b:
                out.append(("ERROR", f"remove {k}: sampling parameters are rejected unless reasoning effort is {allowed_at!r}."))
        if "message.output_text.logprobs" in (b.get("include") or []):
            out.append(("ERROR", "remove message.output_text.logprobs from include while reasoning."))
    if chat and b.get("tools"):
        rule = m.get("chat_completions_tools")
        if rule == "forbidden":
            out.append(("ERROR", f"{m['display']} tool calling requires the Responses API (/v1/responses)."))
        elif rule == "only_at_none" and effort != "none":
            out.append(("ERROR", f"{m['display']} supports Chat Completions function calling only with reasoning_effort 'none'; use Responses."))
    if m["cache"]["replaced"] in b:
        out.append(("ERROR", f"{m['cache']['replaced']} was replaced by {m['cache']['param']}.ttl ('30m') for GPT-6."))
    if not chat and m["cache"]["param"] not in b:
        out.append(("INFO", f"no {m['cache']['param']}; set ttl '30m' so the instruction prefix stays cached."))
    mo = b.get("max_output_tokens")
    w = m["max_output_warn"]
    if mo is not None and mo < w["below"] and effort in w["at_efforts"]:
        out.append(("WARN", f"max_output_tokens {mo:,} at effort {effort!r} is below {w['below']:,}. " + m["_max_output_why"]))
    if mo is not None and mo > m["max_output_tokens"]:
        out.append(("ERROR", f"max_output_tokens {mo:,} exceeds the {m['max_output_tokens']:,} maximum."))
    fmt = (b.get("text") or {}).get("format") or {}
    if fmt.get("type") == "json_schema" and not fmt.get("strict"):
        out.append(("WARN", "json_schema without strict: true; the output may drift from the schema."))
    items = b.get("input") if isinstance(b.get("input"), list) else []
    kinds = [x.get("type") for x in items if isinstance(x, dict)]
    for i in range(1, len(kinds)):
        if kinds[i] == kinds[i - 1] == "configuration_update":
            out.append(("ERROR", "two configuration_update items are adjacent; the API rejects back-to-back updates."))
            break
    if kinds and kinds[-1] == "configuration_update":
        out.append(("ERROR", "the request ends with a configuration_update item; put it before the next user or tool item."))
    instructions = b.get("instructions", "") or ""
    if "precedence over guidelines provided in a skill" not in instructions:
        out.append(("WARN", "no instruction-precedence line; GPT-6 can stall on conflicting skill guidance. Add "
                            "assets/blocks/gpt6-instruction-precedence.txt."))
    user_text = b["input"] if isinstance(b.get("input"), str) else "\n".join(texts(x.get("content")) for x in items if isinstance(x, dict))
    out += common_text_findings(instructions + "\n" + user_text, m)
    est = (len(instructions) + len(user_text)) // CHARS_PER_TOKEN
    lc = m["long_context_surcharge"]
    if est > lc["over_input_tokens"]:
        out.append(("INFO", f"about {est:,} input tokens (estimated at {CHARS_PER_TOKEN} characters per token); over "
                            f"{lc['over_input_tokens']:,} input tokens is billed at {lc['input_multiplier']}x input and "
                            f"{lc['output_multiplier']}x output."))
    return out


def cmd_audit(a: argparse.Namespace) -> int:
    path = Path(a.request)
    if not path.exists():
        fail(f"request file not found: {a.request}")
    req = json.loads(path.read_text("utf-8"))
    m = load_model(a.model or req.get("model") or (req.get("body") or {}).get("model"))
    findings = audit_anthropic(req, m) if m["vendor"] == "anthropic" else audit_openai(req, m)
    for level, msg in findings:
        print(f"{level:5} {msg}")
    errors = sum(1 for f in findings if f[0] == "ERROR")
    warns = sum(1 for f in findings if f[0] == "WARN")
    print(f"audit [{m['id']}]: {errors} error(s), {warns} warning(s)")
    return 1 if errors else 0


# -------------------------------------------------------------------------------- lint

def cmd_lint(a: argparse.Namespace) -> int:
    m = load_model(a.model)
    text = read_text(a.prompt)
    findings = common_text_findings(text, m)
    scan = strip_pasted(text)
    if re.search(r"\b(temperature|top_p|top_k)\b\s*[:=]", scan, re.I):
        level = "ERROR" if m["vendor"] == "anthropic" and m["sampling_params"]["level"] == "ERROR" else "WARN"
        findings.append((level, "the prompt sets sampling parameters; remove them (Claude keeps thinking on; GPT-6 rejects "
                                "them unless reasoning effort is 'none')."))
    if re.search(r"(start|begin) your (response|answer|reply) with\s*[\"']", scan, re.I):
        findings.append(("WARN", "the prompt relies on a forced opening; prefill is unsupported on current Claude models. "
                                 "State the format or use a JSON schema."))
    if re.search(r"\b(never|don'?t|do not)\b[^.\n]{0,40}\b(markdown|bullets?|lists?)\b", scan, re.I):
        findings.append(("WARN", "formatting is stated as a prohibition; say what to produce instead (for example, "
                                 "'Write short prose paragraphs; use a list only for parallel items.')."))
    if m["vendor"] == "anthropic" and m["lint"]["anti_formatting_block_warn"] and "avoid_excessive_markdown" in scan:
        findings.append(("WARN", f"{m['display']} already formats less; remove the markdown-suppression block."))
    if re.search(r"(hold|save) (all )?(findings|updates) (for|until) the (final|end)", scan, re.I):
        findings.append(("WARN", "the prompt suppresses progress narration; long agent turns will look silent."))
    if not a.fragment:
        if m["vendor"] == "anthropic" and not re.search(r"<(instructions|context|examples?|documents?|input)>", text):
            findings.append(("WARN", "no XML structure; wrap instructions, context, examples, and input in tags."))
        if m["vendor"] == "openai":
            if not re.search(r"^#{1,3} ", text, re.M):
                findings.append(("WARN", "no Markdown sections; use # Role, # Task, # Input handling, # Output, # Style."))
            if "precedence" not in text.lower():
                findings.append(("INFO", "no instruction-precedence line (assets/blocks/gpt6-instruction-precedence.txt)."))
        if re.search(r"\{\{\s*input\s*\}\}|\$INPUT", text) and "pasted_content" not in text:
            findings.append(("INFO", "the runtime input slot is not wrapped as pasted content."))
        n = len(re.findall(r"<example>|^#{2,4} Example", text, re.M))
        if 0 < n < 3:
            findings.append(("INFO", f"{n} example(s); 3 to 5 relevant, diverse examples work best."))
    for level, msg in findings:
        print(f"{level:5} {msg}")
    errors = sum(1 for f in findings if f[0] == "ERROR")
    print(f"lint [{m['id']}]: {errors} error(s), {sum(1 for f in findings if f[0] == 'WARN')} warning(s)")
    return 1 if errors else 0


# -------------------------------------------------------------------------------- send

def resolve_headers(headers: dict[str, str]) -> dict[str, str]:
    out = {}
    for k, v in headers.items():
        for var in re.findall(r"\$\{([A-Z0-9_]+)\}", v):
            val = os.environ.get(var)
            if not val:
                fail(f"environment variable {var} is not set; export it or put it in your shell profile")
            v = v.replace("${" + var + "}", val)
        out[k] = v
    return out


def cost_usd(m: dict[str, Any], usage: dict[str, Any]) -> float | None:
    p = m.get("pricing_usd_per_mtok") or {}
    if not p or not usage:
        return None
    if m["vendor"] == "anthropic":
        return (usage.get("input_tokens", 0) * p["input"] + usage.get("output_tokens", 0) * p["output"]
                + (usage.get("cache_read_input_tokens") or 0) * p["cache_read"]
                + (usage.get("cache_creation_input_tokens") or 0) * p["cache_write_5m"]) / 1e6
    cached = ((usage.get("input_tokens_details") or {}).get("cached_tokens") or 0)
    total_in = usage.get("input_tokens", 0)
    lc = m.get("long_context_surcharge") or {}
    in_mult = lc.get("input_multiplier", 1) if total_in > lc.get("over_input_tokens", float("inf")) else 1
    out_mult = lc.get("output_multiplier", 1) if in_mult != 1 else 1
    return ((total_in - cached) * p["input"] * in_mult + cached * p["cached_input"] * in_mult
            + usage.get("output_tokens", 0) * p["output"] * out_mult) / 1e6


def cmd_send(a: argparse.Namespace) -> int:
    req = json.loads(Path(a.request).read_text("utf-8"))
    m = load_model(req.get("model") or req["body"].get("model"))
    body = dict(req["body"])
    body.pop("stream", None)
    url = req["url"]
    base = os.environ.get(m["auth"]["base_url_env"])
    if base:
        url = base.rstrip("/") + ("/v1/messages" if m["vendor"] == "anthropic" else "/responses")
    http = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"),
                                  headers=resolve_headers(req["headers"]), method="POST")
    t0 = time.time()
    try:
        with urllib.request.urlopen(http, timeout=a.timeout) as r:
            resp = json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")
        print(f"HTTP {e.code} from {url}\n{detail}", file=sys.stderr)
        if e.code in (401, 403):
            print(f"Check {m['auth']['env']}: the key is missing, invalid, or lacks access to {m['id']}.", file=sys.stderr)
        elif e.code == 400:
            print("Run `kit.py audit` on the request; most 400s are rules the audit reports.", file=sys.stderr)
        elif e.code == 429 or e.code >= 500:
            print("Rate limit or server error; retry after a pause.", file=sys.stderr)
        return 2
    except urllib.error.URLError as e:
        fail(f"could not reach {url}: {e.reason}")
    ms = int((time.time() - t0) * 1000)
    if a.out:
        Path(a.out).write_text(json.dumps(resp, indent=2), encoding="utf-8")
    usage = resp.get("usage") or {}
    if m["vendor"] == "anthropic":
        content = resp.get("content", [])
        text = "\n".join(x.get("text", "") for x in content if x.get("type") == "text")
        summary = {"stop_reason": resp.get("stop_reason"), "stop_details": resp.get("stop_details"),
                   "progress_updates": [x["thinking"] for x in content if x.get("type") == "thinking" and x.get("thinking")]}
    else:
        text = resp.get("output_text") or "\n".join(
            c.get("text", "") for it in resp.get("output", []) if it.get("type") == "message"
            for c in it.get("content", []) if c.get("type") == "output_text")
        summary = {"status": resp.get("status"), "incomplete_details": resp.get("incomplete_details"),
                   "reasoning_summaries": [s.get("text") for it in resp.get("output", []) if it.get("type") == "reasoning"
                                           for s in (it.get("summary") or [])]}
    c = cost_usd(m, usage)
    summary.update({"usage": usage, "latency_ms": ms, "cost_usd": round(c, 6) if c is not None else None})
    print(text)
    print("\n--- send summary ---\n" + json.dumps(summary, indent=2), file=sys.stderr)
    return 3 if summary.get("stop_reason") == "refusal" else 0


# ------------------------------------------------------------------------------ render

def cmd_render(a: argparse.Namespace) -> int:
    """Print a built request as the prompt a person copies: the text blocks, then a settings table."""
    path = Path(a.request)
    if not path.exists():
        fail(f"request file not found: {a.request}")
    req = json.loads(path.read_text("utf-8"))
    b = req.get("body", {})
    m = load_model(req.get("model") or b.get("model"))
    fence = "````" if "```" in json.dumps(b) else "```"
    out: list[str] = [f"## Prompt for {m['display']} (`{m['id']}`)", ""]
    if m["vendor"] == "anthropic":
        parts = [("System prompt", texts(b.get("system")))]
        for i, msg in enumerate(b.get("messages") or [], 1):
            label = "User message" if msg.get("role") == "user" else f"{msg.get('role', 'message').title()} message"
            parts.append((label if len(b.get("messages")) == 1 else f"{label} {i}", texts(msg.get("content"))))
        th, oc = b.get("thinking") or {}, b.get("output_config") or {}
        settings = [("Endpoint", req.get("url", m["endpoint"])), ("model", b.get("model")),
                    ("output_config.effort", oc.get("effort", f"(default {m['default_effort']})")),
                    ("max_tokens", f"{b.get('max_tokens', 0):,}"),
                    ("thinking", json.dumps(th) if th else "adaptive (default)")]
        if oc.get("format"):
            settings.append(("output_config.format", "json_schema (see request file)"))
        beta = {k.lower(): v for k, v in req.get("headers", {}).items()}.get("anthropic-beta")
        if beta:
            settings.append(("anthropic-beta", beta))
        settings.append(("Not sent", "temperature, top_p, top_k, assistant prefill, forced tool_choice"))
    else:
        inp = b.get("input")
        user = inp if isinstance(inp, str) else "\n\n".join(texts(x.get("content")) for x in (inp or []) if isinstance(x, dict))
        parts = [("Instructions", b.get("instructions", "")), ("Input", user)]
        r, t = b.get("reasoning") or {}, b.get("text") or {}
        settings = [("Endpoint", req.get("url", m["endpoint"])), ("model", b.get("model")),
                    ("reasoning.effort", r.get("effort")), ("text.verbosity", t.get("verbosity", "medium")),
                    ("max_output_tokens", f"{b.get('max_output_tokens', 0):,}")]
        if r.get("summary"):
            settings.append(("reasoning.summary", r["summary"]))
        if t.get("format"):
            settings.append(("text.format", "json_schema, strict (see request file)"))
        cache = m["cache"]["param"]
        if cache in b:
            settings.append((cache, json.dumps(b[cache])))
        if "temperature" in b:
            settings.append(("temperature", str(b["temperature"])))
    for label, text in parts:
        out += [f"### {label}", "", fence + "text", text.rstrip(), fence, ""]
    out += ["### Settings", "", "| Setting | Value |", "|---|---|"]
    out += [f"| {k} | `{v}` |" for k, v in settings]
    slots = sorted(set(re.findall(r"\{\{([A-Za-z][A-Za-z0-9_]*)\}\}", "\n".join(t for _, t in parts))))
    if slots:
        out += ["", "Fill " + ", ".join(f"`{{{{{x}}}}}`" for x in slots) + " at run time; keep the pasted_content tags around it."]
    print("\n".join(out))
    return 0


# ------------------------------------------------------------------------ small commands

def cmd_facts(a: argparse.Namespace) -> int:
    m = load_model(a.model)
    g = m["effort_guidance"]
    print(f"{m['display']} ({m['id']}), verified {m['verified']}")
    print(f"  endpoint     {m['endpoint']}")
    print(f"  efforts      {', '.join(m['efforts'])}; default {m['default_effort']}; start at {g['start']}, "
          f"try {g['try_lower']}, reserve {', '.join(g['reserve'])}")
    print(f"  why          {g['_why']}")
    print(f"  context      {m['context_tokens']:,} tokens; max output {m['max_output_tokens']:,}")
    print(f"  price/MTok   " + ", ".join(f"{k} ${v}" for k, v in m["pricing_usd_per_mtok"].items()))
    if m.get("use_for"):
        print(f"  use for      {m['use_for']}")
    if m.get("refusal_fallback_targets"):
        print(f"  fallback     {', '.join(m['refusal_fallback_targets'])}")
    for k, v in m["sources"].items():
        print(f"  source       {k}: {v}")
    return 0


def cmd_blocks(_: argparse.Namespace) -> int:
    for p in sorted(BLOCKS_DIR.glob("*.txt")):
        first = p.read_text("utf-8").strip().split("\n")[0]
        print(f"{p.stem:40} {first[:90]}{'…' if len(first) > 90 else ''}")
    return 0


def cmd_mark(a: argparse.Namespace) -> int:
    print(wrap_pasted(read_text(a.input)))
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="kit.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--model", help="model id when models/ holds several")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("facts").set_defaults(fn=cmd_facts)
    sub.add_parser("blocks").set_defaults(fn=cmd_blocks)
    mk = sub.add_parser("mark"); mk.add_argument("--input", required=True); mk.set_defaults(fn=cmd_mark)

    b = sub.add_parser("build", help="write a request")
    b.add_argument("--task", required=True, help="the instruction, placed last")
    b.add_argument("--system", help="file with the role or skill body (or - for stdin)")
    b.add_argument("--input", help="file with pasted or transcribed input; wrapped as pasted content")
    b.add_argument("--input-slot", help="build a reusable template: a {{NAME}} placeholder wrapped as pasted content")
    b.add_argument("--document", action="append", help="reference document; repeatable; placed before the input")
    b.add_argument("--examples", help="folder of NAME.input.md / NAME.output.md pairs")
    b.add_argument("--schema", help="JSON schema file for structured output")
    b.add_argument("--effort")
    b.add_argument("--max-tokens", type=int, help="max_tokens (Anthropic) or max_output_tokens (OpenAI)")
    b.add_argument("--mode", choices=["chat", "agent"], default="chat")
    b.add_argument("--long", action="store_true", help="long deliverable: larger default token limit")
    b.add_argument("--add-block", action="append", help="add a named block from assets/blocks (see `blocks`)")
    b.add_argument("--prose", action="store_true", help="prose deliverable: add the writing-style block(s)")
    b.add_argument("--display", choices=["omitted", "summarized", "updates"], default="omitted", help="Anthropic thinking.display")
    b.add_argument("--progress", action="store_true", help="Anthropic agent mode: ask for user-facing progress updates")
    b.add_argument("--action", action="store_true", help="OpenAI: add the initiative blocks in chat mode")
    b.add_argument("--technical", action="store_true", help="OpenAI: add the technical-communication block")
    b.add_argument("--verbosity", choices=["low", "medium", "high"], default="medium", help="OpenAI text.verbosity")
    b.add_argument("--summary", action="store_true", help="OpenAI: request reasoning summaries")
    b.add_argument("--temperature", type=float, help="OpenAI Sol/Luna at effort none only")
    b.add_argument("--stream", action="store_true")
    b.add_argument("-o", "--out")
    b.set_defaults(fn=cmd_build)

    au = sub.add_parser("audit"); au.add_argument("request"); au.set_defaults(fn=cmd_audit)
    rn = sub.add_parser("render", help="print a built request as a copy-paste prompt plus settings")
    rn.add_argument("request"); rn.set_defaults(fn=cmd_render)
    li = sub.add_parser("lint"); li.add_argument("prompt")
    li.add_argument("--fragment", action="store_true", help="text is a body a builder wraps; skip structure checks")
    li.set_defaults(fn=cmd_lint)
    se = sub.add_parser("send"); se.add_argument("request"); se.add_argument("--out")
    se.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT_S); se.set_defaults(fn=cmd_send)

    a = p.parse_args(argv)
    return a.fn(a)


if __name__ == "__main__":
    if hasattr(__import__("signal"), "SIGPIPE"):
        import signal
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)  # quiet exit when piped into head
    sys.exit(main())
