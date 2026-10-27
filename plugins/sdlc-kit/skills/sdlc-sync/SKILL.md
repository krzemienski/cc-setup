---
name: sdlc-sync
description: "Use when the user wants to refresh the SDLC vault — typically via\n`/sdlc-kit:sync`, after bulk edits, at the start of a session, or\nautomatically after any Write/Edit/NotebookEdit inside a vault (triggered\nby the PostToolUse hook). English triggers: `/sdlc-kit:sync`, \"sync\",\n\"reindex\", \"run the librarian\", \"refresh the index\",\n\"regenerate the MOCs\". pt-BR triggers: \"sincronizar o vault\",\n\"reindexar\", \"rodar o bibliotecário\", \"atualizar o índice\",\n\"regenerar os MOCs\". This is a librarian utility — no persona interview,\njust deterministic validation and regeneration. Runs the vault librarian:\ndelta-scans the vault into SQLite, validates frontmatter per document type\n(moc, prd, adr, epic, milestone, spec, task, trd, api, retro, review,\nincident, aggregate, event, contract, token, component, pattern,\nworktree, branch), flags broken wikilinks, orphan files, duplicate titles,\nand stale updates, regenerates every `<phase>/_MOC.md` `## Artifacts`\nsection, and rewrites `_INDEX.md` preserving the canonical 8-phase\nstructure with populated tables or onboarding CTAs when empty. Emits a\nsingle JSON report on stdout with scanned count, db deltas, anomalies\n(severity/type/file/detail), and regenerated files. Never deletes\nanything; never auto-fixes without `--fix` (reserved for future use). Safe\nto invoke repeatedly — idempotent. Do not invoke outside a vault or\nwithout write permission on `.sdlc/`.\n"
---

# sdlc-kit:sync

The vault librarian. Keeps SQLite, MOCs, and `_INDEX.md` consistent with the files on disk.

---

## When to invoke

Invoke when:

- The user types `/sdlc-kit:sync` or asks to "sync", "reindex", "run the librarian", "refresh the index" — or equivalent phrasing in any other language.
- The PostToolUse hook fires `additionalContext` signaling a vault write.
- Before producing any report that depends on the index (`/sdlc-kit:status`, `/sdlc-kit:dash`, `/sdlc-kit:impact`).
- At the start of a session if the user asks for vault health.

**Do not** invoke when:

- cwd is not inside a vault (`<repo_root>/.sdlc/` with `.sdlc-kit/marker.json` missing).
- The user is in the middle of a write-heavy skill that will call sync itself at the end — let the parent skill handle it.

---

## Pre-checks

1. **Resolve vault root.** Use `/sdlc-kit:init` detection or walk ancestors looking for `.sdlc-kit/marker.json`. Abort if not found.
2. **Write permission.** `touch <vault>/.sdlc-kit/.permcheck && rm …`. Abort on failure.
3. **Python 3.10+** available.
4. **Plugin core library** importable — the script imports `core.db`, `core.parser`, `core.scanner` from the plugin root; a broken install surfaces here first.

---

## Flow

Always run in this order:

1. **Dry-run first** (whenever the user invokes manually or you are not sure the vault is clean):
   ```bash
   python "${CLAUDE_PLUGIN_ROOT}/skills/sdlc-sync/scripts/sync.py" \
     --vault-root "<vault_path>" --dry-run
   ```
   Parse the JSON. Surface to the user:
   - `scanned` — total markdown files indexed
   - `db_changes` — `{created, updated, skipped}` from the incremental scanner
   - `anomaly_counts` — `{error, warning, info}` tallies
   - `mocs_regenerated` / `index_regenerated` — what would change

2. **Real run** (no `--dry-run`). Only if the dry-run reported no fatal errors:
   ```bash
   python "${CLAUDE_PLUGIN_ROOT}/skills/sdlc-sync/scripts/sync.py" \
     --vault-root "<vault_path>"
   ```

3. **Report** to the user in their active language. Structure:
   - One-line summary: "Sync complete — 42 docs, 0 errors, 3 warnings, 1 info".
   - If errors exist: list each, grouped by file.
   - If warnings exist: collapse into a short section (titles only, offer to expand).
   - Next-step hints based on the top anomaly type (e.g., orphans → suggest moving to a phase).

