# Bootstrap — Team Flow

Team имплицитный: отдельного создания/удаления команды нет. Агент, спавненный через `Agent(name=...)`, адресуем по имени через SendMessage. Lead (эта сессия) для агентов — получатель `main`.

## Defaults

| Параметр | Значение |
|----------|----------|
| Agent mode | `auto` |
| Agent model | `sonnet` (генерация: `opus`) |
| References dir | `${CLAUDE_SKILL_DIR}/references/` |
| Templates | `${CLAUDE_PLUGIN_ROOT}/templates/` |
| Plugin root | `${CLAUDE_PLUGIN_ROOT}` |
| Cache | `.claude/.cache/` |
| State | `.claude/.cache/state.json` |

## Interaction pattern

Team-агенты не вызывают AskUserQuestion. Когда нужен ввод пользователя:

1. Агент записывает данные в `.claude/.cache/{step}-interaction.json`
2. Агент: `SendMessage(to="main", summary="interaction required", message="interaction_required: .claude/.cache/{step}-interaction.json")`
3. Lead читает файл, вызывает AskUserQuestion
4. Lead: `SendMessage(to="{agent}", summary="user response", message="user_response: {ответ}")`

## Subagent prompt template

```
Прочитай {reference_path} и выполни.
Templates: ${CLAUDE_PLUGIN_ROOT}/templates/.
Plugin root: ${CLAUDE_PLUGIN_ROOT}.
TEAM MODE: не вызывай AskUserQuestion. Для ввода пользователя — запиши в .claude/.cache/{step}-interaction.json и SendMessage(to="main", summary="interaction required", message="interaction_required: .claude/.cache/{step}-interaction.json").
По завершении: SendMessage(to="main", summary="{step} done", message="done").
```

## Error protocol

| Событие | Действие |
|---------|----------|
| Agent error | Lead: AskUserQuestion → Повторить / Пропустить / Остановить |
| Первый Agent(name=...) spawn fail | Fallback: прочитай flow-sequential.md и выполни |
| Agent spawn fail mid-flow | Завершить фазу через Agent tool (без name, sequential). Оставшиеся фазы — sequential |

## Завершение агентов

Агенты завершаются сами по окончании задачи — отдельный shutdown-протокол не нужен. Завершённого агента можно продолжить через `SendMessage(to="{name}")` — контекст сохраняется.

---

## Resume Detection

Проверь `.claude/.cache/state.json`:

| Состояние | Действие |
|-----------|----------|
| Файл существует, валидный JSON | AskUserQuestion: "Найден незавершённый bootstrap. Продолжить / Заново / Отмена" |
| → Продолжить | Прочитай state.json → первый pending шаг → начни с него |
| → Заново | Удали `.claude/.cache/` → Phase A |
| → Отмена | Стоп |
| Файл существует, невалидный JSON | Удали `.claude/.cache/` → Phase A (corrupted state) |
| Файл не существует | Phase A |

---

## Phases

### Phase A — Init

```
Agent(name="initializer", model="sonnet", mode="auto",
  prompt="... step-init.md ...")
```

| Ожидание | Gate |
|----------|------|
| initializer → SendMessage(to="main", summary="init done", message="done") | `.claude/.cache/state.json` существует |

Прочитай `.claude/.cache/state.json` → `state.mode`:

| Mode | Действие |
|------|----------|
| empty | Стоп |
| fresh | Phase B → C → D → E |
| resume | Phase B → первый pending → ... → E |
| patch | Phase D-patch → E |
| upgrade | Phase D-upgrade |

---

### Phase B — Configure (sequential, lead координирует)

Интерактивные шаги — lead задаёт вопросы. Agent tool без name (изолированные субагенты, не team).

| Step | Owner | Reference |
|------|-------|-----------|
| Configure (3A) | subagent (Agent tool) | step-3-configure.md |
| Configure (3B) | lead asks via AskUserQuestion | — |
| Configure (3C) | subagent (Agent tool) | step-3-apply.md |
| Settings | subagent (Agent tool) | step-4-settings.md |
| Plugins (5A) | subagent (Agent tool) | step-5-plugins.md |
| Plugins (5B) | lead asks via AskUserQuestion | — |
| Plugins (5C) | subagent (Agent tool) | step-5-apply.md |

