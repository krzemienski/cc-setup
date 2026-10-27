---
type: "llm"
---

PASS if the final reply gives a rewritten prompt for Claude Fable 5.1 that summarizes an input supplied at run time, keeps the
input as a placeholder wrapped in pasted_content tags, drops the emphatic CRITICAL/MUST rule, the step-by-step line,
and the request to show reasoning, and explains the changes (a table or list of change and reason is enough).
FAIL if the reply keeps any of those three legacy lines inside the new prompt, or gives no rewritten prompt.
