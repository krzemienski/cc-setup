# Open Questions

## cc-setup-full-audit - 2026-03-20

- [ ] **Hook registration matchers need source verification** -- The 6 unregistered hooks have estimated event types and matchers based on naming conventions. The executor must read each hook's source to confirm the correct event/matcher before registering. Incorrect matchers mean hooks never fire.

- [ ] **settings.json merge: who wins for scalar preferences?** -- When template has `effortLevel: "high"` and user has `effortLevel: "medium"`, should the user's value be preserved (user wins) or should template override? Current plan says user wins for preferences, template wins for env/model config. Confirm this is the desired behavior.

- [ ] **--clean mode: should it prompt for confirmation?** -- Currently --clean silently overwrites. The plan adds a warning message, but should it also require interactive confirmation (y/N) or is a printed warning sufficient? Non-interactive (warning only) is simpler for CI/scripted deploys.

- [ ] **Remote machine OS** -- The plan assumes home.hack.ski might be Linux. Confirm the remote OS so platform-awareness testing is targeted correctly.

- [ ] **serena MCP server: macOS-only or cross-platform?** -- serena uses uvx (Python) and may work on Linux. The plan groups it with macOS-only servers (tuist, xcode, pencil). Verify whether serena should be gated or left as cross-platform.

- [ ] **Duplicate agents in plugin agents/ vs global/agents/** -- The 10 agents that exist in both directories (brainstormer, docs-manager, etc.) may have diverged in content. Before deleting global/agents/, diff the overlapping files to check if global/ has newer content that should be synced to plugin agents/ first.
