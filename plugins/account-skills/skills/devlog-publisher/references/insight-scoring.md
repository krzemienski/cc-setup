<reference name="insight-scoring">

<scoring_dimensions>
Rate each session insight on 6 dimensions. Each dimension has a weight reflecting its content value.

| Dimension | Weight | Score 1 (Low) | Score 3 (Medium) | Score 5 (High) |
|-----------|--------|---------------|-------------------|-----------------|
| Novel Problem-Solving | 3x | Routine fix, well-documented solution | Creative approach to a known problem | Entirely new technique or approach nobody has written about |
| Tool/Pattern Discovery | 3x | Standard tool usage | Clever combination of existing tools | Novel MCP usage, custom skill, or workflow pattern |
| Before/After Transform | 2x | Minor improvement | Clear improvement with some metrics | Dramatic transformation with hard numbers |
| Failure + Recovery | 3x | No failure involved | Hit a snag, found a workaround | Spectacular failure, deep debugging, satisfying resolution |
| Reproducibility | 1x | Very project-specific | Could work in similar contexts | Universal technique any developer can use |
| Scale/Performance | 1x | No metrics | Some quantifiable improvement | Hard numbers: X% faster, Y hours saved, Z lines reduced |
</scoring_dimensions>

<composite_calculation>
```
composite = (novel * 3) + (tool_discovery * 3) + (before_after * 2) + (failure_recovery * 3) + (reproducibility * 1) + (scale * 1)
```

**Maximum possible score**: 65 (all dimensions at 5)

| Range | Classification | Content Potential |
|-------|---------------|-------------------|
| 45-65 | Exceptional | Lead blog post, full campaign |
| 30-44 | Strong | Solid blog post or featured thread |
| 20-29 | Moderate | Good for social posts or newsletter items |
| Under 20 | Low | Archive for future reference, not publishable alone |
</composite_calculation>

<content_readiness>
An insight is content-ready when it has:
- [ ] A clear one-sentence summary a developer would want to read
- [ ] At least one real code snippet from the session
- [ ] A "so what" — why should another developer care?
- [ ] A reproducible technique or actionable takeaway
- [ ] Enough context to write 500+ words about it
</content_readiness>

<example_brief_entry>
```markdown
**Insight #1: Debugging HEVC Transcoding Failures with FFmpeg Probe Data**
Composite Score: 52/65
Source: ~/.claude/projects/video-pipeline/sessions/2025-02-10-session.jsonl
Dimension Scores: Novel(4) Tool(5) Transform(4) Failure(5) Repro(3) Scale(4)

Summary: Discovered that HEVC transcoding failures in the JIT pipeline were caused by
mismatched NAL unit headers between input segments. Used FFmpeg's -show_packets probe
combined with a custom jq filter to identify the exact frame boundary causing corruption.

Key Code:
ffprobe -v quiet -show_packets -select_streams v:0 input.ts | \
  grep -A5 "NAL" | jq -r '.packets[] | select(.flags == "K__")'

Story Arc: Production transcoding was silently producing corrupted segments for ~2% of
inputs. Standard debugging showed no errors. Session shows progressive investigation from
log analysis → packet inspection → root cause identification → automated detection script.

Content Angle: "The 2% Bug: How I Found Silent Video Corruption Using FFmpeg Forensics"
```
</example_brief_entry>

</reference>
