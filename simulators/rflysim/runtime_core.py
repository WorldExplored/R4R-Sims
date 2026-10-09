"""Offline-tested supervision/evaluation primitives; no RflySim SDK adapter.

Normalized samples below are our contract, never assumed installed SDK fields.
Workers must not create subprocesses; only supervisor-owned handles are stopped.
"""
from dataclasses import dataclass
import ctypes
import json
import math
import multiprocessing as mp
from queue import Full
import time
from typing import Optional, Tuple


class DeadlineExceeded(RuntimeError):
    pass


class WorkerContext:
    def __init__(self, duration_s, call_s, active_call, operation, attempts, ready):
        self.duration_s = duration_s
        self.end = None
        self.call_s = call_s
        self.active_call = active_call
        self.sequence = 0
        self.operation = operation
        self.attempts = attempts
        self.ready = ready

    def call(self, name, function, *args, **kwargs):
        """Parent can kill a blocked worker; a returned late call also fails."""
        deadline = min(self.end, time.monotonic() + self.call_s)
        if deadline <= time.monotonic():
            raise DeadlineExceeded(name)
        self.operation.value = name.encode('utf-8')[:127]
        self.sequence += 1
        self.active_call.value = self.sequence
        try:
            result = function(*args, **kwargs)
            if time.monotonic() >= deadline:
                raise DeadlineExceeded(name)
            return result
        finally:
            self.active_call.value = 0

    def attempt(self, action):
        # Intent only. Neither a successful call nor acknowledgment confirms land.
        self.attempts.value |= {'land': 1, 'disarm': 2}[action]


def _worker(target, args, context, output, complete):
    context.end = time.monotonic() + context.duration_s
    try:
        while not context.ready.value:
            if time.monotonic() >= context.end:
                raise DeadlineExceeded('parent supervision not ready')
            time.sleep(0.001)
        report = {'status': 'returned', 'result': target(context, *args)}
        encoded = json.dumps(report, allow_nan=False).encode('utf-8')
    except BaseException as exc:
        report = {'status': 'error', 'error_type': type(exc).__name__, 'error': str(exc)}
        encoded = json.dumps(report).encode('utf-8')
    if len(encoded) >= len(output):
        encoded = b'{"status":"error","error":"worker report exceeds fixed buffer"}'
    output.value = encoded
    complete.value = 1  # Publish only after the small report is complete.


def _start(context, role, target, args, end, call_s, ready):
    active = context.RawValue(ctypes.c_uint, 0)
    operation = context.RawArray(ctypes.c_char, 128)
    attempts = context.RawValue(ctypes.c_uint, 0)
    output = context.RawArray(ctypes.c_char, 8192)
    complete = context.RawValue(ctypes.c_uint, 0)
    worker_context = WorkerContext(max(0, end - time.monotonic()), call_s, active, operation, attempts, ready)
    process = context.Process(target=_worker, args=(target, args, worker_context, output, complete),
                              name='rflysim-audit-' + role)
    process.start()
    return {'role': role, 'process': process, 'active': active, 'operation': operation,
            'attempts': attempts, 'output': output, 'complete': complete, 'reason': None,
            'seen_call': 0, 'call_deadline': None}


def _stop(job, reap_s):
    process = job['process']
    if process.is_alive():
        process.terminate()
    process.join(reap_s)
    if process.is_alive():
        process.kill()
        process.join(reap_s)
    # OS termination is not a flight/landing confirmation. Report survivors.
    return {'role': job['role'], 'pid': process.pid, 'exit_status': process.exitcode,
            'still_alive': process.is_alive(), 'stop_reason': job['reason'],
            'active_operation': job['operation'].value.decode('utf-8', 'replace'),
            'attempted_land': bool(job['attempts'].value & 1),
            'attempted_disarm': bool(job['attempts'].value & 2),
            'report': json.loads(job['output'].value) if job['complete'].value else None}


