# OmegaMatch: an offernet mind in Hyperon

4 October 2026. Design candidate, grounded in the local Opus response and primary Hyperon literature. This document distinguishes proposed semantics from installed platform behavior.

## Purpose and boundaries

OmegaMatch reasons about the hive's abilities and needs. Its offernet is a relational view of providers, capabilities, demands, prerequisites and evidence. It interprets vague needs, explains candidate fits, detects reusable code and existing services, and returns recommendations. It does not own planning, plan-to-code traceability, code generation, review, assignments or execution.

Planner creates and revises plans; Code implements and publishes workspace summaries; Review assesses outputs and disputes; the host owns identity, policy, catalogue projection, canonical goals/requests, visibility, budgets and the single matcher. Match is a native mind swarm over those mechanisms. Its craft memory may learn matching patterns, but it must not become a second authoritative capability registry.

This follows an owner workspace record (not included), including the owner's correction recorded there: plan-to-code is for Planner, Coder, the working hive and Reviewer. Match may notice that suitable code exists; it does not certify that a plan is implemented.

## Hyperon basis and what we infer from it

Hyperon describes cognition through shared metagraph representations, MeTTa and interacting cognitive processes. Cognitive synergy includes translating an intermediate problem into a form another process can address. OmegaMatch applies that idea to hive services: it recognizes an opportunity for another mind or swarm to help and preserves the context of the recommendation. This application is our architectural inference, not a claim that the Hyperon paper specifies OmegaMatch. [1, sections 3.1, 3.3 and 4.3]

MeTTa supplies symbols, variables, expressions, types, substitution and pattern matching. Reflective metagraph rewriting allows representations and rules to inhabit the same formal medium. Our DSL should therefore be a small domain vocabulary in MeTTa, not a separate parser or opaque JSON scoring language. A structural match is a binding witness; it does not prove task success. [2, sections 2 and 3]

Meta-MeTTa supplies a formal operational account and discusses resource-bounded transitions using effort objects. That motivates explicit search budgets, but does not establish that our PeTTa runtime implements that metering. Runtime custody and resource enforcement require independent engineering. [3, sections 3 and 6]

## Ontology: relations before rankings

Each record has a canonical host ID. Capabilities are relations among provider, operation, input domain, output contract, prerequisites and context. A provider's claim about itself and evidence about a past performance are different atoms. Equating a capability with an agent name would lose both scope and change history.

Proposed vocabulary, shown as schematic MeTTa expressions (variables are placeholders, not an implemented schema):

```metta
(Capability $cap (In $input) (Out $output) (Requires $conditions))
(Offer $offer $provider $cap $scope $source-revision)
(Need $need $requester $cap $input $output $constraints)
(Projection $snapshot $digest $viewer $policy-revision $observed-at)
(Evidence $evidence $offer $kind $artifact-digest $context $outcome $review-ref)
(Unknown $subject $property $reason)
(Contradicts $evidence-a $evidence-b $context)
(ReuseCandidate $need $offer $workspace $tree-digest $symbol $evidence-refs)
```

A capability with parameters is more useful than a flat tag: converting CSV to a table is not equivalent to safely migrating an authenticated database. Keep versions, scale, environment and material preconditions in the operation's contract. Human descriptions can suggest candidate meanings, but inferred aliases remain proposals until the owning service accepts the mapping.

The projection is generated from existing services, roles, native SkillSignature atoms, app descriptions and Code workspace summaries. It contains only the requesting principal's visible records. Host IDs and a source-revision vector let results bind to exact facts. The space is disposable reasoning input; original stores remain authoritative.

Do not evaluate catalogue contents as code. Deserialize expressions as data, validate constructors and admit only reviewed query rules. A MeTTa space name or an `authority-none` label is no sandbox: grounded operations can have effects. The offline fixture below uses invented literal facts, local pattern queries and no provider/network/host operations. Production custody is still open.

## The meaning of a match

Let P(v,t) be the host projection visible to principal v at time t. Let N be a typed need and O an offer. A structural witness theta satisfies:

`P(v,t) proves Compatible(N,O,theta)`

Here Compatible means the declared operation, inputs, output contract and explicit preconditions agree under a versioned domain relation. It does not mean a type checker proves behavioral correctness. For function-like contracts, candidate input acceptance must cover the needed input domain and promised outputs must satisfy the required output contract; this requires an explicit subtyping or implication relation, not word similarity.

Use four separate statuses for each required condition: supported, contradicted, unknown, and conflicting. "Conflicting" preserves both relevant positive and negative evidence. Absence of an atom is unknown under an incomplete visible projection; it is not a global negative. A scope restriction is a host decision, never an inferred permission.

The host may return a candidate when structural fit is established but performance evidence is missing; label it advertised or declared. An uncertain fit should be a possible candidate with named unresolved conditions. A contradicted hard requirement excludes the offer from eligible recommendations, with the reason shown only if visible. Conflicts require assessment rather than majority voting over duplicate records.

Return the need binding, offer IDs, substitution witness, relevant source IDs/digests, unresolved conditions, evidence basis and current catalogue/policy revisions. Revalidation is required before a requester accepts or dispatches work. A match creates no claim, grant, connection or spend.

## Evidence is a contextual graph

