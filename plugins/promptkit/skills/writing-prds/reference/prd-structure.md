# PRD structure

Use these H2 sections in this order unless the requester specifies another list. Number them (`## 1. Overview and goals`). Sections 4 and 5 apply to products that call models; leave them out otherwise and lint with `--sections`.

## 1. Overview and goals
- What the product does, in the order the user experiences it.
- **Reference application**: the behavior copied, as a table of steps (entry, during, stop, choose, result, library). If the requester did not name one, say which apps the reference behavior is drawn from.
- **Goals** table: `# | Goal | How we measure it`. Every goal has a measure that a validation gate can check (a latency percentile, a count, a pass/fail condition).
- **Non-goals** for this version.
- **Users**: who, and what they already have (for example their own API keys).

## 2. Screens
- One conventions paragraph first: viewport sizes, theme tokens, what "flat" or other style rules mean concretely.
- One `### 2.n S<n> — Name` per screen, each with:
  - **Purpose:** one sentence.
  - **Layout (phone)** and, where different, **Layout (web/desktop)**: regions top to bottom, sizes in px, tokens used.
  - **States:** every state with its visible difference (empty, loading, error, permission-denied, partial, …).
  - **Controls:** every control and where it leads.
  - **APIs called:** internal module calls, then external endpoints with method and path, per provider.

## 3. System architecture
- Diagram (Mermaid) of clients, shared core, services, external systems.
- Repository layout with one line per package.
- Each subsystem (capture pipeline, configuration layer, builder, runner, environments, storage) with its interface or schema written out.
- How results return to the user; security and privacy rules; delivery order.

## 4. Models
- Table: provider, model, model string, context and max output, price, reasoning control, notes. Mark any unverified cell.
- Per-vendor prompting profile: structure (XML or Markdown), input marking, formatting rules, reasoning parameters, caching, known pitfalls, each grounded in a cited source.
- Default model per output type, with the reason.

## 5. Outputs
- Table: output, description shown to users, harness (single, chain, agent), format, how it is produced.
- Regeneration and export rules.

## 6. Configuration
- One table per area: `# | Setting | Default | Set in | Per run`. Every configurable element appears exactly once.
- Theme tokens with hex values.

## 7. Research appendix
- Findings grouped by vendor or topic, each paragraph ending in source tags like [A1].
- A general-techniques subsection saying which classic techniques still apply to current models and which the vendors now advise against.
- `### Sources` list with `[tag] Title — URL`.
- A line naming what could not be verified.
