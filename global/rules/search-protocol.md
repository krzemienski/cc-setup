# Search Protocol

## Hierarchy (mandatory order)

### Symbols (functions, classes, types)
1. lsp_workspace_symbols — search by name across workspace
2. lsp_find_references — find all callers
3. lsp_goto_definition — navigate to source
4. ast_grep_search — structural AST pattern matching

### Files
1. Glob — fast pattern matching (**/*.swift, **/*.ts)
2. smart_search — tree-sitter symbol + file search

### Content
1. Grep — ripgrep content search

### Non-code files (Markdown, YAML, Dockerfile, scripts)
- Glob for paths, Grep for content. LSP/AST do not apply.

## NEVER use in Bash for code search
- find, fd, locate — causes wrong paths, shallow globs, miscounts
- Exception: find OK for non-code ops (disk cleanup, file age, permissions)
