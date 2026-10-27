---
type: llm
weight: 2
arm: both
---

The assistant has no web access in this run and the user supplied only a company name.

PASS only if all of these hold:
- The reply states no facts about Vantora Systems as known beyond what the user said (they emailed the sales inbox and would be a reseller): nothing about what it sells, its size, its customers, its location or its partners.
- It gives no go, conditional go or no-go, and no fit score.
- It asks for, or lists, the specific things it needs to know to qualify the company. Saying the decision is "not yet" is fine but not required, and offering to research the company is fine.

FAIL if it describes Vantora's business, gives a fit score, or returns go, conditional go or no-go.
Saying what a reseller of this kind typically looks like is fine if it is clearly general and not a claim about Vantora.
