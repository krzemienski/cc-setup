# Claude Code 2.1 Adoption Design

**Date:** 2026-01-08
**Status:** Ready for implementation

## Summary

Adopt Claude Code 2.1 features to extend Axiom's router architecture, improving context efficiency and developer experience while fixing a session-halting bug.

## Key Benefits

### For Release Notes

**Precision routing without menu clutter.** Before Claude Code 2.1, creating specialized skills meant cluttering the slash command menu. Now with `user-invocable: false`, Axiom can have many focused skills for precise context loading while keeping the user experience clean. Router decides what to load BEFORE any context is consumed—maximum efficiency.

**Agent-scoped hooks reduce noise.** Global hooks fire on every tool use. Claude Code 2.1's agent hooks only fire within that agent's lifecycle—cleaner output, more focused safety checks.

**Bug fix: Sessions no longer halt on successful bash commands.** Prompt hooks were causing Claude to output verbose explanations on every Bash invocation, halting sessions. Replaced with silent command hooks that only output on pattern match.

## Design Decisions

### Decision 1: Separate Skills over Subdirectories

**Context:** Supporting content files (CARPLAY.md, LEGACY.md, etc.) needed restructuring.

**Options considered:**
- Option B (references/ subdirectory): Standard plugin-dev pattern, Claude decides what to load
- Option E (separate skills): Router decides before context consumed

**Decision:** Option E (separate skills) + `user-invocable: false`

**Rationale:**
- Router decides BEFORE any context consumed (maximum efficiency)
- `user-invocable: false` solves menu clutter that made this impractical before 2.1
- Aligns with Axiom's proven router architecture
- Extends rather than abandons existing patterns

### Decision 2: Command Hooks over Prompt Hooks

**Context:** PostToolUse prompt hook was causing verbose output and session halts.

**Decision:** Remove prompt hook, rely on command hook for error detection.

**Rationale:**
- Prompt hooks cause Claude to reason about every invocation (noisy)
- Command hooks only output when patterns match (silent otherwise)
- Command hook already covers build failure patterns

### Decision 3: Agent-Scoped Hooks for Safety Checks

**Context:** 4 agents make potentially destructive changes (build-fixer, build-optimizer, iap-implementation, simulator-tester).

**Decision:** Add PreToolUse hooks to agent frontmatter rather than global hooks.

**Rationale:**
- Safety warnings only fire within agent lifecycle
- Reduces noise in normal development
- Cleaner separation of concerns

## Implementation Plan

### Phase 1: Create New Specialized Skills (4 skills)

| New Skill | Source | Router |
|-----------|--------|--------|
| `axiom-now-playing-carplay` | CARPLAY.md | ios-integration |
| `axiom-now-playing-musickit` | MUSICKIT.md | ios-integration |
| `axiom-networking-legacy` | LEGACY.md (renamed) | ios-networking |
| `axiom-networking-migration` | MIGRATION.md | ios-networking |

Each skill includes:
```yaml
---
name: axiom-now-playing-carplay
description: This skill should be used when implementing CarPlay Now Playing integration, CPNowPlayingTemplate customization, or CarPlay-specific playback controls.
user-invocable: false
---
```

### Phase 2: Inline REFERENCES.md Files (4 skills)

Append as `## Resources` section to parent skills:
- axiom-now-playing/REFERENCES.md → axiom-now-playing/SKILL.md
- axiom-networking/REFERENCES.md → axiom-networking/SKILL.md
- axiom-foundation-models/REFERENCES.md → axiom-foundation-models/SKILL.md
- axiom-extensions-widgets-ref/REFERENCES.md → axiom-extensions-widgets-ref/SKILL.md

### Phase 3: Add `user-invocable: false` (20 skills)

**Diagnostic skills (15):**
- axiom-accessibility-diag
- axiom-background-processing-diag
- axiom-camera-capture-diag
- axiom-cloud-sync-diag
- axiom-core-data-diag
- axiom-core-location-diag
- axiom-energy-diag
- axiom-foundation-models-diag
- axiom-metal-migration-diag
- axiom-networking-diag
- axiom-storage-diag
- axiom-swiftdata-migration-diag
- axiom-swiftui-debugging-diag
- axiom-swiftui-nav-diag
- axiom-vision-diag

**Internal skill (1):**
- axiom-using-axiom

**New specialized skills (4):**
- axiom-now-playing-carplay
- axiom-now-playing-musickit
- axiom-networking-legacy
- axiom-networking-migration

### Phase 4: Fix Hook Bug

Remove lines 8-10 from `hooks.json`:
```diff
- {
-   "type": "prompt",
-   "prompt": "If this bash command was xcodebuild/swift build and it failed (non-zero exit), suggest: 'Build failed. Run /axiom:fix-build for automatic diagnostics?'"
- },
```

### Phase 5: Add Agent Hooks (4 agents)

| Agent | PreToolUse Hook Purpose |
|-------|------------------------|
| build-fixer | Warn before `killall`, `rm -rf DerivedData` |
| build-optimizer | Warn before modifying `.pbxproj` |
| iap-implementation | Warn before writing StoreKit configs |
| simulator-tester | Warn before simulator state changes |

### Phase 6: Update Routers (2 routers)

**ios-integration:** Add routing for CarPlay, MusicKit keywords
**ios-networking:** Add routing for legacy iOS, migration keywords

## Commit Strategy

```
feat: leverage Claude Code 2.1 for precision routing

- Convert supporting content to specialized skills for maximum context efficiency
- Add user-invocable: false to hide internal skills from menu (2.1 feature)
- Router decides what to load BEFORE context consumed
- Benefits: Same skill count, cleaner UX, lower context usage

fix: remove noisy PostToolUse prompt hook

- Prompt hooks cause Claude to explain every invocation
- Command hooks only output on pattern match (silent otherwise)
- Fixes "stopped continuation" messages halting sessions

feat: add agent-scoped PreToolUse hooks (2.1 feature)

- Safety warnings scoped to agent lifecycle, not global
- build-fixer: warn before killall, rm -rf DerivedData
- build-optimizer: warn before .pbxproj changes
- Cleaner output, more focused safety checks
```

## Testing Plan

1. Verify new specialized skills are discoverable via router but NOT in slash command menu
2. Verify diagnostic skills no longer appear in slash command menu
3. Verify hook bug is fixed (no "stopped continuation" messages)
4. Verify agent hooks fire only within agent context
5. Run version script to confirm all skills counted correctly

## Files Changed

| Category | Count | Files |
|----------|-------|-------|
| New skills | 4 | skills/axiom-now-playing-carplay/SKILL.md, etc. |
| Deleted files | 4 | CARPLAY.md, MUSICKIT.md, LEGACY.md, MIGRATION.md |
| Modified skills | 24 | 20 visibility + 4 resources inlined |
| Modified agents | 4 | build-fixer, build-optimizer, iap-implementation, simulator-tester |
| Modified routers | 2 | ios-integration, ios-networking |
| Modified hooks | 1 | hooks.json |
