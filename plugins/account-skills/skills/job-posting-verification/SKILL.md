---
name: "job-posting-verification"
description: "Independently check that job posting URLs are real, open and applicable before anyone applies, with timestamped evidence. Use to validate job links, find dead postings, clean a tracker, or check sourced roles."
---

# Job posting verification

Decide whether each job row is safe to apply to, and leave evidence that anyone can re-check.

A posting counts as verified only when **two independent kinds of proof** agree:
- the employer's applicant tracking system (ATS) still lists the job
- a rendered page shows the full job description and a working apply control

## Why this is a separate step, done by a separate agent

Whoever found a posting wants it to be real. That bias makes self-verification weak.

Run verification in different subagents from the ones that did the sourcing. Give them only the rows and this skill, not the sourcer's reasoning.

These failure modes all look fine to a status-code check, and all were seen in testing:
- **A careers homepage or filtered list passed off as a posting.** It returns HTTP 200 but has no specific job.
- **A closed posting.** Greenhouse redirects a closed job to the board root with HTTP 200. Only the API 404 and the "no longer open" banner reveal it.
- **A made-up ID.** Ashby renders a page even for a job ID that doesn't exist, so only the feed lookup catches it.
- **The right posting at the wrong company.** Board slugs collide across unrelated companies.

## Checks

Run these five checks per row. Record each one with an ISO-8601 timestamp.

### 1. ATS proof

Confirm that the job ID appears in the ATS's public JSON feed.

| ATS | How to check |
|---|---|
| Greenhouse | `https://boards-api.greenhouse.io/v1/boards/{board}/jobs/{job_id}` returns 200, with a matching `id` |
| Ashby | `https://api.ashbyhq.com/posting-api/job-board/{board}` contains an entry whose `id` equals `job_id` |
| Lever | `https://api.lever.co/v0/postings/{board}/{job_id}` returns 200 |
| Workday / custom / YC | no feed. Record the HTTP status and final URL after redirects, and rely on check 2 |

A 404 from the feed, or a missing ID, means the job is closed. Fail it with `ats_missing`.

### 2. Rendered-page proof

Open `canonical_url` with a rendering scraper (Firecrawl scrape with `waitFor` around 3000 ms and `maxAge: 0`) or a real browser. A plain fetch is not enough on JavaScript-rendered boards. Also record the final URL after redirects, for example with `curl -sL -o /dev/null -w '%{url_effective}'`.

Confirm all of the following:
- **The page is a specific posting.** The title matches the row's title, and the full description text is present (more than a few hundred words, not just a summary card).
- **There is a visible apply control.** Look for text like "Apply", "Apply for this job", "Apply Now", or "Submit application". Platform signals:
  - Greenhouse: an embedded `application_form` or an Apply button
  - Ashby: an "Application" tab or an "Apply for this Job" button
  - Lever: an "Apply for this job" link to `/apply`
- **There is no closed signal**, such as:
  - "no longer accepting applications"
  - "this job is no longer available" / "no longer open"
  - "position has been filled"
  - a "job not found" message
  - a redirect from the posting URL to the board root (for example `?error=true`) or to the careers homepage

### 3. Eligibility

The posting must allow a US location or remote-US work. Check every location field the posting lists, including:
- Ashby `secondaryLocations` and `address`
- Greenhouse `offices`
- Lever `allLocations` and `country`
- remote and workplace-type flags
- location lines inside the description text

A row's own `location` field may show only the primary location. In testing, two rows labeled "United Kingdom" and "London" were in fact open to New York through secondary locations.

Record the field that established eligibility in `us_eligibility_basis`:
- `structured`: a listed location or remote flag
- `jd_text`: a sentence such as "can be executed from anywhere in the United States"; quote it

Both count. When eligibility rests on description text alone, record the quote so a human can check it.

### 4. Company identity

Confirm the board belongs to the company the row names. Compare the description's "About" paragraph, or the company domain, with the row's company. In testing, the Ashby board `odyssey` was a K-12 education company, not the generative-video lab the row claimed. Fail a mismatch with `wrong_company`.

### 5. Age (a flag, not a failure)

Record the posted or updated date, and set `older_than_window: true` when it falls outside the campaign's window (default 60 days). **Never fail a row for age alone.**

Many companies keep evergreen roles posted for months or years. Checks 1 and 2 already prove that the job is open today. In testing, a strict age cutoff rejected 3 of 5 genuinely open, US-eligible postings, including a Palantir NYC role open since 2024. Scoring can deprioritize old postings; verification only answers "can the candidate apply to this today?"

If no date exists, record `date_unavailable`.

## Evidence format

Write one file per batch to `verify/{batch}.json`. Batches of about 40 rows work well.

```json
{
  "job_key": "ashby:acme:3f9c...",
  "canonical_url": "",
  "checks": [
    {"check": "ats", "result": "pass", "at": "2026-10-14T13:02:11-04:00", "detail": "id present in posting-api"},
    {"check": "rendered", "result": "pass", "at": "...", "detail": "title match; 1840 words; 'Apply for this Job' button; final URL unchanged"},
    {"check": "eligibility", "result": "pass", "at": "...", "detail": "structured: secondaryLocations New York, NY"},
    {"check": "company", "result": "pass", "at": "...", "detail": "About paragraph names Acme; domain acme.com"},
    {"check": "age", "result": "flag", "at": "...", "detail": "publishedAt 2025-02-20; older_than_window"}
  ],
  "verified": true,
  "older_than_window": true,
  "us_eligibility_basis": "structured",
  "fail_reason": null
}
```

Allowed values for `fail_reason`:
- `ats_missing`
- `closed_banner`
- `redirect_to_board`
- `not_a_posting`
- `no_apply_control`
- `jd_missing`
- `non_us`
- `wrong_company`
- `fetch_error`

Age is never a `fail_reason`; it is the `older_than_window` flag.

Retry `fetch_error` once after a pause before you record it. Scrapers rate-limit, so back off rather than failing the row.

Write the batch report as JSON (`verify/{batch}.report.json`). Some harnesses block subagents from writing `.md` files.

## Rules that keep the evidence trustworthy

- **Verified means both proofs passed,** plus eligibility and company identity. Custom portals with no feed need HTTP 200 plus rendered-page proof.
- **Inference is not evidence.** Never mark a row verified based on a similar posting, the company's reputation, or an earlier check. Run the check.
- **Be polite to hosts.** Make about one request per second per host, and parallelize across hosts rather than within one host.
- **Re-verify at apply time.** Postings close daily. The application step should repeat a quick ATS check right before it submits.
- **Suggest, don't substitute.** When a failed row has an obvious live alternative (the US copy of a Dublin role, a specific posting instead of a filtered list), name it as a replacement candidate. Never mark the alternative as verified without running the checks on it.

## Replacement loop

Return the failed rows, grouped by originating shard with their `fail_reason`, so the orchestrator can ask those shards for replacement candidates. Repeat until the target count is verified or the shards report that their sources are exhausted.

Report the final numbers: verified count, failed count by reason, rows flagged `older_than_window`, and any shortfall against the target. A shortfall reported honestly is better than a padded list.