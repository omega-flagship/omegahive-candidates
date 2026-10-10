# OmegaFlow theory and competitive analysis

Research date: 4 October 2026. Prepared for the owner and the OmegaHive platform owner. This document combines primary-source product research with a proposed direction for OmegaFlow. Product descriptions are documented capabilities, not independently measured performance. Proposed advantages remain hypotheses until tested.

OmegaFlow should be a shared workspace in which people and the Hive describe, inspect, reuse and improve work across people, minds, services and artifacts. The owner's requirement includes the Hive creating workflows for its own needs and retaining reusable workflows as skills. The graphical editor and agent interface should manipulate the same versioned model.

The recommended initial focus is repeated work involving agents, shared evidence and human judgment. Demonstrate a complete loop from an expressed need through an inspectable workflow, a reusable skill and attributable run records. Broader funnels and relationship maps should share identities with this loop without acquiring execution semantics merely because they appear on the canvas.

## Existing foundation and missing capability

OmegaFlow already provides a typed representation, stable element identifiers, ordered n-ary relations, relations about relations, transitions, structural checks, JSON and inert MeTTa projection, semantic fingerprints and separate layout. Host code supplies durable revisions and a bounded goals-only coordinator. The authoring template candidate adds five local starters. These are source and qualification claims; they do not establish live agent authoring or a deployment of the latest candidate.

The inspected host access path in `hive/core/flows.py` (omegahive) requires a current named person session for stored flow access. Agent-native creation, scoped revision, skill registration and invocation therefore need an explicit platform extension. Do not give a mind a fabricated person session to bridge that gap. Existing Hive skill mechanisms must be mapped before deciding whether to extend their registry or add an adapter.

Native Hyperon inference, reflective workflow rewriting and execution semantics remain unqualified. The current encoding is an interchange and structural-query representation.

## Distinct meanings on one canvas

A relation describes a connection, a dependency constrains availability, and a transition prescribes a change. For example, “Alice owns the proposal,” “review requires the proposal” and “acceptance creates a delivery goal” have different meanings. The visual language should expose their types and operational bindings.

Epistemic origin, revision state and runtime state are independent. An inferred relationship can be a draft; an asserted rule can be adopted; an adopted transition can be idle. Confidence in an inference is not permission to execute it. An identity reference does not authenticate its subject. Evidence custody and freshness are additional questions, not consequences of attaching a reference.

