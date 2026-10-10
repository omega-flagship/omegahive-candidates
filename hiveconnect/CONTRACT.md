# HiveConnect integration contract proposal

Version 0.1 proposal, 4 October 2026. This contract defines the information Hive needs to discover and safely execute an integration. It is not an implemented API or an extension already accepted by the platform owner.

## Local host integration direction

Following Opus's discussion, HiveConnect uses OmegaDot's existing /mcp member bridge (S3) and per-mind inventory (S4). This document specifies external connector requirements; it does not establish a second host identity, credential registry, scheduler or approval queue. New external adapters remain subject to exact capability/route qualification. CONFORMANCE_PLAN.md governs the initial local bridge acceptance; schema field names await the platform draft.

## Capability manifest

Each adapter declares a stable identifier, publisher, version, source pin, license, adapter type, execution route, supported provider/API version, and minimum host contract. Each action declares a canonical capability ID, JSON input/output schemas, effect class, required scopes, limits, timeout, retry behaviour, and reconciliation method. Each event declares its schema, provider identity, ordering guarantees, deduplication key and recovery method.

Proposed capability ID examples are `connect:gmail:messages.search`, `connect:gmail:drafts.create`, `connect:gmail:messages.send`, and `connect:blender:scene.inspect`. The platform must map these IDs to deliberate policy checks. They are not current Hive skills and must not receive permission merely through a wildcard naming convention.

Effect classes are `read`, `local_compute`, `draft`, `write`, `send`, `publish`, `delete`, `financial` and `code_execute`. Reads can still incur cost or transmit data; cost and data egress are separate declarations. An adapter declaring a low-impact class is subject to review, not automatically trusted.

## Connections and grants

A connection binds an authenticated Hive principal to a provider account, tenant, credential reference, granted provider scopes, expiry, and connection health. Tokens remain outside mind prompts and receipts. A usable connection is proven through a bounded account identity/capability probe; successful OAuth alone does not prove every action works.

A grant binds that connection to a named mind or swarm, allowed capabilities, resource constraints, expiry, cost ceiling, and grant version. Examples include one calendar, one Slack channel, one repository, or a local Blender project. Revocation invalidates queued calls and future events; running calls stop where possible and report any already committed effect.

A user confirmation, when policy requires it, binds the exact input digest, capability, adapter version, connection, recipient/resources, grant version, expiry, and cost ceiling. Changing any bound value invalidates that confirmation. Use Hive's existing approval facility after proving these bindings; add no separate approval queue.

## Execution envelope

The request carries `request_id`, `goal_id`, principal, mind, connection reference, grant version, capability ID, pinned adapter version, typed input, input digest, deadline, cost ceiling, and idempotency key. The host computes trusted identity and digests. Minds cannot self-assert another principal or grant.

The response carries status, request ID, provider request ID where available, provider object references, structured output, observed timestamp, effect certainty, actual/estimated cost with its source, and a redacted error. Status values are `succeeded`, `failed`, `refused`, `needs_confirmation`, `cancelled`, `expired`, and `outcome_unknown`. Provider acceptance and verification of the resulting state are recorded separately.

Do not automatically retry a non-idempotent write after a timeout. Query provider state using the recorded key/reference where possible. If reconciliation cannot establish the outcome, preserve `outcome_unknown` and ask for a decision through the normal workflow. Local deduplication alone cannot guarantee exactly-once effects at an external provider.

## Event delivery

Subscriptions bind to a connection, capability grant, filters, expiry, and destination workflow. Validate provider webhook signatures where available and reject replay according to provider semantics. Persist the event before acknowledging receipt; process delivery with deduplication and record the resulting goal reference.

Use provider cursors or bounded polling to recover after downtime. Record gaps explicitly when replay is unavailable. Out-of-order events must not overwrite newer resource state. Events carry data, not authority to execute their instructions. Connecting an account or receiving a webhook must not start an unapproved recurring workflow.

Hive owns scheduling and workflow state. External subscriptions and delivery workers feed its existing goal/flow mechanisms. Flow reuse must be checked against the current qualified subset.

## Isolation and data handling

Execute third-party adapters outside the Hive host process with constrained filesystem, network destinations, time, memory, and concurrency. Local application plugins communicate with a bounded application bridge; arbitrary embedded scripting is a distinct capability. Avoid widening every mind's sandbox to accommodate one adapter.

Credentials are injected only into the permitted worker. Separate secrets from provider content; redact both appropriately in receipts. Preserve source references and data classifications when results enter Hive memory or model context. A catalog/settings WorkGraph may use the existing program host, but that host's context capability checks do not sandbox Python execution.

For MCP, pin server provenance and versions and enforce the same gates on every call. For HTTP/OpenAPI, constrain hosts and redirects, block unintended local/metadata destinations, bound response sizes, and bind credentials to their intended destination. Browser adapters use a named account/session and surface the distinction between a UI action and a verified provider effect.

## Qualification and catalog state

| State | Evidence required |
| --- | --- |
| Proposed | Catalog entry, source/evidence basis, exact intended capabilities |
| Implemented | Adapter code and pinned manifest; no readiness claim |
| Fixture qualified | Disposable tests for schema, policy, isolation, faults and recovery |
| Provider qualified | Dated evidence from the actual provider/application with designated test accounts/projects |
| Enabled | Operator-selected grant and current connection check for the intended scope |
| Degraded or revoked | Visible failure, expired/revoked credential, or withdrawn grant |

Track this state per route and capability, not just per app. A read-only GitHub MCP route does not qualify browser-based publishing or repository deletion.

Receipts bind the adapter pin, action, host revision, synthetic/test scope, assertion, timestamp, outcome, provider reference and redacted error. Fixture evidence and live provider evidence remain separate. A manifest hash proves identity of bytes, not independent review, signature, or security.
