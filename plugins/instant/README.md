# Instant

Domain search and name ideas from [instant.ai](https://instant.ai), inside
Claude or your coding agent. Check indexed registration status across
hundreds of extensions, check full domain names in bulk, and generate
alternatives when a name is taken. Every domain result links to the domain's
research page on [instantdomainsearch.com](https://instantdomainsearch.com). Search indexed
USPTO trademark records and inspect matching filings while choosing a name.

The plugin connects the agent to the hosted MCP server at
`https://mcp.instant.ai/mcp`. It is free and needs
no account or API key. Instant may earn referral fees on registrations completed on
instantdomainsearch.com.

## Install

### Claude chat and Cowork

Install **Instant** from the [Claude directory](https://claude.ai/directory/instant).

To install from this repository instead:

1. Open **Customize → Plugins → Add → Add marketplace** and enter
   `https://github.com/instant-labs/agent-plugins`.
2. Install **Instant** from `instant-marketplace`.
3. Open the plugin's **Connectors** tab and add or connect
   `https://mcp.instant.ai/mcp`. Instant needs no account or sign-in. On Claude
   Team and Enterprise, an Owner first adds the connector for the organization.
4. Ask "Check shipwright across .com, .dev, .io, and .ai" or "Brainstorm five
   names for a matcha cafe and check their .com registration status."

If you already added the Instant connector, use the same URL to reuse it.

### ChatGPT

Install **Instant** from the [ChatGPT plugin directory](https://chatgpt.com/plugins/plugin_asdk_app_6ab70b1720748191bcfd401a52975db0).

### Coding agents

See the [repository README](https://github.com/instant-labs/agent-plugins#install)
for every client. In short:

```sh
claude plugin marketplace add instant-labs/agent-plugins
claude plugin install instant@instant-marketplace

codex plugin marketplace add https://github.com/instant-labs/agent-plugins
codex plugin add instant@instant-marketplace

grok plugin marketplace add instant-labs/agent-plugins
grok plugin install instant --trust
```

Cursor and Grok Bot: search for **Instant** under Settings →
Plugins, or import `https://github.com/instant-labs/agent-plugins` as a team
marketplace.

If you installed this plugin under its old id, follow the
[upgrade steps](https://github.com/instant-labs/agent-plugins#upgrading-from-instantdomainsearch)
first.

## What you get

| Component | Name | Purpose |
| --- | --- | --- |
| MCP server | `instant` | Domain search and USPTO trademark records |
| Skill | `instant` | When to call which tool, argument rules, how to read results |
| Skill | `domain-brainstorm` | Generate name ideas and check them for available domains in one pass |
| Command | `/domain <name> [tld ...]` or `/domain a.com b.io` | Check a name across extensions, or a list of full names |
| Command | `/domain-variations <name>` | Prefix and suffix alternatives for a taken name |

Claude chat treats commands as skills and applies them when they fit the request.
Clients that treat skills as slash commands also expose `/domain-brainstorm`.
Claude Code namespaces commands as `/instant:domain`,
`/instant:domain-variations`, and `/instant:domain-brainstorm`.
Clients prefix tool names with the server, for example
`instant__search_domains` in Grok Build.

The hosted server exposes:

- `search_domains`, `check_domain_availability`, and `generate_domain_variations`
  for domain searches.
- `search_trademarks` and `get_trademark_details` for indexed USPTO records.

## Network and credentials

- The only endpoint the plugin calls is
  `https://mcp.instant.ai/mcp`, the hosted MCP
  server, over streamable HTTP.
- No credentials. The server takes no API key, token, or sign-in, and the
  plugin sets no headers.
- No hooks, agents, scripts, or local processes. The plugin is the MCP pointer
  plus markdown.
- Tool calls send their arguments to Instant's hosted server. Every tool reads
  domain or trademark data. The plugin does not register or purchase domains.

## Notes

- Registration status comes from a search index built from registry zone
  files and DNS observation feeds, refreshed daily, not from a live registry
  query. A name absent from the index is not guaranteed to be available;
  confirm availability with a registrar before registering it.
- `isRegistered` is `true`, `false`, or `null` when the index has no data for
  that extension.
- Prices (`premium.usd_cents`, `listings.lowestPrice`, `markets[].price`) are
  USD cents.
- Limits: `search_domains` and `generate_domain_variations` return at most 100
  results; `check_domain_availability` takes at most 50 names per call.
- Trademark search returns up to 100 matches and includes snapshot freshness.
  An empty result does not establish that a name is legally clear to use.
- The server also publishes prompts (`analyze-domain-brandability`,
  `domain-investment-strategy`, `generate-business-names`) and resources
  (`instant-domains://tld-categories`, `instant-domains://domain-guidelines`)
  for clients that support them.

## Support

Setup guides for other clients live at
[instant.ai/mcp](https://instant.ai/mcp). Open an
issue in this repository for plugin problems, or [contact Instant](https://instant.ai/contact).
See the [privacy policy](https://instant.ai/policies/privacy) and
[terms of use](https://instant.ai/policies/terms).

## License

MIT. See [LICENSE](https://github.com/instant-labs/agent-plugins/blob/main/LICENSE).