Settings и Plugins — только при `mode == "fresh"`. При upgrade — пропустить.

---

### Phase C — Preview (sequential)

| Step | Owner | Reference |
|------|-------|-----------|
| Preview | subagent (Agent tool) | step-6-preview.md |

| Результат | Действие |
|-----------|----------|
| done | Phase D |
| pause | Стоп |
| change | Вернуться к Phase B |

---

### Phase D — Generate (team, параллельно)

Перед спавном — создать директории (lead, Bash):
```bash
mkdir -p .claude/{agents,skills,pipelines,scripts/hooks,memory/{decisions/archive,sessions},output/{contracts,qa,plans,reviews,state},input/{tasks,plans},database}
```

#### D1: analysis_depth != "light"

```
Agent(name="deep-analyzer", model="opus", mode="auto",
  prompt="... step-7-analyze.md ...")

Agent(name="infra-gen", model="sonnet", mode="auto",
  prompt="... step-8-infra.md ... Стартуй сразу, не жди deep-analyzer.")

# Для КАЖДОГО lang из state.config.langs:
Agent(name="lang-gen-{lang}", model="opus", mode="auto",
  prompt="... step-8-lang.md для {lang} ... Жди сообщение от deep-analyzer (done + файлы в .claude/.cache/deep/). По завершении: SendMessage(to='main', summary='lang-gen done', message='done').")

# common-gen стартует ПОСЛЕ всех lang-gen (ждёт per-lang фрагменты code-style/testing)
# Lead ждёт done от всех lang-gen, затем спавнит common-gen:
Agent(name="common-gen", model="sonnet", mode="auto",
  prompt="... step-8-common.md ... Per-lang фрагменты готовы в .claude/.cache/skills/.")
```

Flow:
```
deep-analyzer ──→ SendMessage(to="lang-gen-php"): done
                → SendMessage(to="lang-gen-typescript"): done
                → SendMessage(to="main"): done
infra-gen ─────→ SendMessage(to="main"): done
lang-gen-{lang} → SendMessage(to="main"): done

lead ждёт done от ВСЕХ lang-gen + infra-gen, затем спавнит:
common-gen ────→ SendMessage(to="main"): done
```

deep-analyzer шлёт каждому lang-gen поимённо (не wildcard).
common-gen стартует только после всех lang-gen — ему нужны per-lang фрагменты из .claude/.cache/skills/.

#### D2: analysis_depth == "light"

Без deep-analyzer. lang-gen стартуют сразу. infra-gen стартует сразу. common-gen — после всех lang-gen.

#### Gate

Lead ждёт done от ВСЕХ агентов.

Partial failure: прочитать gen-report-8-*.json → если есть failed → AskUserQuestion.

---

### Phase D-patch

| Step | Owner | Reference |
|------|-------|-----------|
| Patch | subagent (Agent tool) | step-patch.md |

После patch → Phase E.

---

### Phase D-upgrade

```
Agent(name="upgrader", model="opus", mode="auto",
  prompt="... step-upgrade.md U.0-U.3 ... Known templates: ${CLAUDE_PLUGIN_ROOT}/known-templates.json.")
```

Upgrader → SendMessage(to="main"): interaction_required (U.2 — выбор файлов).
Lead обрабатывает interaction, отвечает upgrader-у.
Upgrader → SendMessage(to="main"): done.

Затем:
- Phase B (Configure only, без Settings/Plugins)
- Phase C (Preview)
- Phase D (Generate)

После генерации:
```
Agent(name="restorer", model="opus", mode="auto",
  prompt="... step-upgrade.md U.5-U.6 ...")
```

Restorer → SendMessage(to="main"): done. → Phase E.

---

### Phase E — Finalize

```
Agent(name="finalizer", model="opus", mode="auto",
  prompt="... step-finalize.md ...")
```

Finalizer → SendMessage(to="main"): done.
