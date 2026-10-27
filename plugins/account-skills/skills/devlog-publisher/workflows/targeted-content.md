<workflow name="targeted-content">

<objective>
The user already knows what insight or topic they want to publish. Skip the full session scan and go directly to the teammate content pipeline, using the user-provided topic as the primary insight. Optionally search sessions for supporting evidence.
</objective>

<parameters>
- **topic**: from $ARGUMENTS — the specific insight or topic to write about
- **platforms**: which platforms to target (default: all)
- **blog_length**: target word count (default: 1500-2500)
</parameters>

<process>

1. **Clarify the insight**: Confirm with the user:
   - What is the core technical insight or technique?
   - Which project/session does it come from (if known)?
   - What's the target audience level (junior, mid, senior)?
   - Any specific angle or framing they want?

2. **Search sessions for evidence** (optional but recommended):
   ```bash
   # Search for relevant sessions containing the topic
   grep -rl "${topic}" ~/.claude/projects/*/sessions/*.jsonl 2>/dev/null
   ```
   - Extract relevant code snippets from matching sessions
   - Pull actual terminal output and error messages
   - Build the evidence base for the content

3. **Quick traction check**: Search for similar content that's performing well to inform the angle.

4. **Spawn teammate content pipeline** (same as full-pipeline Phase 3):
   - Blog Writer, Twitter Thread Writer, LinkedIn Writer, Newsletter Writer
   - Each chooses a unique angle on the provided topic
   - All include real code/output from sessions when available

5. **Synthesis review**: Cross-platform consistency check.

Save all to `outputs/devlog-publisher/{date}/`.

</process>

<success_criteria>
- Content produced for all specified platforms
- Real session evidence incorporated where available
- All pieces lead with different angles
- Technical depth maintained throughout
</success_criteria>

</workflow>
