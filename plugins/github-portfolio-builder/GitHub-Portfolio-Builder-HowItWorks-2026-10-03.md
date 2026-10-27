## Trigger

- The user requests a review of a GitHub profile or repository.

## Inputs

- The profile or repository URL identifies the target.
- The intended audience and review focus guide the assessment.
- Current GitHub pages, repository files, and relevant linked sources supply evidence.
- Existing access is required for a private target.

## What happens

1. The plugin asks up to three questions about a missing target, audience, or focus. It waits for answers that affect the review. A clear target and review request can be enough.
2. It resolves an ambiguous target before inspection. It reads the current default branch and relevant sources through available read tools.
3. For a profile, it samples representative repositories and records the scope. For a repository, it reads the entry point and supporting files needed for the question.
4. It checks direct file paths before claiming something is absent. It treats inaccessible pages, incomplete trees, and failed links as evidence gaps.
5. It labels statements verified, reported, inferred, or unresolved. A source file does not establish deployment or a real-world outcome.
6. It ranks up to five useful improvements. It gives fewer when the evidence supports fewer. Suggested public additions include required proof, permission, or attribution.
7. It returns Scope, Assessment, Priorities, and Limits. It includes Worth sharing only when a supported addition is available. A correction prompts a source check and revision.

## Outputs

- A sourced review in the current chat.
- No repository edit, profile change, pull request, or publication.
