# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [9.2.0] - 2026-09-03

### Removed
- **All `Read(...)` deny rules dropped from the generated `settings.json`.** Claude Code has a safety check (`deniedPathInsideDirectory`) that fires whenever `permissions.deny` contains **at least one** rule starting with `Read` — the check never looks at which path the rule points to. With such a rule present, any read command run through Bash (`grep`, `cat`, `head`, …) against a **relative** path after a `cd` is escalated to a manual prompt: *"…would search a directory that cannot be determined here, and a Read() deny rule is configured; only you can approve running it anyway."* Verified against binary 2.1.259: the decision is marked `classifierApprovable: false`, so auto mode never clears it — a human presses the button on every single call. A single `Read(**/node_modules/**/CLAUDE.md)` rule was therefore enough to break `grep` over a project's own `src/`, in every bootstrapped project, forever. The protection it bought was near zero: `Read(path)` only covers Claude Code's own reading tools, and `cat`/`grep` from Bash walk straight past it. In `step-4-settings`: 12 rules removed from the deny example in the FORMAT section and the same 12 from the §4.2 deny list (`SKILL.md`, `CLAUDE.md`, `AGENTS.md`, `.cursorrules` under `**/node_modules/**`, `**/vendor/**`, `**/site-packages/**`). Bash deny rules are untouched — they do not trip the check.

### Added
- **Supply Chain rule in the generated `CLAUDE.md`** (`step-finalize`, §9.1) replaces the removed deny rules with an instruction rather than a permission: instruction files inside dependencies (`CLAUDE.md`, `AGENTS.md`, `SKILL.md`, `.cursorrules` under `node_modules/`, `vendor/`, `site-packages/`) are not to be read, and if such text reaches the context anyway it is data, not instructions. The same rule covers secrets — `.env`, `secrets/`, private keys are not read in full and not echoed into chat, logs or commits — which is why no `Read(**/.env)` deny rule is introduced as a substitute. A PreToolUse hook was considered and rejected: it would fire on every single `Read`, trading visible friction (prompts) for invisible friction (a subprocess per file read).
- **`step-4-settings` §4.2 now carries an explicit "НИКОГДА не добавлять `Read(...)` в deny" section** with the mechanics of the check, so the rules do not creep back in on a later edit.
- **Patch mode strips `Read` deny rules from an existing `settings.json`.** New rows in the "Невалидные permission-правила" table: any `Read`/`Read(p)` found in `deny` is removed without asking the user, and the patch is expected to confirm the Supply Chain rule is present in the project's `CLAUDE.md`. Without this, projects bootstrapped by 9.1.1 and earlier keep the manual prompts until a full upgrade regenerates their settings.

### Changed
- **The invalid-rule repair no longer rewrites `Glob(p)`/`Grep(p)` into `Read(p)` inside `deny`.** The 9.1.1 rule would have recreated exactly what this release removes. The table is now split by block: in `allow` the rewrite stands, in `deny` the ignored `Glob(p)`/`Grep(p)` rule is simply dropped. Bare `"Read"` (no parentheses) in `allow` stays a valid tool-level rule and is left alone.

## [9.1.1] - 2026-08-21

### Fixed
- **Generated `settings.json` produced invalid file-permission rules.** Claude Code applies file permission checks only to `Edit(path)` and `Read(path)`: `Edit` covers every file-writing tool (Write, Edit, NotebookEdit), `Read` covers every file-reading tool (Read, Glob, Grep). Rules like `Write(path)` and `Glob(path)` are ignored, and Claude Code printed a warning for each one on every session start in every bootstrapped project. In `step-4-settings`: `Write(.claude/**)` dropped from the base allow list (duplicate of the adjacent `Edit(.claude/**)`), and six `Glob(**/node_modules|vendor|site-packages/**/SKILL.md|CLAUDE.md)` deny rules dropped from both deny blocks (duplicates of the `Read(...)` rules right above them, which already cover a wider file set). The note next to the base allow list now explains the Edit/Read coverage rule so the entries do not come back.
- Section numbering in `step-4-settings`: the `fresh` mode section was a second `## 4.3` (now `## 4.4`).

