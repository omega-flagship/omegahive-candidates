# OmegaMatch: contextual capability and reflective boundaries

Design extension, 4 October 2026. This is proposed OmegaMatch theory, not a Hyperon theorem or installed host authority model.

## What the literature supports

The Hyperon architecture paper presents a framework for interacting cognitive processes and discusses reflective self-modification. It supports using a common representation to connect reasoning processes, but does not establish OmegaMatch's admission or permission rules. [Hyperon architecture](https://arxiv.org/abs/2310.18318).

The reflective metagraph paper treats symbols, types, substitutions and pattern matching as basic MeTTa facilities, with rewrite rules themselves representable as metagraphs. That motivates inspectable domain relations and explanations of rule application. It does not make every represented rule safe to execute. [Reflective metagraph rewriting](https://arxiv.org/abs/2112.08272).

Meta-MeTTa gives an operational semantics for MeTTa. Its formal account is a reference for specifying transitions; correspondence with local PeTTa, host transactions and resource enforcement must be separately established. [Meta-MeTTa](https://arxiv.org/abs/2305.17218).

Everything below is an architectural inference and engineering proposal derived from those foundations and the observed Omega host interfaces.

## Capability is a relation with several independent dimensions

Represent a capability judgment at a context key K=(requester, provider, agent-generation, skill, source-manifest, catalogue, policy, observation). Do not replace this tuple with an agent name or a confidence number.

A declared skill belongs to a source vocabulary. A configured import belongs to a loader selection. A loaded module belongs to a particular running generation and an observed import outcome. A callable operation belongs to a runtime binding and argument convention. A policy decision belongs to the current principal, target and rules. Task fitness belongs to a need, contracts and evidence. Historical performance belongs to a specific execution environment and artifact.

These dimensions are related but none is interchangeable:

- A Provides declaration can support source provenance while runtime loading remains unknown.
- A literal import can support configuration while import success remains unknown.
- A successful read-only binding check can support callability without establishing safe behavior for arbitrary arguments.
- Policy.decide may say allow while command-specific file/service constraints or approvals still refuse the effect.
- An accepted past output can support historical performance while the new provider revision has no applicable evidence.

A single advertised/demonstrated/reviewed label therefore remains an index into evidence, not a proof of all dimensions. Preserve the underlying basis and adverse records.

Schematic atoms:

```metta
(Context $key $requester $provider $generation $skill $manifest $policy)
(StateEvidence $key configured supported $config-ref)
(StateEvidence $key loaded unknown missing-import-receipt)
(StateEvidence $key callable supported $binding-ref)
(StateEvidence $key policy contradicted $deny-ref)
(StructuralWitness $key $need $substitution $contract-refs)
(ObservationDependency $derived $source-ref $source-digest)
```

These describe knowledge. There is intentionally no inference from a supported condition to an execution grant. The host's authorized effect route remains the only way to perform work.

## Knowledge growth and state changes obey different rules

Historical observations may accumulate monotonically in an append-only evidence graph. Current readiness is a view over the exact context key and can disappear after revocation, restart or source change. Adding a new source observation is not a reason to retain an old authorization.

Use four evidence reports: supported, contradicted, unknown and conflicting. Unknown is not false. Conflicting retains positive and adverse evidence together; neither evidence count nor a tier maximum resolves it. This is a small reporting discipline, not a claim to implement a complete paraconsistent calculus.

Provider generation prevents a previous process's loaded/callable receipts from establishing the replacement process's state. Source manifest changes prevent an old signature or verification from silently applying to new code. Policy epoch and requester scope prevent an earlier view from serving as a current grant. Historical records remain accessible where authorized, labelled historical or applicability-unknown rather than deleted.

## Projection and matching preserve context

The host catalogue is a scoped projection P(K), not the whole hive. All joins must retain the same requester and provider/source context. Joining a visible capability name to an inaccessible provider's evidence would disclose private existence and misbind the explanation.

The current codec encodes external strings as inert symbols. This prevents textual rule injection, but proves neither information-flow isolation nor evaluator sandboxing. Static parser output proves declaration extraction only. It cannot establish that a deployment used that loader, resolved that source or completed that import.

Structural matching may produce a substitution witness over declared contracts. Matching an input/output type does not prove behavioral correctness, availability or authorization. Planner's existing matcher owns ranking and search; Match owns explanations and interpretation. No new planner or scorer follows from this theory.

An empty scoped projection establishes only that it contains no offers. An incomplete search can support a bounded no-candidate report with the actual search receipt; it cannot support global absence. Search expansion is a request for a wider authorized observation, not a permission inferred from uncertainty.

## Reflection proposes changes; the host admits effects

Rules and knowledge sharing a representational medium allows Match to inspect why a candidate was proposed, identify missing evidence and propose revised interpretation rules. Reflective inspection should return dependency-linked proposals with rule version, input/source digests and expected changed conclusions.

A proposed rewrite does not install itself, enlarge visibility, import a module or change a policy. Owner review and the host's existing version/admission paths govern changes. Learned matching patterns stay craft memory until qualified; they are not canonical provider facts.

Rule changes require replay against visible synthetic cases and observed outcomes with provenance. Evaluate preservation of unknowns, adverse evidence, scope and non-authority alongside fit quality. Equivalent outputs on a fixture are not a proof of trace equivalence or general semantic equivalence.

## Runtime acceptance remains an engineering obligation

At persistence, recheck goal/request lifecycle, requester scope, source/catalogue/policy versions and evidence applicability. The adopted goal-state compare-and-swap covers only that goal record; it does not provide a transaction over all catalogue sources or revoke effects already executed.

A future import receipt must name host-resolved agent generation, selected loader digest, repository/module source digests, imported module and observed outcome. This is a requirement for a genuine runtime observation, not a receipt Match may manufacture. No receipt is currently supplied by the inspected host surface.

The native example runtime_dimensions.metta qualifies only exact-context relational reporting on invented facts. It does not prove live module loading, permission enforcement, matching quality or acceptance. Production admission remains closed while witnesses, bounded search receipts, custody/applicability and transaction consistency are absent.