---

## Output contract

`sync.py` prints a single JSON object on stdout:

```json
{
  "status": "ok" | "dry-run" | "error",
  "vault_root": "/abs/path/.sdlc",
  "scanned": 42,
  "db_changes": { "created": 1, "updated": 3, "skipped": 38 },
  "mocs_regenerated": ["01-planning/_MOC.md", "04-specs/_MOC.md"],
  "index_regenerated": true,
  "anomalies": [
    {
      "severity": "error",
      "type": "missing_field",
      "file": "01-planning/prd/auth.md",
      "detail": "missing required frontmatter field `status` for type `prd`"
    },
    {
      "severity": "warning",
      "type": "broken_wikilink",
      "file": "02-architecture/adr/ADR-0003.md",
      "detail": "wikilink target `[[context-map]]` not found in vault"
    }
  ],
  "anomaly_counts": { "error": 1, "warning": 1 },
  "errors": []
}
```

**Exit codes:**
- `0` — success or dry-run (anomalies are reported as data, not as failure).
- `1` — user error (vault missing, bad arguments).
- `2` — fatal (DB failure, core import failure, IO error).

---

## Anomaly types

| Type | Severity | Meaning |
|---|---|---|
| `missing_field` | error | Required frontmatter field missing for this `type`. |
| `invalid_status` | warning | `status` value outside the allowed enum for this `type`. |
| `broken_wikilink` | warning | `[[target]]` points to a note that doesn't exist. |
| `orphan` | warning | File lives outside `00-` through `07-` and isn't a canonical root doc. |
| `duplicate_title` | info | Two or more notes share a normalized title. |
| `stale_update` | info | `updated` frontmatter field is more than 90 days old. |

Required frontmatter and status enums are defined in `scripts/sync.py` (`REQUIRED_FIELDS_BY_TYPE`, `VALID_STATUS_BY_TYPE`). Adding a new doc type means updating both constants.

---

## Guardrails

**Never:**
- Delete files (the librarian only reads, regenerates MOCs, and rewrites `_INDEX.md`).
- Edit `CLAUDE.md` — it is sovereign, user-owned.
- Edit `_MOC.md` sections other than `## Artifacts` — the rest is user prose.
- Edit files under `_templates/` or `.sdlc-kit/`.
- Auto-fix anomalies without `--fix` (the flag is reserved — today it is a no-op).
- Run without `--dry-run` first when the vault has errors flagged by a previous run.

**Always:**
- Emit a single JSON object on stdout; diagnostics go to stderr.
- Match the user's conversation language in reports and suggestions.
- Preserve the canonical 8-phase `_INDEX.md` structure (headings and empty-state CTAs) — never degrade to a flat table.
- Skip `_templates/` and `.sdlc-kit/` while walking the vault.
- Commit anomaly types and severity — downstream skills (`/sdlc-kit:status`, `/sdlc-kit:dash`) depend on the contract.

---

## Examples

**Manual sync on a healthy vault:**
```
User: /sdlc-kit:sync
AI:   [dry-run] 42 docs scanned, 0 errors, 2 info notes (stale updates).
      Proceed with full run? (y/n)
User: y
AI:   [real run] `_INDEX.md` and 3 MOCs refreshed. 2 info notes remain — want to see them?
```

**Sync reveals a broken wikilink after a refactor:**
```
User: renomei o arquivo `context-map.md` — roda o sync
AI:   [dry-run] Found 1 warning: `02-architecture/adr/ADR-0003.md` references
      `[[context-map]]` which no longer exists. Should I run the real sync and leave the
      warning for you to fix, or hold while you rename the wikilink?
```

**Post-write hook trigger:**
```
(hook additionalContext: "vault write detected at 04-specs/login/tasks.md — please run sync")
AI:   [sync.py invoked with --vault-root <…>]
AI:   "Synced. `04-specs/_MOC.md` updated."
```

---

## See also

- `scripts/sync.py` — the librarian script.
- `core/scanner.py` — delta scanner used under the hood.
- `core/parser.py` — frontmatter + wikilink parser.
- `assets/vault-tree/_INDEX.md.tpl` — the canonical structure the regenerator preserves.
- `docs/decisions/ADR-0001-estrutura-canonica.md` — why the 8-phase layout is fixed.
