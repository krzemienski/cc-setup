---
name: "job-role-sourcing"
description: "Find real, open job postings at scale through company ATS feeds and job boards, run as parallel subagents. Use when asked to find, research or list roles to apply to, even casually ('find me 300 AI and video jobs')."
---

# Job role sourcing

Turn a hiring direction ("senior agent-infra and AI-video roles, US or remote") into deduplicated rows. Each row points at one live, individual job posting and has enough detail for verification and scoring.

The output feeds a verification step and then real applications, so precision matters more than volume. One bad link is a wasted application. One duplicate is an embarrassing second submission.

## Why ATS feeds come first

Most careers pages are rendered by JavaScript. A plain fetch sees only a fraction of the postings: one Ashby board returned 17 postings through WebFetch against a true count of 120.

The applicant tracking systems (ATS) that host the postings publish public JSON feeds instead. These feeds list every posting with a stable ID, location fields, and a direct posting URL. Use them whenever the company is on a supported ATS. Use HTML scraping only as a fallback.

| ATS | Feed | Useful fields |
|---|---|---|
| Greenhouse | `https://boards-api.greenhouse.io/v1/boards/{board}/jobs?content=true` | `jobs[].id`, `title`, `location.name`, `offices[]`, `absolute_url`, `updated_at`, `content` |
| Ashby | `https://api.ashbyhq.com/posting-api/job-board/{board}?includeCompensation=true` | `jobs[].id`, `title`, `location`, `secondaryLocations[]`, `address`, `isRemote`, `workplaceType`, `jobUrl`, `applyUrl`, `publishedAt`, `descriptionPlain` |
| Lever | `https://api.lever.co/v0/postings/{board}?mode=json` | `[].id`, `text`, `categories.location`, `categories.allLocations`, `categories.commitment`, `country`, `workplaceType`, `hostedUrl`, `applyUrl`, `createdAt` (ms) |
| Workday / custom | none | Use the site's own search. Record the requisition ID and the posting URL. Note `needs_signin` if applying needs an account. |

**Finding a company's board slug.** Open its careers page and look at where the apply links point:
- `job-boards.greenhouse.io/{board}`, `boards.greenhouse.io/{board}`, or a `gh_jid=` parameter (Greenhouse)
- `jobs.ashbyhq.com/{board}` (Ashby)
- `jobs.lever.co/{board}` (Lever)

If one feed returns 404, try the other two before falling back to scraping.

**Confirm the board belongs to the company you mean.** Slugs collide across unrelated companies. In testing:
- the Ashby slug `odyssey` belonged to a K-12 education company, and a run without this check sourced its full-stack role as a generative-video lab's opening
- `runway` and `river` were also unrelated companies

Before keeping any rows from a board, read one description's "About" paragraph, or match the company domain in the posting URLs, against the company you intended. Record that check as `company_confirmed: true`.

### Feed fetch sketch

This is a sketch for orchestrators. Adapt it rather than copying it blindly.

```python
import json, urllib.request

def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "job-sourcing/1.0"}), timeout=30) as r:
        return json.load(r)

def greenhouse(board):
    for j in get(f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs?content=true")["jobs"]:
        locs = [j.get("location", {}).get("name", "")] + [o.get("name", "") for o in j.get("offices", [])]
        yield dict(ats="greenhouse", board=board, job_id=str(j["id"]), title=j["title"],
                   locations=locs, canonical_url=j["absolute_url"], posted_or_updated=j.get("updated_at"))

def ashby(board):
    for j in get(f"https://api.ashbyhq.com/posting-api/job-board/{board}?includeCompensation=true")["jobs"]:
        locs = [j.get("location", "")] + [s.get("location", "") for s in j.get("secondaryLocations", [])]
        yield dict(ats="ashby", board=board, job_id=j["id"], title=j["title"], locations=locs,
                   remote=j.get("isRemote"), canonical_url=j["jobUrl"], posted_or_updated=j.get("publishedAt"))

def lever(board):
    for j in get(f"https://api.lever.co/v0/postings/{board}?mode=json"):
        c = j.get("categories", {})
        yield dict(ats="lever", board=board, job_id=j["id"], title=j["text"],
                   locations=[c.get("location", "")] + c.get("allLocations", []),
                   canonical_url=j["hostedUrl"], posted_or_updated=j.get("createdAt"))
```

## Discovery: finding companies you don't already know

Use these sources, roughly in this order:

1. **The campaign's own target company lists.** Hit each company's ATS feed directly. In testing, this produced most of the kept rows.
2. **YC.** The public YC company directory (Algolia-backed, filterable by `isHiring`) and each company's public YC jobs page work without signing in. Filtered Work at a Startup search needs the user's sign-in, so ask once and batch the request.
3. **Wellfound.** Sign-in gated for full results.
4. **Hacker News "Who is hiring?".** A new thread posts on the first weekday of each month. Find it with `https://hn.algolia.com/api/v1/search_by_date?tags=story,author_whoishiring`, then read the comments with `https://hn.algolia.com/api/v1/items/{id}`. Comments that mention a remote or US location plus your role keywords are leads. Resolve each one to the company's posting; email-only leads go in the report, not in rows.
5. **VC portfolio job boards** (a16z, Sequoia, Greylock, Conviction, South Park Commons). Most run on Getro or Consider. Use them to list companies, then go to each company's own ATS.
6. **Aggregators: discovery only.** LinkedIn Jobs, the Pragmatic Engineer job board, any job-search MCP, Firecrawl or Exa search. Every hit must resolve to the company's canonical posting. If it can't, drop it, or flag it `manual_linkedin` when the role is strong.

