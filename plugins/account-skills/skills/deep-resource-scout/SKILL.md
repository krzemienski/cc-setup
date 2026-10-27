---
name: deep-resource-scout
description: Multi-agent deep research workflow to discover, validate, deduplicate, and catalog at least N high-quality resources (tools, repos, links, papers, tutorials) on a topic. Use whenever a user asks to "find N resources about X", "collect resources on X", "build an awesome-list", "find new tools/links/papers about X", "resource discovery", or to extend an existing resource list with new entries. Handles quota-driven escalation when the first pass yields too few results, source-diversity rules, live-URL validation, deduplication against an existing list, categorization, and structured catalog output (awesome-list markdown + JSON/CSV).
---

# Deep Resource Scout

Orchestrate deep research to deliver at least N validated, deduplicated, categorized resources on a topic.

## Workflow

1. **Parse the request.** Extract: topic X, quota N, any existing list to dedupe against, any requested output format. If N is unstated, confirm or default to a reasonable target (e.g. 50) and say so.

2. **Plan search coverage.** Before searching, write a coverage plan that maps the topic into subtopics and source types (see `references/taxonomy.md`). Enforce source diversity — do not let one source type (e.g. GitHub) exceed ~40% of the catalog. Target source classes:
   - GitHub/GitLab repos and awesome-lists (mine their links too)
   - Official docs, standards bodies, vendor pages
   - Technical blogs, tutorials, courses, videos
   - Papers (arXiv, ACM, IEEE, Semantic Scholar) and surveys
   - Conference talks, podcasts, newsletters
   - Communities (forums, Discord/Slack, subreddits, Stack Overflow tags)

3. **Fan out research (multi-agent when available).** Split the plan across subagents by subtopic or source type. Instruct each to return candidates as `{title, url, description, source-found-via}` — far more candidates than their share of N (aim 1.5–2x), since validation and dedupe will discard many.

4. **Deduplicate.** Normalize URLs and check title similarity against the user's existing list and within the new candidates. Follow `references/validation.md`.

5. **Validate live URLs.** Run `scripts/validate_urls.py` on the deduped candidate list. Drop dead links (404/410), parked/placeholder domains, and redirects to unrelated content. **Keep-but-disclose soft failures:** entries the checker could not confirm (403/429 bot-blocks, timeouts) may be kept when clearly high-value and corroborated by independent search evidence — mark their `http-status` (e.g. `"blocked-checker"`), note it in the description, and disclose the kept-unverified count in the run summary. Never silently present unverified entries as validated.

6. **Escalate until quota is met.** If validated count < N, do not stop. Escalate in order:
   - Broaden query phrasing (synonyms, adjacent terms, "awesome-X", "X tools", "X vs Y")
   - Expand to adjacent subtopics and older-but-classic resources
   - Mine links from already-found resources (docs' "ecosystem" pages, awesome-lists, paper references)
   - Add source classes not yet tapped (papers if you only searched repos, etc.)
   - Repeat passes until N is reached or the topic is genuinely exhausted — if exhausted, report the true attainable count explicitly rather than padding with low-quality links.

   **Category-level escalation.** Quota N is necessary but not sufficient: also check per-category fill before declaring done. Any default category (see `references/taxonomy.md`) with 0–2 entries is under-filled — run targeted searches for it before finishing:
   - Papers & Research thin → search arXiv, ACM DL, IEEE Xplore, Google Scholar / Semantic Scholar for "<topic> survey", "<topic> paper"; mine references of found papers. Never list a bare search-query URL as a paper.
   - Talks & Videos thin → search conference archives (e.g. official conf sites, InfoQ, Strange Loop, FOSDEM), topic-dedicated YouTube/Vimeo channels, recorded meetups.
   - Never pad the count with non-resource entries (search URLs, `chrome://`-style pseudo-URLs, listicles you already mined).

7. **Categorize.** Assign each resource to the taxonomy in `references/taxonomy.md`. Create subtopic-specific categories when the generic ones do not fit.

8. **Write the catalog.** Produce awesome-list style markdown plus a machine-readable JSON catalog using the templates in `references/report-format.md`. Every entry needs: title, url, category, description, source-found-via, date-checked, http-status. Also emit CSV if requested or if the user will likely process the list in a spreadsheet.

9. **Report.** Summarize: target N, delivered count, pass/escalation history, validation drop-rate, and category distribution.

## Quality bar

- Every delivered URL was HTTP-checked on the delivery date.
- No duplicates by normalized URL or near-identical title.
- No parked domains, link farms, or placeholder pages.
- Descriptions are one sentence, specific, and non-marketing.
- Sources are diverse per step 2.

## Bundled resources

- `scripts/validate_urls.py` — concurrent HTTP status checker; input JSON `[{title,url},...]`, outputs JSON with added `status` fields.
- `references/validation.md` — URL validation, parked-domain detection, and dedupe rules.
- `references/taxonomy.md` — categorization taxonomy and source-diversity rules.
- `references/report-format.md` — markdown/JSON/CSV catalog templates.
