# Proposed Match validation context adapter

4 October 2026. Follows an owner workspace record (not included).
The general program-owned semantic hook is decided by Opus; the Match-specific
generic context is decided; the catalogue record shape below remains a proposal
awaiting the host catalogue contract.

Binding or request constraints must name `validate: "program:omegamatch"`.
After schema validation, inside the same host completion transaction, call
`program.validate_result(ctx, goal, proposal)`. `goal` is the trusted current
record, with actual host id and binding.request_id. Binding may be a parsed object
or the host's stored JSON. The program returns only `{ok:true}` or `{errors:[codes]}`.
It does not accept results, persist state, grant access or compute a ranking.

Observed first host cut: synchronous validation calls supply `ctx.validation`
with goal, request and attempts_so_far. Match also supports the proposed method
below when present. Catalogue and requester viewer remain absent in that cut.
Async resolver values are refused cleanly; host synchronous calls must not receive
a coroutine as an acceptance result.

Host API being prepared: `ctx.validation_context(goal)` returns the trusted goal,
full request, request_state, requester_swarm, deadline and attempts_so_far. The
host also supplies `ctx.viewer_for_requester`. The program checks actual goal and
request IDs and active request state before asking for catalogue data.

Draft 1 catalogue API: `ctx.catalogue(context.requester_swarm)` (synchronous for the current host).
`ctx.viewer_for_requester` remains required host visibility context. The published
projection shape is not the admission record below; it is refused explicitly until
request-specific witnesses/search/source facts are supplied. See
an owner workspace record (not included).
The Match record shape we propose for its response is:

```
{
  goal_id, request_id, active,
  binding: {request_id, need_revision, need_digest, catalogue_digest,
            policy_revision, rule_version},
  current_binding: {same fields, freshly derived},
  need_id,
  visible_offers: {offer_id: {provider_id, target_kind, locator, artifact_digest}},
  evidence: {evidence_id: {reference, offer_id, artifact_digest,
                         custody_verified, applicable}},
  host_candidates: {offer_id: {contract_fit, unresolved_conditions,
                             required_evidence_ids, hard_requirement_contradicted}},
  required_conditions: []
}
```

Construct this from the requester principal and actual request, not the producing
mind's broader visibility. Recheck connection/grant revocation, lifecycle, current
policy/catalogue/source versions, evidence custody and applicability at completion.
`binding` captures the immutable requested context; `current_binding` detects drift.
The actual allocated request ID belongs in both, derived from the goal binding.
`active` must be exactly true; missing/unavailable context refuses validation.

Evidence reference is an exact host-resolved object including id, digest, basis,
context and observed_at. Review references also require verdict, mandate and origin.
`required_evidence_ids` must include adverse/conflicting evidence chosen by the
shared matcher/host; a model must not choose the required evidence set itself.
`custody_verified` establishes resolved reference custody, not general truth.
`applicable` is a host/owner decision concerning this offer's exact artifact/context.

Code locator: exactly `{workspace, symbol}`, both nonempty.
Service locator: exactly `{service}`, nonempty. These are references, never executable
instructions. A locator grants neither access nor permission to invoke a service.

Host must refuse unknown/missing validation programs and malformed hook responses;
only explicit `{ok:true}` with no errors permits persistence. An exception must not
silently fall back to schema-only completion. Preserve failed attempts and claimed
status, with bounded visible errors. Requester/Planner R17 acceptance remains separate.

Qualification still needed: real host resolver, atomic enforcement, transaction
rollback, failed-attempt preservation, concurrent catalogue changes and grant
revocation, cancellation races, isolation/resource custody, connection-only service
advertisement, and bounded live native cognition. The read-only program checker and
mock context unit checks do not prove these behaviors.

Program loads its sibling `protocol.py` by local path. All admission dependencies
are Python standard library modules; no workspace PYTHONPATH is needed. Root
`omegamatch/protocol.py` is a compatibility re-export of the bundled implementation.
The host Updates digest can cover the complete program folder. Nothing is copied
into the platform owner's checkout or mounted on the shared hive.


## Additional proposed catalogue facts by result kind

Common trusted binding, current_binding, active, goal_id and request_id apply to
all kinds. For typed-need, the host additionally derives source_need
{hard_constraints, preferences, source_refs, unknowns} and known_operations from
the normalized requester input and visible catalogue. Match cannot supply either.
For no-candidate, the host derives need_id and search_receipt
{candidate_count, searched_scope, unknowns, search_complete, truncation_reason}
from the actual bounded matcher search. This is a proposal pending the final host
catalogue contract, not installed host behavior. Do not build a second registry or
scorer to fill these fields.