### Added
- **Patch mode now repairs invalid permission rules in an existing `settings.json`.** New "Невалидные permission-правила" section in `step-4-settings` (§4.2): `Write(p)`/`NotebookEdit(p)` and `Glob(p)`/`Grep(p)` found in `allow` or `deny` are dropped when an `Edit(p)`/`Read(p)` twin already exists, otherwise rewritten to it — without asking the user. Tool-level `"Write"`/`"Glob"`/`"Grep"` (no parentheses) are left alone. Without this, projects bootstrapped by 9.0.x–9.1.0 keep the warnings until a full upgrade regenerates their settings.

## [9.1.0] - 2026-07-02

### Breaking
- **Team mode migrated to implicit Agent Teams.** Claude Code removed `TeamCreate`/`TeamDelete`, and `team_name` on the Agent tool is deprecated (ignored). Availability probe is now `ToolSearch(select:SendMessage)` — bootstrap router and pipeline router (шаг 3.5). Agents are spawned as `Agent(name=...)` without a team; the lead is addressed as `"main"` (was `"team-lead"` / `"lead"`).

### Changed
- `flow-team.md`: no team create/delete, shutdown protocol removed — agents terminate on task completion; a completed agent is resumed via `SendMessage(to="{name}")` with context preserved.
- `templates/skills/pipeline.md`: Team Mode / Team Fallback / Team Resume rewritten for implicit teams; «Протокол: Team Shutdown» removed; `team_name` dropped from the state.json schema; mode selection asks the user only when SendMessage resolves.
- Pipeline `[team]` sections (new-code, fix-code, tests, brainstorm, full-feature): no `TeamCreate`/`team_name=T`/`Cleanup: shutdown` lines; cross-phase agent reuse expressed as `SendMessage` resume (brainstorm Phase 2, full-feature Phase 7).
- `Task()` pseudo-syntax renamed to `Agent()` (the Claude Code tool was renamed): `task-syntax.md`, pipeline router, `step-8-lang/common.md`, `pipelines/gitlab.md`, `pipelines/github.md`. Patch-mode validation and phases-conversion accept both notations in previously generated files.
- README (ru/en): team mode described as implicit (named agents + SendMessage).

### Fixed
- `full-feature.md` `[team]` Phase 7: malformed doubled quotes in the SendMessage example.

## [9.0.3] - 2026-07-02

### Fixed
- **track-agent.sh hook never fired on current Claude Code.** The subagent tool was renamed `Task` → `Agent`; the generated `settings.json` registered the hook with `matcher: "Task"`, so `usage.jsonl` stayed empty in every bootstrapped project. Matcher is now `"Task|Agent"` (the script itself already handled both names).
- **TaskCreate call in pipeline router was missing the required `description` field** — templates taught an invalid tool call (`subject` + `activeForm` only).
- `Task` removed from the tool-name list in step-4-settings (tool no longer exists).
- README (ru/en): stale `.bootstrap-cache/state.json` → `.claude/.cache/state.json` (moved in v9.0.0); mode selection described as a user prompt while the router picks Team/Sequential automatically; hooks table said `PostToolUse (Task)`.

## [9.0.2] - 2026-05-27

### Fixed
- **Capture phase had no executor.** Pipeline frontmatter declared `capture: full|partial|review`, but neither agents nor router actually wrote to memory. `decisions/`, `patterns.md`, recurring `issues.md` stayed empty across sessions. Now the router executes capture inline (no Task(), no Agent()) after the last phase per Протокол: Capture, before the final report.

### Changed
- `templates/skills/pipeline.md` — «Протокол: Capture» rewritten from a placeholder lookup table into explicit per-level steps (full/partial/review) executed by the router. Decision template + dedup rules + MEMORY.md index update inline.
- `templates/skills/pipeline.md` — «Протокол: Финализация» step 3 now explicitly lists what was written to memory in the final report.

### Removed
- `templates/includes/capture-full.md`, `capture-partial.md`, `capture-review.md` — content folded into the router's protocol (one source of truth). Placeholders `{CAPTURE:full|partial|review}` removed from `placeholder-registry.md` and `step-8-*.md` (active list → removed list).

