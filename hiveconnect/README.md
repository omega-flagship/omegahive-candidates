# HiveConnect integration plan

HiveConnect is the working name for OmegaHive's application adapters, event connections, local application plugins, and computational modules. This package turns the competitor research into a proposed implementation sequence. The name remains undecided. Prepared 4 October 2026 for the owner and the platform implementer.

The recommended approach is to own a small set of dependable adapters, support MCP and general API connections, and evaluate a provider bridge for the wider catalog. Launch around complete workflows. A directory entry alone does not establish a working integration.

## Package and current status

- [Competitor research](RESEARCH.md) records sources, popularity signals, and limits.
- [Adapter catalog](catalog.json) contains the proposed backlog, priority, route, and evidence basis for each entry.
- [Integration contract](CONTRACT.md) defines proposed connection, execution, event, and qualification requirements.
- [Delivery sequence](ROADMAP.md) defines bounded slices and acceptance evidence.
- [Baseline implementation status](IMPLEMENTATION_STATUS.md) records the offline client checks and foundation limits.
- [Outside adapter conformance plan](CONFORMANCE_PLAN.md) and [case specification](conformance_cases.json), and [field coverage ledger](s3_field_coverage.json) define the first S3/S4 bridge qualification.
- [OmegaDot tool map](HIVE_TOOL_MAP.md) compares current local interfaces and candidate tools with Codex capabilities; [metadata inventory](hive_inventory.json) records the source observations.

This package now includes a baseline and draft read-only client cores with forty-one L0 offline checks; see IMPLEMENTATION_STATUS.md and evidence/draft-r26-client-l0.json. It has no production transport or credentials. No OAuth connection, platform mount, live service qualification, or deployment is claimed. Priority and implementation route are recommendations. Named commercial services and community projects remain candidates until evaluated against exact actions, scopes, licensing, cost, and current versions.

## Product scope

The person connects an account or application, sees the capabilities it supplies, chooses which minds can use them, and can inspect or revoke access. A mind discovers only its permitted capabilities and receives structured results with provider references and explicit uncertainty about external effects.

Application adapters expose actions such as finding an email or creating a calendar event. Event adapters expose changes such as a received message. Local plugins connect to an application's project and selection, as with Blender. Computational modules expose bounded functions, as with data analysis. Workflow templates combine these capabilities through Hive's existing goals and flows.

An assistant embedded inside Blender and a background mind controlling Blender share the adapter but need different interfaces. Preserve both product directions.

## First product families

| Family | Initial focus | Reason for priority |
| --- | --- | --- |
| Personal and team work | Gmail, Calendar, Drive, Docs, Sheets, Outlook and Microsoft calendars | Strong catalog overlap; email to meeting to document workflow |
| Collaboration | Slack, Notion, GitHub | Recurring popularity signals; communication to task to review workflow |
| General connectivity | MCP, HTTP and OpenAPI, webhooks | Extend coverage without one bespoke implementation per service |
| Creative work | Blender and Figma | Demonstrate work inside substantial creative applications |
| Computational work | Sandboxed Python, structured data processing | Turn retrieved data into useful calculations and artifacts |

Microsoft inclusion is a product coverage decision. Blender is an early specialist track rather than a claim that it exceeds email demand. Browser automation is a useful secondary route whose exact session and authority must be scoped.

## Relationship to the existing platform

Local naming guidance calls the product OmegaHive and agents minds. The existing platform owns the host, policy, goals, flows, approvals, and program loading. HiveConnect should supply integrations beneath those mechanisms rather than introduce a second scheduler or approval system.

The inspected program contract in `hive/PROGRAMS.md` (omegahive) describes trusted Python loaded in process and explicitly says context capabilities are not a sandbox. Therefore third-party integration code should not be mounted as a program and described as isolated. Propose a catalog/settings program for display and a separately isolated execution service for adapters.

The inspected `hive/core/policy.py` (omegahive) contains wildcard defaults, including `hive-*`. New execution skills must be deliberately mapped to the policy gate; their naming must not accidentally inherit broad permission. Proposed canonical capability identifiers in CONTRACT.md are not currently registered skills.

Tools integration is already under platform review according to an owner workspace record (not included). Reuse its reviewed execution and resource mechanisms where suitable after confirming its current state. This research package establishes no current runtime readiness for that candidate.

## Decisions to preserve

- Account authentication, mind authorization, and action confirmation are separate states.
- Read, draft, send, publish, delete, purchase, and arbitrary code execution are separate capabilities.
- Each catalog card reports the exact actions and events supported, maintainer, route, and qualification date.
- Private credentials stay in the connection service. Catalogs, logs, and mind context contain references rather than secrets.
- User data entering model context follows the account's data policy. Connecting a provider does not grant permission to export all its contents.
- Native, official MCP, community MCP, bridge, and browser routes remain visible. Their completeness is measured independently.

## Next implementation slice

Following the discussion with Opus, first qualify the existing MCP bridge: read-only actual capability discovery and scoped query, then typed bound goals, cancellation and Planner exchange. The platform owns S3/S4; HiveConnect owns the outside adapter and conformance suite. Then use the shared contract to qualify the Gmail, Calendar, and Drive workflow against designated test accounts. Keep the Blender track in parallel as a separate implementation sequence, without requiring additional agents.

Cleaned: no temporary clones, dependencies, database files, or build outputs were created; only this durable planning package is retained.
