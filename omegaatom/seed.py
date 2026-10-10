"""Read Root's exact declarative seed wrappers as DATA, never execute them.

Caller supplies source text and pins. I/O and custody remain caller-owned.
Original Provides/Needs/Source and IntegrationProposal vocabulary is retained.
"""
import hashlib
import json
import re
from .envelope import require, validate, inert_atom

LEX = re.compile(r'\s+|;[^\n]*|"(?:\\.|[^"\\])*"|[()]|[^\s()]+')
SPACES = {"&omega-knowledge", "&omega-intent", "&omega-evidence"}


def _forms(text):
    require(isinstance(text, str) and len(text.encode()) <= 2_000_000, "seed byte bound exceeded")
    tokens = [m.group() for m in LEX.finditer(text) if not m.group().isspace() and not m.group().startswith(";")]
    require(len(tokens) <= 50000, "seed token bound exceeded")
    cursor = 0
    def parse(depth=0):
        nonlocal cursor
        require(depth <= 32 and cursor < len(tokens), "invalid seed depth/end")
        token = tokens[cursor]
        cursor += 1
        if token == "(":
            result = []
            while cursor < len(tokens) and tokens[cursor] != ")":
                result.append(parse(depth + 1))
            require(cursor < len(tokens), "unclosed seed expression")
            cursor += 1
            return result
        require(token != ")", "unexpected close")
        if token.startswith('"'):
            return json.loads(token)
        if re.fullmatch(r"[0-9]+", token):
            return int(token)
        return token
    result = []
    while cursor < len(tokens):
        # Only this seed's bang wrappers are recognized, then unwrapped as data.
        require(tokens[cursor] == "!", "seed requires exact declarative wrapper")
        cursor += 1
        result.append(parse())
    return result


def adapt_seed(sources, *, owner="omega-reason-seed", scope="synthetic-seed"):
    """sources: filename -> {text, digest}. Hash verification is local, not authority."""
    require(isinstance(sources, dict) and bool(sources) and len(sources) <= 3, "invalid seed sources")
    records = []
    for name in sorted(sources):
        supplied = sources[name]
        require(isinstance(supplied, dict) and set(supplied) == {"text", "digest"}, "invalid seed source")
        actual = hashlib.sha256(supplied["text"].encode()).hexdigest()
        require(actual == supplied["digest"], "seed hash drift")
        declared = set()
        for position, form in enumerate(_forms(supplied["text"]), 1):
            require(isinstance(form, list) and bool(form), "invalid seed wrapper")
            if form[0] == "bind!":
                require(len(form) == 3 and isinstance(form[1], str) and form[1] in SPACES and form[2] == ["new-space"], "unsupported seed binding")
                require(form[1] not in declared, "duplicate seed binding")
                declared.add(form[1])
                continue
            require(len(form) == 3 and form[0] == "add-atom" and isinstance(form[1], str) and form[1] in declared, "unsupported seed command")
            statement = form[2]
            inert_atom(statement)
            n = len(records) + 1
            records.append({"id": ["ev", owner, n], "statement": statement,
                            "source": {"owner": owner, "subject": f"{name}:{position}", "revision": 0, "digest": actual},
                            "status": "borrowed-prior", "scope": scope, "stamp": [["ev", owner, n]], "unknown": True})
    return validate({"version": "0.1", "owner": owner, "scope": scope, "revision": 0, "records": records})
