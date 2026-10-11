"""Bounded installed-SDK SITL adapter. No automatic parameter changes.

Canonical SDK hashes are checked before import. Raw MAVLink reception belongs to
this adapter; InitMavLoop/initOffboard/SendMavArm are deliberately not called.
"""
import argparse
import hashlib
import json
import math
import multiprocessing as mp
from pathlib import Path
from queue import Empty
import sys
import time

from runtime_core import FlightEvaluation, Sample, offer, run_phase

SDK_HASH = 'e1aab5b0f8ef30fd70bb4ba41da50e8d4dc936068763945a047c404d807a17f8'


def evidence_value(value):
    """Preserve nonfinite telemetry explicitly without invalid JSON."""
    if isinstance(value, float) and not math.isfinite(value):
        return {'nonfinite': str(value)}
    if isinstance(value, (bytes, bytearray)):
        return {'bytes_hex': value.hex()}
    if isinstance(value, dict):
        return {k: evidence_value(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [evidence_value(v) for v in value]
    return value


def emit(queue, counters, kind, **data):
    record = {'kind': kind, 'monotonic_s': time.monotonic(),
              'utc_unix_s': time.time(), **data}
    offer(queue, json.dumps(evidence_value(record), allow_nan=False).encode(), counters, essential=True)


class Link:
    def __init__(self, ctx, install, queue):
        self.ctx, self.queue, self.counters = ctx, queue, {}
        sdk = Path(install) / 'RflySimAPIs' / 'RflySimSDK'
        path = sdk / 'ctrl' / 'PX4MavCtrlV4.py'
        if hashlib.sha256(path.read_bytes()).hexdigest() != SDK_HASH:
            raise ValueError('canonical installed SDK changed; inspect before use')
        sys.path.insert(0, str(sdk))
        from ctrl.PX4MavCtrlV4 import PX4MavCtrler
        from pymavlink import mavutil
        self.m = mavutil.mavlink
        self.sdk = ctx.call('SDK constructor', PX4MavCtrler, 1, '127.0.0.1')
        # Matches installed InitMavLoop transport, without its thread/disarm side effect.
        self.conn = ctx.call('open local MAVLink', mavutil.mavlink_connection,
                             'udpin:127.0.0.1:20101')
        self.sdk.the_connection = self.conn
        self.sdk.UDPMode = 2
        self.sdk.startTime = time.time()
        self.conn.target_system, self.conn.target_component = 1, 1
        self.hb = self.landed = self.pos = None
        self.hb_t = self.landed_t = self.pos_t = None
        self.acks = []
        self.last_source_ms = None
        self.last_new_sample_t = None
        self.telemetry_gaps = []
        self.next_hb_request = 0

    def command(self, command, *params):
        emit(self.queue, self.counters, 'command', command=command, params=params)
        self.ctx.call('command_long', self.sdk.SendMavCmdLong, command, *params)

    def read(self):
        # HEARTBEAT is a fixed 1Hz stream on this installed firmware. Request a
        # newly emitted message at 5Hz; do not reinterpret old heartbeats as fresh.
        now = time.monotonic()
        if now >= self.next_hb_request:
            self.command(512, 0)
            self.next_hb_request = now + .2
        # Nonblocking calls; parent enforces 2s per SDK/transport call.
        for _ in range(80):
            msg = self.ctx.call('MAVLink nonblocking receive', self.conn.recv_match,
                                blocking=False)
            if msg is None:
                break
            now = time.monotonic()
            kind = msg.get_type()
            data = msg.to_dict()
            if kind == 'BAD_DATA':
                emit(self.queue, self.counters, 'bad_mavlink', representation=str(msg))
                continue
            emit(self.queue, self.counters, 'mavlink', message=data,
                 source_system=msg.get_srcSystem(), source_component=msg.get_srcComponent())
            if msg.get_srcSystem() != 1 or msg.get_srcComponent() != 1:
                continue
            if kind == 'HEARTBEAT':
                self.hb, self.hb_t = data, now
            elif kind == 'EXTENDED_SYS_STATE':
                self.landed, self.landed_t = data, now
            elif kind == 'COMMAND_ACK':
                self.acks.append({'received_s': now, **data})
                self.acks = self.acks[-30:]
            elif kind == 'LOCAL_POSITION_NED':
                if self.last_source_ms is None or data['time_boot_ms'] > self.last_source_ms:
                    if self.last_new_sample_t is not None:
                        self.telemetry_gaps.append(now - self.last_new_sample_t)
                    self.last_new_sample_t = now
                    self.last_source_ms = data['time_boot_ms']
                    self.pos, self.pos_t = data, now

    def sample(self):
        if self.pos is None:
            return None
        p = self.pos
        return Sample(p['time_boot_ms'] / 1000.0, self.pos_t,
                      tuple(p[k] for k in ('x', 'y', 'z')),
                      tuple(p[k] for k in ('vx', 'vy', 'vz')), 'px4_estimate',
                      None if self.hb is None else bool(self.hb['base_mode'] & 128),
                      self.hb_t, None if self.landed is None else self.landed['landed_state'] == 1,
                      self.landed_t)

    def fresh(self, now):
        return all(t is not None and 0 <= now-t <= .5
                   for t in (self.pos_t, self.hb_t, self.landed_t))

    def request_streams(self):
        # MAV_CMD_SET_MESSAGE_INTERVAL: requested 20Hz position, 5Hz landed and heartbeat.
        for message_id, us in [(32, 50000), (245, 200000), (0, 200000)]:
            self.command(511, message_id, us)

    def setpoint(self, pos):
        self.ctx.call('SendPosNED', self.sdk.SendPosNED, *pos, 0)
        emit(self.queue, self.counters, 'setpoint', position_ned_m=pos, yaw_rad=0)
        s = self.sdk
        self.ctx.call('sendMavOffboardAPI', s.sendMavOffboardAPI, s.type_mask,
                      s.coordinate_frame, s.pos, s.vel, s.acc, s.yaw, s.yawrate)

    def close(self):
        self.conn.close()
        for name in ('udp_socket', 'udp_socketUDP', 'udp_socketTrue', 'udp_socketPX4', 'udp_socketUE4'):
            getattr(self.sdk, name).close()

    def report(self):
        return {'heartbeat': self.hb, 'landed': self.landed, 'position': self.pos,
                'acks': self.acks, 'telemetry_gap_max_s': max(self.telemetry_gaps, default=None),
                'evidence_queue': self.counters}


def writer(ctx, path, queue):
    with open(path, 'ab', buffering=0) as out:
        while time.monotonic() < ctx.end:
            try:
                value = queue.get(timeout=.05)
            except Empty:
                continue
            ctx.call('evidence write', out.write, value + b'\n')
    return {'closed': True}


def probe(ctx, install, queue):
    link = Link(ctx, install, queue)
    try:
        link.request_streams()
        while time.monotonic() < ctx.end - 2:
            link.read()
            time.sleep(.01)
        now = time.monotonic()
        sample = link.sample()
        ready = (link.fresh(now) and sample.armed is False and sample.landed_on_ground
                 and math.sqrt(sum(v*v for v in sample.velocity_ned_m_s)) <= .2
                 and math.sqrt(sum(x*x for x in sample.position_ned_m)) <= .25)
        return {'B_initial_telemetry_ready': bool(ready), **link.report(),
                'source': 'PX4 estimate; simulator truth not verified',
                'timestamp': 'time_boot_ms is PX4 boot time, reception uses Windows Python monotonic'}
    finally:
        link.close()


def checkpoint_write(shared, evaluation, initial):
    value = json.dumps({'summary': evaluation.summary(), 'initial': initial,
                        'takeoff_s': evaluation.takeoff_s,
                        'landing_request_s': evaluation.landing_request_s}).encode()
    if len(value) >= len(shared):
        raise ValueError('checkpoint buffer too small')
    shared.value = value


def flight(ctx, install, config, queue, checkpoint):
    link = Link(ctx, install, queue)
    start = time.monotonic()
    evaluation = None
    try:
        link.request_streams()
        while time.monotonic() < min(ctx.end, start+3):
            link.read()
            if link.fresh(time.monotonic()):
                break
            time.sleep(.01)
        s = link.sample()
        if not link.fresh(time.monotonic()) or s.armed or not s.landed_on_ground:
            return {'blocked': 'fresh initial disarmed ON_GROUND telemetry unavailable', **link.report()}
        initial = s.position_ned_m
        if math.sqrt(sum(x*x for x in initial)) > .25:
            return {'blocked': 'PX4 initial origin exceeds .25m; do not shift frozen route', **link.report()}
        # Keepalive before explicit mode/arm; no failsafe parameter modifications.
        pre_end = time.monotonic()+2
        while time.monotonic() < pre_end:
            link.setpoint(config['B']['route_ned_m'][0])
            link.read()
            time.sleep(.1)
        emit(queue, link.counters, 'command', command=176, params=[65,6,0], sdk_method='SendSetMode')
        link.ctx.call('SendSetMode OFFBOARD', link.sdk.SendSetMode, 6)
        link.command(400, 1)  # ordinary arm; no force code
        transition_end = time.monotonic()+3
        transition_verified = False
        while time.monotonic() < transition_end:
            link.setpoint(config['B']['route_ned_m'][0])
            link.read()
            now = time.monotonic()
            acked = all(any(v['command'] == c and v['result'] == 0 for v in link.acks)
                        for c in (176, 400))
            hb = link.hb
            if (acked and link.fresh(now) and hb['base_mode'] & 128
                    and ((hb['custom_mode'] >> 16) & 255) == 6):
                transition_verified = True
                break
            time.sleep(.1)
        if not transition_verified:
            return {'blocked': 'OFFBOARD/arming ACK and fresh mode not confirmed', **link.report()}
        evaluation = FlightEvaluation(config, time.monotonic(), initial, 'px4_estimate')
        next_setpoint = time.monotonic()
        landing = False
        ground_since = None
        disarm_sent = False
        last_sample_ms = None
        while time.monotonic() < ctx.end-.05:
            now = time.monotonic()
            link.read()
            evaluation.tick(now)
            s = link.sample()
            if s is not None and s.source_time_s != last_sample_ms:
                evaluation.update(now, s)
                last_sample_ms = s.source_time_s
            if not landing and (evaluation.failed or evaluation.next_leg == 5):
                ctx.attempt('land')
                evaluation.request_landing(now)
                link.command(21)
                landing = True
            if not landing and now >= next_setpoint:
                target = config['B']['route_ned_m'][evaluation.next_leg]
                emit(queue, link.counters, 'control_tick', target_deadline_s=next_setpoint,
                     deadline_miss_s=max(0, now-next_setpoint))
                link.setpoint(target)
                next_setpoint += .1
                if next_setpoint < now-.1:
                    next_setpoint = now+.1
            if landing and s is not None:
                grounded = (link.fresh(now) and s.landed_on_ground and
                            math.sqrt(sum(v*v for v in s.velocity_ned_m_s)) <= .2)
                ground_since = (ground_since or now) if grounded else None
                if ground_since and now-ground_since >= 2 and not disarm_sent:
                    ctx.attempt('disarm')
                    link.command(400, 0)  # never force disarm in air
                    disarm_sent = True
            checkpoint_write(checkpoint, evaluation, initial)
            if evaluation.summary()['landing_confirmed']:
                break
            time.sleep(.005)
        return {'evaluation': evaluation.summary(), **link.report()}
    finally:
        link.close()


def cleanup(ctx, install, config, queue, checkpoint):
    link = Link(ctx, install, queue)
    old = json.loads(checkpoint.value) if checkpoint.value else None
    evaluation = FlightEvaluation(config, time.monotonic(), (0,0,0), 'px4_estimate')
    if old:
        evaluation.initial = old['initial']
        evaluation.takeoff = old['summary']['takeoff_confirmed']
        evaluation.takeoff_s = old['takeoff_s']
        evaluation.reached = old['summary']['reached_legs']
        evaluation.failed = old['summary']['failure']
        evaluation.next_leg = len(evaluation.reached)+1
    try:
        link.request_streams()
        ctx.attempt('land')
        evaluation.request_landing(time.monotonic())
        link.command(21)
        ground_since = None
        disarm_sent = False
        last_source = None
        while time.monotonic() < ctx.end-.05:
            now = time.monotonic()
            link.read()
            s = link.sample()
            if s and s.source_time_s != last_source:
                evaluation.update(now, s)
                last_source = s.source_time_s
            grounded = (s and link.fresh(now) and s.landed_on_ground and
                        math.sqrt(sum(v*v for v in s.velocity_ned_m_s)) <= .2)
            ground_since = (ground_since or now) if grounded else None
            if ground_since and now-ground_since >= 2 and not disarm_sent:
                ctx.attempt('disarm')
                link.command(400, 0)
                disarm_sent = True
            if evaluation.summary()['landing_confirmed']:
                break
            time.sleep(.01)
        return {'evaluation': evaluation.summary(), 'prior_checkpoint_available': bool(old),
                **link.report()}
    finally:
        link.close()


def execute_phase(function, args, duration, root, name):
    context = mp.get_context('spawn')
    queue = context.Queue(maxsize=8192)
    log = root/(name+'.jsonl')
    report = run_phase(function, (*args, queue) if function is probe else args,
                       duration_s=duration, call_s=2,
                       auxiliaries=[('writer', writer, (str(log), queue))])
    # Control is stopped; finish any queued metadata outside its timing path.
    with log.open('ab') as out:
        drain_end = time.monotonic()+2
        while time.monotonic() < drain_end:
            try:
                out.write(queue.get(timeout=.05)+b'\n')
            except Empty:
                break
    queue.close()
    (root/(name+'-supervision.json')).write_text(json.dumps(report, indent=2)+'\n')
    return report


def result_exit_status(report, mode):
    primary = report.get('workers', [{}])[0] if mode == 'probe' else report['flight']['workers'][0]
    result = (primary.get('report') or {}).get('result', {})
    passed = result.get('B_initial_telemetry_ready') if mode == 'probe' else result.get('evaluation', {}).get('full_route_pass')
    incomplete = result.get('evidence_queue', {}).get('evidence_incomplete', False)
    if mode == 'B':
        cleanup_worker = report['cleanup']['workers'][0]
        cleanup_result = (cleanup_worker.get('report') or {}).get('result', {})
        cleanup_ok = (cleanup_worker.get('exit_status') == 0 and
                      cleanup_result.get('evaluation', {}).get('landing_confirmed') is True and
                      not cleanup_result.get('evidence_queue', {}).get('evidence_incomplete', False))
        passed = passed and cleanup_ok
    return 0 if passed and not incomplete and primary.get('exit_status') == 0 else 2


def main():
    p = argparse.ArgumentParser()
    p.add_argument('mode', choices=['probe', 'B'])
    p.add_argument('--install', required=True)
    p.add_argument('--config', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--freeze', type=Path)
    p.add_argument('--capture', action='store_true')
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    config = json.loads(a.config.read_text())
    (a.output/'config.json').write_text(json.dumps(config, indent=2)+'\n')
    if a.mode == 'probe':
        report = execute_phase(probe, (a.install,), 15, a.output, 'probe')
    else:
        freeze = json.loads(a.freeze.read_text()) if a.freeze else {}
        if not config.get('execution_authorized') or freeze.get('B_verified') is not True:
            raise SystemExit('BLOCKED: B installed-interface/initial-state freeze required')
        if freeze.get('config_sha256') != hashlib.sha256(a.config.read_bytes()).hexdigest():
            raise SystemExit('BLOCKED: freeze/config mismatch')
        (a.output/'freeze.json').write_text(json.dumps(freeze, indent=2)+'\n')
        context = mp.get_context('spawn')
        checkpoint = context.RawArray('c', 8192)
        queue = context.Queue(maxsize=8192)
        log = a.output/'flight.jsonl'
        side_workers=[('writer', writer, (str(log), queue))]
        if a.capture:
            from capture_adapter import capture
            side_workers.append(('capture',capture,(a.install,config,str(a.output/'rgb'),'mounted')))
        report = run_phase(flight, (a.install, config, queue, checkpoint), 75, 2,
                           auxiliaries=side_workers)
        with log.open('ab') as out:
            while True:
                try: out.write(queue.get(timeout=.05)+b'\n')
                except Empty: break
        # A forcibly stopped writer may leave Queue transport locks/feeder state
        # unusable. Cleanup must own a fresh queue, independently of flight.
        queue.cancel_join_thread()
        queue.close()
        queue = context.Queue(maxsize=8192)
        recovery_log = a.output/'cleanup.jsonl'
        recovery = run_phase(cleanup, (a.install, config, queue, checkpoint), 15, 2,
                             auxiliaries=[('writer', writer, (str(recovery_log), queue))],
                             primary_role='cleanup')
        with recovery_log.open('ab') as out:
            while True:
                try: out.write(queue.get(timeout=.05)+b'\n')
                except Empty: break
        queue.close()
        report = {'flight': report, 'cleanup': recovery}
    (a.output/'run.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))
    return result_exit_status(report, a.mode)


if __name__ == '__main__':
    mp.freeze_support()
    raise SystemExit(main())
