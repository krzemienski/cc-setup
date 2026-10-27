# Catalog Output Formats

Deliver at minimum (1) awesome-list markdown and (2) JSON catalog. Add CSV when requested or when the list is large.

## 1. Awesome-list markdown (`RESOURCES.md`)

```markdown
# Awesome <Topic>

> N curated and validated resources on <topic>. Last validated: <YYYY-MM-DD>.

## Contents
- [Tools & Libraries](#tools--libraries)
- [Official Docs & Standards](#official-docs--standards)
- ...

## Tools & Libraries
- [ffmpeg](https://ffmpeg.org) — Complete cross-platform solution to record, convert and stream audio and video.
- [hls.js](https://github.com/video-dev/hls.js) — JavaScript HLS client using MSE for browsers.

## Official Docs & Standards
- [RFC 8216 — HTTP Live Streaming](https://datatracker.ietf.org/doc/html/rfc8216) — IETF specification for HLS.
```

Rules:
- One line per resource: `- [Title](url) — one-sentence description.`
- Dual links: when a project has both a repo and a homepage/docs site, link both: `- [Title](repo-url) ([homepage](homepage-url)) — description.` Primary link = most useful entry point.
- Description: specific, factual, no marketing adjectives ("amazing", "best").
- Alphabetize within categories, or order by importance with a stated rationale.
- Header notes the count and the validation date.
- Include a short "How to use this catalog" intro after the header when the topic has a learning curve: 3–5 suggested starting points or learning paths (e.g. "New to X: start with [doc], then [tutorial]; building production systems: see Tools & Libraries and Services & Vendors"). Keep it under ~10 lines.

## 2. JSON catalog (`catalog.json`)

```json
{
  "topic": "<topic>",
  "generated": "YYYY-MM-DD",
  "target_count": 100,
  "delivered_count": 102,
  "resources": [
    {
      "title": "ffmpeg",
      "url": "https://ffmpeg.org",
      "category": "Tools & Libraries",
      "description": "Complete cross-platform solution to record, convert and stream audio and video.",
      "source-found-via": "github awesome-list search / subtopic: encoders",
      "date-checked": "YYYY-MM-DD",
      "http-status": 200,
      "homepage": "https://ffmpeg.org/about.html"
    }
  ]
}
```

Field rules:
- `title`: canonical name, no trailing punctuation.
- `url`: final validated URL (after redirects), no tracking params.
- `homepage` (optional): secondary link when the resource has both a repo and a homepage/docs site. Validate it too.
- `category`: from `references/taxonomy.md` (or topic-specific extension).
- `description`: one sentence.
- `source-found-via`: how it was discovered (query, subagent, subtopic, or parent page it was mined from) — enables escalation auditing.
- `date-checked`: ISO date of validation.
- `http-status`: integer code from the checker; use `"blocked-checker"` or `"timeout-kept"` strings for soft-kept entries.

## 3. CSV (`catalog.csv`)

Columns exactly: `title,url,category,description,source-found-via,date-checked,http-status` — one header row, UTF-8, quote fields containing commas.

## 4. Run summary (return in the final message)

- Target N vs delivered count; explain any shortfall.
- Number of discovery passes and what each escalation pass added.
- Candidates found → dropped by dedupe → dropped by validation → delivered.
- Category distribution table.
