"""Data-only query closure, including withdrawal controls. No grants/cursors."""
import copy
from .envelope import validate, evidence_id, lineage_state, require


def project(snapshot, roots, *, record_limit=200):
    """Project admitted same-scope data without losing retraction state.

    Host selects roots after authenticating scope/grant. Overflow refuses,
    never returns partial lineage. This is one closure group, not pagination.
    """
    snapshot = validate(snapshot)
    require(type(record_limit) is int and 0 < record_limit <= 1000, "invalid projection record bound")
    require(isinstance(roots, list) and len(roots) <= 1000, "invalid projection roots")
    keys = [evidence_id(e) for e in roots]
    require(len(set(keys)) == len(keys), "duplicate projection root")
    index = {evidence_id(r["id"]): r for r in snapshot["records"]}
    require(all(k in index for k in keys), "missing projection root")
    retractors = {}
    for k, r in index.items():
        if r["statement"][0] == "Retracted":
            retractors.setdefault(evidence_id(r["statement"][1]), []).append(k)
    retained = set()
    pending = list(keys)
    while pending:
        key = pending.pop()
        if key in retained:
            continue
        retained.add(key)
        require(len(retained) <= record_limit, "closure group exceeds record bound; partial lineage refused")
        r = index[key]
        pending.extend(evidence_id(p) for p in r.get("premises", []))
        if r["statement"][0] == "Retracted":
            pending.append(evidence_id(r["statement"][1]))
        pending.extend(retractors.get(key, []))
    result = copy.deepcopy(snapshot)
    result["records"] = [copy.deepcopy(index[k]) for k in sorted(retained)]
    result = validate(result)
    # Internal guarantee: roots retain exact withdrawal/staleness/cause state.
    full = {evidence_id(s["id"]): s for s in lineage_state(snapshot)}
    shown = {evidence_id(s["id"]): s for s in lineage_state(result)}
    require(all(full[k] == shown[k] for k in retained), "projection changed lineage state")
    return result


def project_pages(snapshot, roots, *, record_limit=200):
    """Pack authorized roots into closed pages; no transport cursor or grant.

    A root's complete group never splits. Shared ancestors are deduplicated
    within a page and may recur on different pages. All groups are checked
    before results return, so overflow cannot leak an earlier partial result.
    """
    snapshot = validate(snapshot)
    require(type(record_limit) is int and 0 < record_limit <= 200, "invalid query page bound")
    require(isinstance(roots, list) and len(roots) <= 1000, "invalid projection roots")
    keys = [evidence_id(e) for e in roots]
    require(len(set(keys)) == len(keys), "duplicate projection root")
    groups = [project(snapshot, [root], record_limit=record_limit) for root in roots]
    pages, accumulated = [], {}
    def flush():
        page = copy.deepcopy(snapshot)
        page["records"] = [accumulated[k] for k in sorted(accumulated)]
        pages.append(validate(page))
    for group in groups:
        records = {evidence_id(r["id"]): r for r in group["records"]}
        if accumulated and len(set(accumulated) | set(records)) > record_limit:
            flush()
            accumulated = {}
        accumulated.update(records)
    if accumulated or not pages:
        flush()
    return [{"snapshot": page, "closure_complete": True, "result_complete": i == len(pages) - 1}
            for i, page in enumerate(pages)]
