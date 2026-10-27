---
name: domain
description: Check a name across popular extensions, or a list of full domain names
argument-hint: <name> [tld ...] | <domain.tld> ...
---

# Check domain availability

Check domain availability for: $ARGUMENTS

Rules:

- Use the tools on the `instant` MCP server.
- If every argument contains a dot (for example `acme.com shop.io`), call
  `check_domain_availability` once with all of them as
  `domains`.
- If the first argument has no dot, it is the name. Any further arguments are
  extensions. Call `search_domains` with
  `{"name": "<first>", "tlds": [<rest without leading dots>]}`, or omit `tlds`
  when there are no further arguments.
- Lowercase names, strip spaces, and remove leading dots from extensions. The
  server rejects malformed domain input.

Reply with each domain and its indexed status: not registered, registered, or
unknown when `isRegistered` is null. Mention aftermarket listings or premium prices when present; prices are
USD cents. Note that
status is as of the last index build and availability must be confirmed with a
registrar before registration.
