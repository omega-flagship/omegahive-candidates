# OmegaChill 0.1 — L0 advisory candidate

Monitor, identify, intercede cautiously, propose fixes. Preserve useful speed and clarity.

Built in response to an owner workspace record (not included) and the shared modular/Hyperon direction. Python 3.12; imports the existing OmegaAtom validator and digest implementation. No new scheduler, process, service, registry or host changes.

- `findings(events)` checks a bounded caller-supplied chronological window. Three matching actions or replans with unchanged supplied outcome and progress witnesses produce a hypothetical loop/stall. Unknown witnesses and changed results break the run. At most the last 12 events per subject are considered.
- Message signatures must represent the information in an update, not merely its sender/template. Three repeated signatures yield a spam suggestion. Only explicit Murmur/Beat metadata qualifies; decision requests, requested cadence and all other tiers are protected. Host adapters must mark asks/approvals as decisions. No message is suppressed by this library.
- `envelope(...)` packages trace observations and unknown-valued findings into the existing D2 shape, validated by OmegaAtom. Inputs are supplied metadata, not verified custody. Findings include premise references and one proposed correction separately. Preserve evidence IDs across replay; caller owns durable sequence allocation and scope/authentication. No probability is invented.
- `pressure(...)` evaluates supplied session counts, RSS and swap measurements. Ten sessions and 80% swap are configurable advisory defaults, not universal overload diagnoses. A host must distinguish allocated swap from physical-memory pressure before interpreting the ratio. No OS sampling or process control runs. These pressure findings are currently plain proposals, not D2 exports.
- `Gate` bounds notifications with an allowance and per-signature cooldown. Acknowledge/dismiss records are idempotent advisory metadata, retained in memory. The caller owns persistence and monotonic time. Dismissal does not automatically change detection thresholds or grant authority.

No spending, code/policy changes, goal cancellation, permissions, human telemetry or runtime intervention. Desk-time support is deferred: opt-in, off by default, person-private preferences and one notice with snooze. A future host must exclude self-intervention and apply Chill's own hard budget.

## Qualification and next steps

L0: eight focused offline cases pass. No L1/L2/L3 or efficiency improvement claim. No active monitor is installed. Run:

`PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s omegachill/tests -v`

Next: platform review of adapter semantics and progress coverage, stable evidence identity, durable feedback, machine-sampler privacy, and pressure/feedback atom projection. Then an isolated host qualification, keeping notification/cancellation policy owned by the platform. Native NAL/PLN ingestion, catalogue registration and matched Bench comparisons remain unqualified. Overengineering and runaway-spend detection need task/budget evidence beyond this first trace slice.
