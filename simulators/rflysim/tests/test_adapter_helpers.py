import json
import math
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from installed_adapter import evidence_value, result_exit_status
from capture_adapter import capture_duration, sensor_euler_degrees

class AdapterHelperTests(unittest.TestCase):
    def test_nonfinite_and_bytearray_evidence_remain_valid_json(self):
        result = evidence_value({'v': [float('nan'), float('inf')], 'raw': bytearray([0, 255])})
        self.assertEqual(result['raw'], {'bytes_hex': '00ff'})
        self.assertEqual(result['v'][0], {'nonfinite': 'nan'})
        json.dumps(result, allow_nan=False)

    def test_frozen_capture_durations_are_not_shortened(self):
        config = json.loads((Path(__file__).resolve().parents[1] / 'audit-config.json').read_text())
        self.assertEqual(capture_duration(config, 'sequence'), 26)
        self.assertEqual(capture_duration(config, 'rate'), 35)
        self.assertEqual(capture_duration(config, 'mounted'), 75)

    def test_camera_euler_degrees_are_not_converted_to_radians(self):
        self.assertEqual(sensor_euler_degrees({'rpy_deg': [0, 0, 15]}), [0, 0, 15])
        self.assertEqual(sensor_euler_degrees({'rpy_deg': [0, 10, 0]}), [0, 10, 0])

    def test_cleanup_deadline_cannot_be_hidden_by_flight_pass(self):
        def worker(exit_status):
            return {'exit_status': exit_status, 'report': {'result': {'evaluation':
                    {'full_route_pass': True, 'landing_confirmed': True}, 'evidence_queue': {}}}}
        report = {'flight': {'workers': [worker(0)]}, 'cleanup': {'workers': [worker(-15)]}}
        self.assertEqual(result_exit_status(report, 'B'), 2)
        report['cleanup']['workers'][0]['exit_status'] = 0
        self.assertEqual(result_exit_status(report, 'B'), 0)
