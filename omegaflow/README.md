# OmegaFlow — typed flow foundation

OmegaFlow is an object-and-link authoring module for OmegaHive. This first stage supplies a typed relational representation, lossless JSON/MeTTa encoding, structural checks and an invented garden sign-up example. It now includes a local authoring canvas. An isolated Hive candidate now integrates the canvas, durable storage and a conservative goals-only coordinator; platform review and live integration remain pending.

`model.py` defines schema `omegaflow/1`. Objects have stable ids; relations have ordered named roles whose members may themselves be relations. Nodes, relations, transitions, constraints, events and pinned subflows are first-class. Every element separates semantic kind, epistemic origin/confidence/evidence, revision state and runtime state. Identity references are data and do not authenticate a person or service.

`revision(flow, layout)` creates a detached candidate snapshot and semantic SHA-256 digest. Layout changes do not change that digest. Durable immutability, authentication and adoption belong to the host. The digest is a content fingerprint, not a signature or access grant. Element and role ordering is part of v1 content, so reordering can produce a new digest.

`symbolic.py` emits fixed-predicate MeTTa data atoms. Each field retains its JSON value as hex-encoded UTF-8. Derived `OFRole` and `OFTransition` indexes expose graph structure. Recovery accepts only this finite encoding and verifies that all indexes exactly match the retained fields and revision digest. Imported strings cannot become executable predicates. The encoding preserves arbitrary properties, unicode, n-ary relations, relations about relations, and subflow digest references. It is an interchange and query representation; it does not establish Hyperon's reflective rewriting, probabilistic inference, or native flow execution semantics.

`check_structure` identifies unreachable marked control steps, declared approval requirements without an approver, and failed distinct-members constraints. It does not verify that a target exists, that an approver is a person, that events are visible, that action permissions exist, or that evidence is authentic. Constraint names are bounded built-in data; they are not arbitrary executable expressions. Cycles are representable but iteration and join semantics are not defined for execution. Subflow references are pinned but their bodies are not resolved by this module.

Run offline checks from the workspace root:

```sh
python -m pytest omegaflow/tests -q
```

Run the disposable native structural-query proof:

```sh
PETTA_PATH="$PETTA_PATH" \
PYTHONPATH="$PETTA_PATH/python:$PWD" \
python -m omegaflow.native_check
```

This uses a fresh local interpreter and invented facts. It performs no provider calls, Hive activation, workflow actions or messages. The native proof checks exact members of a three-part relation, a relation whose subject is another relation, and three transition edges. Receipt: an owner workspace record (not included).

The candidate `7b35361`, based on platform `be6e0e5`, is retained in platform Git and integrated as `61f0c54`. The obsolete candidate clone was removed after merge confirmation; the historical qualification remains in receipts; It adds immutable C39 flow revisions, separately versioned layouts, exact-digest adoption, actor-scoped runs, deterministic goal dispatch and transition receipts inside Hive's existing reconcile loop. See the candidate's `hive/FLOWS.md` for the trust boundaries, supported subset and qualification. Platform owns review, integration and deployment. No live provider run has been performed.


## Local flow studio

Launch the stateless authoring preview from the workspace root:

```sh
python -m omegaflow.editor.server --port 8766
```

Open the printed `http://127.0.0.1:8766/` URL. The server binds loopback only, checks Host and Origin, limits requests, and serves a fixed asset allowlist. It calls the shared Python model for validation, fingerprints, structural checks and data projections. It has no storage, provider access, Hive connection or run endpoint.

The canvas supports new flows, draggable objects, keyboard placement, zoom/fit, graphical transitions, n-ary role editing, direct type/trigger/target/approver controls, advanced typed JSON, undo/redo, MeTTa data inspection and revision import/export. Drafts stay in browser memory; export before closing or refreshing. Import validates the revision digest before replacing the current draft. Existing references prevent unsafe element deletion; removing dependent references is an explicit edit. Mobile layout stacks the inspector below the canvas.

`admission.prepare` is a fail-closed structural preflight for a conservative subset of Opus's proposed first host execution model. It accepts only run-start and run-local goal/request completion triggers, goal/request/message action kinds, adopted transition descriptions, and acyclic single-predecessor flow shapes. It refuses subflows, guards, joins and declared approval requirements until the host qualifies them. Events bind to an upstream transition through `props.source_transition`. Descriptive adoption is not host adoption, and eligible shapes still return `execution_authorized: false` with the host checks required. The garden authoring example is deliberately ineligible for execution.

Recorded qualification at the time: 38 Python tests and 17 real-browser checks. Native relational-query proof remains separate. The browser acceptance scripts were tied to the owner's workspace layout and are not included in this repository; see STATUS.md at the repository root. The candidate tests exercise the named-person review gate, cancellation, restart recovery and concurrent database controllers against disposable fixtures. These receipts do not establish live service deployment or native Hyperon execution.

## Integrated host status

Platform integrated the candidate as `61f0c54`. Independent disposable qualification: 651 backend tests plus 456 subtests, 236 UI tests, 7 native browser checks and the production build passed; 24 backend tests skipped. Deployment is not verified. See an owner workspace record (not included) and [Using OmegaFlow](QUICKSTART.md).

Read-only live check at 04:46 UTC: Hive on localhost:8700 serves the integrated studio assets and Flow UI chunk; the unauthenticated example API refuses access with 401. Exact running build and signed-in workflow execution remain unverified. See an owner workspace record (not included).

## Frame isolation candidate

Candidate `6c70176` replaces the same-origin iframe with an opaque srcdoc frame. All API work stays in the parent bridge, bound to the exact frame and per-load channel. 243 UI tests, 25 flow backend tests and 30 browser checks passed; platform review/deployment pending. Details: an owner workspace record (not included).

Isolation candidate merged as `dfe7e9e`, followed by cleanup fix `1eafb1f`. Requalification at `0149578`: 243 UI tests, production build and 13 hosted/security browser checks pass. Live browser confirms opaque srcdoc and sandbox without allow-same-origin. Named-person live workflow acceptance remains outstanding. See an owner workspace record (not included).

## Authoring templates

Use **Templates** in the canvas toolbar for task review workflows, lead funnels, interaction handoffs, connection maps and the invented garden example. Selection replaces the local draft and is undoable; export it to keep it. Connections support ordered n-ary roles and links about links. The catalogue supplies no live identities or permissions, and selecting a starter never saves, adopts or starts a run. Configure actual host bindings and approvals separately.

## Theory and agent authoring

[Theory and competitive analysis](research/THEORY_AND_COMPETITIVE_ANALYSIS.md) develops the shared human and Hive authoring model, reusable workflow skills and a proposed benchmark. [Agent authoring design](research/AGENT_AUTHORING_DESIGN.md) specifies the proposed capability path and acceptance scenario. These are research and design artifacts; agent-native authoring and skill invocation are not yet implemented.

[OmegaDot tool map](research/OMEGADOT_TOOL_MAP.md) maps native core skills, module organs and Hive services to this agent's working systems. The [native inventory](research/OMEGADOT_TOOL_INVENTORY.json) retains source catalogues and hashes. A prior map mixed in an unrelated connector and is marked superseded.