## [9.0.1] - 2026-04-12

### Fixed
- SendMessage формат с обязательным summary во всех шаблонах (pipelines, skills, includes)
- verify-bootstrap.sh: legacy путь `.bootstrap-cache` → `.claude/.cache`
- Deny rules: .cursorrules и AGENTS.md покрыты для vendor/ и site-packages/
- enableAllProjectMcpServers: привязка к любому MCP серверу, не только GitLab
- Patch manifest: классификация через known-templates.json при пустых registries
- Corrupted state.json: fallback в Resume Detection (удалить cache, начать заново)
- Team mode: common-gen стартует после всех lang-gen (per-lang фрагменты ready)
- Пустой .claude/ без agents/skills/pipelines → fresh вместо upgrade
- step-init: Write state.json отклонён → error (bootstrap невозможен)
- tar backup: проверка exit code
- Удалена мёртвая секция 4.4 (patch mode) из step-4-settings
- Checkpoint keys: числовые → именованные (init, configure, settings, plugins, preview, analyze, patch, finalize)
- Удалён current_step из всех step-файлов
- step-finalize: redundant rm убран, gen-reports помечены как опциональные для patch mode
- step-5-apply: нумерация секций исправлена (1,2,3,4)
- step-3-configure: "Правило resume" → "Правило skip", проверка config.analysis_depth
- step-upgrade U.4: явно указано "без Settings и Plugins"

## [9.0.0] - 2026-04-12

### Breaking
- Pipeline frontmatter v9: `phases[]` array of objects, `agents{}` section, `modes[]`, structured `error_routing`
- SKILL.md = чистый router (определяет mode → читает flow файл). Sequential и team flow в отдельных references/
- `.bootstrap-cache/` → `.claude/.cache/`, бэкапы → `.claude/.cache/backups/`
- Permissions: `Read` + `Edit` (не Write). `Edit(.claude/**)` для .claude/ директории
- Version убран из frontmatter шаблонов — версионирование через manifest

### Added
- **Router architecture** — SKILL.md (30 строк) → flow-sequential.md / flow-team.md. LLM видит только один flow
- **Agent Teams** — обязательный режим если TeamCreate доступен. Team flow с TeamCreate → Agent(name, team_name) → SendMessage
- **known-templates.json** — кумулятивный реестр template-файлов всех версий для upgrade classification
- **Two-level upgrade classification** — known template + v9 template exists. DELETE только если оба true
- **Upgrade safety** — бэкап с --exclude, safety check перед удалением, hooks protected
- **Patch mode** — cleanup deprecated + frontmatter v8→v9 + router regen
- **Upgrade mode** — backup → classify → configure → generate → restore
- Pipeline templates: gitlab.md, github.md (ранее inline)
- Dual-mode pipeline router (sequential/team), condition resolution, on-block retry, autonomous mode
- `.bootstrap-manifest.json` replaces `.bootstrap-version`

### Changed
- .gitignore проекта не трогаем вообще
- Settings/plugins не запускаются при patch/upgrade
- Sequential generation: lang → common → infra последовательно (не параллельно)
- mkdir директорий перед генерацией (оркестратор/lead, не субагенты)
- bump-version.sh не трогает template файлы

### Removed
- **Peer validation**, **hotfix pipeline**
- 6 deprecated includes, `.bootstrap-version`
- step-10-finalize.md (мёртвый файл)
- bootstrap-team-flow.md (заменён flow-team.md)

## [8.2.0] - 2026-04-09

### Added
- **Peer Validation** — validator agent reviews author's output before user approval gate. Author receives remarks, fixes, validator re-checks (max 2-3 iterations). User sees already reviewed plan.
- New include: `peer-review.md` — parameterized author↔validator cycle template with `{PEER_AUTHOR}`, `{PEER_VALIDATOR}`, `{PEER_ARTIFACT}`, `{PEER_PHASE}`, `{PEER_MAX_ITERATIONS}` placeholders
- `peer_validation` section in pipeline frontmatter — declarative author/validator pairs per phase
- `peer_review_stuck: show_with_warnings` error routing — shows unresolved remarks to user after max iterations
- **REUSE FIRST rule** in all agents — mandatory search for existing code before creating new helpers/utilities/services. Applied to: analyst, lang-architect, lang-developer, lang-test-developer, lang-reviewer
- `version` field in all agent frontmatter (was missing)

