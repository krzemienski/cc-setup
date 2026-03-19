# Common Patterns

## Explore Before Implementing (MANDATORY)
1. Search for existing solutions — `gh search code`, package registries, OSS
2. Explore the codebase — use Glob/Grep/Read to understand what exists
3. Check documentation — use Context7 MCP for library docs
4. Use sequential thinking — reason through the approach before coding
5. Invoke relevant skills — skills carry project-specific context you lack

## Skeleton Projects
When implementing new functionality:
1. Search for battle-tested skeleton projects
2. Evaluate options (security, extensibility, relevance)
3. Clone best match as foundation
4. Iterate within proven structure

## Repository Pattern
Encapsulate data access behind consistent interface:
- Standard operations: findAll, findById, create, update, delete
- Business logic depends on abstract interface, not storage
- Enables easy swapping of data sources

## API Response Format
Consistent envelope for all API responses:
- Success/status indicator
- Data payload (nullable on error)
- Error message (nullable on success)
- Metadata for pagination (total, page, limit)
