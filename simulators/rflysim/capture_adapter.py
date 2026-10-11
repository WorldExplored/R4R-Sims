"""Installed native RGB capture. Raw timestamps are never relabeled acquisition UTC.

Pixel copying and encoding run in this process, separately from B control.
CameraData is exported independently; geometric association remains a check.
"""
import argparse
import hashlib
import json
import mmap
from pathlib import Path
import socket
import struct
import sys
import time
from runtime_core import run_phase

VISION_HASH='6bc6680b87d88d86239c16290a45b15372c1e8ec4a8844792d097ae60d9e5943'
UE_HASH='f299b946d905b846de87b548a43bbeed9563376593a7e801d44177d8ae09c770'


def capture_duration(config, mode):
    if mode == 'sequence':
        return config['A']['warmup_s'] + config['A']['per_pose_s'] * len(config['A']['poses'])
    if mode == 'rate':
        return config['A']['rate_test_warmup_s'] + config['A']['capture_rate_test_s']
    return config['limits']['flight_s']


def sensor_euler_degrees(pose):
    """SensorAngEular uses degrees (official vis-cfg, checked 2026-10-10)."""
    return list(pose['rpy_deg'])


def capture(ctx, install, config, output, mode='mounted', ground_ned_z_m=-8.05):
    sdk=Path(install)/'RflySimAPIs'/'RflySimSDK'
    for relative, expected in [('vision/VisionCaptureApi.py',VISION_HASH),('ue/UE4CtrlAPI.py',UE_HASH)]:
        if hashlib.sha256((sdk/relative).read_bytes()).hexdigest()!=expected:
            raise ValueError('camera SDK hash mismatch: '+relative)
    sys.path.insert(0,str(sdk))
    from vision.VisionCaptureApi import VisionCaptureApi, VisionSensorReq
    from ue.UE4CtrlAPI import UE4CtrlAPI
    import cv2
    import numpy as np
    root=Path(output); (root/'frames').mkdir(parents=True,exist_ok=True)
    records=open(root/'camera.jsonl','ab',buffering=0)
    def log(kind,**value):
        data={'kind':kind,'receiver_monotonic_s':time.monotonic(),'receiver_utc_unix_s':time.time(),**value}
        ctx.call('camera metadata write',records.write,(json.dumps(data,allow_nan=False)+'\n').encode())
    vision=ctx.call('VisionCaptureApi constructor',VisionCaptureApi)
    ue=ctx.call('UE4CtrlAPI constructor',UE4CtrlAPI)
    sensor=VisionSensorReq(); sensor.SeqID=0; sensor.TypeID=1; sensor.TargetCopter=1
    sensor.TargetMountType=0 if mode=='mounted' else 2
    sensor.DataWidth=640; sensor.DataHeight=480; sensor.DataCheckFreq=10
    sensor.CameraFOV=90; sensor.SendProtocol=[0,127,0,0,1,9999,0,0]
    sensor.SensorPosXYZ=[.3,0,0] if mode=='mounted' else [0,0,ground_ned_z_m-2]
    sensor.SensorAngEular=[0,0,0]
    vision.isNewJson=True
    # Installed addVisSensor is shadowed by its Type9 overload. jsonLoad uses
    # this same VisSensor list; preserve upstream rather than patching it.
    vision.VisSensor=[sensor]
    camera_socket=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    camera_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    camera_socket.bind(('0.0.0.0',20006)); camera_socket.setblocking(False)
    camera_socket.setsockopt(socket.IPPROTO_IP,socket.IP_ADD_MEMBERSHIP,
                            socket.inet_aton('224.0.0.10')+socket.inet_aton('0.0.0.0'))
    truth=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    truth.bind(('0.0.0.0',30101)); truth.setblocking(False)
    shared=mmap.mmap(0,640*480*3+9,'RflySim3DImg_0')
    log('configuration',mode=mode,resolution=[640,480],requested_hz=10,fov_deg=90,
        mount_type=sensor.TargetMountType,sensor_position_command=sensor.SensorPosXYZ,
        ground_map_ned_z_m=ground_ned_z_m,ground_source='CopterSim GUI stock initial Z; provisional',
        actual_pose_source='native CameraData packets if received',
        timestamp_meaning='native raw double; acquisition semantics/clock offset not independently verified',
        intrinsics_status='FOV axis and projection unverified',pixel_order='SDK BGR convention; independent color check pending',
        association_status='pending bracketed truth/clock verification; receiver time is not acquisition time')
    ctx.call('request one RGB camera',vision.sendReqToUE4,0)
    ctx.call('request actual camera metadata',ue.reqCam,[0],0)
    start=time.monotonic(); warmup=5; frames=duplicates=0; last=None; pose_index=-1
    duration=capture_duration(config, mode)
    # The parent watchdog enforces the budget; never shorten a requested test
    # and then report that shortened capture as completed.
    end=start+duration
    try:
        while time.monotonic()<end:
            elapsed=time.monotonic()-start
            if mode=='sequence':
                index=max(0,min(6,int((elapsed-warmup)//3)))
                if index!=pose_index:
                    pose_index=index; pose=config['A']['poses'][index]
                    sensor.SensorPosXYZ=[pose['ned_m'][0],pose['ned_m'][1],pose['ned_m'][2]+ground_ned_z_m]
                    sensor.SensorAngEular=sensor_euler_degrees(pose)
                    ctx.call('update world-fixed camera',vision.sendUpdateUEImage,sensor,0)
                    log('pose_command',pose_id=pose['id'],desired_local_ned_m=pose['ned_m'],
                        native_position_command=sensor.SensorPosXYZ,rpy_command_deg=sensor.SensorAngEular,
                        settling=1,command_is_not_truth=True)
            for stream,sock in [('camera_packet',camera_socket),('truth_packet',truth)]:
                for _ in range(40):
                    try: buf,addr=sock.recvfrom(65500)
                    except BlockingIOError: break
                    if stream=='camera_packet' and len(buf) in (56,72):
                        values=struct.unpack('5i7f1d' if len(buf)==56 else '5i11f1d',buf)
                        if values[0]==1234567891:
                            log('actual_camera',raw=values,seq_id=values[1],dimensions=[values[4],values[3]],
                                fov=values[5],native_position=values[6:9],native_euler=values[9:12],
                                native_quaternion=None if len(buf)==56 else values[12:16],raw_timestamp=values[-1],
                                units_and_axes='native metadata, independently unverified')
                    elif stream=='truth_packet' and len(buf)==168:
                        values=struct.unpack('4i24f7d',buf)
                        if values[0]==123456789:
                            log('simulator_body_truth',raw_timestamp=values[28],position_map_ned_m=values[29:32],
                                velocity_ned_m_s=values[4:7],rpy_rad=values[7:10],quaternion_native=values[10:14],
                                timestamp_meaning='runnedTime seconds documented, clock correspondence pending')
                    elif stream=='camera_packet' and len(buf)==12:
                        log('collision_packet',raw=struct.unpack('3i',buf))
            if shared[0]==2:
                shared.seek(0); shared.write_byte(3)
                stamp=struct.unpack('d',shared[1:9])[0]
                pixels=bytes(shared[9:])
                shared.seek(0); shared.write_byte(4)
                duplicate=stamp==last
                if duplicate: duplicates+=1
                last=stamp; name='frames/frame-%06d.png'%frames
                image=np.frombuffer(pixels,dtype=np.uint8).reshape(480,640,3)
                if not ctx.call('RGB PNG encode/write',cv2.imwrite,str(root/name),image):
                    raise IOError('PNG write returned false')
                log('frame',frame_id=frames,path=name,raw_timestamp=stamp,
                    warmup=elapsed<warmup,pose_id=None if pose_index<0 else config['A']['poses'][pose_index]['id'],
                    pose_elapsed_s=None if mode!='sequence' else max(0,elapsed-warmup)-pose_index*3,
                    duplicate_timestamp=duplicate,
                    acquisition_utc=None,actual_pose_association='pending independent clock/transform verification')
                frames+=1
            time.sleep(.002)
        log('capture_finished',frames=frames,duplicate_timestamps=duplicates,elapsed_s=time.monotonic()-start)
        return {'frames':frames,'duplicate_timestamps':duplicates,'wall_capture_s':time.monotonic()-start,
                'geometric_A':'blocked until units/calibration/acquisition clock independently verified'}
    finally:
        shared.close();camera_socket.close();truth.close();records.close()
        vision.stopFlag=True
        # Only capture actors are cleared; this does not kill simulator processes.
        ctx.call('clear native capture actors',vision.sendUE4Cmd,'RflyClearCapture',0)


def main():
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['sequence','rate','mounted'])
    p.add_argument('--install',required=True);p.add_argument('--config',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--ground-z',type=float,default=-8.05)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    config=json.loads(a.config.read_text());(a.output/'config.json').write_bytes(a.config.read_bytes())
    budget=40 if a.mode=='sequence' else 45 if a.mode=='rate' else 75
    report=run_phase(capture,(a.install,config,str(a.output),a.mode,a.ground_z),budget,2)
    (a.output/'run.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
    result=(report['workers'][0].get('report') or {}).get('result',{})
    completed = result.get('wall_capture_s', 0) >= capture_duration(config, a.mode)
    return 0 if result.get('frames', 0) > 0 and completed else 2

if __name__=='__main__':
    import multiprocessing as mp
    mp.freeze_support();raise SystemExit(main())
