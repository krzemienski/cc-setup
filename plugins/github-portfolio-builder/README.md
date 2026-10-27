# GitHub Portfolio Builder

Review a GitHub profile or repository as professional portfolio evidence. Receive an assessment and up to five useful improvements with direct source links.

Start with `/github-portfolio-builder:github-portfolio-builder`. If details are missing, the plugin asks for the target, intended audience, and review focus. It waits for required answers. A clear target and review request can be enough to start.

- Checks current pages, files, and relevant linked sources.
- Labels verified facts, reported claims, interpretations, and gaps.
- Ranks changes by what a visitor needs to understand.
- Gives fewer findings when the evidence supports fewer.
- Identifies proof, permission, and attribution needed for suggested additions.

Read [how it works](GitHub-Portfolio-Builder-HowItWorks-2026-10-03.md).

## Data and permissions

The plugin instructs the assistant to review without editing repositories, changing profile pins, opening pull requests, or publishing files. The host's tools and permissions determine what actions are technically possible.

Public reviews can use GitHub pages or its public data interface without a token. Private targets require access you already have. The package does not install a connection or request credentials in chat. An existing GitHub connection is optional.

The review can request GitHub pages and relevant linked sites. The requested addresses and normal request metadata reach those sites. The host processes review content under its own terms and settings. The package has no publisher-operated service or telemetry. It does not request uploading private repository content to a linked site.

See [the privacy notice](PRIVACY.md). Installation instructions and source are in [the project repository](https://github.com/RachaelQuisel/github-portfolio-builder).

## License

MIT. See [LICENSE](LICENSE).
