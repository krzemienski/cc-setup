# Swift Health Check Agent — Design

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** A meta-audit agent that auto-detects relevant auditors, runs them in parallel, deduplicates findings by file:line, and produces a single prioritized report.

**Architecture:** Single agent orchestrating existing auditors. No new skills — just orchestration logic.

## Auto-Detection

Grep/glob the project for framework signals:

| Signal | Auditors Triggered |
|--------|-------------------|
| `import SwiftUI` | swiftui-performance, swiftui-architecture, swiftui-layout, swiftui-nav |
| `import SwiftData` / `@Model` | swiftdata |
| `import CoreData` / `.xcdatamodeld` | core-data |
| `async` / `await` / `actor` | concurrency |
| `Timer` / `CLLocationManager` | energy |
| `AVCaptureSession` | camera |
| `LanguageModelSession` / `@Generable` | foundation-models |
| `import SpriteKit` | spritekit |
| `NWConnection` / `URLSession` | networking |
| `NSUbiquitousKeyValueStore` / `CKContainer` | icloud |
| Any Swift file | memory, security-privacy, swift-performance, modernization, codable, accessibility |

"Always run" auditors (memory, security, accessibility, swift-performance, modernization, codable) launch regardless — these apply to every project.

## User Override

User can say "skip spritekit, skip camera" to exclude auto-detected auditors. No "include" override — if auto-detection misses something, run that auditor individually.

## Deduplication

After all auditors complete, scan results for duplicate file:line references. Merge into single finding with multiple domain tags:
`[Memory, Concurrency] AppViewModel.swift:47 — closure captures self strongly in async context`

## Output Format

```
## Swift Health Check — [Project Name]
## [Date] — [N] auditors ran, [M] findings

### Critical Findings

1. [Security] AppConfig.swift:12 — Hardcoded API key in source
2. [Memory, Concurrency] DataManager.swift:89 — Strong self capture in Task
3. [Accessibility] LoginView.swift:34 — Image missing accessibility label
4. [SwiftUI Performance] FeedView.swift:56 — DateFormatter created in view body
5. [Concurrency] NetworkService.swift:23 — Missing @MainActor on UI update

### Concurrency (4 findings)
...

### Memory (3 findings)
...

### Passed Audits
✓ Networking — no issues found
✓ Energy — no issues found
```

## Invocation

- Command: `/axiom:health-check`
- Natural language: "run a health check on my project" / "scan everything"
- Alias: `/axiom:audit all`

## Implementation

- Agent file: `agents/health-check.md`
- Uses `axiom-ios-build` skill for project structure detection
- Launches auditors via Agent tool with `run_in_background: true`
- Writes combined report to `scratch/health-check-{date}.md`
- No new skills needed — just orchestration
