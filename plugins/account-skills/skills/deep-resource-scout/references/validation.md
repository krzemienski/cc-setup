# Validation & Deduplication Rules

## URL validation

Check every candidate with a live HTTP request (use `scripts/validate_urls.py`).

Status handling:
- **2xx** → accept.
- **3xx** → follow redirects; accept if the final destination is the same resource. Record final URL.
- **401/403/429** → soft failure. Many good sites block bots (GitHub API limits, Cloudflare, Medium). Keep only if the resource is clearly high-value and corroborated by search snippets; mark `http-status` accordingly and note "blocked-checker" in the description.
- **404/410** → drop, unless an archived copy (web.archive.org) exists and the resource is uniquely valuable; then link the archive.
- **Timeout / DNS failure / 5xx** → retry once after a delay; drop on second failure unless clearly high-value (mark it).
- **SSL errors** → treat as failure; do not downgrade to http silently.

Checker etiquette: send a real browser-like `User-Agent`, use HEAD where supported with GET fallback, concurrency ~10, timeout ~10s.

## Parked / placeholder domain detection

Drop a URL if any of these hold:
- Domain parking markers in page content: "domain is for sale", "buy this domain", GoDaddy/Sedo/Afternic/Hugedomains landing pages.
- Blank page, default server page (nginx/Apache default), or "coming soon"/"under construction" with no substantive content.
- Link-farm pages: dozens of unrelated outbound links, keyword-stuffed text.
- Redirect chain ends on a domain unrelated to the original (e.g. blog post → casino/pharma site — indicates expired domain takeover).
- URL shorteners that cannot be resolved to a meaningful final destination.

## Deduplication

### By normalized URL

Normalize before comparing:
1. Lowercase scheme and host.
2. Strip `www.` prefix.
3. Strip default ports (`:80`, `:443`).
4. Remove trailing slash on path (but keep `/` root).
5. Remove fragments (`#...`).
6. Remove tracking query params: `utm_*`, `ref`, `fbclid`, `gclid`, `mc_cid`, `mc_eid`, `igshid`, `si`, `feature` (YouTube), `spm`. Keep content-bearing params (e.g. `?id=` on arXiv, `?v=` on YouTube).
7. Map known aliases to canonical form:
   - `github.com/user/repo` == `github.com/user/repo/` == `github.com/user/repo.git`
   - arXiv `abs/NNNN` == `pdf/NNNN` (treat as one paper)
   - `docs.google.com/.../edit` vs `/view` — same document

### Against an existing list

Parse the user's existing list (markdown links, plain URLs, or JSON) into normalized URLs plus titles. Drop any candidate matching either.

### By title similarity

Flag as probable duplicate when normalized titles (lowercase, punctuation stripped, stopwords removed) match exactly, OR token-set similarity (Jaccard) ≥ 0.8. Manually review flagged pairs: same resource → keep the better URL; genuinely different resources with similar names (e.g. two tools both called "streamx") → keep both and disambiguate descriptions.
