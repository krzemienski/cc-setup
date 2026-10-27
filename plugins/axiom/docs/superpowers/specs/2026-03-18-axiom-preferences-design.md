# Axiom Project Preferences

Per-project persistent preferences that survive across sessions, starting with simulator context.

## Problem

Axiom forgets project-specific context between sessions. The most concrete pain point: developers re-specify their preferred simulator device and app bundle ID every time they use xclog or simulator-related commands.

## Solution

A `.axiom/preferences.yaml` file in the project root. Gitignored, per-project, per-developer. Platform-agnostic — readable by Claude Code plugin, MCP server, and any Agent Skills host.

## Schema

```yaml
simulator:
  device: iPhone 16 Pro
  deviceUDID: 1A2B3C4D-5E6F-7890-ABCD-EF1234567890
  bundleId: com.example.myapp
```

- `device` — display name (human-readable, used in logs and prompts)
- `deviceUDID` — simulator UDID (precise identifier, used for xclog/simctl commands)
- `bundleId` — last-used app bundle identifier

Flat YAML, no schema version field. Add keys as needed over time. If a key ever needs renaming, readers should support both old and new names temporarily.

## File Location

```
project-root/
└── .axiom/
    └── preferences.yaml
```

"Project root" is the current working directory in Claude Code. For MCP, it is the `rootUri` provided by the client during initialization.

- `.axiom/` directory is gitignored (personal preferences, not shared)
- Created on first write, not eagerly

## How It Gets Populated

Mix of auto-detect and ask:

1. Developer uses `/axiom:console` or an agent that invokes xclog
2. `xclog list` discovers available simulators and installed apps
3. Developer picks a device and bundle ID (or Claude detects from context)
4. Claude writes the values to `.axiom/preferences.yaml` using the Write tool
5. Subsequent sessions read preferences before prompting

**Write mechanism**: Claude writes the file, guided by instructions in `axiom-xclog-ref`. There is no code or binary that writes preferences — it is Claude using the Write tool, following the skill's guidance on what YAML structure to produce.

**Write instructions for Claude** (to be added to `axiom-xclog-ref`):

1. Read `.axiom/preferences.yaml` if it exists (to preserve other keys)
2. Update the `simulator:` section with device name, UDID, and bundle ID
3. Write the merged result back using the Write tool
4. If `.axiom/` doesn't exist, create it first

**`.gitignore` handling**: After creating `.axiom/`, read `.gitignore` (if it exists), check if any line matches `.axiom/` exactly. If not found, append `\n.axiom/\n`. If `.gitignore` doesn't exist, create it with `.axiom/` as its content.

## How It Gets Read

**Primary consumers:**

- **Claude (Read tool)**: Agents and skills read the file directly when they need simulator context. No special parsing — Claude reads YAML natively.
- **MCP server (TypeScript)**: `yaml` npm package or simple string parsing.
- **xclog skill guidance**: `axiom-xclog-ref` instructs Claude to check preferences before running `xclog list`.

**Not consumed by:**

- Bash hooks. Hooks don't need simulator preferences. If they ever do, they can shell out to Python's `yaml` module.

## What Gets Modified

### New files

- `.axiom/preferences.yaml` — created at runtime in user projects (not in Axiom repo)

### Modified files

- **`axiom-xclog-ref` skill** — add guidance: "Before running `xclog list`, check `.axiom/preferences.yaml` for saved simulator device and bundle ID. Use saved values if present. After a successful launch, save the device and bundle ID to preferences."
- **`/axiom:console` command** — add step: read preferences at start, write preferences after successful capture
- **`simulator-tester` agent** — add preference check for simulator device (uses `simctl`, not xclog, but benefits from saved device preference)

### Not modified

- Session-start hook — no startup overhead, preferences are read on-demand
- hooks.json — no new hook events needed
- claude-code.json manifest — no new skills or commands

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| Preferences file doesn't exist | Fall back to discovery (xclog list), then save |
| Saved simulator no longer exists | xclog fails, fall back to discovery, save new preference |
| Multiple apps in project | `bundleId` stores last-used; developer can override per-session |
| `.gitignore` doesn't exist | Create it with `.axiom/` as sole entry |
| `.axiom/` already in `.gitignore` | Don't duplicate the entry |
| Developer hand-edits the YAML | Works fine — YAML is human-readable by design |
| YAML is malformed or unparseable | Fall back to discovery, warn the developer, do not overwrite (let them fix it) |
| Multiple simulators match device name | Use `deviceUDID` for precise targeting; display name is for human readability |
| MCP server needs preferences | Read from `rootUri` / project root, same path |

## What We're NOT Building

- No SessionStart hook overhead (on-demand reads only)
- No project profile or framework detection system
- No schema versioning
- No `${CLAUDE_PLUGIN_DATA}` usage (project-local, not platform-specific)
- No audit history or trend tracking (separate future concern)
- No user preferences beyond simulator context (expand later if needed)

## Future Expansion

The `.axiom/` directory and `preferences.yaml` schema can grow:

```yaml
simulator:
  device: iPhone 16 Pro
  bundleId: com.example.myapp

# Future possibilities (not implemented now):
# scheme: MyApp-Debug
# team: ABCDE12345
```

New keys are additive. Missing keys fall back to discovery. No migration needed.

## Design Decisions

**Why `.axiom/` and not `.claude/axiom.local.md`?**
`.claude/` is Claude Code-specific. Axiom supports Claude Code, MCP (VS Code, Cursor, Gemini CLI), and the Agent Skills standard. A platform-agnostic location ensures all runtimes can read preferences.

**Why YAML and not JSON?**
YAML is human-editable, matches the Agent Skills frontmatter convention, and every language has a parser. JSON would work but is less pleasant to hand-edit. Bash hooks don't need to read this file, so YAML's lack of native bash parsing is not a cost.

**Why no schema version?**
YAGNI. The schema is additive — new keys don't break old readers. If a breaking change is ever needed, a version field can be added then.

**Why gitignored?**
Simulator preferences are personal. Developer A uses iPhone 16 Pro, developer B uses iPhone 15. Committing preferences would cause conflicts.

**Why on-demand and not SessionStart?**
Most sessions don't use xclog. Loading preferences at startup adds latency to every session for a feature used in a minority of them.
