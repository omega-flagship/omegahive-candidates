# HiveConnect competitor research

Research date: 4 October 2026. The audience is the owner and the OmegaHive implementation team. The purpose is to identify the integration families most worth supporting and the ecosystems worth reusing.

## Findings and evidence limits

Email, spreadsheets, messaging, files, knowledge tools, and developer services recur across the inspected catalogs. This supports prioritizing them for Hive. It does not establish a global market-share ranking or Hive user demand. Vendor popularity labels lack a shared published denominator, GitHub stars measure interest, and app counts differ from action or server counts.

Counts below are vendor catalog observations at the research date. Dynamic pages and documentation branches can disagree; repeat collection before procurement or public claims. No paid API or private account was queried.

## Competitor comparison

| Ecosystem | Observed catalog evidence | Implication for Hive |
| --- | --- | --- |
| [Zapier](https://zapier.com/apps) | Directory shows 9,000+ integrations and a most-popular ordering. Separate marketing text uses a larger connections figure. | Study setup, triggers/actions, templates and broad coverage. Keep units explicit. |
| [Make](https://www.make.com/en/integrations) | Advertises 3,000+ apps and distinguishes verified/community apps. | Separate app identity from its constituent modules and maintainer status. |
| [n8n](https://n8n.io/integrations) | Shows 2,285 integrations, popularity ordering, regular/trigger/core types, and AI categories. | Put app adapters and computational building blocks in one discoverable catalog with clear types. |
| [Composio](https://docs.composio.dev/toolkits) | Main catalog shows 1,558 toolkits. Popular section includes GitHub, Gmail, Slack, Notion, Sheets, Shopify, Drive, Supabase and HubSpot. | Candidate agent-tool bridge; evaluate exact tool and auth support. |
| [Pipedream](https://pipedream.com/apps) | Shows 3,223 apps and 14,977 registry tools; offers SDK, REST and app-specific MCP access. | Candidate managed connection bridge. |
| [Activepieces](https://www.activepieces.com/pieces) | Shows 762 open-source pieces. | Study contributor packaging and maintenance model; inspect licenses per dependency. |
| [LangChain](https://docs.langchain.com/oss/python/integrations/providers/overview) | Integration documentation covers model providers and associated integrations. | Reuse useful libraries through bounded adapters; framework adoption is a separate choice. |
| [LlamaIndex](https://developers.llamaindex.ai/python/framework/module_guides/loading/connector/) | Documents data connectors for ingestion. | Separate importing/indexing knowledge from acting on the original application. |
| [MCP Registry](https://registry.modelcontextprotocol.io/docs) | Official registry supports discovering versioned servers. | Build MCP compatibility and provenance-aware catalog discovery; discovery alone is not qualification. |

## Popular application evidence

[Zapier's popularity page](https://zapier.com/apps) starts with Sheets, Gmail, Slack, Calendar, Drive, HubSpot, Facebook Lead Ads, Forms, Notion and Mailchimp. Its first page also includes Stripe, LeadConnector, Outlook, Calendly, Typeform, Airtable, Trello, Docs, Salesforce, Jotform, Gravity Forms and monday.com. These are ordering observations within Zapier, not usage counts.

[n8n's popularity ordering](https://n8n.io/integrations) reinforces Sheets, Gmail, Slack, Airtable, Drive and Notion, and also prominently exposes HTTP Request, AI Agent, model providers, Telegram, Webhook, Excel, Supabase, Discord and Postgres. This is evidence that useful integration coverage includes infrastructure primitives as well as named apps.

[Composio's popular toolkits](https://docs.composio.dev/toolkits) add an agent-specific signal for GitHub and reinforce Gmail, Slack, Notion, Sheets, Drive and HubSpot. Its toolkit API documentation describes popularity sorting and versioned tools: [toolkit reference](https://docs.composio.dev/reference/v3/api-reference/toolkits).

The machine-readable catalog records `evidence_basis` for each proposed item. Items without direct ranking evidence are labelled coverage or workflow choices. Cross-catalog presence is not converted into a fictitious numeric popularity score.

## Creative and browser integrations

| Candidate | Observation | Scope of conclusion |
| --- | --- | --- |
| [MCP for Blender](https://github.com/ahujasid/mcp-for-blender) | Approximately 29.9k stars and 2.7k forks. Community project, explicitly unaffiliated with the Blender Foundation. | Substantial interest in agent-controlled Blender. No Hive compatibility or operational reliability established. |
| [Playwright MCP](https://github.com/microsoft/playwright-mcp) | Approximately 37.8k stars. Microsoft-maintained repository. | Strong interest in browser tooling. Browser sessions still require explicit account and execution scope. |
| [GitHub MCP](https://github.com/github/github-mcp-server) | Approximately 33.4k stars. Official GitHub server. | A concrete official-server reuse candidate for developer workflows. |
| [Figma MCP](https://developers.figma.com/docs/figma-mcp-server/) | Official documentation recommends its remote server; tools documentation includes reading and writing designs. | Prefer evaluating the official route. Check action-specific plan, access, and rate limits before promising support. |

## Social integration economics

[X's current pricing documentation](https://docs.x.com/x-api/getting-started/pricing) describes usage-based credits and spending limits. Different reads and writes have different costs. A Hive X adapter should show its supported account/action scope and meter usage. Do not use a historical fixed subscription price as the planning assumption.

Other social adapters remain coverage candidates. This research does not verify approval eligibility, account types, publishing permissions, or costs for LinkedIn, Instagram, Reddit or YouTube. Those are per-adapter qualification tasks.

## Bridge evaluation

Compare Composio and Pipedream using the same Gmail, Calendar, Drive, Slack and GitHub task set. Measure action completeness, per-user OAuth, token custody, webhook recovery, exportability, error detail, latency and total cost. Include current pricing, service terms, data location, retention, and dependency exit in the decision. No provider has been selected.

MCP is a transport and discovery option. It does not by itself supply Hive policy, workflow persistence, effect reconciliation, or isolation. A bridge may accelerate coverage but still needs the common execution contract.

## Research still needed before expansion

Collect demand from actual Hive workflows; inspect individual candidate licenses and versions; verify creative-app APIs beyond Blender/Figma; compare Microsoft action coverage; verify social account restrictions; and qualify the computational modules against their intended tasks. Adobe, CAD, GIS, simulation and home integrations should enter implementation only with a concrete workflow and a maintainable route.
