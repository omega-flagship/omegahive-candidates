import copy
import unittest
from omegaatom import Refused, validate, sidecars
from omegagraft import validate_manifest, manifest_atoms, binding_graph, blast_radius, propose_swap
from omegagraft.wiring import digest

SLOTS = [{'id': s, 'family': 'synthetic', 'input_schema': 'a'*64,
          'result_schema': 'b'*64, 'suite': 'lab.synthetic.'+s} for s in ('lookup', 'summary')]


def manifest(mid, provides=(), needs=(), adaptor=False):
    return {'schema': 'omegagraft-plug/0.1', 'id': mid, 'version': '1.0',
            'provides': [{'slot': s, 'contract': digest(next(x for x in SLOTS if x['id']==s))} for s in provides],
            'consumes': [{'slot': s, 'contract': digest(next(x for x in SLOTS if x['id']==s)),
                         'mode': mode, 'primary': primary, 'fallbacks': list(fallbacks)} for s,mode,primary,fallbacks in needs],
            'effects': [], 'entrypoints': {'library': 'synthetic.module'},
            'source_pins': {'synthetic.py': 'c'*64}, 'licence': 'MIT', 'adaptor': adaptor}


def snapshot(manifests, extra=()):
    atoms = []
    for m in manifests:
        atoms.extend(manifest_atoms(m, SLOTS))
        for p in m['provides']:
            suite = next(s['suite'] for s in SLOTS if s['id']==p['slot'])
            atoms.append(['Conforms', m['id'], p['slot'], m['version'], digest(m), suite, 'pass'])
    return from_atoms(atoms + list(extra))


def from_atoms(atoms):
    records = []
    for i, a in enumerate(atoms, 1):
        eid = ['ev','synthetic',i]
        records.append({'id': eid, 'statement': a, 'source': {'owner': 'synthetic', 'subject': 'fixture',
                        'revision': 1, 'digest': digest(a)}, 'status': 'simulated', 'scope': 'synthetic',
                        'stamp': [eid], 'unknown': False, 'truth': ['stv',1,0.5]})
    return validate({'version': '0.1', 'owner': 'synthetic', 'scope': 'synthetic', 'revision': 1, 'records': records})


def basic():
    return snapshot([manifest('old', ['lookup']), manifest('backup',['lookup']), manifest('new',['lookup']),
                     manifest('required', ['summary'], [('lookup','required','old',[])]),
                     manifest('degrade', [], [('lookup','degrade','old',['backup'])]),
                     manifest('optional', [], [('lookup','optional','old',[])]),
                     manifest('downstream', [], [('summary','required','required',[])])])