Workflow, case and funnel views answer different questions. A workflow specifies progression; a case gathers evolving information and available work; a funnel measures a population under defined identity, stage and time-window rules. A relationship view describes context. A run view shows recorded behavior. They should share object identity while retaining their own semantics. CMMN provides a separate reference for case modeling; BPMN and DMN provide references for process and decision modeling. [OMG CMMN](https://www.omg.org/spec/CMMN/1.1/About-CMMN), [Camunda BPMN and DMN](https://docs.camunda.io/docs/components/concepts/bpmn-dmn-feel/)

Funnel measurement must define the population, entry rule, stage membership, repeated entries, observation window and missing observations. Conversion attribution is not proof of causation. Customer.io's documented conversion criteria and windows illustrate why a sequence of stage boxes is only the beginning of a funnel product. [Customer.io conversion criteria](https://docs.customer.io/messaging/send/automations/conversions/)

## Workflows as reusable procedural knowledge

Distinguish four objects. A workflow definition describes a procedure. A skill describes when and how that procedure is useful, its contract and requirements. An invocation binds a skill to an actor, inputs and scope. A run records the resulting work. A single definition can support several skill descriptions, and a skill can incorporate a pinned workflow plus instructions and supporting resources.

Proposed skill content includes purpose, suitable triggers, input and output schemas, a pinned workflow revision, required capabilities, parameter binding rules, limits, evaluation evidence and failure behavior. These fields describe requirements; host policy decides whether an invocation can satisfy them. Registration must not issue credentials or grant permissions.

For portable packaging, the Agent Skills specification supplies metadata and instructions in SKILL.md plus optional scripts, references and assets, with progressive loading. A workflow revision and explanatory resources could be packaged alongside that file. That is a proposed OmegaFlow adapter, not a claim that the standard defines workflow execution, revocation or adoption. [Agent Skills specification](https://agentskills.io/specification)

Repeated successful work is a candidate for a skill, not automatic proof of generality. Extract the reusable procedure while separating instance-specific participants, private inputs and credentials. Record where it has been evaluated and where its behavior remains unknown. A skill should be inspectable and editable by people after its creating agent has gone away.

## Hyperon contribution and comparison baseline

Hyperon's metagraph theory allows representations and rewrite rules themselves to be represented and manipulated. This makes relations about evidence, constraints on handoffs and proposed transformations of procedures conceptually natural. Goertzel's paper discusses metagraph rewriting, reflection and representation of rules. It does not establish that OmegaFlow currently implements these capabilities. [Reflective Metagraph Rewriting](https://arxiv.org/abs/2112.08272)

The proposed cycle is need → retrieve or compose procedure → inspect and validate → invoke under scope → retain outcome evidence → propose a revision. Reasoning should return an inspectable proposal, including sources and assumptions. Adoption and operational authority are host decisions. Running instances remain pinned unless an explicit migration mechanism is designed.

Compare native MeTTa reasoning against a typed relational graph using the same facts and questions. Suitable tasks include identifying a missing accountable participant, retrieving a procedure under scope constraints and explaining which observations support a proposed change. Measure correctness, unsupported conclusions, latency and explanation fidelity. Prefer the simpler mechanism when it performs equivalently.

## Competitive assessment

| Reference | Documented capability | Proposed implication for OmegaFlow |
| --- | --- | --- |
| n8n Assistant | Creates, edits, tests and troubleshoots normal n8n workflows through chat; currently documented as Preview. | Agent authoring on the same canvas is already a competitive expectation. Test the shared skill and organizational context loop. |
| Zapier Canvas | Human and team steps, split paths, and links to existing automation assets. | Connecting a diagram to executable assets is insufficient differentiation. |
| Langflow | Visual AI components, tools, playground testing, logs and application integration options. | Visual agent composition needs a strong reuse and inspection experience. |
| Dify | Workflows can be published as reusable tools. | “Workflow as skill or tool” alone is insufficient differentiation. |
| Camunda | Separate process, decision and expression concepts using BPMN, DMN and FEEL. | Learn explicit branch, join and decision semantics before expanding execution. |
| Temporal | Durable execution using retained event history to recover progress. | Treat recovery as an engineering obligation; do not imply local goal deduplication guarantees unique external effects. |
| LangGraph | Thread checkpoints and cross-thread stores for persistent state and information. | Persistence needs an explicit model for scope and continuity. |
| Customer.io | Conversion criteria and observation windows for journey outcomes. | Build measurement semantics before claiming operational funnel analysis. |

Sources: [n8n Assistant](https://docs.n8n.io/build/ways-of-building-workflows/n8n-assistant), [Zapier Canvas](https://help.zapier.com/hc/en-us/articles/23479101666573-Element-types-in-Zapier-Canvas), [Langflow](https://docs.langflow.org/concepts-overview), [Dify workflows as tools](https://dify.ai/blog/dify-ai-blog-workflow-major-update-workflows-as-tools), [Camunda](https://docs.camunda.io/docs/components/concepts/bpmn-dmn-feel/), [Temporal](https://docs.temporal.io/temporal), [LangGraph](https://docs.langchain.com/oss/python/langgraph/persistence), [Customer.io](https://docs.customer.io/messaging/send/automations/conversions/).

A current competitive correction matters: n8n's September 2026 announcement describes an assistant that builds, executes and repairs workflows, superseding its earlier builder. It also says the launch is not proactive and does not learn preferences over time. This is a dated vendor description, not proof of a durable market gap. [n8n announcement](https://blog.n8n.io/introducing-n8n-assistant/)

Our hypothesis is that Hive continuity can make workflows useful beyond one build session: shared identities, persistent goals, attributable evidence and procedural skills remain available to future minds and people. Validate this through tasks; do not claim uniqueness from an architectural description.

## Proposed product direction

Use the positioning: “OmegaFlow is the shared visual and agent workspace for designing, reusing and improving work in OmegaHive.” People can draw or describe a process; minds can retrieve, compose and revise it through structured operations. Either can inspect the same result.

Start with research intake → evidence collection → proposal → review → delivery. The Hive creates a draft, the person inspects it, a permitted invocation creates native goals, and the resulting records support reuse as a skill. A second task should reuse the skill with different inputs and scope. A changed policy should produce a reviewable new revision without altering the running instance.

Avoid expanding into a second general scheduler or a large connector catalogue before this loop is useful. Use existing Hive work and policy mechanisms. Extend execution constructs only with explicit semantics for branch selection, parallel work, joins, retries, deadlines and cancellation. Case views and measured funnels can follow when their underlying contracts are defined.

## Benchmark protocol

The research above has not run a competitive benchmark. The following protocol is proposed and ready for review.

Use invented records and equivalent tasks. Record product version, deployment mode, model, configuration and enabled capabilities. Compare a manual typed procedure, OmegaFlow, n8n Assistant and one visual AI builder. Compare packaging and discovery against an instruction skill baseline. Test Hyperon separately so representation and runtime differences do not obscure its contribution.

| Scenario | Observable success | Measurements |
| --- | --- | --- |
| Author a procedure from an ambiguous need | Inspectable definition with correct responsibilities and unresolved assumptions visible. | Time to a valid definition; corrections; unsupported bindings. |
| Reuse as a skill for a second task | Same pinned procedure, fresh inputs and correct scope. | Discovery success; context required; accidental carryover. |
| Diagnose a failed handoff | Explanation supported by specific run records. | Diagnosis accuracy; evidence navigation effort. |
| Co-edit with a person | Conflicting edits preserve both intentions or report a conflict. | Lost edits; misleading diffs; recovery effort. |
| Change policy during a run | Old run stays pinned; prohibited effects stop; revision remains separate. | Incorrect advancement; clarity of blocked state. |
| Revoke a capability | Invocation cannot continue outside permitted scope. | Time to block; orphan work; truthful status. |
| Restart after admission | No duplicate native goals; recoverable run state. | Duplicate work; recovery time; missing receipts. |
| Extract a skill from successful work | Reusable definition separates instance data and retains evaluation limits. | Portability; private-data carryover; contract completeness. |

Choose success thresholds before running the benchmark. Retain raw receipts and failed cases. Report cost only with measured model usage, runtime and operator effort. Do not infer market share, pricing advantage or production reliability from these documentation comparisons.

## Next implementation decision

The next platform review should settle a scoped agent authoring API, mapping to the existing skill registry, and the authority required for invocation. Preserve the existing named-person execution path while designing the additional agent path. The companion AGENT_AUTHORING_DESIGN.md specifies the proposed operations and acceptance checks. No live activation or permission changes are part of this research work.
