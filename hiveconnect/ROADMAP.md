# HiveConnect delivery sequence

The objective is a dependable integration layer for OmegaHive, proven through complete workflows. This is an ordered backlog rather than a promised calendar. The platform owner retains host integration and runtime ownership.

## Slice 1 Existing MCP bridge and scoped discovery

Use platform S3 and S4 rather than introduce a new dispatcher inside Hive. HiveConnect owns the outside client/catalog/conformance suite. The platform owns capability discovery from actual load receipts and the existing member policy path. OmegaAtom owns query envelopes; Planner owns plan checks.

First freeze the platform schema, then implement identity, read-only capability discovery and scoped query. Add typed bound goal results, heartbeat and cancel acknowledgement before long-running work. Qualify artifact/exhibit access and Planner requests with revision/digest bindings. Root Tools and Reason are not dependencies for this slice.

Acceptance and receipts follow CONFORMANCE_PLAN.md and conformance_cases.json. Start on an isolated disposable host through the actual MCP handler. An authenticated scratch loopback run is a separate stage. No shared-Hive enrollment, deployment or new grant follows from fixture conformance.

## Slice 2 Everyday work

Qualify Gmail message search and drafts; Calendar availability and event creation; Drive file discovery; Docs creation; and Sheets reads/writes. Begin with least-privilege read/draft capabilities, then qualify effects individually. Evaluate a native route and a provider bridge with the same task set before choosing ownership for each adapter.

Acceptance workflow: an invented incoming email requests a meeting; the mind checks a designated test calendar, prepares an event and reply, creates a meeting document, and records a link in a test sheet. Required confirmations use Hive policy. Replaying the event creates no duplicate goal or external effect. A provider outage, expired token, revoked grant and post-write timeout produce explicit recoverable states. Test cross-principal denial.

Output: real provider/application receipts for test accounts, cost observations, scope list and cleanup of created test objects. Sending a test message is a separately authorized qualification step.

## Slice 3 Collaboration and development

Add Slack, Notion and GitHub; broaden Microsoft email/calendar/files in response to intended users. Qualify incoming events and bounded writes separately.

Acceptance workflow: a test message leads to a task and a GitHub issue or draft change proposal, with linked evidence and status returned to the permitted destination. Publishing and messaging remain separate capabilities. Hive records provenance and resumes after restart without duplicating committed effects.

## Slice 4 Creative work

Evaluate the pinned community Blender bridge and official Figma server. Begin with project/scene inspection, then asset changes and rendering. Keep local project writes scoped to a disposable project and designated output folder.

Acceptance workflow: an invented brief creates a small Blender scene, produces a render artifact, records the project revision and output reference, and recovers from a failed render. Verify undo or recovery in the actual app. Arbitrary Python execution is independently controlled. Figma read and write capabilities are qualified against a disposable design file.

## Slice 5 Wider coverage

Select a managed bridge only after comparing action completeness, auth ownership, per-user tenancy, webhook recovery, costs, data policy and exportability. Add CRM, support, commerce, social publishing, model, retrieval and numerical modules according to concrete demand.

Each expanded adapter enters with an exact workflow and action list. Social adapters document account-type restrictions and metered costs. Computational modules declare execution limits and output artifact custody. Financial and destructive actions retain deliberate grants and confirmations.

## Implementation review questions

- Which existing reviewed Tools worker and policy mechanisms can serve the common dispatcher?
- Does the current approval mechanism bind every external-effect field required by CONTRACT.md?
- Where should per-principal credential custody live, and who owns the connection UI?
- Which current goals/flows support persistent subscriptions and restart recovery without a new scheduler?
- Which integrations should Hive own natively after the native-versus-bridge comparison?

These are engineering questions to resolve by inspecting and testing the current host. They do not block the offline first slice or require revisiting the product direction.

## Launch acceptance

Launch readiness is capability-specific: the intended actions have dated provider evidence, per-principal denial is proven, connection health is visible, grants can be revoked, unknown external outcomes are reconciled, and workflow restart avoids duplicate effects. An operator should be able to tell which capabilities are proposed, fixture-tested, provider-tested and enabled.

No real accounts, live Hive, application projects, credentials or recurring subscriptions were changed while preparing this plan. No handoff to another agent has been sent.
