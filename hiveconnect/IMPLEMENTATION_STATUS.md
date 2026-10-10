# HiveConnect baseline client implementation

Status on 4 October 2026: L0 offline client checks only. The client is implemented in `client.py` against `baseline_schema.json`, extracted without importing code from platform source `99c2d74`. No live transport, credentials, account enrollment or host integration is included.

## Foundation direction applied

Read the platform owner's D0 study and follow-up contract notes (owner workspace records, not included) before implementation. The study's source findings and runtime reports are platform-owner evidence, not newly reproduced by this client work.

D0 prioritizes separating conflicting NAL/NARS rules, proper PLN term priors, stamped revision inside minds, bounded core-led reasoning and platform security repairs. HiveConnect does not implement or claim these foundations. The client must not present logical calculators or declared capability sets as an autonomous reasoning substrate.

The study also reports member/operator authority problems, provenance lookup weaknesses and policy/placement issues. Offline client refusal does not repair the host. No wider enrollment or live connector activation is proposed before the platform supplies scoped authority and qualification evidence.

## Implemented behaviour

- An injected transport interface makes the client testable without a network, credentials or provider calls.
- Initialization checks protocol and server identity label, and compares input schemas for permitted read tools. These checks detect advertised mismatch; they do not cryptographically authenticate a server.
- Only `hive_whoami` and `hive_query` are callable through this client. `tools/list` is read for discovery. Future `hive_capabilities` is explicitly unavailable until S4's schema arrives.
- Flat input validation matches the current read schemas. It is not a general JSON Schema implementation.
- JSON-RPC replies must match the request ID and envelope. Oversized, malformed, duplicate-key and non-finite JSON are refused.
- Tool output uses the baseline JSON-text shape; absent truth values are preserved. The client does not mint evidence, normalize confidence or infer an Atom envelope.
- Error messages are stable local codes, with no provider error payload copied. No automatic retry follows transport failure.

An injected transport must itself bound reads, timeout, authenticate the designated destination, handle MCP session headers/lifecycle and prohibit redirects that could leak credentials. No such production transport is supplied yet. The client core is not a complete interoperable MCP harness, capability authorization service or proof that host query scope is enforced.

## Qualification boundary

The offline tests exercise the client with deliberately faulty synthetic responses. They verify client behaviour, not actual host dispatch, cross-principal denial, shared memory persistence, reasoning correctness or live capability discovery. The thirty S3 conformance cases remain planned and unexecuted.

Run the client checks from the workspace root:

```
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s hiveconnect/tests -v
```

The receipt in `evidence/baseline-client-l0.json` records the source pin, file hashes, command and outcome. No L1, L2 or L3 acceptance is claimed. No measured synergy or improvement is claimed; those require matched Bench baselines under D7/D8.

## Next required interface

Await Opus's S3 draft and S4 inventory schema. Bind the thirty conformance cases to their exact fields. Reuse OmegaAtom's envelope and validator rather than create a competing schema. Then qualify the actual host handler on an isolated PeTTa/ASGI fixture at L1, with explicit denial, binding, expiry and replay cases. Live 8700 acceptance remains L2 under the platform's restart hold and designated synthetic enrollment.

Cleaned: no clone, dependency install, runtime job, test database or Python bytecode created. Only small source, schema, test and evidence files remain.

## Draft r1 continuation

Read the supplied PLATFORM_S3_DRAFT_RESPONSE.md and PLATFORM_SEAM_CONTRACTS_DRAFT_20261004.md. The draft states all four seams are unimplemented and names are unfrozen. The thirty case specifications are bound to draft tool names, not reported as passing.

Added draft_client.py: read-only identity, capabilities, goal-get and evidence-query; structured-content handling; declared remote error codes; explicit host version/schema pins; inventory identity/status/policy distinction; no fallback to legacy JSON-text data. A separately supplied Atom snapshot is validated by OmegaAtom's own validator. Query rows are not silently converted into that snapshot. Explicit scopes and mutating tools remain refused until qualified.

Twenty-seven L0 checks now pass (13 baseline, 14 draft). Evidence: evidence/draft-r1-client-l0.json. The prototype input schemas, marker placement, null boot-receipt representation and partial inventory checks are unfrozen assumptions, detailed in an owner workspace record (not included). No production transport, full schema conformance, host authorization or live query is proven. The earlier baseline receipt is historical; its source pins predate the new error-handler extension.

## r2 continuation (current)

The seam amendments through r2.5 and accepted OmegaAtom envelope 0.1 supersede the r1 prototype assumptions above. The read-only draft client now includes tagged scopes, artifact/exhibit reads with required wire digests, exact retained revision checks, result._meta schema marker, explicit no-boot states and structured error handling. Query-page validation uses the owner's validator on explicitly supplied snapshots, with complete closure and page/end bounds; automatic wire projection awaits the published schema.

37 L0 checks pass (13 baseline, 24 draft). Current receipt: evidence/draft-r2-client-l0.json. All nine field questions are answered; remaining work is build-schema synchronization and actual L1 host qualification. Thirty updated host specifications remain unexecuted. Digest echo is not content-hash verification; synthetic revocation responses are not proof of host grant enforcement. See an owner workspace record (not included). No production transport or activation was added.

## r2.6 continuation (current)

Read Platform's 16:30Z reply and r2.6. Platform acknowledges the 37-check L0 receipt; S3 schemas remain queued for build publication. Four additional checks use Atom project_pages directly: withdrawal preservation, controls on controls, overflow refusal, and the limitation that a structurally valid page cannot reveal a host-omitted control. Total: 41 L0 checks (13 baseline, 28 draft), receipt evidence/draft-r26-client-l0.json.

Host cases now require the owner projection API, own-actor issuance, separately listed dynamic workflows and r2.6 typed request/idempotency fields. No host case or live access was exercised. Closure completeness remains a host assertion until tested against authenticated source data.

## 17:00Z security continuation

Platform reports 4aad53d deployed and accepts the r2.6 continuation. Read-only source review finds local HEAD b35b052 (later S5, not deployed) and unchanged baseline MCP source; S3/S4 and full schemas remain pending. No new client code or test run; latest executed client evidence remains 41 L0 checks. Updated host cases cover exact citations, restrictive/newer policy, high-risk standing refusal, bundle authority isolation, narrowed code capabilities and request-selected finding validators. See evidence/security-source-review.json and an owner workspace record (not included).
