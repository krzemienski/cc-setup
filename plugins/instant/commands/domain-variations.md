---
name: domain-variations
description: Generate prefix and suffix alternatives for a taken name and show which are available
argument-hint: <name> [--limit N]
---

# Generate domain alternatives

Generate domain alternatives for: $ARGUMENTS

Call `generate_domain_variations` on the `instant` MCP server with `name` set to the
first argument, lowercased, with any extension, spaces, and leading dots
stripped. The server rejects names that contain an extension or spaces.
Pass `limit` when `--limit N` is present, otherwise 20.

Results are `.com` only. Reply with the names not registered in the index and
how many were taken. Offer
to check the best names on other extensions with `/domain <name> io dev ai`.
Note that status is as of the last index build and availability must be
confirmed with a registrar before registration.