def run_phase(target, args=(), duration_s=75, call_s=2, auxiliaries=(),
              poll_s=0.01, reap_s=0.1, primary_role="control"):
    """Independent parent watchdog with separate capture/writer/GPU processes.

    auxiliaries is a sequence of (role, top-level function, arguments). A side
    worker timeout is recorded without stalling control. All targets must be
    spawn-safe and must not spawn children. No SDK is imported by this module.
    Phase budget starts before spawn; bounded reap overhead is reported separately.
    """
    if not all(math.isfinite(x) and x > 0 for x in (duration_s, call_s, poll_s, reap_s)):
        raise ValueError('positive finite phase/call/poll/reap limits required')
    if primary_role not in ('control', 'cleanup'):
        raise ValueError('primary role must be control or cleanup')
    if len({role for role, _, _ in auxiliaries}) != len(auxiliaries):
        raise ValueError('side worker roles must be unique')
    if len(auxiliaries) > 3 or any(role not in ('capture', 'writer', 'gpu')
                                 for role, _, _ in auxiliaries):
        raise ValueError('at most three named side workers')
    context = mp.get_context('spawn')
    start = time.monotonic()
    end = start + duration_s
    jobs = []
    ready = context.RawValue(ctypes.c_uint, 0)
    decision = None
    try:
        jobs.append(_start(context, primary_role, target, args, end, call_s, ready))
        for role, function, arguments in auxiliaries:
            jobs.append(_start(context, role, function, arguments, end, call_s, ready))
        ready.value = 1  # No callback/SDK work until parent enters monitoring loop.
        while True:
            now = time.monotonic()
            for job in jobs:
                if job['reason'] is not None:
                    continue
                if now >= end:
                    job['reason'] = 'phase_deadline'
                else:
                    active_call = job['active'].value
                    if active_call and active_call != job['seen_call']:
                        # Never compare absolute monotonic clocks across processes.
                        job['seen_call'] = active_call
                        job['call_deadline'] = now + call_s
                    if not active_call:
                        job['call_deadline'] = None
                    elif now >= job['call_deadline']:
                        job['reason'] = 'call_deadline'
                if job['reason'] is None and not job['process'].is_alive():
                    job['reason'] = 'worker_exited'
                if job['reason'] == 'call_deadline' and job is not jobs[0]:
                    if job['process'].is_alive():
                        job['process'].terminate()  # Reap after control stops, never delay its watchdog.
            if jobs[0]['reason'] is not None:
                decision = time.monotonic()
                break
            time.sleep(min(poll_s, max(0, end - time.monotonic())))
    finally:
        # No executable-name taskkill or unrelated process termination.
        records = []
        for job in jobs:
            if job['reason'] is None:
                job['reason'] = 'phase_finished'
            records.append(_stop(job, reap_s))
    return {'wall_s': time.monotonic() - start,
            'watchdog_decision_s': None if decision is None else decision - start,
            'budget_s': duration_s, 'poll_s': poll_s, 'reap_s_per_step': reap_s,
            'call_clock': 'parent elapsed since observed active token; at most one poll detection delay',
            'workers': records, 'landing_confirmation_source': 'telemetry evaluator only'}


def supervise(control, cleanup, args=(), cleanup_args=(), auxiliaries=(),
              flight_s=75, cleanup_s=15, call_s=2):
    """Cleanup gets its own budget and fresh worker even after blocked control."""
    try:
        flight = run_phase(control, args, flight_s, call_s, auxiliaries)
    except Exception as exc:
        flight = {'startup_error': type(exc).__name__, 'error': str(exc)}
    try:
        recovery = run_phase(cleanup, cleanup_args, cleanup_s, call_s, primary_role="cleanup")
    except Exception as exc:
        recovery = {'startup_error': type(exc).__name__, 'error': str(exc)}
    return {'flight': flight, 'cleanup': recovery,
            'landing_confirmed': 'not determined by process supervision'}


def offer(queue, record, counters, essential=False):
    """Control offers only prebuilt immutable metadata, never pixels or file I/O.

    Capture owns pixel copying; writer owns encoding/files; GPU worker owns polling.
    Essential telemetry/log overflow must invalidate the future measured run.
    """
    if not isinstance(record, bytes) or len(record) > 65536:
        raise ValueError('control metadata must be bytes <= 64 KiB')
    try:
        queue.put_nowait(record)
        counters['accepted'] = counters.get('accepted', 0) + 1
        return True
    except Full:
        counters['dropped'] = counters.get('dropped', 0) + 1
        if essential:
            counters['evidence_incomplete'] = True
        return False


@dataclass(frozen=True)
class Sample:
    # Mapping, units, timestamp ownership and origin must be verified in adapter.
    source_time_s: float
    received_monotonic_s: float
    position_ned_m: Tuple[float, float, float]
    velocity_ned_m_s: Tuple[float, float, float]
    state_source: str
    armed: Optional[bool]
    heartbeat_received_s: Optional[float]
    landed_on_ground: Optional[bool]
    landed_received_s: Optional[float]


