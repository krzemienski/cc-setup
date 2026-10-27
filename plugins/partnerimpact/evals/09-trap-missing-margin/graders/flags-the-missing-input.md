---
type: llm
weight: 2
arm: both
---

The user gave no gross margin and no cost to serve the partner. The answer depends on both.

PASS if the reply does one of these:
- asks for the gross margin before giving a verdict, or
- gives a verdict and states explicitly, next to it, that it assumed a gross margin (naming the figure, such as 75%) and that the verdict changes if the real margin is lower.

FAIL if it says the fee is affordable or not affordable without telling the user that a gross margin was assumed, or if the assumption is only visible inside a table of inputs with no sentence pointing to it.
