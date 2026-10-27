# Source routing

Choose the least burdensome available read path. The plugin does not require a GitHub token or MCP for public targets.

## Public GitHub target

- Use the live GitHub profile page for the visible profile, README, and pinned versus automatically selected showcase items. Do not infer pins from a repository list or stars.
- Use public GitHub pages or unauthenticated GitHub REST reads for repository metadata, the default branch, README, tree, license, and relevant files. Inspect linked sites or demos separately when a recommendation depends on what actually renders.
- If an official GitHub MCP is already configured, its **read** tools can provide repository files, tree, metadata, releases, and user information. Use only the toolsets relevant to the review, such as `repos`, `users`, and `git`; do not invoke write tools even if offered. MCP data does not verify a rendered website, video, deployment, or real-world outcome.
- Resolve file-specific evidence to a commit permalink when practical. A default-branch URL can change after the review; record the date and branch or SHA so a reader can interpret it.

## Private or incomplete target

- Review a private repository only when the user supplied that target and existing access allows it. Do not request a token for an ordinary public review or broaden inspection to other private repositories.
- Treat 403, 404, 429, truncated trees, partial pages, and failed external links as distinct access or evidence gaps. A 404 alone does not prove a repository never existed or is public; a partial tree does not prove a file is absent.
- Stop expanding a large profile or repository once the sampled evidence answers the review question. Name the sampled repositories and any material coverage limit.