class FlightEvaluation:
    def __init__(self, config, start_s, initial_ned_m, state_source):
        if state_source not in ('simulator_truth', 'px4_estimate'):
            raise ValueError('explicit verified state source required')
        self.b = config['B']
        self.end = start_s + config['limits']['flight_s']
        self.initial = initial_ned_m
        self.source = state_source
        self.next_leg = 1
        self.leg_start = start_s
        self.reached = []
        self.takeoff = False
        self.takeoff_s = None
        self.touchdown_s = None
        self.disarmed = False
        self.landing_request_s = None
        self.failed = None
        self.previous_source_time = None
        self.previous_receive = None
        self.dwell = {}
        self.events = []
        self.rejected = 0

    def request_landing(self, now):
        if (self.landing_request_s is None or
                (self.takeoff_s is not None and self.landing_request_s < self.takeoff_s)):
            self.landing_request_s = now
            self.dwell.pop('touchdown', None)
            self.events.append({'event': 'land_requested', 'monotonic_s': now})

    def _fresh(self, stamp, now):
        return stamp is not None and math.isfinite(stamp) and 0 <= now - stamp <= self.b['telemetry_stale_s']

    def _held(self, key, condition, now, duration):
        if not condition:
            self.dwell.pop(key, None)
            return False
        since = self.dwell.setdefault(key, now)
        return now - since >= duration

    def tick(self, now):
        # Invoke every control iteration even when no telemetry arrives.
        if self.failed is None and self.next_leg < len(self.b['route_ned_m']):
            if now >= self.end:
                self.failed = 'flight_deadline'
            elif now - self.leg_start > self.b['waypoint_deadline_s']:
                self.failed = 'waypoint_deadline'
        if self.previous_receive is not None and not self._fresh(self.previous_receive, now):
            self.dwell.clear()
        return self.summary()

    def update(self, now, sample):
        self.tick(now)
        finite = all(math.isfinite(x) for x in (*sample.position_ned_m,
                                               *sample.velocity_ned_m_s, sample.source_time_s))
        valid = (finite and len(sample.position_ned_m) == len(sample.velocity_ned_m_s) == 3
                 and sample.state_source == self.source and self._fresh(sample.received_monotonic_s, now)
                 and (self.previous_source_time is None or sample.source_time_s > self.previous_source_time)
                 and (self.previous_receive is None or sample.received_monotonic_s > self.previous_receive))
        if not valid:
            self.dwell.clear()
            self.rejected += 1
            return self.summary()
        if (self.previous_receive is not None and
                sample.received_monotonic_s - self.previous_receive > self.b['telemetry_stale_s']):
            self.dwell.clear()
        self.previous_source_time = sample.source_time_s
        self.previous_receive = sample.received_monotonic_s
        fresh_heartbeat = self._fresh(sample.heartbeat_received_s, now)
        airborne = (fresh_heartbeat and sample.armed is True and
                    self.initial[2] - sample.position_ned_m[2] >= self.b['takeoff_criterion']['height_above_initial_m'])
        if not self.takeoff and self._held('takeoff', airborne, now, self.b['takeoff_criterion']['continuous_s']):
            self.takeoff = True
            self.takeoff_s = now
            self.events.append({'event': 'takeoff_confirmed', 'monotonic_s': now})
        if (self.failed is None and self.next_leg < len(self.b['route_ned_m'])
                and self.landing_request_s is None):
            target = self.b['route_ned_m'][self.next_leg]
            error = math.sqrt(sum((a - b) ** 2 for a, b in zip(sample.position_ned_m, target)))
            held = self._held('waypoint', self.takeoff and fresh_heartbeat and sample.armed is True
                              and error <= self.b['waypoint_tolerance_m'], now, self.b['continuous_dwell_s'])
            if held:
                self.reached.append(self.next_leg)
                self.events.append({'event': 'waypoint_confirmed', 'leg': self.next_leg,
                                    'monotonic_s': now, 'position_error_m': error})
                self.next_leg += 1
                self.leg_start = now
                self.dwell.pop('waypoint', None)
        criterion = self.b['touchdown_criterion']
        after_request = (self.takeoff_s is not None and self.landing_request_s is not None
                         and self.landing_request_s >= self.takeoff_s
                         and sample.landed_received_s is not None
                         and sample.landed_received_s >= self.landing_request_s)
        grounded = (self.takeoff and after_request and sample.landed_on_ground is True
                    and self._fresh(sample.landed_received_s, now)
                    and math.sqrt(sum(v * v for v in sample.velocity_ned_m_s)) <= criterion['speed_norm_max_m_s'])
        if self.touchdown_s is None and self._held('touchdown', grounded, now, criterion['continuous_s']):
            self.touchdown_s = now
            self.events.append({'event': 'touchdown_confirmed', 'monotonic_s': now})
        if (self.touchdown_s is not None and grounded and fresh_heartbeat and sample.armed is False
                and sample.heartbeat_received_s >= self.touchdown_s and not self.disarmed):
            self.disarmed = True
            self.events.append({'event': 'disarmed_confirmed', 'monotonic_s': now})
        return self.summary()

    def summary(self):
        landed = self.touchdown_s is not None and self.disarmed
        return {'takeoff_confirmed': self.takeoff, 'reached_legs': list(self.reached),
                'touchdown_confirmed': self.touchdown_s is not None, 'disarmed_confirmed': self.disarmed,
                'landing_confirmed': landed,
                'minimum_integration_pass': self.takeoff and 2 in self.reached and 3 in self.reached and landed,
                'full_route_pass': self.reached == [1, 2, 3, 4] and landed and self.failed is None,
                'position_measurement_source': self.source,
                'ground_truth_outcome': 'evaluated' if self.source == 'simulator_truth' else 'blocked',
                'failure': self.failed, 'rejected_samples': self.rejected, 'events': list(self.events)}
