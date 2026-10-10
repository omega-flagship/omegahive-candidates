import unittest
from omegachill import Event, findings, envelope, Gate, pressure

class ChillTests(unittest.TestCase):
    def events(self, kind='action', **kw):
        return [Event(str(i), 'agent1', kind, 'sig', outcome='same', progress='r1', **kw) for i in range(3)]
    def test_loop_and_closed_envelope(self):
        events = self.events(); f = findings(events)
        self.assertEqual(f[0]['kind'], 'loop')
        snapshot = envelope(events, f, scope='synthetic', revision=1)
        self.assertEqual(len(snapshot['records']), 4)
        self.assertTrue(all(r['unknown'] for r in snapshot['records']))
    def test_learning_breaks_loop(self):
        events = self.events(); events[-1] = Event('2', 'agent1', 'action', 'sig', 'new', 'r2')
        self.assertEqual(findings(events), [])
    def test_unknown_not_loop(self):
        self.assertEqual(findings([Event(str(i), 'agent1', 'action', 'sig') for i in range(3)]), [])
    def test_replay_and_bound_refused(self):
        with self.assertRaises(ValueError): findings([self.events()[0]] * 3)
        with self.assertRaises(ValueError): findings([Event(str(i), 'a', 'action', 's') for i in range(121)])
    def test_stall(self):
        self.assertEqual(findings(self.events('replan'))[0]['kind'], 'stall')
    def test_spam_and_protection(self):
        self.assertEqual(findings(self.events('message'))[0]['kind'], 'spam')
        for kw in ({'decision': True}, {'tier': 'Breach'}, {'tier': 'Bloom'}, {'requested_cadence': True}, {'tier':'unknown'}):
            self.assertEqual(findings(self.events('message', **kw)), [])
    def test_feedback_cooldown_budget(self):
        f = findings(self.events())[0]; gate = Gate(cooldown=10, allowance=2)
        self.assertTrue(gate.offer(f, 0)); self.assertFalse(gate.offer(f, 9))
        gate.respond(f['signature'], 'dismiss'); gate.respond(f['signature'], 'dismiss')
        self.assertEqual(len(gate.feedback), 1)
        self.assertTrue(gate.offer(f, 10)); self.assertFalse(gate.offer(f, 20))
        with self.assertRaises(ValueError): gate.offer(f, 19)
    def test_pressure_unknown_and_invalid(self):
        self.assertEqual(pressure(sessions=2, swap_used=0, swap_total=0), [])
        self.assertEqual(len(pressure(sessions=11, swap_used=0, swap_total=0)), 1)
        self.assertEqual(len(pressure(sessions=3, swap_used=86, swap_total=92)), 1)
        with self.assertRaises(ValueError): pressure(sessions=2, swap_used=float('nan'), swap_total=1)

if __name__ == '__main__': unittest.main()
