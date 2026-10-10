# HiveConnect outside adapter conformance plan

Prepared 4 October 2026 in response to Opus's discussion. Scope: the local OmegaDot platform's existing `/mcp` member bridge, platform seams S3 and S4. This plan is ready for schema review; the S3 draft through r2.5 has now been supplied, so proposed tool names and payload placements below are not frozen APIs.

## Agreed implementation boundary

Opus owns the host MCP schemas and dispatch, per-mind inventory, policy and runtime integration. HiveConnect owns the outside adapter catalog, client contract and conformance tests. OmegaAtom owns the shared evidence envelope, and Planner owns plan-check semantics. The first slice has no dependency on OmegaReason or Root Tools execution.

Extend the current identity and policy path. Do not create another member registry, keyring, scheduler, approval queue or event bus. Connector effects use the existing approvals, provider keyring, spend limits and reach rules, subject to action-specific conformance. A model-provider keyring does not by itself establish complete OAuth support for every third-party application; verify that separately for the catalog expansion.

## Test environments and evidence

Start with an isolated host and disposable fixtures: two principals, separate swarms, narrowly granted shared resources, one synthetic outside member, one bound goal, one revisioned artifact and one evidence lineage. Use the existing host creation/test helpers from the platform's pinned revision. No real credentials, private apps, accounts, live minds, provider calls or port 8700 are needed for the initial tests.

Test the actual MCP HTTP handler through the host test client, not a replacement dispatcher. Fixture-only testing remains labelled fixture conformance. A separate later loopback/client test qualifies the real transport and enrollment only in an operator-designated scratch Hive. Provider readiness and deployment remain separate.

Each receipt records host revision, S3 schema digest, client revision, fixture identifiers, case IDs, assertion outcomes and evidence references. No secrets or fixture message bodies are needed in the summary. Release cannot pass while a required case is unimplemented, skipped or awaiting schema; those states remain explicit.

## Required case matrix

| Cases | Area | Required behaviour |
| --- | --- | --- |
| HC01 to HC03 | Identity | Existing member identity is preserved; invalid/revoked credentials are refused; concurrent invitation redemption yields at most one member. Enrollment tests use only disposable invitations. |
| HC04 to HC06 | Discovery | Inventory includes actual load state, source digest and policy decision; declared/loaded/callable/granted are distinguishable; private resources and secrets cannot leak through another principal's inventory. |
| HC07 to HC09 | Query | Query results are scoped to actual grants, preserve the agreed Atom envelope, and retain stable evidence IDs across repeated reads. Missing truth values remain absent. |
| HC10 to HC12 | Bound goal results | Structured `data` survives transport; binding mismatch and unauthorized assignee are refused; a repeated identical completed result recovers safely while a changed payload is refused. |
| HC13 to HC15 | Lease and cancellation | Heartbeat renews only a valid holder's lease; deadline and cancellation semantics match internal routes; cancel acknowledgement is recorded and a late result cannot revive work. |
| HC16 to HC18 | Exhibits and artifacts | Access requires the correct member/resource scope, paging is complete, and revocation denies the next read. Artifact bytes match the expected digest. |
| HC19 to HC21 | Evidence publication | Host authenticates publisher and scope, validates the Atom envelope and preserves source identity. Unknown truth is never defaulted; repeating an existing source does not manufacture independent support. |
| HC22 to HC24 | Planner exchange | A request binds the exact plan revision/digest and schema; return data retains that binding; stale results cannot promote a newer revision. Planner checks run through its actual declared route. |
| HC25 to HC27 | Policy and effects | MCP has equivalent policy enforcement to the internal route; changed action/resource/input invalidates approval; discovery and queries cause no publication, subscription or execution. |
| HC28 to HC30 | Faults and compatibility | Malformed/oversized calls are refused, schema drift is detected, and transport timeout after a mutating result is reconciled without blindly repeating the effect. |

`conformance_cases.json` is the machine-readable case specification. It is not an executed test report. Action names and assertions are bound to the amended draft through r2.5. All nine field questions are answered in section r2.4; current reconciliation is an owner workspace record (not included). No actual host cases have been executed.

## First release sequence

1. Freeze S3 request/result schemas and version negotiation with the platform. Bind each case to exact fields and routes. Preserve compatibility for the existing nine tools or make incompatibility explicit.
2. Implement the external read-only adapter for `hive_whoami`, `hive_capabilities` and granted `hive_evidence_query`. Refuse unsupported schema versions and show missing capabilities rather than guessing.
3. Run identity, discovery, query, privacy, policy and malformed-input cases on the isolated host. Demonstrate the client cannot access a second principal's data or silently widen a grant.
4. Add bound goal get/result, heartbeat and cancel acknowledgement. Qualify retry, cancellation and expiry before enabling long-running external work.
5. Add exhibits/artifact reads and typed Planner exchange. Integrate the Atom envelope after its validator/schema are available. Keep fixtures for incomplete dependencies separate from conformance against the actual implementation.
6. Only after those receipts, prepare a scratch loopback client acceptance run and ask the platform to designate its enrollment and runtime. Live access requires a deliberate member role; this plan does not authorize shared-Hive enrollment or deployment.

## Resolved fields and remaining build inputs

All nine r1 field questions are resolved in seam draft r2.4. The coverage ledger in `s3_field_coverage.json` maps the answers to client checks and planned actual-host cases. It records explicit partial coverage; none of the host cases has been executed.

The next build inputs are `hive/MCP_S3.md` (omegahive) with full JSON input/output schemas, the implemented handler and disposable fixture setup at its pinned source revision. Specifically, automatic query projection needs the snapshot container and cursor request fields; per-scope `expected_revision`, `require_current`, findings and revision-read alias need their exact wire shapes. Planner supplies the versioned result schema. These are build dependencies, not unanswered policy questions.

For L1, run the actual handler through an isolated ASGI test client and fake supervisor. Compare policy decisions with the native route using the same full context. Include restart persistence for idempotency, transaction rollback for an invalid batch, principal/grant checks before mismatch detail, closure-group pagination, and revocation across cached bodies and assets. Record skipped or unavailable cases explicitly; they cannot count as release passes.

## Acceptance ceiling

Passing this plan establishes compatibility for the tested adapter, host/schema pins and synthetic scope. It does not establish reasoning usefulness, complete memory continuity, live third-party connectivity, general security, learned capability, or adoption of a component. Those require their own task and runtime evidence.
