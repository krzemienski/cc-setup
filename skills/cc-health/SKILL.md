---
name: cc-health
description: Verify Claude Code setup — hooks, plugins, MCP servers, rules, agents
triggers:
  - "health check"
  - "verify setup"
  - "check config"
  - "cc health"
  - "cc-health"
---

# CC Health Check

Verify the entire Claude Code setup is working correctly.

## What It Checks
- Hook syntax (node --check on all .js/.cjs files)
- Enabled plugins count
- MCP server count (.mcp.json + .claude.json)
- Rules file count
- Agent file count
- Empty hook matcher groups in settings.json
- settings.json valid JSON

## Usage
Run the health check script:
```bash
~/cc-setup/health.sh
```

Report results to user with pass/fail for each category.
