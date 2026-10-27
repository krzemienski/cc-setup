---
name: devlog-publisher
description: Mines Claude Code session history across all projects on the local machine over a configurable timeframe (default 30 days), extracts technical insights and patterns, then spawns a teammate-based content pipeline to produce deeply technical blog posts, social media campaigns, and engagement-optimized content for an agentic developer's personal brand. Use when asked to create devlogs, publish session insights, build content from Claude Code history, or generate technical blog posts from coding sessions.
---

<essential_principles>

This skill turns real Claude Code session history into a high-signal content engine. It analyzes JSONL session logs across every project on your machine, identifies the most compelling technical patterns, breakthroughs, and problem-solving approaches, then orchestrates a multi-agent teammate pipeline to produce publication-ready content with extreme technical depth.

**Real Sessions, Real Insights** — Every piece of content originates from actual Claude Code conversations. No fabricated examples. No generic advice. Your authentic development workflow IS the content.

**Technical Depth Over Fluff** — Every blog post includes real code snippets, actual terminal output, concrete architecture decisions, and measurable outcomes extracted from sessions. Readers should be able to reproduce your techniques.

**Traction-Aware** — Before writing, analyze what technical content is performing well in the current landscape (HackerNews, Dev.to, X/Twitter dev community, LinkedIn engineering). Adapt angles and framing to match high-performing patterns while keeping content authentic.

**Teammate Orchestration** — Uses Claude Code's `teammate` spawning to parallelize content creation across platforms, ensuring zero overlap in angles while maintaining consistent technical accuracy.

**Configurable Lookback** — User specifies the timeframe window (default: 30 days). The skill scans ALL projects and sessions within that window.

</essential_principles>

<intake>
What would you like to do?

1. **Full Pipeline** — Analyze sessions → Extract insights → Create all content (blog + social + newsletter)
2. **Session Analysis Only** — Scan and summarize sessions, surface top insights without writing content
3. **Content From Specific Insight** — You already know what to write about, need the pipeline to produce it
4. **Traction Research** — Analyze what technical content is performing well right now to inform your next post

Specify your **lookback window** (default: 30 days) and any **topic filters** (e.g., "only Kubernetes sessions", "focus on debugging").

**Wait for response before proceeding.**
</intake>

<routing>
| Response | Next Action |
|----------|-------------|
| 1, "full pipeline", "full", "everything" | Read workflows/full-pipeline.md |
| 2, "analysis", "scan", "sessions only" | Read workflows/session-analysis.md |
| 3, "specific", "write about", "insight" | Read workflows/targeted-content.md |
| 4, "traction", "research", "trending" | Read workflows/traction-research.md |

**Default parameters (override with $ARGUMENTS):**
- Lookback: 30 days
- Projects: ALL on machine
- Blog length: 1,500–2,500 words
- Social platforms: X/Twitter thread, LinkedIn post, Dev.to cross-post
- Newsletter: 400–600 words
- Technical depth: Maximum (include code, terminal output, architecture diagrams)

**After reading the workflow, follow it exactly.**
</routing>

<session_discovery>
Claude Code stores session data in JSONL format. The skill MUST scan these locations:

```bash
find ~/.claude/projects -name "*.jsonl" -type f
find ~/.claude -name "session*" -type f
find / -maxdepth 5 -path "*/.claude/sessions*" -type f 2>/dev/null
```

**Session parsing strategy:**
1. List all JSONL session files modified within the lookback window
2. Parse each file line-by-line extracting human/assistant message pairs
3. Identify sessions with substantial technical content (>10 message exchanges)
4. Extract: tools used, files modified, errors encountered, solutions found
5. Rank sessions by "insight density" — ratio of novel problem-solving to routine tasks

**Filtering:** by date range (lookback window), by project path, by keyword/topic, by session length (skip under 5 exchanges).
</session_discovery>

<insight_extraction>
Score each session on these dimensions:

1. **Novel Problem-Solving** (weight 3x) — Non-obvious solutions, debugging approaches, architecture pivots, creative workarounds
2. **Tool/Pattern Discovery** (weight 3x) — Effective Claude Code techniques, MCP usage, skill creation, agent orchestration
3. **Before/After Transformation** (weight 2x) — Clear state change with measurable improvement
4. **Failure + Recovery** (weight 3x) — Something broke, deep debugging, satisfying resolution
5. **Reproducibility** (weight 1x) — Can another developer follow these exact steps?
6. **Scale/Performance** (weight 1x) — Quantifiable metrics: time saved, lines changed, builds improved

Rank insights by composite score. Select top 3-5 for content pipeline.
</insight_extraction>

<teammate_architecture>
The full pipeline spawns these teammates:

1. **Session Miner** — Scans all JSONL sessions, extracts and ranks insights, produces a structured insight brief with code snippets and context. Must complete before writers begin.
2. **Traction Analyst** — Researches current high-performing technical content across platforms. Shares findings with all writers before they start.
3. **Blog Writer** — Transforms the top insight into a 1,500–2,500 word deeply technical blog post. First person. Extreme technical specificity. Every code block from actual sessions.
4. **Social Thread Writer** — Creates a 7-12 post X/Twitter thread from a DIFFERENT angle than the blog.
5. **LinkedIn Writer** — Creates a 200-350 word LinkedIn post from ANOTHER unique angle. Max 3 hashtags.
6. **Newsletter Writer** — Creates a 400-600 word email newsletter. One exclusive insight NOT in the blog.

**Coordination:** Session Miner and Traction Analyst run first (parallel). Writers share chosen angles before drafting to prevent overlap. Synthesis review checks consistency after all complete.
</teammate_architecture>

<output_structure>
All outputs saved to `outputs/devlog-publisher/{date}/`:

```
outputs/devlog-publisher/{YYYY-MM-DD}/
├── session_analysis.md
├── insight_brief.md
├── traction_report.md
├── blog_post.md
├── twitter_thread.md
├── linkedin_post.md
├── newsletter.md
├── campaign_summary.md
└── publishing_checklist.md
```
</output_structure>

<reference_index>
All domain knowledge in `references/`:

**Session Mechanics:** session-parsing.md — How to locate, parse, and filter JSONL session files across all projects
**Insight Evaluation:** insight-scoring.md — 6-dimension weighted scoring system for ranking content-worthy insights
**Content Strategy:** traction-patterns.md — What technical content formats and angles drive engagement in 2025-2026
</reference_index>

<workflows_index>
| Workflow | Purpose |
|----------|---------|
| full-pipeline.md | Complete 4-phase pipeline: scan → research → write (4 teammates) → synthesis |
| session-analysis.md | Scan-only mode: catalog sessions and rank insights without generating content |
| targeted-content.md | Write about a specific known insight using the teammate content pipeline |
| traction-research.md | Research current high-performing technical content to inform strategy |
</workflows_index>

<success_criteria>
A successful run produces:
- Session analysis covering ALL projects within the lookback window
- At least 3 ranked insights with supporting code/output evidence
- Blog post with real code snippets from actual sessions (no fabrication)
- All 4 content pieces lead with DIFFERENT angles (no overlap)
- Cross-platform consistency review completed with no contradictions
- Every claim in content is traceable to a specific session
- Technical depth sufficient for a senior engineer to reproduce the techniques
</success_criteria>