class WiringTests(unittest.TestCase):
    def test_required_pauses_transitively(self):
        result = blast_radius(basic(), SLOTS, 'old')
        self.assertEqual(result['after']['modules']['required'], 'paused')
        self.assertEqual(result['after']['modules']['downstream'], 'paused')
        self.assertIn('downstream', result['affected'])

    def test_degrade_falls_back_exactly(self):
        result = blast_radius(basic(), SLOTS, 'old')['after']
        edge = next(e for e in result['edges'] if e['consumer']=='degrade')
        self.assertEqual((edge['provider'], edge['outcome']), ('backup','fallback'))
        self.assertEqual(result['modules']['degrade'], 'degraded')
        self.assertIn(['Unavailable','degrade','lookup','old','fallback'], result['absence_statements'])

    def test_optional_continues(self):
        after = blast_radius(basic(), SLOTS, 'old')['after']
        self.assertEqual(after['modules']['optional'], 'running')
        self.assertEqual(next(e['outcome'] for e in after['edges'] if e['consumer']=='optional'), 'omitted')

    def test_no_fallback_is_typed_unavailable(self):
        after = binding_graph(basic(), SLOTS, ['old','backup'])
        e = next(e for e in after['edges'] if e['consumer']=='degrade')
        self.assertIsNone(e['provider']); self.assertEqual(e['outcome'], 'unavailable')

    def test_missing_provider_is_honest(self):
        s = snapshot([manifest('c', [], [('lookup','required','missing',[])])])
        self.assertEqual(binding_graph(s,SLOTS)['modules']['c'], 'paused')

    def test_cycle_refused(self):
        s = snapshot([manifest('a',['lookup'],[('lookup','required','b',[])]),
                      manifest('b',['lookup'],[('lookup','optional','a',[])])])
        with self.assertRaisesRegex(Refused,'cyclic'):
            binding_graph(s,SLOTS)

    def test_latent_fallback_cycle_refused(self):
        s = snapshot([manifest('a',['lookup'],[('lookup','degrade','old',['b'])]),
                      manifest('b',['lookup'],[('lookup','required','a',[])]), manifest('old',['lookup'])])
        with self.assertRaisesRegex(Refused,'cyclic'):
            binding_graph(s,SLOTS)

    def test_adaptor_requires_target_suite_and_exact_pin(self):
        for field, value in ((5,'wrong-suite'),(4,'d'*64),(3,'2.0'),(6,'fail')):
            with self.subTest(field=field):
                s = snapshot([manifest('old',['lookup']),manifest('adaptor',['lookup'],adaptor=True),
                              manifest('c',[],[('lookup','required','old',[])])])
                r = next(r for r in s['records'] if r['statement'][:3]==['Conforms','adaptor','lookup'])
                r['statement'][field] = value
                with self.assertRaisesRegex(Refused,'conformance'):
                    propose_swap(s,SLOTS,'c','lookup','adaptor')
        s = snapshot([manifest('old',['lookup']),manifest('adaptor',['lookup'],adaptor=True),
                      manifest('c',[],[('lookup','required','old',[])])])
        self.assertEqual(propose_swap(s,SLOTS,'c','lookup','adaptor')['candidate']['kind'],'adaptor')

    def test_no_conformance_means_no_binding(self):
        s = basic(); s['records'] = [r for r in s['records'] if r['statement'][:3] != ['Conforms','old','lookup']]
        self.assertEqual(binding_graph(s,SLOTS)['modules']['required'], 'paused')

    def test_proposal_never_mints_grant_or_mutates_inputs(self):
        s = basic(); original = copy.deepcopy(s)
        p = propose_swap(s,SLOTS,'required','lookup','new')
        self.assertEqual(s,original); self.assertEqual(p['authority'],'none')
        self.assertEqual(p['rollback_target']['id'],'old')
        self.assertEqual(p['steps'][:2],['shadow','compare-with-Bench'])
        self.assertNotIn('grant',p); self.assertNotIn('approved',p)
        self.assertIn('owner-approval',p['steps'])
        p['candidate']['digest'] = 'e'*64
        self.assertEqual(s,original)

    def test_manifest_unknown_fields_and_bad_modes_refuse(self):
        m = manifest('c',[],[('lookup','required','old',[])])
        for key,value in (('grant',True),('authority','allow')):
            bad = dict(m,**{key:value})
            with self.assertRaises(Refused): validate_manifest(bad,SLOTS)
        m['consumes'][0]['mode'] = 'invent-answer'
        with self.assertRaises(Refused): validate_manifest(m,SLOTS)

    def test_contract_mismatch_refused(self):
        m = manifest('old',['lookup']); m['provides'][0]['contract'] = 'd'*64
        with self.assertRaisesRegex(Refused,'contract'): validate_manifest(m,SLOTS)
        s = basic(); next(r for r in s['records'] if r['statement'][0]=='Provides')['statement'][3]='e'*64
        with self.assertRaisesRegex(Refused,'contract'): binding_graph(s,SLOTS)

    def test_shared_validator_rejects_executable_atom_and_unknown_tv(self):
        for statement in (['eval',['bad']], ['Provides','old','lookup','$var']):
            s = basic(); s['records'][0]['statement'] = statement
            with self.assertRaises(Refused): binding_graph(s,SLOTS)
        s = basic(); s['records'][0]['unknown'] = True
        with self.assertRaises(Refused): binding_graph(s,SLOTS)

    def test_unknown_and_hypothetical_provides_are_not_available(self):
        for status in ('unknown','hypothetical','predicted'):
            s = basic(); r = next(r for r in s['records'] if r['statement'][:3]==['Provides','old','lookup'])
            if status=='unknown': r['unknown']=True; del r['truth']
            else: r['status']=status
            self.assertEqual(binding_graph(s,SLOTS)['modules']['required'],'paused')

    def test_retracted_conformance_withdraws_provider_and_restores(self):
        s = basic(); target = next(r['id'] for r in s['records'] if r['statement'][:3]==['Conforms','old','lookup'])
        atoms = [r['statement'] for r in s['records']]
        atoms.append(['Retracted',target,'synthetic-failure','synthetic',0])
        s = basic(); eid=['ev','synthetic',len(s['records'])+1]
        r=copy.deepcopy(s['records'][0]); r.update(id=eid,statement=atoms[-1],stamp=[eid],status='observed')
        s['records'].append(r)
        self.assertEqual(binding_graph(s,SLOTS)['modules']['required'],'paused')
        r2=copy.deepcopy(r); eid2=['ev','synthetic',len(s['records'])+1]
        r2.update(id=eid2,statement=['Retracted',eid,'restore','synthetic',1],stamp=[eid2])
        s['records'].append(r2)
        self.assertEqual(binding_graph(s,SLOTS)['modules']['required'],'running')

    def test_ambiguous_bound_refused(self):
        s=basic(); atoms=[r['statement'] for r in s['records']]+[['Bound','required','lookup','old'],['Bound','required','lookup','new']]
        with self.assertRaisesRegex(Refused,'ambiguous binding'): binding_graph(from_atoms(atoms),SLOTS)

    def test_explicit_binding_takes_precedence(self):
        s=basic(); atoms=[r['statement'] for r in s['records']]+[['Bound','required','lookup','new']]
        after=blast_radius(from_atoms(atoms),SLOTS,'old')['after']
        self.assertEqual(after['modules']['required'],'running')

    def test_swap_cycle_refused(self):
        s=snapshot([manifest('old',['lookup']),manifest('c',['summary'],[('lookup','required','old',[])]),
                    manifest('new',['lookup'],[('summary','required','c',[])])])
        with self.assertRaisesRegex(Refused,'cyclic'): propose_swap(s,SLOTS,'c','lookup','new')

    def test_permutation_invariance_and_no_input_mutation(self):
        s=basic(); before=copy.deepcopy(s); a=binding_graph(s,SLOTS)
        self.assertEqual(s,before)
        s['records'].reverse(); b=binding_graph(s,SLOTS)
        self.assertEqual(a['modules'],b['modules'])
        self.assertEqual(sorted(a['edges'],key=lambda e:e['consumer']),sorted(b['edges'],key=lambda e:e['consumer']))
        self.assertTrue(sidecars(s))

    def test_malformed_wiring_refuses_cleanly(self):
        for atom in (['Provides', ['nested'], 'lookup', 'a'*64],
                     ['Needs', 'required', 'lookup', digest(SLOTS[0]), 'degrade', 'old', {}],
                     ['Plug', 'old', '1', [], 'module']):
            with self.subTest(atom=atom):
                s=basic(); s['records'][0]['statement']=atom
                with self.assertRaises(Refused): binding_graph(s,SLOTS)
        s=basic(); r=copy.deepcopy(s['records'][0]); eid=['ev','synthetic',999]
        r.update(id=eid,stamp=[eid],statement=[['Unrelated'], 'data'])
        s['records'].append(r)
        self.assertEqual(binding_graph(s,SLOTS)['modules']['required'], 'running')

    def test_stale_derived_conformance_does_not_bind(self):
        s=basic()
        con=next(r for r in s['records'] if r['statement'][:3]==['Conforms','old','lookup'])
        premise=next(r for r in s['records'] if r['statement'][:2]==['Plug','backup'])
        con.update(premises=[premise['id']], rule=['synthetic-rule','1'], stamp=premise['stamp'])
        r=copy.deepcopy(premise); eid=['ev','synthetic',999]
        r.update(id=eid,stamp=[eid],status='observed',statement=['Retracted',premise['id'],'withdraw','synthetic',0])
        # Withdraw a premise that is not a structural Plug, preserving closure.
        premise['statement']=['Witness','synthetic-check']
        # Remove now-orphaned backup Provides and Conforms in this standalone case.
        s['records']=[x for x in s['records'] if not (x['statement'][0] in {'Provides','Conforms'} and x['statement'][1]=='backup')]
        s['records'].append(r)
        self.assertEqual(binding_graph(s,SLOTS)['modules']['required'],'paused')

    def test_paused_fallback_is_not_selected(self):
        s=snapshot([manifest('old',['lookup']),
                    manifest('backup',['lookup'],[('summary','required','missing',[])]),
                    manifest('c',[],[('lookup','degrade','old',['backup'])])])
        after=blast_radius(s,SLOTS,'old')['after']
        self.assertEqual(next(e['outcome'] for e in after['edges'] if e['consumer']=='c'), 'unavailable')

    def test_unplug_unknown_module_refused(self):
        with self.assertRaisesRegex(Refused,'unknown unplug'): blast_radius(basic(),SLOTS,'typo')


if __name__ == '__main__':
    unittest.main()
