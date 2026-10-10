"""Supervised prerequisite relation extraction; bounded explicit interpreter."""
import re
from .core import Refused

_ID = re.compile(r'[A-Za-z][A-Za-z0-9_-]{0,63}\Z')
_RULE = re.compile(r'\(= \(prerequisite-for ([A-Za-z][A-Za-z0-9_-]{0,63})\) ([A-Za-z][A-Za-z0-9_-]{0,63})\)\Z')


def ids(values):
    if type(values) is not list or len(values) > 128 or any(type(x) is not str or not _ID.fullmatch(x) for x in values) or len(set(values)) != len(values):
        raise Refused('bounded unique identifiers required')
    return set(values)


def learn(episodes, track_record_refs):
    if type(episodes) is not list or not 2 <= len(episodes) <= 128:
        raise Refused('two or more bounded episodes required')
    relations = {}
    for e in episodes:
        if type(e) is not dict or set(e) != {'action', 'required', 'available', 'missing'} or type(e['action']) is not str or not _ID.fullmatch(e['action']):
            raise Refused('episode shape required')
        required, available, missing = (ids(e[k]) for k in ('required', 'available', 'missing'))
        if not required or missing != required - available:
            raise Refused('inconsistent prerequisite observation')
        if e['action'] in relations and relations[e['action']] != required:
            raise Refused('conflicting action requirements')
        relations[e['action']] = required
    if type(track_record_refs) is not list or not track_record_refs or any(type(r) is not str or not r for r in track_record_refs):
        raise Refused('source track record required')
    return {'rules': [f'(= (prerequisite-for {a}) {p})' for a in sorted(relations) for p in sorted(relations[a])],
            'procedure': {'id':'check-learned-prerequisites', 'steps':['validate-vocabulary','resolve-known-actions','subtract-available','return-sorted-missing'],
                          'prerequisites':['explicit-owner-episodes','current-source-eligibility','supported-action-vocabulary']},
            'track_record_refs': list(track_record_refs)}


def check(content, prompt):
    if type(prompt) is not dict or set(prompt) != {'case', 'prerequisite_ids'}:
        raise Refused('Bench prompt shape required')
    vocabulary = ids(prompt['prerequisite_ids'])
    case = prompt['case']
    if type(case) is not dict or set(case) != {'actions', 'available'}:
        raise Refused('approved action/availability case required')
    actions, available = ids(case['actions']), ids(case['available'])
    if not available <= vocabulary:
        raise Refused('availability outside vocabulary')
    if type(content) is not dict or type(content.get('rules')) is not list or not 1 <= len(content['rules']) <= 16384:
        raise Refused('bounded declarative rules required')
    relations = {}
    for rule in content['rules']:
        match = _RULE.fullmatch(rule) if type(rule) is str else None
        if not match:
            raise Refused('unsupported prerequisite rule')
        a,p = match.groups()
        relations.setdefault(a,set()).add(p)
    if not actions <= relations.keys():
        raise Refused('unseen action')
    required = set().union(*(relations[a] for a in actions))
    if not required <= vocabulary:
        raise Refused('requirements outside vocabulary')
    return sorted(required - available)
