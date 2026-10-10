"""Bounded advisory detectors. No host actions or automatic collection."""
from collections import defaultdict
from dataclasses import dataclass
import math
from omegaatom.envelope import digest, validate

@dataclass(frozen=True)
class Event:
    id: str
    subject: str
    kind: str  # action, replan, message
    signature: str
    outcome: str | None = None
    progress: str | None = None  # caller's complete scoped state-delta digest
    room: str = "default"
    tier: str = "Murmur"
    decision: bool = False
    requested_cadence: bool = False


def findings(events):
    """At most 120 unique supplied observations, in chronological order.

    Digests are supplied witnesses, not verified custody. Unknown outcomes or
    progress never establish a loop/stall. Findings are hypotheses, not verdicts.
    """
    events = list(events)
    if len(events) > 120 or len({e.id for e in events}) != len(events):
        raise ValueError("bounded unique event window required")
    for e in events:
        if e.kind not in {"action", "replan", "message"}:
            raise ValueError("unsupported event kind")
        if any(not isinstance(v, str) or not v or len(v) > 256
               for v in (e.id, e.subject, e.signature, e.room, e.tier)):
            raise ValueError("bounded nonempty metadata required")
        if any(v is not None and (not isinstance(v, str) or not v or len(v) > 256)
               for v in (e.outcome, e.progress)):
            raise ValueError("invalid witness")
        if type(e.decision) is not bool or type(e.requested_cadence) is not bool:
            raise ValueError("explicit boolean controls required")
    groups = defaultdict(list)
    # Last 12 events per subject; another subject's activity cannot mask a loop.
    subjects = defaultdict(list)
    for e in events:
        subjects[e.subject].append(e)
    for subject_events in subjects.values():
        for e in subject_events[-12:]:
            if e.kind in {"action", "replan"}:
                groups[(e.kind, e.subject, e.signature)].append(e)
    results = []
    def add(kind, subject, evidence, correction):
        signature = digest([kind, subject, evidence[-1].signature])
        results.append(dict(kind=kind, subject=subject, signature=signature,
                            evidence=[e.id for e in evidence], correction=correction,
                            status="hypothetical", authority="advice-only"))
    for (kind, subject, signature), group in groups.items():
        # Only the trailing run counts: changed/unknown outcomes break the run.
        run = []
        for e in group:
            if e.outcome is None or e.progress is None:
                run = []
            elif run and (e.outcome, e.progress) != (run[-1].outcome, run[-1].progress):
                run = [e]
            else:
                run.append(e)
        if len(run) >= 3:
            add("loop" if kind == "action" else "stall", subject, run,
                "Check the repeated outcome; change approach or request focused help.")
    messages = defaultdict(list)
    for e in events:
        if e.kind == "message":
            key = (e.subject, e.room, e.signature)
            # Protected notices and requested cadence break the candidate run.
            if e.decision or e.requested_cadence or e.tier not in {"Murmur", "Beat"}:
                messages[key] = []
            else:
                messages[key].append(e)
    for (subject, room, signature), group in messages.items():
        if len(group) >= 3:
            add("spam", subject, group,
                "Offer one digest of repeated low-information updates; preserve decisions and urgent notices.")
    return results


def pressure(*, sessions, swap_used, swap_total, session_cap=10, rss=None):
    """Caller-supplied machine sample; does not inspect processes or pause them."""
    if type(sessions) is not int or sessions < 0 or type(session_cap) is not int or session_cap < 1:
        raise ValueError("invalid session count/cap")
    for n in (swap_used, swap_total):
        if type(n) not in (int, float) or not math.isfinite(n) or n < 0:
            raise ValueError("invalid swap sample")
    if swap_used > swap_total:
        raise ValueError("used exceeds total")
    if rss is not None and any(type(n) is not int or n < 0 for n in rss.values()):
        raise ValueError("invalid RSS sample")
    ratio = swap_used / swap_total if swap_total else None
    if sessions <= session_cap and (ratio is None or ratio < .8):
        return []
    return [dict(kind="pressure", status="hypothetical", authority="advice-only",
                 sessions=sessions, swap_ratio=ratio, rss=rss,
                 correction="Review resource pressure and identify idle sessions with their owners before proposing pauses.")]


def envelope(events, candidates, *, scope, revision, sequence=1):
    """Closed canonical D2 proposal, validated with OmegaAtom's existing API.

    Source leaves describe supplied metadata; candidates have unknown truth.
    Reuse this snapshot on replay rather than minting new observation IDs.
    Host authentication and admission remain external.
    """
    records = []
    ids = {}
    for e in events:
        eid = ["ev", "omegachill", sequence]; sequence += 1
        ids[e.id] = eid
        statement = ["ChillTrace", e.subject, e.id, e.kind, e.signature,
                     e.outcome or "unknown", e.progress or "unknown"]
        records.append(dict(id=eid, statement=statement, source=dict(
            owner="omegachill", subject=e.subject, revision=revision,
            digest=digest(e.__dict__)), status="observed", scope=scope,
            stamp=[eid], unknown=True))
    for candidate in candidates:
        eid = ["ev", "omegachill", sequence]; sequence += 1
        premises = [ids[ref] for ref in candidate["evidence"]]
        records.append(dict(id=eid,
            statement=["ChillFinding", candidate["subject"], candidate["kind"], candidate["signature"]],
            source=dict(owner="omegachill", subject=candidate["subject"], revision=revision,
                        digest=digest(candidate)), status="hypothetical", scope=scope,
            stamp=sorted(premises, key=lambda p: p[2]), unknown=True,
            premises=premises, rule=["chill-window", "0.1"]))
    return validate(dict(version="0.1", owner="omegachill", scope=scope,
                         revision=revision, records=records))


class Gate:
    """Explicit caller-owned, in-memory cooldown and notification allowance.

    Feedback is retained as advisory evidence, never automatic NAL learning.
    Caller persists state and supplies monotonic seconds if needed.
    """
    def __init__(self, cooldown=300, allowance=5):
        if type(cooldown) not in (int, float) or not math.isfinite(cooldown) or cooldown < 0:
            raise ValueError("invalid cooldown")
        if type(allowance) is not int or allowance < 0:
            raise ValueError("invalid allowance")
        self.cooldown, self.remaining = cooldown, allowance
        self.seen, self.feedback = {}, []
        self.clock = -1

    def offer(self, candidate, now):
        if type(now) not in (int, float) or not math.isfinite(now) or now < self.clock:
            raise ValueError("monotonic finite time required")
        self.clock = now
        signature = candidate["signature"]
        if not self.remaining or now - self.seen.get(signature, -math.inf) < self.cooldown:
            return False
        self.seen[signature] = now
        self.remaining -= 1
        return True

    def respond(self, signature, answer):
        if signature not in self.seen or answer not in {"acknowledge", "dismiss"}:
            raise ValueError("known finding and explicit answer required")
        item = {"signature": signature, "answer": answer}
        if item not in self.feedback:
            self.feedback.append(item)