Opus proposes declared, advertised, demonstrated and reviewed labels. Preserve these as evidence facets with explicit semantics rather than one universal ability ladder. A review may criticize an output; a valid result schema proves shape; a passed fixture covers only its fixture. None automatically proves general ability.

Opus's interim demonstrated label is a schema-valid done goal pending R17 reviewer-accepted completion. Represent its basis as `schema-valid-completion`, and keep `accepted-performance` separate. A review reference must carry verdict, mandate and exact artifact digest. Never interpret the bare presence of a review as favorable evidence.

Evidence must bind to provider identity, capability/version, environment, artifact, time and task context. Multiple reports from the same underlying run share an origin and cannot be counted as independent confirmations. A newer code tree invalidates claims about the old tree's verification unless the responsible owner establishes applicability. Capability confidence and evidence confidence are separate; arbitrary numeric confidence is not justified. Start with explicit evidence, uncertainty and rationale. Calibrated outcome estimates are a later empirical extension.

## Reuse and cognitive synergy

Two useful motifs fit this ontology:

1. A requester needs an operation; an allowed Code workspace summary advertises a corresponding symbol. Match reports its location, tree digest, input/output contract and relevant verification. It recommends investigation or reuse to the requester; Code/Planner/Review decide applicability.
2. A swarm proposes a new planning service while an existing planning offer is visible. Match suggests asking that service, or asking for a connection if permitted discovery exposes it. The same pattern covers designers, reviewers and tools. It never contacts a hidden service or creates the connection itself.

Embeddings or language models may retrieve candidate synonyms and paraphrases. Symbolic contract checks and evidence bind the recommendation. Match can suggest complementary services when no provider covers the whole need; operational decomposition, ordering and ownership are returned to Planner. This keeps cognitive synergy without adding another planner.

## Reflection, learning and attention

Store proposed ontology mappings and matching heuristics as inspectable candidate artifacts with provenance. Evaluate changes against retained counterexamples and require owner acceptance before changing shared rules. Self-inspection means explaining which rules and evidence produced a match; it does not confer authority to rewrite host policy.

Feedback should distinguish recommendation made, seen, accepted, reused and independently successful. Rejected recommendations are not automatically wrong, and accepted recommendations are not automatically successful. Learn retrieval priorities from authorized, contextual outcomes while retaining negative and conflicting evidence. The host remains owner of scoring; Match contributes proposals and explanations, not a parallel scorer.

A finite search budget bounds candidate retrieval, inference depth, wall time and returned explanations. Return a truncation marker when exhausted. "No match in this search" is not "no provider exists". Across hives, use visible directory summaries and connection scopes; do not assume distributed AtomSpace is installed or that all hive knowledge belongs in one globally readable space.

## Concrete next slice

The host and Planner retain their current matcher/API work. Match contributes a typed-need contract, a reuse-alert contract, reviewed domain atoms, explanations and native role prompts. Begin with two literal synthetic reuse cases and negative cases for hidden offers, incompatible output, changed tree digests, adverse reviews and missing prerequisites. Prove bindings and preserved uncertainty before a stopped registration, then separately qualify a bounded live native-mind run.

The sample `examples/reuse.metta` demonstrates variable binding over explicit invented offers and needs only. It is not a production projection, policy gate, inference engine, ranking implementation, qualified type system or live mind. No change is made to Planner's `matching.py` or the platform checkout.

## Sources and local evidence

1. Goertzel et al., *OpenCog Hyperon: A Framework for AGI at the Human Level and Beyond* (2023), [primary text](https://arxiv.org/html/2310.18318v1).
2. Goertzel, *Reflective Metagraph Rewriting as a Foundation for an AGI Language of Thought* (2021), [primary text](https://arxiv.org/html/2112.08272v1).
3. Meredith et al., *Meta-MeTTa: an operational semantics for MeTTa* (2023), [primary text](https://arxiv.org/html/2305.17218v1).
4. [MeTTa reference implementation](https://github.com/trueagi-io/hyperon-experimental); implementation behavior is version-specific.
5. Local architecture: owner workspace records (not included), plus `README.md` and `matching.py` in the omegaplanner repository, read 4 October 2026.

Local PeTTa source HEAD observed: `ae66fa8e41dcd5539d614706bd4e5cfb34f9608d`. Platform source HEAD observed: `a9e277740ea80b3846e3e083815a4f07ef4ac776`. These are observations, not clean-tree or runtime deployment claims.


## Native relational evidence example

`examples/evidence_reasoning.metta` now makes part of this theory executable over
invented facts. Queries join a visible offer's current tree to each required condition.
They retain supporting and contradicting records, derive an explicit unknown when
no current-tree record exists, and avoid surfacing a provider without an Offer atom.
Six checks pass locally. This shows the specific query rules' behavior; it does not
prove runtime visibility, host catalogue provenance, a general contradiction-tolerant
logic, learned confidence or complete ability assessment. It adds no ranking policy.

## Runtime and reflection extension

See [Contextual capability and reflective boundaries](HYPERON_RUNTIME_THEORY.md)
for configured/loaded/callable/policy/fitness separation, generation-bound evidence,
non-monotonic current readiness, contextual joins, reflective rule proposals and
persistence obligations. These are OmegaMatch design inferences from primary
Hyperon literature, not claims that the papers supply the host contracts.
The accompanying runtime_dimensions.metta passes6 native synthetic reporting
checks; it adds no authority or production runtime qualification.
