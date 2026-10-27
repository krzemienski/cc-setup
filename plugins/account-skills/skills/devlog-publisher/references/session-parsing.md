<reference name="session-parsing">

<primary_locations>
Claude Code stores session data as JSONL (JSON Lines) files. Each line is a complete JSON object representing one message in the conversation.

```bash
# User-level sessions (most common)
~/.claude/projects/*/sessions/*.jsonl

# Global Claude config area
~/.claude/sessions/*.jsonl

# Project-level .claude directories (when projects use local config)
./.claude/sessions/*.jsonl
```
</primary_locations>

<message_structure>
Each line in a session file is a JSON object with these typical fields:

```json
{
  "role": "human" | "assistant",
  "content": "message text or structured content",
  "timestamp": "ISO 8601 timestamp",
  "tools_used": ["tool_name"],
  "session_id": "unique session identifier"
}
```
</message_structure>

<parsing_commands>
```bash
# Count sessions within timeframe
find ~/.claude -name "*.jsonl" -mtime -30 -type f | wc -l

# Get message count per session
for f in $(find ~/.claude -name "*.jsonl" -mtime -30 -type f); do
  echo "$(wc -l < "$f") messages: $f"
done | sort -rn

# Extract all human messages (prompts) from a session
cat session.jsonl | jq -r 'select(.role == "human") | .content' 2>/dev/null

# Search across all sessions for a keyword
grep -l "kubernetes" ~/.claude/projects/*/sessions/*.jsonl 2>/dev/null

# Extract tool usage patterns
cat session.jsonl | jq -r 'select(.tools_used) | .tools_used[]' 2>/dev/null | sort | uniq -c | sort -rn
```
</parsing_commands>

<quality_indicators>
**High-value sessions** (prioritize for content):
- 10+ message exchanges
- Multiple tool invocations (indicates complex problem-solving)
- Error messages followed by successful resolution
- File creation/modification (indicates building something tangible)
- Long assistant responses (indicates deep technical explanation)

**Low-value sessions** (skip or deprioritize):
- Under 5 exchanges
- Simple Q&A without tool usage
- Abandoned sessions (no resolution)
- Routine/repetitive tasks
</quality_indicators>

<project_association>
Sessions are typically stored under project paths that reveal what was being worked on:

```bash
# List all projects with sessions in the last N days
find ~/.claude/projects -maxdepth 1 -type d | while read project; do
  count=$(find "$project" -name "*.jsonl" -mtime -30 -type f 2>/dev/null | wc -l)
  if [ "$count" -gt 0 ]; then
    echo "$count sessions: $(basename $project)"
  fi
done | sort -rn
```
</project_association>

</reference>
