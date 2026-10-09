#!/usr/bin/env python3
"""Check nominal rig against recorded RGB/depth response poses; no pose correction."""
import argparse,json,math,numpy as np
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('run',type=Path);a=p.parse_args();r=a.run
rows=lambda n:[json.loads(x) for x in (r/n).read_text().splitlines()]
def rotation(q):
 x,y,z,w=np.asarray(q)/np.linalg.norm(q)
 return np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
states={s['index']:s for s in rows('actual_vehicle.jsonl')};settings=json.loads((r/'settings.json').read_text())['Vehicles']['Drone_1']['Cameras'];items=[]
for c in rows('actual_camera.jsonl'):
 s=states[c['index']];body=rotation(s['orientation_xyzw']);mount=settings[c['camera']];offset=np.array([mount[k] for k in ['X','Y','Z']]);roll,pitch,yaw=np.radians([mount[k] for k in ['Roll','Pitch','Yaw']]);cx,sx=math.cos(roll),math.sin(roll);cy,sy=math.cos(pitch),math.sin(pitch);cz,sz=math.cos(yaw),math.sin(yaw)
 rig=np.array([[cz,-sz,0],[sz,cz,0],[0,0,1]])@np.array([[cy,0,sy],[0,1,0],[-sy,0,cy]])@np.array([[1,0,0],[0,cx,-sx],[0,sx,cx]])
 expected=np.asarray(s['position_ned_m'])+body@offset;diff=np.asarray(c['position_ned_m'])-expected;relative=(body@rig).T@rotation(c['orientation_xyzw']);angle=math.degrees(math.acos(np.clip((np.trace(relative)-1)/2,-1,1)))
 item={'index':c['index'],'camera':c['camera'],'expected_from_measured_vehicle_ned_m':expected.tolist(),'actual_ned_m':c['position_ned_m'],'translation_residual_ned_m':diff.tolist(),'translation_residual_norm_m':float(np.linalg.norm(diff)),'orientation_residual_deg':angle}
 if 'depth_position_ned_m' in c:item.update(depth_to_rgb_position_error_m=float(np.linalg.norm(np.asarray(c['depth_position_ned_m'])-c['position_ned_m'])),depth_to_rgb_orientation_error_deg=math.degrees(math.acos(np.clip((np.trace(rotation(c['orientation_xyzw']).T@rotation(c['depth_orientation_xyzw']))-1)/2,-1,1))))
 items.append(item)
result={'records':items,'maximum_translation_residual_m':max(x['translation_residual_norm_m'] for x in items),'maximum_orientation_residual_deg':max(x['orientation_residual_deg'] for x in items),'depth_response_pose_count':sum('depth_to_rgb_position_error_m' in x for x in items),'maximum_depth_rgb_position_error_m':max([x['depth_to_rgb_position_error_m'] for x in items if 'depth_to_rgb_position_error_m' in x],default=None),'meaning':'nominal body mount versus actual paused response poses; actor update/offset may differ; actual extrinsics retained'}
(r/'calibration-validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='records'}))
