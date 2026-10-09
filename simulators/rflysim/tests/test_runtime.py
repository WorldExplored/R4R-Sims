"""Synthetic local tests only: no simulator, SDK, GPU, or flight validation."""
from dataclasses import replace
import json
import multiprocessing as mp
import os
from pathlib import Path
from queue import Queue
import sys
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from runtime_core import FlightEvaluation, Sample, offer, run_phase, supervise


def forever():
    while True:
        time.sleep(0.01)


def blocked_call(context):
    return context.call('synthetic_blocked_call', forever)


def blocked_phase(context):
    forever()  # Deliberately bypass call wrapper: parent phase limit still applies.


def quick_control(context):
    time.sleep(0.3)
    return {'synthetic': True}


def blocked_cleanup(context):
    context.attempt('land')
    context.call('synthetic_land_call', forever)


def error_control(context):
    raise RuntimeError('synthetic failure')


def reported_cleanup(context):
    context.attempt('land')
    return {'landing_confirmed': False, 'reason': 'no telemetry'}


def record_case(name, result):
    directory = os.environ.get('RFLYSIM_LOCAL_TEST_EVIDENCE')
    if directory:
        Path(directory, name + '.json').write_text(json.dumps({
            'kind': 'synthetic local test, not simulator validation', 'result': result
        }, indent=2) + '\n')


class SupervisionTests(unittest.TestCase):
    def test_blocked_call_has_independent_deadline_and_exit_status(self):
        result = run_phase(blocked_call, duration_s=2, call_s=0.2)
        record_case('blocked-call', result)
        worker = result['workers'][0]
        self.assertEqual(worker['stop_reason'], 'call_deadline')
        self.assertFalse(worker['still_alive'])
        self.assertIsNotNone(worker['exit_status'])
        self.assertGreaterEqual(result['watchdog_decision_s'], 0.2)
        self.assertLess(result['wall_s'], 1.5)  # Generous OS scheduling allowance.
        self.assertIsNone(worker['report'])

    def test_unwrapped_blocking_worker_and_cleanup_are_bounded(self):
        result = supervise(blocked_phase, blocked_cleanup, flight_s=0.5, cleanup_s=0.5, call_s=0.15)
        record_case('bounded-flight-and-cleanup', result)
        self.assertEqual(result['flight']['workers'][0]['stop_reason'], 'phase_deadline')
        cleanup = result['cleanup']['workers'][0]
        self.assertGreaterEqual(result['cleanup']['watchdog_decision_s'], 0.15)
        self.assertTrue(cleanup['attempted_land'])
        self.assertFalse(cleanup['attempted_disarm'])
        self.assertIsNone(cleanup['report'])
        self.assertEqual(result['landing_confirmed'], 'not determined by process supervision')
        self.assertLess(result['flight']['wall_s'] + result['cleanup']['wall_s'], 2.5)

    def test_capture_writer_gpu_blocking_does_not_block_control(self):
        sides = [(role, blocked_call, ()) for role in ('capture', 'writer', 'gpu')]
        result = run_phase(quick_control, duration_s=2, call_s=0.1, auxiliaries=sides)
        record_case('isolated-side-workers', result)
        self.assertEqual(result['workers'][0]['report']['status'], 'returned')
        self.assertTrue(all(w['stop_reason'] == 'call_deadline' for w in result['workers'][1:]))
        self.assertFalse(any(w['still_alive'] for w in result['workers']))

    def test_control_exception_still_attempts_cleanup(self):
        result = supervise(error_control, reported_cleanup, flight_s=2, cleanup_s=2)
        record_case('exception-cleanup', result)
        self.assertEqual(result['flight']['workers'][0]['report']['error_type'], 'RuntimeError')
        cleanup = result['cleanup']['workers'][0]
        self.assertTrue(cleanup['attempted_land'])
        self.assertFalse(cleanup['report']['result']['landing_confirmed'])

    def test_queue_pressure_is_nonblocking_and_counted(self):
        queue = Queue(maxsize=1)
        counts = {}
        self.assertTrue(offer(queue, b'first', counts))
        start = time.monotonic()
        for _ in range(10000):
            self.assertFalse(offer(queue, b'overflow', counts, essential=True))
        self.assertLess(time.monotonic() - start, 1)
        record_case('queue-pressure', counts)
        self.assertEqual(counts, {'accepted': 1, 'dropped': 10000, 'evidence_incomplete': True})
        with self.assertRaises(ValueError):
            offer(queue, b'x' * 65537, counts)

    def test_spawn_queue_pressure(self):
        queue = mp.get_context('spawn').Queue(maxsize=1)
        try:
            counts = {}
            self.assertTrue(offer(queue, b'one', counts))
            self.assertFalse(offer(queue, b'two', counts))
            self.assertEqual(counts['dropped'], 1)
            self.assertEqual(queue.get(timeout=1), b'one')  # Drain before closing feeder.
        finally:
            queue.close()
            queue.join_thread()


