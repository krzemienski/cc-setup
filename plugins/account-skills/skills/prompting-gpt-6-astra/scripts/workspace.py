"""workspace.py: the file and shell tools the agent loops expose, confined to one directory.

Shared by agent_loop.py for Anthropic and OpenAI. Standard library only.

Tools: list_dir, read_file, write_file, edit_file, run_command, todo.
- Paths are resolved (symlinks included) and must stay inside the working directory.
- run_command refuses destructive or hard-to-reverse commands unless allow_destructive is set;
  the refusal text tells the model to continue with independent work and report the blocker.
- todo replaces the checklist; open_items() drives the loops' continuation messages.
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any

# Commands that delete data, rewrite shared history, or skip safety hooks. Matched case-insensitively
# anywhere in the command string, so `cd x && rm -rf y` is caught too.
DESTRUCTIVE = re.compile(
    r"(\brm\s+(-[a-z]*r[a-z]*|--recursive)\b|"
    r"git\s+push\s+.*--force|git\s+push\s+-f\b|git\s+reset\s+--hard|git\s+clean\s+-[a-z]*f|"
    r"git\s+branch\s+-D\b|\bdrop\s+(table|database|schema)\b|\btruncate\s+table\b|"
    r"\bmkfs\b|\bdd\s+if=|--no-verify|\bchmod\s+-R\s+777\b|\bshred\b)",
    re.I,
)

# Tool output is capped so one noisy command cannot fill the context window. The tail is kept
# because test runners and compilers print the summary and the first error near the end.
STDOUT_TAIL_CHARS = 20_000
STDERR_TAIL_CHARS = 8_000
READ_MAX_CHARS = 200_000
# Commands may run long builds or test suites; 30 minutes is the ceiling, 2 minutes the default.
COMMAND_TIMEOUT_DEFAULT_S = 120
COMMAND_TIMEOUT_MAX_S = 1800

_OBJ = {"type": "object", "additionalProperties": False}

TOOL_SPECS: list[dict[str, Any]] = [
    {"name": "list_dir",
     "description": "List the entries of a directory inside the working directory. Directories end with '/'.",
     "schema": {**_OBJ, "properties": {"path": {"type": "string"}}, "required": ["path"]}},
    {"name": "read_file",
     "description": "Read a UTF-8 text file inside the working directory.",
     "schema": {**_OBJ, "properties": {"path": {"type": "string"}}, "required": ["path"]}},
    {"name": "write_file",
     "description": "Create a file or replace its whole content. For changes to an existing file, use edit_file "
                    "so the change stays reviewable.",
     "schema": {**_OBJ, "properties": {"path": {"type": "string"}, "content": {"type": "string"}},
                "required": ["path", "content"]}},
    {"name": "edit_file",
     "description": "Replace one exact occurrence of old_text with new_text in a file. old_text must match exactly once.",
     "schema": {**_OBJ, "properties": {"path": {"type": "string"}, "old_text": {"type": "string"},
                                       "new_text": {"type": "string"}},
                "required": ["path", "old_text", "new_text"]}},
    {"name": "run_command",
     "description": "Run a shell command in the working directory; returns the exit code and the tail of stdout and "
                    "stderr. Destructive or hard-to-reverse commands are refused and need the user.",
     "schema": {**_OBJ, "properties": {"command": {"type": "string"}, "timeout_seconds": {"type": "integer"}},
                "required": ["command", "timeout_seconds"]}},
    {"name": "todo",
     "description": "Replace the task checklist. Track every part of the task here and mark an item completed only "
                    "after checking it.",
     "schema": {**_OBJ, "properties": {"items": {"type": "array", "items": {
         **_OBJ, "properties": {"text": {"type": "string"},
                                "status": {"type": "string", "enum": ["pending", "in_progress", "completed", "blocked"]}},
         "required": ["text", "status"]}}}, "required": ["items"]}},
]


def anthropic_tools() -> list[dict[str, Any]]:
    return [{"name": t["name"], "description": t["description"], "strict": True, "input_schema": t["schema"]}
            for t in TOOL_SPECS]


def openai_tools() -> list[dict[str, Any]]:
    return [{"type": "function", "name": t["name"], "description": t["description"], "strict": True,
             "parameters": t["schema"]} for t in TOOL_SPECS]


class Workspace:
    def __init__(self, root: Path, allow_destructive: bool = False):
        self.root = root.resolve()
        if not self.root.is_dir():
            raise SystemExit(f"error: working directory not found: {root}")
        self.allow_destructive = allow_destructive
        self.todos: list[dict[str, str]] = []

    def _path(self, p: str) -> Path:
        full = (self.root / p).resolve()
        if full != self.root and self.root not in full.parents:
            raise ValueError(f"path {p!r} is outside the working directory")
        return full

    def call(self, name: str, args: dict[str, Any]) -> tuple[str, bool]:
        """Run one tool. Returns (output, is_error); errors go back to the model as tool errors."""
        try:
            if name == "list_dir":
                d = self._path(args["path"])
                return "\n".join(sorted(e.name + ("/" if e.is_dir() else "") for e in d.iterdir())) or "(empty)", False
            if name == "read_file":
                text = self._path(args["path"]).read_text("utf-8")
                if len(text) > READ_MAX_CHARS:
                    return text[:READ_MAX_CHARS] + f"\n[truncated at {READ_MAX_CHARS} characters]", False
                return text, False
            if name == "write_file":
                f = self._path(args["path"])
                f.parent.mkdir(parents=True, exist_ok=True)
                f.write_text(args["content"], "utf-8")
                return f"wrote {args['path']} ({len(args['content'])} characters)", False
            if name == "edit_file":
                f = self._path(args["path"])
                text = f.read_text("utf-8")
                n = text.count(args["old_text"])
                if n != 1:
                    return f"old_text occurs {n} times in {args['path']}; it must occur exactly once", True
                f.write_text(text.replace(args["old_text"], args["new_text"], 1), "utf-8")
                return f"edited {args['path']}", False
            if name == "run_command":
                cmd = args["command"]
                if DESTRUCTIVE.search(cmd) and not self.allow_destructive:
                    return ("Refused: this command is destructive or hard to reverse and needs the user's confirmation. "
                            "Continue with work that does not depend on it, and list it in your report."), True
                limit = max(1, min(int(args.get("timeout_seconds") or COMMAND_TIMEOUT_DEFAULT_S), COMMAND_TIMEOUT_MAX_S))
                r = subprocess.run(cmd, shell=True, cwd=self.root, capture_output=True, text=True, timeout=limit)
                out = (f"exit {r.returncode}\n--- stdout ---\n{r.stdout[-STDOUT_TAIL_CHARS:]}"
                       f"\n--- stderr ---\n{r.stderr[-STDERR_TAIL_CHARS:]}")
                return out, r.returncode != 0
            if name == "todo":
                self.todos = [{"text": str(t["text"]), "status": str(t["status"])} for t in args["items"]]
                return json.dumps(self.todos), False
            return f"unknown tool {name!r}", True
        except subprocess.TimeoutExpired:
            return "command timed out; rerun with a larger timeout_seconds or a narrower command", True
        except (OSError, ValueError, KeyError, UnicodeDecodeError) as e:
            return f"{type(e).__name__}: {e}", True

    def open_items(self) -> list[str]:
        return [t["text"] for t in self.todos if t.get("status") != "completed"]
