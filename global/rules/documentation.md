# Documentation Management

## Project Documentation
- **Roadmap** (`./docs/development-roadmap.md`): Phases, milestones, progress
- **Changelog** (`./docs/project-changelog.md`): Changes, features, fixes
- **Architecture** (`./docs/system-architecture.md`): System design
- **Standards** (`./docs/code-standards.md`): Coding conventions

## Accuracy Verification
- Before committing docs, verify status labels match actual codebase state
- Cross-check route/API docs against real code (grep for handlers)
- Never label implemented features as 'Future' or 'Planned'

## Update Triggers
After: feature implementation, major milestones, bug fixes, security updates

## Plans
Save plans in `./plans` directory with timestamp and descriptive name.
Format: `plans/YYMMDD-HHMM-descriptive-slug/`

Plan files: plan.md (overview), phase-XX-name.md (detailed phases)
Each phase: context links, overview, requirements, architecture, implementation steps, success criteria, risks.