class EvaluationTests(unittest.TestCase):
    def setUp(self):
        self.config = json.loads((ROOT / 'audit-config.json').read_text())
        self.e = FlightEvaluation(self.config, 0, (0, 0, 0), 'simulator_truth')
        self.time = 0

    def sample(self, now, position=(0, 0, -2), armed=True, ground=False):
        return Sample(now, now, position, (0, 0, 0), 'simulator_truth', armed, now, ground, now)

    def hold(self, position, steps=36, armed=True, ground=False):
        for _ in range(steps):
            self.time += 0.1
            self.e.update(self.time, self.sample(self.time, position, armed, ground))

    def land(self):
        self.e.request_landing(self.time)
        self.hold((0, 0, 0), steps=24, armed=True, ground=True)
        self.hold((0, 0, 0), steps=1, armed=False, ground=True)

    def test_exact_route_full_pass_and_separate_minimum(self):
        for point in self.config['B']['route_ned_m'][1:]:
            self.hold(tuple(point))
        self.assertFalse(self.e.summary()['full_route_pass'])  # No landing yet.
        self.land()
        result = self.e.summary()
        record_case('synthetic-route-and-landing', result)
        self.assertTrue(result['full_route_pass'])
        self.assertTrue(result['minimum_integration_pass'])
        self.assertEqual(result['reached_legs'], [1, 2, 3, 4])

    def test_minimum_can_pass_without_full_route(self):
        for point in self.config['B']['route_ned_m'][1:4]:
            self.hold(tuple(point))
        self.land()
        self.assertTrue(self.e.summary()['minimum_integration_pass'])
        self.assertFalse(self.e.summary()['full_route_pass'])

    def test_stale_duplicate_future_and_wrong_source_do_not_advance(self):
        original = self.sample(0.1)
        self.e.update(0.1, original)
        self.e.update(0.2, original)  # Cached packet.
        self.e.update(2, original)  # Stale.
        self.e.update(2, self.sample(3))  # Future receipt.
        self.e.update(3, replace(self.sample(3), state_source='px4_estimate'))
        self.assertEqual(self.e.summary()['rejected_samples'], 4)
        self.assertFalse(self.e.summary()['takeoff_confirmed'])
        self.assertEqual(self.e.summary()['reached_legs'], [])

    def test_gap_and_outside_tolerance_break_continuous_dwell(self):
        self.hold((0, 0, -2), steps=15)
        self.time += 0.7
        self.hold((0, 0, -2), steps=10)
        self.assertEqual(self.e.reached, [])
        self.hold((0.3, 0, -2), steps=1)
        self.hold((0, 0, -2), steps=10)
        self.assertEqual(self.e.reached, [])
        self.hold((0, 0, -2), steps=12)
        self.assertEqual(self.e.reached, [1])

    def test_no_telemetry_leg_deadline(self):
        self.e.tick(12.1)
        self.assertEqual(self.e.summary()['failure'], 'waypoint_deadline')
        self.hold((0, 0, -2))
        self.assertEqual(self.e.reached, [])

    def test_false_landing_from_intent_initial_ground_or_stale_data(self):
        self.e.request_landing(0)
        self.hold((0, 0, 0), armed=False, ground=True)
        self.assertFalse(self.e.summary()['landing_confirmed'])
        self.hold((0, 0, -2))
        self.hold((0, 0, 0), armed=False, ground=True)
        self.assertFalse(self.e.summary()['landing_confirmed'])  # Preflight request cannot prove later landing.
        airborne = FlightEvaluation(self.config, 0, (0, 0, 0), 'simulator_truth')
        self.e = airborne
        self.time = 0
        self.hold((0, 0, -2))
        self.e.request_landing(self.time)
        for _ in range(30):
            self.time += 0.1
            stale = replace(self.sample(self.time, (0, 0, 0), False, True), landed_received_s=0)
            self.e.update(self.time, stale)
        self.assertFalse(self.e.summary()['landing_confirmed'])

    def test_touchdown_without_fresh_disarm_is_incomplete(self):
        self.hold((0, 0, -2))
        self.e.request_landing(self.time)
        self.hold((0, 0, 0), steps=24, ground=True)
        self.assertTrue(self.e.summary()['touchdown_confirmed'])
        self.assertFalse(self.e.summary()['landing_confirmed'])
        self.time += 0.1
        self.e.update(self.time, replace(self.sample(self.time, (0, 0, 0), False, True), heartbeat_received_s=0))
        self.assertFalse(self.e.summary()['landing_confirmed'])

    def test_estimated_state_is_not_truth(self):
        estimated = FlightEvaluation(self.config, 0, (0, 0, 0), 'px4_estimate')
        self.assertEqual(estimated.summary()['ground_truth_outcome'], 'blocked')


if __name__ == '__main__':
    unittest.main()