## Parallel sharding

For large targets (hundreds of roles), split the work into shards by **lane × source**, so no two shards cover the same company list. Examples:
- frontier labs
- agent dev-tools
- generative-media AI
- streaming platforms
- video infrastructure vendors
- founding roles from YC and Hacker News
- aggregator sweep

Launch every sourcing subagent in a single message so they run concurrently. Give each one:
- the hiring direction: role families, seniority, exclusions, locations
- its shard definition and company list
- its quota, plus 30% extra to cover rows that fail verification later. The extra applies only to orchestrator quotas. When a person asks directly for N roles, return exactly N rows and list the reserves in the report
- the path to the dedup index and the row schema below
- its output path, `shards/S{n}.json`

Subagents write files and return only the path and row counts. Returning prose wastes the orchestrator's context and invites copy errors. The orchestrator merges the shard files and dedups across them.

## Filtering

- **Seniority.** Match the title against the target levels (Senior, Staff, Principal, Founding, Lead, Head of, Manager where requested). Drop Intern, New Grad, Junior, and roles with I/II levels unless the campaign asks for them.
- **Location.** US eligibility often lives only in a secondary field. Check every location the posting lists (Greenhouse `offices`, Ashby `secondaryLocations` and `address`, Lever `allLocations` / `country` / `workplaceType`, and any remote flag) before you drop a role as non-US.
  - If no structured location is in the US, read the description's location paragraph. Sentences like "can be executed from anywhere in the US" or "Europe and US East Coast" make the role eligible.
  - Set `us_eligibility_basis` to `structured` or `jd_text`, and quote the sentence for `jd_text`.
  - Generic boilerplate that the same description contradicts ("executed globally" in a role that also says "anywhere in Mexico") does not count.
- **Exclusions.** Apply the campaign's exclude list, for example TPM, PhD research-scientist roles, pure frontend, agency reposts, and contract-only roles (Lever `commitment`).
- **Requirements.** Keep 3–6 requirement lines **verbatim** from the description. Scoring and cover notes need the employer's exact words, not a paraphrase.

## Dedup

- **Primary key:** `(ats, board, job_id)`.
- **Fallback key:** a normalized URL. Lowercase the host, drop tracking query parameters but keep `gh_jid`, and strip the trailing slash.
- Check against every ledger the campaign has, including older campaigns, plus its `dedup_index.json`. A previously submitted job ID is never re-sourced. Set `dedup_hit: true` and drop it.
- **Cross-posted roles.** The same role often appears on both an ATS and YC. Keep the ATS row and record the YC copy in `siblings`.
- **Per-city requisitions.** Greenhouse and Lever companies (Palantir, for example) often post the same role under a separate ID per city. For an application campaign, keep the single best-fit location (NYC first, then remote-US, then elsewhere in the US) and record the other IDs in `siblings`, so the same role is never applied to twice. Keep every ID only when the user explicitly asks for one row per posting.
- **No ledger yet?** Say so in the report (`dedup: no prior ledger supplied`), rather than silently skipping the check.

## Canonical URL rules

Accept only a URL that opens one specific posting:
- accepted: `job-boards.greenhouse.io/acme/jobs/4012345008`
- accepted: `jobs.ashbyhq.com/acme/3f9c...`
- accepted: `jobs.lever.co/acme/9a1b...`
- accepted: a YC company job page (`ycombinator.com/companies/{co}/jobs/{id}`)
- accepted: `acme.com/careers?gh_jid=4012345008`, rewritten to the canonical Greenhouse URL
- rejected: careers homepages (`careers.snowflake.com`)
- rejected: search results pages
- rejected: talent-pool / "general application" pages
- rejected: aggregator redirect links
- rejected: Hacker News comments and email-only leads

## Row schema

```json
{
  "shard": "S4",
  "lane": "AI|AIxMedia|Media|Mixed",
  "company": "",
  "company_stage": "bigtech|public|late|seriesA-C|seed",
  "title": "",
  "role_family": "",
  "location": "",
  "remote_us": true,
  "ats": "greenhouse|ashby|lever|workday|yc|custom",
  "board": "",
  "job_id": "",
  "canonical_url": "",
  "siblings": [],
  "source": "where it was discovered",
  "posted_or_updated": "",
  "jd_excerpt_requirements": ["verbatim lines"],
  "compensation_listed": "",
  "dedup_hit": false,
  "company_confirmed": true,
  "us_eligibility_basis": "structured|jd_text"
}
```

## Report back

Write the report as `report.json`, or as markdown if the environment allows it. Some harnesses block subagents from writing `.md` files; JSON always works.

For each shard, report:
- rows found and rows kept
- rows dropped, broken down by reason: dedup, location, seniority, exclusion, non-canonical, wrong company
- sources exhausted
- reserves
- anything that needs the user, such as sign-in-gated sources and email-only leads

If a shard can't reach its quota under these rules, say so plainly. Never pad it with weaker rows.