### Changed
- Peer review applied to 5 gates: new-code Phase 1 (analyst→architect), new-code Phase 2 (architect→reviewer), fix-code Phase 1 (analyst→developer), tests Phase 1 (analyst→qa-engineer), brainstorm Phase 2 SEQUENTIAL (architect→analyst)
- fix-code Phase 1: refactored from inline steps to Task(analyst) for consistency with peer review pattern
- tests Phase 1: refactored from inline steps to Task(analyst) for consistency with peer review pattern
- Placeholder registry: added `{PEER_REVIEW}` with parameterized include documentation
- Version bump: all pipelines, agents, skills, references, plugin.json → 8.2.0

## [8.1.1] - 2026-04-06

### Fixed
- **Custom mode parsing (BUG-001)** — "Other" input in analysis_depth question now fuzzy-matches mode keywords (`standart` → `standard`, `стандарт` → `standard`, etc.) and extracts custom instructions after `+`, `,`, `:`, `;` separators into `config.custom_instructions`
- **Subagent silent write failure (BUG-002)** — step-8 subagents now track Write results per-file with `written[]`/`failed[]` arrays in gen-report; orchestrator reads reports after step 8, offers retry for failed files only instead of redoing everything; team-flow fallback is now granular (skips already-written files)

### Changed
- gen-report schema for step-8-lang, step-8-common, step-8-infra: added `written[]` and `failed[]` fields
- SKILL.md header: v7 → v8
- state.json config schema: added `custom_instructions` field
- step-7-analyze.md: passes `custom_instructions` to per-lang analysis subagent prompts
- bootstrap-team-flow.md: granular fallback for Phase D — retries only missing/failed files

## [8.1.0] - 2026-04-04

### Added
- **Pipeline state persistence** — resume interrupted pipelines from the last completed phase
- `{PIPELINE_STATE_INIT}` include — reads or creates `.claude/output/state/{task-slug}.json` with per-phase status tracking
- `{PIPELINE_STATE_UPDATE}` include — marks phases completed, auto-cleans state file on pipeline completion
- **Resume detection in pipeline router** — Шаг 0 checks for unfinished state files, offers resume/restart/cancel
- All 9 pipelines updated with state init (after Phase 0) and state update (after each working phase)

### Changed
- Pipeline templates version bump: 8.0.1 → 8.1.0
- Pipeline router (skills/pipeline.md) version bump: 8.0.1 → 8.1.0
- Placeholder registry updated with `{PIPELINE_STATE_INIT}` and `{PIPELINE_STATE_UPDATE}`

## [8.0.1] - 2026-04-04

### Added
- **Deny rules** in settings.json — blocks reading AI instruction files (SKILL.md, CLAUDE.md, AGENTS.md, .cursorrules) from dependency directories (node_modules, vendor, site-packages). Blocks global package installs (`npm i -g`, `yarn global add`) and pipe-to-shell (`curl|bash`, `wget|sh`). Generated always, regardless of stack.

### Changed
- step-4-settings.md: new section 4.2 Deny Rules with full deny list template
- Validate mode: missing deny rules → `[+ADD]`, user deny rules → `[USER]` preserved

## [8.0.0] - 2026-04-03

### Breaking Changes
- Pipeline templates: `<!-- version -->` HTML comment replaced with YAML frontmatter
- `bump-version.sh` updated — uses `sed` on YAML frontmatter for pipelines instead of HTML comments
- Pipelines validated against `version: "8.0.0"` — all `< 8.0.0` trigger `[REGEN]`

