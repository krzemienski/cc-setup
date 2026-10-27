<workflow name="full-pipeline">

<objective>
Execute the complete devlog publishing pipeline: scan Claude Code sessions across all projects within the specified lookback window, extract and rank technical insights, research current content traction patterns, then spawn a coordinated teammate pipeline to produce a deeply technical blog post, X/Twitter thread, LinkedIn post, and email newsletter — each with a unique angle and zero content overlap.
</objective>

<required_reading>
Before executing, read:
- references/session-parsing.md (how to find and parse JSONL sessions)
- references/insight-scoring.md (how to rank insights)
- references/traction-patterns.md (what technical content performs well)
- templates/blog-post.md (blog structure template)
- templates/social-content.md (social platform templates)
</required_reading>

<parameters>
Parse from $ARGUMENTS or use defaults:
- **lookback_days**: Number of days to scan back (default: 30)
- **topic_filter**: Optional keyword filter (default: none — scan everything)
- **project_filter**: Optional project path filter (default: all projects)
- **blog_length**: Target word count for blog (default: 1500-2500)
- **platforms**: Content platforms to target (default: blog, twitter, linkedin, newsletter)

Example invocations:
- `/devlog` → Full pipeline, 30 day lookback, all projects
- `/devlog 14` → Full pipeline, 14 day lookback
- `/devlog 60 kubernetes` → 60 day lookback, only Kubernetes-related sessions
</parameters>

<process>

<phase name="1-session-mining">
**Phase 1: Session Discovery and Mining**

1. **Locate all session files** within the lookback window:
   ```bash
   find ~/.claude -name "*.jsonl" -type f -mtime -${lookback_days}
   find ~/ -maxdepth 6 -path "*/.claude/*.jsonl" -type f -mtime -${lookback_days} 2>/dev/null
   ```

2. **Parse each session file**: Read line-by-line, each line is a JSON object. Extract message pairs (human prompt → assistant response). Identify tools invoked, files created/modified, errors hit, solutions applied. Calculate session metrics: duration, message count, complexity score.

3. **Apply filters** if specified: Date range (only sessions within lookback window), topic (grep for keyword matches in message content), project (filter by file path prefix).

4. **Score and rank sessions** using the insight extraction criteria from SKILL.md: Novel problem-solving (3x), Tool/pattern discovery (3x), Before/after transformation (2x), Failure + recovery narrative (3x), Reproducibility (1x), Scale/performance metrics (1x).

5. **Produce the insight brief**: Top 5 insights with one-sentence summary, source session path and timestamp, key code snippets (actual, from the session), terminal output or error messages (actual), and the story arc (problem → investigation → solution).

Save to `outputs/devlog-publisher/{date}/session_analysis.md` and `outputs/devlog-publisher/{date}/insight_brief.md`.
</phase>

<phase name="2-traction-research">
**Phase 2: Traction Research**

Run in parallel with Phase 1 if possible, otherwise immediately after.

1. **Search current technical content landscape**: What Claude Code / AI coding content is trending on HackerNews, Dev.to, X/Twitter. What formats are performing (tutorials vs. war stories vs. benchmarks vs. opinion). What hooks are getting engagement. Identify 3-5 high-performing posts in the AI development tools space.

2. **Extract traction patterns**: Common title structures that get clicks, optimal thread length for X/Twitter developer audience, LinkedIn engagement triggers for engineering content, newsletter subject line patterns with high open rates.

3. **Map insights to traction patterns**: For each top insight from Phase 1, suggest the best content angle and format based on what's working now.

Save to `outputs/devlog-publisher/{date}/traction_report.md`.
</phase>

<phase name="3-content-pipeline">
**Phase 3: Teammate Content Pipeline**

Spawn 4 teammates. Before any writing begins, share the insight brief and traction report with all teammates. Each teammate MUST declare their chosen primary angle and get confirmation it doesn't overlap with others.

**Teammate 1: Blog Writer** — Read the full insight brief and traction report. Select the #1 ranked insight as the primary story. Write a 1,500–2,500 word blog post with this structure: Hook (2-3 sentences with the problem or surprising result), Context (1-2 paragraphs on what you were building), Technical Deep-Dive (bulk of post with ACTUAL code, ACTUAL terminal output, ACTUAL error messages, inline and full code blocks, every decision explained), Results (what changed, metrics, before/after), Takeaway (what another developer can immediately apply). First person voice. Conversational but technically precise. Save to `outputs/devlog-publisher/{date}/blog_post.md`.

**Teammate 2: X/Twitter Thread Writer** — Choose a DIFFERENT angle from the Blog Writer. Write a 7-12 tweet thread: Tweet 1 is the hook (most surprising or contrarian statement), Tweets 2-10 build the narrative (one concept per tweet, self-contained but sequential), include descriptions of what code screenshots would show, final tweet is CTA linking to blog post. Each tweet ≤ 280 characters. Save to `outputs/devlog-publisher/{date}/twitter_thread.md`.

**Teammate 3: LinkedIn Writer** — Choose ANOTHER unique angle (neither Blog nor Twitter angle). Write a 200-350 word LinkedIn post: Professional hook line (pattern interrupt or counterintuitive insight), 3 key technical takeaways as short paragraphs, engagement question that invites technical discussion, max 3 relevant hashtags. Save to `outputs/devlog-publisher/{date}/linkedin_post.md`.

**Teammate 4: Newsletter Writer** — Choose the remaining angle. Write a 400-600 word email newsletter edition: Subject line (under 50 characters, curiosity-driven), preview text (under 100 characters), conversational body with ONE exclusive insight NOT in the blog, single clear CTA to the blog post. Save to `outputs/devlog-publisher/{date}/newsletter.md`.
</phase>

<phase name="4-synthesis">
**Phase 4: Synthesis and Quality Review**

After all 4 teammates complete:

1. **Cross-platform consistency check**: No contradictory technical claims across any pieces, same core value proposition present in all pieces, no two pieces lead with the same angle or example, all code snippets accurate and from actual sessions.

2. **Technical accuracy verification**: Every code snippet traceable to a specific session, no fabricated output or hallucinated results, commands and techniques are reproducible.

3. **Campaign summary**: Document which angle each piece uses, the publishing order recommendation, and any platform-specific formatting notes.

Save to `outputs/devlog-publisher/{date}/campaign_summary.md` and `outputs/devlog-publisher/{date}/publishing_checklist.md`.
</phase>

</process>

<success_criteria>
- [ ] Session scan covered ALL projects within lookback window
- [ ] At least 3 insights ranked with supporting evidence from actual sessions
- [ ] Traction report completed with current landscape analysis
- [ ] Blog post: 1,500-2,500 words, real code, step-by-step technical depth
- [ ] X/Twitter thread: 7-12 tweets, unique angle, hook-first structure
- [ ] LinkedIn post: 200-350 words, professional tone, engagement question
- [ ] Newsletter: 400-600 words, exclusive insight, single CTA
- [ ] All 4 pieces lead with DIFFERENT angles — zero overlap
- [ ] Cross-platform consistency review passed
- [ ] All code/output traceable to actual sessions (no fabrication)
- [ ] Publishing checklist with platform-specific formatting notes
</success_criteria>

</workflow>
