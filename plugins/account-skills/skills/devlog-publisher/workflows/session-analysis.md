<workflow name="session-analysis">

<objective>
Scan and analyze Claude Code sessions across all projects on the local machine within the specified lookback window. Produce a comprehensive summary of technical activity, ranked insights, and content-worthy moments — without generating any written content.
</objective>

<parameters>
- **lookback_days**: from $ARGUMENTS or default 30
- **topic_filter**: optional keyword filter
- **project_filter**: optional project path
</parameters>

<process>

1. **Discover all session files** within the lookback window:
   ```bash
   find ~/.claude -name "*.jsonl" -type f -mtime -${lookback_days} 2>/dev/null
   find ~/ -maxdepth 6 -path "*/.claude/*.jsonl" -type f -mtime -${lookback_days} 2>/dev/null
   ```

2. **Parse and catalog every session**:
   - Total sessions found
   - Sessions per project (group by project path)
   - Average session length (message count)
   - Date distribution (activity heatmap)
   - Tools most frequently used across sessions

3. **Deep-scan each substantial session** (>5 message exchanges):
   - What was being built or debugged
   - Key technical decisions made
   - Errors encountered and how they were resolved
   - Files created or significantly modified
   - Any novel techniques or patterns used

4. **Score and rank insights** using the 6-dimension scoring system:
   - Novel problem-solving (3x weight)
   - Tool/pattern discovery (3x weight)
   - Before/after transformation (2x weight)
   - Failure + recovery (3x weight)
   - Reproducibility (1x weight)
   - Scale/performance (1x weight)

5. **Produce structured output**:
   - **Session Inventory**: Every session cataloged with metadata
   - **Project Activity Summary**: What happened per project
   - **Top 5 Insights**: Ranked with evidence, source sessions, code excerpts
   - **Content Opportunities**: Which insights are most publishable and why

Save all to `outputs/devlog-publisher/{date}/session_analysis.md` and `outputs/devlog-publisher/{date}/insight_brief.md`.

</process>

<success_criteria>
- All session files within lookback window discovered and parsed
- Every substantial session cataloged with metadata
- Top 5 insights ranked with composite scores
- Each insight includes actual code/output evidence from sessions
- Content opportunity assessment for each insight
</success_criteria>

</workflow>
