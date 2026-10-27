# Шаг 4: Settings.json

> Modes: fresh

> **SUBAGENT ISOLATION:** Этот шаг выполняется как изолированный субагент.

## Вход
- `.claude/.cache/state.json` → `config` (permissions_level, git_permissions), `stack`

**Defaults если поля отсутствуют в config:**
- `permissions_level` → `"balanced"`
- `git_permissions` → `["read"]`
- `analysis_depth` → `"standard"`

## Выход
- `.claude/settings.json` (базовые permissions + hooks)
- Обновлённый state

---

## ФОРМАТ SETTINGS.JSON

Важно: Соблюдай точный формат Claude Code settings.json.

### Permissions

Все bash-команды обёрнуты в `Bash(command:*)`:
```json
{
  "permissions": {
    "allow": [
      "Read",
      "Write",
      "Edit",
      "Bash(git status:*)"
    ],
    "deny": [
      "Bash(*npm install -g*)",
      "Bash(*npm i -g*)",
      "Bash(*yarn global add*)",
      "Bash(*pnpm add -g*)",
      "Bash(*curl*|*bash*)",
      "Bash(*curl*|*sh*)",
      "Bash(*wget*|*bash*)",
      "Bash(*wget*|*sh*)"
    ]
  }
}
```

Формат: `Bash(команда:*)` — двоеточие перед wildcard.
Инструменты без Bash: `Read`, `Write`, `Edit`, `Glob`, `Grep`, `WebSearch`, `WebFetch`, `Agent`.

### Hooks

