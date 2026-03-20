---
name: cc-health
description: Run health check on Claude Code configuration — hooks, plugins, MCP servers, rules, agents
---

# CC Health Check

Run the cc-setup health check to verify your Claude Code environment is working correctly.

## Usage

Execute the health check script:
```bash
~/cc-setup/health.sh
```

## What It Checks
- Hook syntax (node --check on all .js/.cjs files)
- Enabled plugins count
- MCP server count (.mcp.json + .claude.json)
- Rules file count
- Agent file count
- settings.json valid JSON
- Empty hook matcher groups

Report results to the user with pass/fail for each category.
