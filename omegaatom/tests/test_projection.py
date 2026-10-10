import pytest
from omegaatom import Refused, project, lineage_state
from test_envelope import chain, retract, ev


def test_projection_keeps_ancestors_and_withdrawal_controls():
    s = chain()
    s["records"].append(retract(5, 1))
    shown = project(s, [ev(3)])
    assert {tuple(r["id"]) for r in shown["records"]} == {tuple(ev(n)) for n in (1, 2, 3, 5)}
    assert next(r for r in lineage_state(shown) if r["id"] == ev(3))["stale"]


def test_projection_keeps_retraction_of_retraction_and_independent_controls():
    s = chain()
    s["records"].extend([retract(5, 1), retract(6, 5), retract(7, 1)])
    shown = project(s, [ev(3)])
    assert {r["id"][2] for r in shown["records"]} == {1, 2, 3, 5, 6, 7}
    assert next(r for r in lineage_state(shown) if r["id"] == ev(3))["stale"]


def test_independent_projection_does_not_disclose_other_records():
    s = chain()
    s["records"].append(retract(5, 1))
    assert [r["id"] for r in project(s, [ev(4)])["records"]] == [ev(4)]
    assert project(s, [])["records"] == []


def test_retained_revision_data_remains_detached():
    s = chain()
    shown = project(s, [ev(3)])
    shown["records"][0]["statement"].append("changed")
    assert s == chain()


@pytest.mark.parametrize("roots", [[ev(99)], [ev(1), ev(1)], [["ev", "%", 1]]])
def test_missing_duplicate_and_pattern_roots_refused(roots):
    with pytest.raises(Refused):
        project(chain(), roots)


def test_closure_exhaustion_is_all_or_error():
    s = chain()
    with pytest.raises(Refused, match="partial lineage"):
        project(s, [ev(3)], record_limit=2)
    assert project(s, [ev(3)], record_limit=3)["revision"] == s["revision"]


def test_pages_preserve_closed_groups_and_terminal_flag():
    from omegaatom import project_pages
    s = chain()
    s["records"].append(retract(5, 1))
    pages = project_pages(s, [ev(3), ev(4)], record_limit=4)
    assert len(pages) == 2
    assert [p["result_complete"] for p in pages] == [False, True]
    assert all(p["closure_complete"] for p in pages)
    assert next(r for r in lineage_state(pages[0]["snapshot"]) if r["id"] == ev(3))["stale"]
    assert [r["id"] for r in pages[1]["snapshot"]["records"]] == [ev(4)]


def test_pages_deduplicate_shared_ancestry_without_dropping_roots():
    from omegaatom import project_pages
    pages = project_pages(chain(), [ev(2), ev(3)], record_limit=3)
    assert len(pages) == 1
    assert {r["id"][2] for r in pages[0]["snapshot"]["records"]} == {1, 2, 3}


def test_later_oversized_group_refuses_whole_result():
    from omegaatom import project_pages
    with pytest.raises(Refused, match="partial lineage"):
        project_pages(chain(), [ev(4), ev(3)], record_limit=2)


def test_empty_query_has_complete_empty_page():
    from omegaatom import project_pages
    page, = project_pages(chain(), [])
    assert page["snapshot"]["records"] == []
    assert page["result_complete"] and page["closure_complete"]


@pytest.mark.parametrize("bound", [0, 201, True])
def test_query_page_bound_matches_host_contract(bound):
    from omegaatom import project_pages
    with pytest.raises(Refused):
        project_pages(chain(), [ev(4)], record_limit=bound)