Формат: `matcher` (опционально) + `hooks` array:
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Task|Agent",
        "hooks": [
          {"type": "command", "command": "bash $CLAUDE_PROJECT_DIR/.claude/scripts/hooks/track-agent.sh"}
        ]
      }
    ],
    "SessionStart": [
      {
        "hooks": [
          {"type": "command", "command": "bash $CLAUDE_PROJECT_DIR/.claude/scripts/hooks/maintain-memory.sh"}
        ]
      }
    ]
  }
}
```

---

## 4.1 Построение permissions

### Базовые (всегда)
```json
"Read", "Write", "Edit",
"Read(.claude/**)", "Edit(.claude/**)",
"WebSearch", "WebFetch",
"Bash(wc:*)", "Bash(sort:*)", "Bash(du:*)", "Bash(touch:*)",
"Bash(test:*)", "Bash(mkdir:*)"
```

> `Edit(.claude/**)` — explicit allow для .claude/ директории.
>
> **Не добавлять `Write(.claude/**)`.** Файловые permission-проверки применяются только к
> `Edit(path)` и `Read(path)`: `Edit` покрывает все инструменты записи (Write, Edit, NotebookEdit),
> `Read` — все инструменты чтения (Read, Glob, Grep). Правила вида `Write(path)`, `Glob(path)`,
> `Grep(path)` игнорируются, и Claude Code пишет предупреждение на каждом старте сессии.
> Голые `"Write"`, `"Glob"` без скобок — правила уровня инструмента, они валидны.

### Git (из `config.git_permissions[]`)

| Выбор | Permissions |
|-------|-------------|
| `read` | `Bash(git status:*)`, `Bash(git log:*)`, `Bash(git diff:*)`, `Bash(git show:*)`, `Bash(git branch:*)`, `Bash(git rev-parse:*)` |
| `write` | `Bash(git add:*)`, `Bash(git commit:*)` |
| `push` | `Bash(git push:*)`, `Bash(git pull:*)`, `Bash(git fetch:*)` |
| `delete` | `Bash(git reset:*)`, `Bash(git checkout:*)`, `Bash(git clean:*)`, `Bash(git branch -D:*)`, `Bash(git stash:*)` |

Добавь ТОЛЬКО те группы, которые пользователь выбрал на step 3.
Если `git_permissions` нет в state — по умолчанию `["read"]`.

### Level-based (из `config.permissions_level`)

#### conservative
Только базовые + git (по выбору).

#### balanced
Всё из conservative, плюс:
```json
"Bash(make:*)", "Bash(curl:*)", "Bash(chmod:*)", "Bash(mkdir:*)", "Bash(bash:*)"
```

Плюс lang-specific (на основе `stack.langs` и `stack.pkg_managers`):
- php → `"Bash(composer:*)"`, `"Bash(php:*)"`
- node/ts/js → `"Bash(npm:*)"`, `"Bash(npx:*)"`, `"Bash(node:*)"`
- yarn → `"Bash(yarn:*)"`
- pnpm → `"Bash(pnpm:*)"`
- go → `"Bash(go:*)"`
- python → `"Bash(python:*)"`, `"Bash(python3:*)"`, `"Bash(pip:*)"`, `"Bash(pip3:*)"`
- cargo/rust → `"Bash(cargo:*)"`
- ruby → `"Bash(bundle:*)"`, `"Bash(rails:*)"`, `"Bash(rake:*)"`
- dotnet → `"Bash(dotnet:*)"`
- java/mvn → `"Bash(mvn:*)"`
- java/gradle → `"Bash(gradle:*)"`

Плюс lint/test команды из `stack.lint_cmds` и `stack.test_cmds` — обернуть в `Bash(command:*)`.

#### permissive
Всё из balanced, плюс git write/push если не были выбраны:
```json
"Bash(git add:*)", "Bash(git commit:*)", "Bash(git push:*)", "Bash(git pull:*)"
```

---

## 4.2 Deny rules (всегда, независимо от стека)

Защита от установки пакетов мимо lock-файла и от `curl | bash`.

```json
"deny": [
  "Bash(*npm install -g*)",
  "Bash(*npm i -g*)",
  "Bash(*yarn global add*)",
  "Bash(*pnpm add -g*)",
  "Bash(*curl*|*bash*)",
  "Bash(*curl*|*sh*)",
  "Bash(*wget*|*bash*)",
  "Bash(*wget*|*sh*)"
]
```

Генерировать **ВСЕГДА**, независимо от стека.

В patch mode: если deny отсутствует → `[+ADD]`. Если есть кастомные deny-правила пользователя → `[USER]`, сохранить.

### НИКОГДА не добавлять `Read(...)` в deny

**Ни одного правила `Read` или `Read(path)` в `permissions.deny`** — ни на vendor-каталоги, ни на
секреты, ни на что-либо ещё. Причина не в самом правиле, а в safety-проверке Claude Code:

Если в `deny` есть **хотя бы одно** правило, начинающееся на `Read` — неважно, на какой путь оно
указывает, — то любая read-команда в Bash (`grep`, `cat`, `head`, `less`, …) с **относительным**
путём после `cd` уходит в ручной промпт:

> `grep on '...' after a cd would search a directory that cannot be determined here, and a Read()
> deny rule is configured; only you can approve running it anyway.`

Это решение помечено `classifierApprovable: false` — auto mode его не снимает никогда, кнопку
жмёт человек, на каждый такой вызов. Фильтрации по каталогу в проверке нет: одно правило на
`**/node_modules/**` ломает `grep` по своему же `src/`. Абсолютный путь проверку проходит,
относительный после `cd` — нет.

Цена при этом почти нулевая: `Read(path)` покрывает только инструменты чтения Claude Code, а
`cat`/`grep` из Bash обходят его тривиально — реальной защиты правило не даёт.

Защита инструкционных файлов из зависимостей (`node_modules/`, `vendor/`, `site-packages/`)
переехала в правило Supply Chain в генерируемом `CLAUDE.md` (см. step-finalize). Защита секретов —
там же; правил `Read(**/.env)` и подобных в settings.json не заводить.

---

### Невалидные permission-правила (чинить автоматически в patch mode)

Файловые permission-проверки применяются только к `Edit(path)` и `Read(path)`. Правила вида
`Write(path)`, `Glob(path)`, `Grep(path)`, `NotebookEdit(path)` игнорируются, и Claude Code
печатает предупреждение по каждому на старте сессии.

Если в текущем `settings.json` (в `allow` или `deny`) найдены такие правила — починить БЕЗ
подтверждения пользователя:

| Найдено | Где | Действие |
|---------|-----|----------|
| `Write(p)`, `NotebookEdit(p)` — рядом уже есть `Edit(p)` с тем же путём | allow, deny | удалить как дубль |
| `Write(p)`, `NotebookEdit(p)` — `Edit(p)` нет | allow, deny | переписать в `Edit(p)` |
| `Glob(p)`, `Grep(p)` — рядом уже есть `Read(p)` с тем же путём | allow | удалить как дубль |
| `Glob(p)`, `Grep(p)` — `Read(p)` нет | allow | переписать в `Read(p)` |
| `Glob(p)`, `Grep(p)` | deny | удалить (переписывать в `Read(p)` НЕЛЬЗЯ, см. §4.2) |
| `Read`, `Read(p)` — любое правило | deny | удалить, см. §4.2 |

Голые `"Write"`, `"Glob"`, `"Grep"` без скобок — правила уровня инструмента, НЕ трогать.
Голый `"Read"` без скобок в `allow` — тоже валидное правило, НЕ трогать; удаляется только из `deny`.

Если из `deny` удалены правила на инструкционные файлы зависимостей
(`Read(**/node_modules|vendor|site-packages/**/SKILL.md|CLAUDE.md|AGENTS.md|.cursorrules)`) —
убедиться, что правило Supply Chain есть в `CLAUDE.md` проекта (step-finalize, §9.2 шаг 3).

Лог:
- `[FIX] permissions.deny Read(**/vendor/**/CLAUDE.md) → ломает Bash-grep после cd, удалено`
- `[FIX] permissions.deny Glob(**/vendor/**/SKILL.md) → правило игнорируется, удалено`

---

## 4.3 Hooks

Базовые hooks (всегда):
- `track-agent.sh` → PostToolUse, matcher: "Task|Agent"
- `maintain-memory.sh` → SessionStart

Если `stack.db` != none (реальная БД, не кэш/очередь):
- `update-schema.sh` → SessionStart

### Deprecated hooks (удалять автоматически в patch mode)

Если в текущем `settings.json` найдены — удалить БЕЗ подтверждения пользователя:

| Hook | Event | Причина удаления |
|------|-------|-----------------|
| `session-summary.sh` | Stop | Удалён в v5.2 — генерировал неиспользуемые отчёты |
| `git-context.sh` | SessionStart | Удалён в v5.2 — Claude Code имеет нативный доступ к git |

Также удалить:
- Весь блок `"Stop"` из hooks, если содержит только deprecated хуки
- Ссылки на несуществующие скрипты (проверить `[ -f "$CLAUDE_PROJECT_DIR/.claude/scripts/hooks/{name}.sh" ]`)

Лог: `[DEL] hooks.Stop.session-summary.sh (deprecated since v5.2)`

---

## 4.4 Режим `fresh`

Собрать permissions + hooks → записать в `.claude/settings.json`.

Если Write отклонён пользователем — верни error.

---

## Лог

Перед checkpoint запиши лог в `.claude/.cache/step-4-log.md`:

```markdown
# Step 4: Settings.json — Log

## Выполненные действия
- {что конкретно было сделано, файлы созданные/изменённые}

## Пропущенные действия
- {что было пропущено и почему}

## Ошибки
- {ошибки если были, или "нет"}
```

Записать лог ПЕРЕД checkpoint.

## Checkpoint

Обнови `.claude/.cache/state.json`:
- `steps.settings.status` → `"completed"`
- `steps.settings.completed_at` → `"{ISO8601}"`
