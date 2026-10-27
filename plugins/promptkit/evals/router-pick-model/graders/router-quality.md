---
type: "llm"
---

PASS if the final reply names the target model it chose with a one-line reason, and gives a ready-to-use prompt that
turns a daily standup transcript into three bullet points per person (done, next, blocked).
FAIL if no model is named, or the reply writes the standup summary itself instead of a prompt.
