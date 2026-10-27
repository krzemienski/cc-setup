---
name: domain-brainstorm
description: Brainstorm brandable names for a product, company, or project and check each one's indexed domain registration status in the same pass. Use when the user asks for name ideas, business names, startup names, app names, or "what should I call this", and a domain is part of what makes a name usable. Pairs generated ideas with the instant MCP tools so suggestions include checked registration status rather than guesses about availability.
---

# Domain brainstorm

Generate candidates, check their registration status in bulk, shortlist names
not registered in the index, and expand on the best root when nothing fits.
Index results do not guarantee that a registrar can register a name.

## Workflow

1. **Understand the brief.** Industry, audience, tone (modern, classic,
   playful, professional), and any keywords the user wants in the name. Ask
   one question at most; guess sensibly otherwise.
2. **Generate 15-25 candidates.** Short (6-14 characters), pronounceable, easy
   to spell, no hyphens or digits unless they mean something. Mix invented
   words, compounds, and real words with a twist.
3. **Check them in one call.** `check_domain_availability` on the
   `instant` MCP server, with every candidate as `<name>.com` (at
   most 50 per call). Add a second call for `.io`, `.ai`, `.dev`, or `.app`
   when the brief is a tech product.
4. **Expand the strongest roots.** For the best two or three names that are
   taken on `.com`, call `generate_domain_variations` with
   `{"name": "<root>", "limit": 15}`, or `search_domains` with
   `{"name": "<root>"}` to try other extensions.
5. **Present a shortlist.** Five to ten names, each with a one-line reason.
   Note aftermarket listings or premium
   prices when present (prices are USD cents). Say the status is as of the
   last index build and tell the user to confirm availability with a registrar
   before registering a name.

## Guardrails

- Never suggest a name you did not check.
- Lowercase candidates and strip spaces before checking; the server rejects
  malformed domain input.
- `isRegistered: null` means the index has no data for that extension; label
  it unknown, not available.
- Prefer `.com` unless the user names another extension or the product is
  clearly developer-facing.
- Skip names that are trademarks of well-known companies.