### Added
- **YAML frontmatter in pipelines** — `name`, `description`, `version`, `phases`, `capture`, `triggers`, `error_routing`, `adaptive_teams`, `chains` fields. Enables machine-readable pipeline metadata and self-describing router triggers
- **Include mechanism** — `{CAPTURE:full/partial/review}`, `{PARALLEL_PER_LANG}`, `{CAPABILITY_DETECT}` placeholders resolved from `templates/includes/` at generation time
- **Agent Teams (adaptive)** in 5 pipelines: new-code, fix-code, tests, review, brainstorm. Phase 0 detects `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS`, dual "Режим TEAM / Режим SEQUENTIAL" branches, automatic fallback
- **File-based communication** for team mode — agents read/write `.claude/output/` as message bus; reviewer returns BLOCK via verdict file, developer reads and fixes
- **brainstorm pipeline** (9th pipeline) — FRAME → PERSPECTIVES → CAPTURE. Team mode: analyst + architect + storage-architect + devops discuss in parallel. Sequential fallback
- **Error matrix** in all 9 pipelines (was only in new-code)
- **`error_routing` in frontmatter** — formalized error handling rules (`retry_current`, `retry_from:N`, `stop_and_report`, `fallback_sequential`, `skip_capture`, `prerequisite:pipeline`)
- **`triggers` in frontmatter** — pipeline keywords for router classification, self-describing instead of hardcoded table
- **`mode` field in agent frontmatter** — `"plan"` (read-only, 6 agents) or `"implement"` (writes project files, 2 agents: developer, test-developer)
- **Task() syntax spec** — `templates/includes/task-syntax.md`, 4 mandatory fields: Вход, Выход, Ограничение (`read-only`/`project-write`), Верни
- **Placeholder registry** — `templates/includes/placeholder-registry.md`, 50+ variables with source mapping
- **`capture-full.md`**, **`capture-partial.md`**, **`capture-review.md`** — deduplicated CAPTURE phase from 5 pipelines into 3 include files
- **`parallel-per-lang.md`** — deduplicated per-lang parallelization rule from 4 pipelines
- **BRAINSTORM in pipeline router** — added to intent classification table and fallback options

### Changed
- All 9 pipelines rewritten with YAML frontmatter, standardized Task() format, include placeholders
- Step-8 generators (lang, common, infra) updated: know about frontmatter, includes, `mode` field, Task() format
- Step-8 adaptive teams: generators no longer inject dual modes on-the-fly — templates are self-contained
- Validation rules: check YAML frontmatter presence, `adaptive_teams` ↔ Phase 0 consistency
- Pipelines: 8 → 9 (added brainstorm)

### Fixed
- Inconsistent frontmatter quoting in `p.md` and `pipeline.md` skills (unquoted `name:` → quoted)
- Malformed placeholder in `storage.md:71` (`{STORAGE_ANTIPATTERNS — адаптируй:...}` → `{STORAGE_ANTIPATTERNS}`)
- `bump-version.sh` verification: `head -1` → `grep -m1 'version:'` for pipeline version check

## [7.3.1] - 2026-04-03

### Changed
- Steps 3 & 5 orchestrator phases: explicit imperative tone to prevent LLM skipping phases
- Control checks after apply phase (verify state not empty)
- Renumbered phases: 3A/3B/3C and 5A/5B/5C

## [7.3.0] - 2026-04-02

### Changed
- **Anti-loop architecture**: steps 3 & 5 refactored to three-phase pattern (scan → ask → apply). Subagent collectors return JSON, never call AskUserQuestion. Orchestrator batches questions, eliminates resume-loop
- **Templates path flatten**: `prompts/bootstrap/templates/` → `templates/`
- Batch AskUserQuestion in step-3 (4 questions in one call)
- Batch AskUserQuestion in step-4 validate mode (1 question)

### Fixed
- step-1 initial state missing step "10"
- step-9 misleading comment ("last of step 8")
- step-10 reference to nonexistent "step 9.5"
- All path references updated (CLAUDE.md, bump-version.sh, SKILL.md)

## [7.2.1] - 2026-04-02

### Fixed
- AskUserQuestion schema: `questions` array + `multiSelect` required field
- Deferred tools: AskUserQuestion schema + SendMessage summary format

## [7.2.0] - 2026-04-02

