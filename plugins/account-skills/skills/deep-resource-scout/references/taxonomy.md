# Categorization Taxonomy

## Default category set

Use these top-level categories; rename or extend with topic-specific ones (e.g. for video streaming: "Codecs & Encoding", "Players", "CDN & Delivery", "Protocols (HLS/DASH/WebRTC)", "DRM").

| Category | Contents | Typical sources |
|---|---|---|
| Tools & Libraries | Open-source repos, SDKs, CLIs, frameworks | GitHub, GitLab, package registries |
| Official Docs & Standards | Specs, RFCs, standards bodies, official documentation | w3.org, ietf.org, vendor docs |
| Tutorials & Courses | How-to guides, courses, books, interactive learning | blogs, MOOCs, O'Reilly, YouTube |
| Papers & Research | Academic papers, surveys, benchmarks, technical reports | arXiv, ACM DL, IEEE, Semantic Scholar |
| Articles & Blogs | Deep-dives, case studies, engineering blogs | company eng blogs, Medium, dev.to |
| Talks & Videos | Conference talks, recorded meetups, webinars | YouTube conf channels, InfoQ, conference sites |
| Services & Vendors | Commercial products, hosted services, SaaS | vendor sites, product directories |
| Communities & Newsletters | Forums, subreddits, Discords, newsletters, podcasts | reddit, Discord, substack |
| Datasets & Benchmarks | Datasets, test suites, leaderboards (when relevant) | HuggingFace, Kaggle, Papers with Code |

## Source-diversity rules

- No single category should exceed ~40% of the final catalog unless the user explicitly asked for one type (e.g. "find 100 GitHub repos").
- Cover at least 5 of the categories above when the request is generic ("resources about X").
- Within "Tools & Libraries", diversify by language/ecosystem and by subtopic — not 30 links that are all wrappers of the same project.
- Mix eras: foundational/classic resources AND recent (last ~2 years) ones. Note recency in descriptions when it matters.
- Prefer primary sources over listicles. When you find a good listicle or awesome-list, mine its best links individually rather than listing the listicle alone.

## Subtopic mapping

Before searching, decompose the topic into 5–10 subtopics (query angles). Example for "video streaming": protocols (HLS, DASH, WebRTC, SRT), encoders (ffmpeg, x264/x265, AV1), players (video.js, hls.js, Shaka), CDN/delivery, DRM/cas, analytics/QoE, live vs VOD workflows, low-latency streaming, cloud transcoding services, standards (MPEG, CMAF). Assign each subtopic a candidate quota so coverage is balanced and the escalation pass can target gaps precisely.
