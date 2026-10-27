# PRD review checklist

A reviewer (human or model) marks each item pass or fail and gives the section and the fix for each failure.

## Completeness
1. Every required section exists, in the requested order.
2. Every screen has Purpose, Layout, States, Controls, and APIs called.
3. Every API call names method and path; every model reference uses the exact model string.
4. Every configurable element is in the Configuration tables with a default and a location.
5. Every goal has a measure a test can check.
6. The reference behavior is specified step by step, or the choice of reference is stated.

## Correctness
7. Current-world facts (model names, parameters, prices, SDK APIs) cite a source with a retrieval date.
8. Model parameters match the vendor rules, for example: Claude Opus 5.5 and Fable 5.1 never disable thinking and never force tool use; GPT-6 Astra never uses reasoning effort `none` or sampling parameters with reasoning.
9. No two requirements contradict each other (for example "keys never leave the device" and "the proxy stores keys").

## Buildability
10. An engineer could create the repository layout, the storage schema, and the interfaces from the text alone.
11. Error and edge states are specified: permission denied, network failure, refusal, cancellation, empty data.
12. The delivery order is stated and each step is independently shippable.

## Writing
13. No placeholders, TODOs, or "[Description of …]" text.
14. Requirements are literal sentences with units; no metaphor stands in for a requirement.
15. Unverified facts are labeled where they appear.