### Added
- **Step 5: Plugins & MCP** — per-plugin AskUserQuestion with install instructions (Playwright, Context7, LSP, GitLab MCP, GitHub MCP, Docker MCP)
- **GitHub MCP** support with token configuration and .mcp.json generation
- **Docker MCP** support via mcp-docker-server
- **Per-lang parallelism** in pipelines: new-code, review, tests, fix-code run per-language reviewers/developers in parallel
- **Git permissions granularity**: read/write/push/delete as separate multiSelect options
- **Settings.json before plugins** (step 4→5): base permissions generated first, plugins append MCP permissions after installation

### Changed
- Bootstrap flow: 8 → 9 steps (added step 5 plugins, settings moved to step 4)
- Step order: scan → detect → configure → settings → plugins → preview → analyze → generate → finalize
- Generation step: per-artifact-type (6a/6b/6c) → per-domain (8-lang/8-common/8-infra)
- Removed Adaptive Teams from v7 scope (deferred)
- Docker permissions moved from configure to plugins step (MCP-based, not Bash)
- Agents write artifacts to files BEFORE returning summary ("write first" pattern)
- Removed legacy `commands/bootstrap.md` — skill-only invocation
- Removed all recommendations from finalize step

### Fixed
- `${CLAUDE_SKILL_DIR}` resolution for subagent step files
- settings.json format: `Bash(command:*)` syntax, hooks with matcher+hooks array
- bump-version.sh exit code on non-dry-run
- State file path: `.bootstrap-cache/state.json`

## [7.0.0] - 2026-04-02

### Breaking Changes
- Bootstrap flow redesigned: 5 steps → 7 atomic subagent steps
- Agent templates: 12 → 8 (frontend-* removed, reviewers merged)
- `database` skill/agent renamed to `storage`
- Step files renamed (step-1..5 → step-1..7 with sub-steps)

### Added
- **Checkpoint/Resume**: `.bootstrap-state.json` + `.bootstrap-cache/` persist progress between sessions
- **Analysis Depth**: 3 levels (light/standard/deep) — user chooses token budget
- **Dry-Run Preview**: file counts, token estimates, artifact list before generation
- **Pause Point**: manual pause after planning step, resume via `/bootstrap`
- **Plugin Recommendations**: detect useful plugins (Playwright, context7, docker, LSP), show install commands
- **Settings Diff-Merge**: `[KEEP]/[+ADD]/[-DEL]/[USER]` markers, per-permission approval
- **Permission Levels**: conservative / balanced / permissive
- **Progress Indicators**: `[N/7] Step Name ✓` after each step
- **Git Commit Reminder**: before generation start
- **Custom File Protection**: `[USER]` marker in validate mode for unknown files
- **CHANGELOG.md**: version history
- **bump-version.sh**: automated version bump across all files

### Changed
- `{lang}-reviewer-logic` + `{lang}-reviewer-security` → single `{lang}-reviewer` (architecture, logic, security, static analysis, optimization)
- `db-architect` → `storage-architect` (SQL, NoSQL, Redis, S3, queues) — conditional on storage detection
- `devops` expanded: host machine support (WSL, native Linux, macOS)
- `qa-engineer` expanded: Playwright E2E, manual testing, smoke tests
- `review` pipeline simplified: single reviewer, no TEAM/SEQUENTIAL modes
- `new-code` pipeline: Phase STORAGE replaces Phase DATABASE
- `qa-docs` pipeline: +Playwright E2E stubs
- CLAUDE.md generation moved to end of step-6 (tables reflect actual generated files)
- All questions collected in single step-3 block (was spread across steps)
- Each step runs as isolated subagent (conversation context not used)

### Removed
- `frontend-developer`, `frontend-reviewer`, `frontend-test-developer` agents (covered by `{js/ts}-*`)
- `{lang}-reviewer-logic`, `{lang}-reviewer-security` (merged into `{lang}-reviewer`)

## [6.0.1] - 2026-03-30

### Added
- `marketplace.json` for self-hosted plugin distribution
- `install.sh` and `commands/bootstrap.md` for one-step legacy install

## [6.0.0] - 2026-03-30

### Added
- **Claude Code Plugin** — plugin manifest (`.claude-plugin/plugin.json`)
- Command → Skill migration (`commands/bootstrap.md` → `skills/bootstrap/SKILL.md`)
- English versions: `README.en.md`, `CLAUDE.en.md`
- `PRIVACY.md` (no data collection, all local)

