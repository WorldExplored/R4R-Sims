#!/usr/bin/env python3
"""Preparation-only configuration and evidence tools. No simulator execution."""
import argparse
import hashlib
import json
import math
from pathlib import Path

ROUTE = [[0, 0, 0], [0, 0, -2], [2, 0, -2], [2, 2, -2], [0, 0, -2]]


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def validate(config):
    errors = []
    if config.get('execution_authorized') is not False:
        errors.append('preparation config must keep execution_authorized=false')
    b = config.get('B', {})
    a = config.get('A', {})
    if b.get('route_ned_m') != ROUTE:
        errors.append('B route must preserve the specified NED route')
    if b.get('waypoint_tolerance_m') != 0.25 or b.get('continuous_dwell_s') != 2:
        errors.append('B criterion must remain 0.25 m / continuous 2 s')
    if a.get('pose_position_tolerance_m') != 0.02 or a.get('pose_angle_tolerance_deg') != 1:
        errors.append('A repeatability must remain 0.02 m / 1 degree')
    if a.get('feature_tolerance_dimension_fraction') != 0.02:
        errors.append('feature residual must remain 2% of dimension')
    limits = config.get('limits', {})
    for key, value in [('flight_s', 75), ('cleanup_s', 15), ('active_setup_total_s', 7200), ('repair_attempts_max', 2)]:
        if limits.get(key) != value:
            errors.append(f'{key} must be {value}')
    poses = a.get('poses', [])
    if not poses or a.get('sequence_duration_s') != len(poses) * a.get('per_pose_s', 0):
        errors.append('A sequence duration must match numeric pose schedule')
    for pose in poses:
        for key in ['ned_m', 'rpy_deg']:
            v = pose.get(key, [])
            if len(v) != 3 or not all(isinstance(x, (int, float)) and math.isfinite(x) for x in v):
                errors.append(f'pose {pose.get("id")} {key} must be a finite three-vector')
    if b.get('repeat_count_after_success') != 1 or not b.get('same_route_required'):
        errors.append('one repeat with same route is required after success')
    if config.get('association', {}).get('receiver_time_as_acquisition') is not False:
        errors.append('receiver time must not be substituted for acquisition time')
    return errors


def within(path, root):
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def manifest(root):
    root = root.resolve(strict=True)
    result = {}
    for p in sorted(root.rglob('*')):
        if p.is_symlink():
            raise ValueError(f'symlink not accepted: {p.relative_to(root)}')
        if p.is_file():
            result[p.relative_to(root).as_posix()] = {'bytes': p.stat().st_size, 'sha256': digest(p)}
    return result


def verify(root, entries):
    if not isinstance(entries, dict):
        raise ValueError("manifest must map relative paths to byte counts and SHA-256 values")
    root = root.resolve(strict=True)
    failures = []
    for rel, expected in entries.items():
        relative = Path(rel)
        if relative.is_absolute() or '..' in relative.parts or '\\' in rel or ':' in rel:
            raise ValueError(f'unsafe manifest path: {rel}')
        p = root / relative
        if p.is_symlink() or not within(p.resolve(), root):
            raise ValueError(f'manifest path escapes root: {rel}')
        if not p.is_file() or p.stat().st_size != expected['bytes'] or digest(p) != expected['sha256']:
            failures.append(rel)
    return failures


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['validate', 'readiness', 'manifest', 'verify', 'run'])
    parser.add_argument('--config', type=Path)
    parser.add_argument('--root', type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--manifest', type=Path)
    args = parser.parse_args(argv)
    if args.mode == 'run':
        print('BLOCKED: preparation only. No SDK adapter, verified host or execution authorization.')
        return 2
    try:
        if args.mode in ['validate', 'readiness']:
            if not args.config:
                parser.error('--config required')
            c = json.loads(args.config.read_text())
            errors = validate(c)
            if args.mode == 'validate':
                print(json.dumps({'review_config_valid': not errors, 'errors': errors,
                                  'execution_ready': False}, indent=2))
                return 1 if errors else 0
            print(json.dumps({'preparation_config_valid': not errors, 'execution_ready': False,
                              'blockers': c.get('freeze_blockers', []) + ['execution authorization pending'],
                              'errors': errors}, indent=2))
            return 2
        if not args.root:
            parser.error('--root required')
        if args.mode == 'manifest':
            if not args.output:
                parser.error('--output required')
            if within(args.output.resolve(), args.root.resolve()):
                raise ValueError('manifest output must be outside the evidence root')
            records = manifest(args.root)
            args.output.write_text(json.dumps(records, indent=2) + '\n')
            print(json.dumps({'files': len(records), 'manifest': str(args.output)}, indent=2))
            return 0
        if not args.manifest:
            parser.error('--manifest required')
        failures = verify(args.root, json.loads(args.manifest.read_text()))
        print(json.dumps({'verified': not failures, 'failures': failures,
                          'media_open_check': 'separate inspection required'}, indent=2))
        return 3 if failures else 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({'error': str(exc)}))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