## [5.4.2] - 2026-03-17

### Changed
- AskUserQuestion for all interactive prompts in bootstrap and runtime
- Teams API: natural language Teammate syntax instead of deprecated TeamCreate/Spawn/Shutdown

## [5.4.1] - 2026-03-17

### Added
- Template versioning — `version` field in skill/pipeline frontmatter
- Auto-`[REGEN]` for outdated skills/pipelines in validate mode

## [5.4.0] - 2026-03-17

### Added
- **Analyst agent** (`analyst.md`) — technical analysis, reads code/schema/infra, creates spec
- Phase 1 ANALYSIS in new-code and full-feature pipelines
- Pipeline router: skip-analysis flag (`--no-analysis`, `--skip-analyst`)

## [5.3.0] - 2026-03-13

### Added
- File-based context: agents write results to `output/plans/` and `output/reviews/`, return summary only
- Sectional CAPTURE: REPLACE/MERGE semantics for `facts.md` with dedup rules
- Pipeline router: structured context collection via AskUserQuestion (Step 3.5)
- Plan approval in fix-code and tests pipelines
- Stack tables extracted to `includes/stack-adaptations.md`

### Changed
- Architect agent enforced PLAN MODE — no file creation/modification
- Orchestrator converted to Task() dispatcher with parallel step-4/4b/4c
- All step files have input/output contracts
- `issues.md`: 30-row limit, frequency dedup
- `maintain-memory.sh`: dead link cleanup, issues compaction, `output/` rotation

## [5.2.0] - 2026-02-23

### Changed
- Hook system refactor: 5 → 3 hooks
- Removed `git-context.sh` (Claude Code has native git access)
- Removed `session-summary.sh` (generated unused reports)
- `track-agent.sh`: `grep -oP` → `jq capture()`, drop session_id/char counters
- `maintain-memory.sh`: drop file init, POSIX-only commands, env var thresholds
- `update-schema.sh`: credentials via `docker exec printenv`, staleness check
- `settings.json.tpl`: hooks integrated, Stop section removed

## [5.1.0] - 2026-02-23

### Changed
- Cleanup README: remove generated output descriptions (Invocable Skills, Pipeline-система, Memory-система, Hooks, MCP, Кастомизация)
- Fix `state/` → `memory/` references

## [5.0.0] - 2026-02-16

### Added
- **Adaptive Teams** — `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` env detection
- `includes/capability-detect.md` — Phase 0 for team/sequential mode selection
- Team mode sections in new-code and review pipelines
- Graceful degradation: team spawn fail → sequential fallback

## [4.0.0] - 2026-02-15

### Changed
- **Modular architecture** — monolithic meta-prompt extracted into 5 step files + templates/
- step-4-generate (638 lines) split into 3 batches: agents, skills+pipelines, hooks+settings+MCP
- Fixes context window overflow on late generation steps
- Orchestrator runs 7 sequential steps with compression between batches

## [3.0.0] - 2026-02-13

### Added
- **Optional GitLab MCP integration** — `.mcp.json` generation, `gitlab-manager` agent, `skills/gitlab/SKILL.md`

## [2.1.0] - 2026-02-13

### Changed
- Replace text-based questions (y/n, comma-separated) with structured AskUserQuestion calls
- Two-step flow for custom agents/skills/pipelines with multiSelect support

## [2.0.0] - 2026-02-13

### Added
- **Pipeline skill-router** (`/pipeline`, `/p`) replaces passive routing
- **Memory system**: `patterns.md`, `issues.md`, `maintain-memory.sh`
- Verification moved to `scripts/verify-bootstrap.sh`
- Upgrade mode with SHA256 diff detection
- `git-context.sh` hook, CI Manager agent, input templates
- Error handling (`trap ERR`) in all hooks
- Auto-Pipeline Rule in CLAUDE.md template

### Removed
- Dead `session.md` and `task-log.md`

## [1.0.0] - 2026-02-10
- Initial commit — bootstrap system with meta-prompt, agents, commands
