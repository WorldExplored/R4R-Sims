import json, csv, pathlib, collections, math, hashlib
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image
import argparse
p=argparse.ArgumentParser(); p.add_argument('--input',type=pathlib.Path,required=True);p.add_argument('--output',type=pathlib.Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
def read(path): return [json.loads(x) for x in path.read_text().splitlines() if x.strip()]
def scalar(value):
 if isinstance(value, np.generic): return value.item()
 raise TypeError('Unsupported evidence value: '+type(value).__name__)
def dump(path,v): path.write_text(json.dumps(v,indent=2,allow_nan=False,default=scalar)+'\n')
def stats(v):
 v=np.asarray(v,float);return dict(n=len(v),mean=float(np.mean(v)),median=float(np.median(v)),p95=float(np.percentile(v,95)),max=float(np.max(v))) if len(v) else None
metrics={}; data={}
for name in ['B1','B2']:
 root=a.input/name
 if not root.exists():continue
 rows=read(root/'flight.jsonl'); report=json.loads((root/'run.json').read_text());result=report['flight']['workers'][0]['report']['result'];ev=result['evaluation']
 origin=rows[0]['monotonic_s'];state=[];truth=[];sets=[];acks=[];ticks=[]
 for r in rows:
  m=r.get('message',{});t=r['monotonic_s']
  if r['kind']=='mavlink':
   if m['mavpackettype']=='LOCAL_POSITION_NED':state.append(dict(receiver_monotonic_s=t,receiver_utc_unix_s=r['utc_unix_s'],source_boot_ms=m['time_boot_ms'],position_ned_m=[m[k] for k in ['x','y','z']],velocity_ned_m_s=[m[k] for k in ['vx','vy','vz']],source='PX4 LOCAL_POSITION_NED estimate'))
   if m['mavpackettype']=='HIL_ACTUATOR_CONTROLS' and m.get('flags')==1234567890:
    truth.append(dict(receiver_monotonic_s=t,raw_time_usec=m['time_usec'],position_map_ned_m=m['controls'][3:6],velocity_ned_m_s=m['controls'][6:9],rpy_rad=m['controls'][0:3],source='SDK-defined CopterSim truth multiplex; PX4MavCtrlV4.py:3227-3245; source clock unverified'))
   if m['mavpackettype'] in ['COMMAND_ACK','HEARTBEAT','EXTENDED_SYS_STATE']:acks.append(r)
  elif r['kind']=='setpoint':sets.append(r)
  elif r['kind']=='control_tick':ticks.append(r)
 out=a.output/name;out.mkdir(exist_ok=True)
 for fn,records in [('estimated-state.jsonl',state),('simulator-truth-multiplex.jsonl',truth),('actions.jsonl',sets),('ack-mode-arm-land.jsonl',acks)]:
  (out/fn).write_text(''.join(json.dumps(r)+'\n' for r in records))
 intervals=np.diff([r['monotonic_s'] for r in sets]);tickstart=ticks[0]['monotonic_s'] if ticks else origin
 active_sets=[r for r in sets if r['monotonic_s']>=tickstart]; active_intervals=np.diff([r['monotonic_s'] for r in active_sets]); pos_gaps=np.diff([r['receiver_monotonic_s'] for r in state]);miss=[r['deadline_miss_s'] for r in ticks]
 mt=dict(evaluation=ev,supervised_wall_s=report['flight']['wall_s'],control_exit_status=report['flight']['workers'][0]['exit_status'],control_setpoint_interval_s=stats(active_intervals),position_receive_gap_s=stats(pos_gaps),deadline_lateness_s=stats(miss),deadline_lateness_gt_10ms=sum(x>.01 for x in miss),deadline_lateness_gt_100ms=sum(x>.1 for x in miss),position_samples=len(state),truth_samples=len(truth),simulation_time_span_s=None,px4_boot_clock_span_s=(state[-1]['source_boot_ms']-state[0]['source_boot_ms'])/1000,truth_clock='raw time_usec retained; SDK scaling not independently verified')
 # Truth comparison uses receive-nearest <= 0.05s; origin alignment fitted only from first sample.
 if truth and state:
  tt=np.array([r['receiver_monotonic_s'] for r in truth]);tp=np.array([r['position_map_ned_m'] for r in truth]);sp=np.array([r['position_ned_m'] for r in state]);st=np.array([r['receiver_monotonic_s'] for r in state]);idx=np.searchsorted(tt,st).clip(0,len(tt)-1);prev=(idx-1).clip(0,len(tt)-1);idx=np.where(abs(tt[prev]-st)<abs(tt[idx]-st),prev,idx);mask=abs(tt[idx]-st)<=.05
  offset=tp[idx[0]]-sp[0];diff=np.linalg.norm(tp[idx[mask]]-offset-sp[mask],axis=1)
  mt['receive_nearest_truth_disagreement_m']=stats(diff);mt['truth_alignment_offset_map_minus_estimate_m']=offset.tolist();mt['truth_comparison_limit']='receive-nearest <=0.05s; initial offset fit; no acquisition synchronization, no ground-truth pass claim'
  fig,ax=plt.subplots(figsize=(9,3));ax.plot(st[mask]-origin,diff);ax.set(xlabel='Receiver wall time from run start (s)',ylabel='Position difference (m)',title=name+' estimate vs CopterSim multiplex truth (receive-nearest, initial offset fitted)');ax.grid(alpha=.3);fig.tight_layout();fig.savefig(out/'truth-disagreement.png',dpi=160);plt.close(fig)
 xyz=np.array([r['position_ned_m'] for r in state]);ts=np.array([r['receiver_monotonic_s']-origin for r in state]);sx=np.array([r['position_ned_m'] for r in sets]);ss=np.array([r['monotonic_s']-origin for r in sets]);data[name]=(ts,xyz,ss,sx,ev)
 fig,ax=plt.subplots(1,2,figsize=(11,4));ax[0].plot(xyz[:,1],xyz[:,0],label='PX4 estimate');ax[0].plot(sx[:,1],sx[:,0],'--',label='Reference');ax[0].set(xlabel='East (m)',ylabel='North (m)',title=name+' route');ax[0].axis('equal');ax[0].legend();ax[0].grid(alpha=.3);ax[1].plot(ts,-xyz[:,2],label='Estimated height');ax[1].step(ss,-sx[:,2],where='post',label='Position target');ax[1].set(xlabel='Receiver wall time (s)',ylabel='Local height (m)',title='Takeoff, route and landing');ax[1].legend();ax[1].grid(alpha=.3);fig.tight_layout();fig.savefig(out/'trajectory.png',dpi=160);plt.close(fig)
 ix=np.searchsorted(ss,ts,side='right')-1;ix=ix.clip(0,len(ss)-1);err=np.linalg.norm(xyz-sx[ix],axis=1)
 fig,ax=plt.subplots(2,1,figsize=(10,5));land_time=next(e['monotonic_s']-origin for e in ev['events'] if e['event']=='land_requested');ax[0].plot(ts,np.where(ts<=land_time,err,np.nan));ax[0].axvspan(land_time,ts[-1],color='grey',alpha=.15,label='NAV_LAND, position reference inactive');ax[0].axhline(.25,color='r',ls='--',label='0.25 m criterion');ax[0].legend();ax[0].set(ylabel='Reference error (m)',title=name+' estimated tracking; dwell evaluated by fresh telemetry');ax[1].plot([r['monotonic_s']-origin for r in ticks],miss,label='Tick lateness');ax[1].plot(ts[1:],pos_gaps,label='Position receipt gap',alpha=.7);ax[1].set(xlabel='Receiver wall time (s)',ylabel='Seconds');ax[1].legend();[v.grid(alpha=.3) for v in ax];fig.tight_layout();fig.savefig(out/'tracking-timing.png',dpi=160);plt.close(fig)
 gpu=a.input/(name+'-gpu.csv')
 if gpu.exists():
  records=list(csv.reader(gpu.read_text().splitlines())); mem=[float(r[3].split()[0]) for r in records];util=[float(r[5].split()[0]) for r in records];mt['gpu_sampled_window_memory_MiB']=stats(mem);mt['gpu_sampled_window_utilization_percent']=stats(util);mt['gpu_limits']='100 samples over~104s, includes preflight/Moonlight/desktop; 1Hz requested; B2 misses final flight/landing under inferred UTC-04, not render-only throughput'
  fig,ax=plt.subplots(1,2,figsize=(10,3));ax[0].plot(mem);ax[0].set(ylabel='GPU memory (MiB)',xlabel='Sample index (~1 s)',title=name+' whole desktop GPU');ax[1].plot(util);ax[1].set(ylabel='Utilization (%)',xlabel='Sample index (~1 s)');fig.tight_layout();fig.savefig(out/'gpu.png',dpi=160);plt.close(fig)
 metrics[name]=mt;dump(out/'metrics.json',mt)
for name in ['A1','A2','A1-retest','rate','B2/rgb']:
 root=a.input/name
 if not (root/'camera.jsonl').exists():continue
 rows=read(root/'camera.jsonl');frames=[r for r in rows if r['kind']=='frame'];actual=[r for r in rows if r['kind']=='actual_camera'];warm=[r for r in frames if r['warmup']];steady=[r for r in frames if not r['warmup']];times=[r['receiver_monotonic_s'] for r in steady]; raw=[r['raw_timestamp'] for r in steady];out=a.output/name;out.mkdir(parents=True,exist_ok=True)
 mt=dict(frames=len(frames),warmup_frames=len(warm),post_warmup_frames=len(steady),receive_interval_s=stats(np.diff(times)),delivered_rate_count_over_receive_span_hz=(len(times)-1)/(times[-1]-times[0]) if len(times)>1 else None,duplicate_raw_timestamps=sum(r['duplicate_timestamp'] for r in frames),receive_gaps_gt_150ms=sum(x>.15 for x in np.diff(times)),actual_camera_packets=len(actual),simulator_body_truth_packets=sum(r['kind']=='simulator_body_truth' for r in rows),pose_commands=[r for r in rows if r['kind']=='pose_command'],raw_timestamp_interval=stats(np.diff(raw)),latency_s=None,geometric_A='blocked: acquisition clock, projection/geometry, transform verification incomplete',camera_metadata_limit='native raw pose exported; no silent frame-to-pose association')
 mt['frames_open_verified']=0
 for r in frames:
  im=Image.open(root/r['path']);im.verify();mt['frames_open_verified']+=1
 if steady:
  for label,i in [('first',0),('middle',len(steady)//2),('last',len(steady)-1)]:
   r=steady[i];Image.open(root/r['path']).save(out/('preview-'+label+'.png'))
 if times:
  fig,ax=plt.subplots(figsize=(9,3));ax.plot(np.array(times[1:])-times[0],np.diff(times));ax.axhline(.1,color='k',ls='--');ax.set(xlabel='Receiver wall time after warmup (s)',ylabel='Frame receipt interval (s)',title=name+' delivered RGB timing; acquisition latency unknown');ax.grid(alpha=.3);fig.tight_layout();fig.savefig(out/'capture-timing.png',dpi=160);plt.close(fig)
 for filename,kind in [('camera-actual.jsonl','actual_camera'),('camera-reference.jsonl','pose_command'),('body-truth.jsonl','simulator_body_truth')]:
  (out/filename).write_text(''.join(json.dumps(x)+'\n' for x in rows if x['kind']==kind))
 published_frames=[]
 for frame in frames:
  asset=root/frame['path'];published_frames.append({**frame,'asset_base_path':str(root.resolve()),'bytes':asset.stat().st_size,'sha256':hashlib.sha256(asset.read_bytes()).hexdigest(),'width':640,'height':480,'intrinsics_matrix':None,'intrinsics_status':'FOV supplied; axis/projection not independently verified','actual_camera_pose_at_acquisition':None})
 (out/'frames.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in published_frames))
 metrics[name]=mt;dump(out/'metrics.json',mt)
dump(a.output/'metrics.json',metrics)
print(json.dumps({k:{j:v for j,v in m.items() if j in ['frames','delivered_rate_count_over_receive_span_hz','supervised_wall_s','evaluation','gpu_sampled_window_memory_MiB','position_receive_gap_s']} for k,m in metrics.items()},indent=2))

# Offline corroboration and illustrative trace; no acquisition association inferred.
import bisect
checks={}
for n in ['B1','B2']:
 rows=read(a.input/n/'flight.jsonl');metric=json.loads((a.output/n/'metrics.json').read_text());positions=read(a.output/n/'estimated-state.jsonl');events=metric['evaluation']['events'];config=json.loads((a.input/n/'config.json').read_text());checks[n]=[]
 for ev in events:
  if ev['event']!='waypoint_confirmed':continue
  end=ev['monotonic_s'];target=config['B']['route_ned_m'][ev['leg']];samples=[s for s in positions if end-2<=s['receiver_monotonic_s']<=end+.001];errors=[math.dist(s['position_ned_m'],target) for s in samples]
  before=[s for s in positions if s['receiver_monotonic_s']<end-2][-1:];all_s=before+samples
  checks[n].append(dict(leg=ev['leg'],reported_confirmation_s=end,preceding_window_s=2,samples=len(samples),maximum_sampled_error_m=max(errors),all_sampled_errors_within_tolerance=all(x<=.25 for x in errors),max_receipt_gap_s=max(b['receiver_monotonic_s']-a['receiver_monotonic_s'] for a,b in zip(all_s,all_s[1:])),interpretation='offline sampled-position corroboration, not independent truth or continuous unsampled motion'))
dump(a.output/'dwell-corroboration.json',checks)
# Join illustrative stages by UTC receive time, retaining unknown acquisition association.
rows=read(a.input/'B2'/'flight.jsonl');cam=read(a.input/'B2/rgb/camera.jsonl');frames=[x for x in cam if x['kind']=='frame'];frame=frames[len(frames)//2];t=frame['receiver_utc_unix_s']
def nearest(items,timekey):return min(items,key=lambda x:abs(x[timekey]-t))
trace={'status':'control and native RGB paths demonstrated; calibrated frame association blocked','asset_config':{'stock_scene':'Grasslands','vehicle':'10016_iris / CopterSim model0','config_sha256':hashlib.sha256((a.input/'B2/config.json').read_bytes()).hexdigest(),'weights':'none','split':'stock integration scene, no train/test split'},'frame':frame,'image_sha256':hashlib.sha256((a.input/'B2/rgb'/frame['path']).read_bytes()).hexdigest(),'setpoint_reference':nearest([x for x in rows if x['kind']=='setpoint'],'utc_unix_s'),'actual_estimate':nearest([x for x in rows if x.get('message',{}).get('mavpackettype')=='LOCAL_POSITION_NED'],'utc_unix_s'),'mode_armed':nearest([x for x in rows if x.get('message',{}).get('mavpackettype')=='HEARTBEAT'],'utc_unix_s'),'command_ack':nearest([x for x in rows if x.get('message',{}).get('mavpackettype')=='COMMAND_ACK'],'utc_unix_s'),'body_truth':nearest([x for x in cam if x['kind']=='simulator_body_truth'],'receiver_utc_unix_s'),'native_camera_pose':nearest([x for x in cam if x['kind']=='actual_camera'],'receiver_utc_unix_s'),'actual_camera_pose_at_acquisition':None,'association_uncertainty_s':None,'join_method':'illustrative UTC receiver-nearest only; no acquisition-time interpolation or calibrated extrinsics; temporal proximity does not prove causal command-to-frame identity'}
dump(a.output/'trace-example.json',trace)
clock={}
for n in ['A1','A2','rate','B2/rgb']:
 rows=read(a.input/n/'camera.jsonl');fs=[x for x in rows if x['kind']=='frame'];ps=[x for x in rows if x['kind']=='actual_camera'];deltas=[]
 for f in fs:
  p=min(ps,key=lambda x:abs(x['receiver_monotonic_s']-f['receiver_monotonic_s']));deltas.append(p['raw_timestamp']-f['raw_timestamp'])
 clock[n]={'receive_nearest_native_pose_minus_image_timestamp':{'min':min(deltas),'max':max(deltas),'median':sorted(deltas)[len(deltas)//2]},'units':'native numerical timestamp units, documented seconds but acquisition origin unverified','meaning':'diagnostic only, neither latency nor verified synchronization','first_frame':fs[0],'last_frame':fs[-1]}
dump(a.output/'camera-clock-diagnostics.json',clock)

angle_checks=[]
rows=read(a.input/'A2/camera.jsonl')
commands=[x for x in rows if x['kind']=='pose_command']
for command in commands:
 if command['pose_id'] not in ('p4','p5'):continue
 packets=[x for x in rows if x['kind']=='actual_camera' and command['receiver_monotonic_s']+1 <= x['receiver_monotonic_s'] < command['receiver_monotonic_s']+3]
 angles=[math.degrees(2*math.acos(min(1,abs(x['native_quaternion'][0])))) for x in packets if x['native_quaternion']]
 angle_checks.append(dict(pose_id=command['pose_id'],executed_command=command,returned_quaternion_rotation_degrees=stats(angles),convention='wxyz documented; native response diagnostic, not calibrated optical pose',cause='authored radians conversion sent to documented degree field'))
dump(a.output/'camera-angle-diagnostics.json',angle_checks)

# Timezone alignment is a declared inference, not a clock calibration.
import datetime
d={}
for n in ['B1','B2']:
 rows=[json.loads(x) for x in (a.input/n/'flight.jsonl').read_text().splitlines()];s,e=rows[0]['utc_unix_s'],rows[-1]['utc_unix_s'];g=list(csv.reader((a.input/(n+'-gpu.csv')).read_text().splitlines()));times=[datetime.datetime.strptime(x[0],'%Y/%m/%d %H:%M:%S.%f').replace(tzinfo=datetime.timezone(datetime.timedelta(hours=-4))).timestamp() for x in g];overlap=max(0,min(e,times[-1])-max(s,times[0]));d[n]={'samples':len(g),'local_csv_start':g[0][0],'local_csv_end':g[-1][0],'csv_window_s':times[-1]-times[0],'mean_sample_interval_s':(times[-1]-times[0])/(len(times)-1),'timezone_alignment':'UTC-04 inferred from contemporaneous Windows UI/UTC records; formal timezone export missing','apparent_flight_overlap_s':overlap,'flight_record_span_s':e-s,'apparent_full_flight_coverage':times[0]<=s and times[-1]>=e,'limit':'whole-desktop polling, not rendering-exclusive or synchronized GPU timing; B2 misses final flight/landing'}
dump(a.output/'resource-coverage.json',d)

for name in ['B1','B2']:
 metrics[name]['resource_coverage']=d[name]
 dump(a.output/name/'metrics.json',metrics[name])
dump(a.output/'metrics.json',metrics)
process_samples=read(a.input/'B1-resources.jsonl')
processes={}
for snapshot in process_samples:
 for item in snapshot:
  key=str(item['Id']);info=processes.setdefault(key,dict(samples=0,max_working_set_bytes=0,cpu_counter_last_s=None))
  info['samples']+=1;info['max_working_set_bytes']=max(info['max_working_set_bytes'],item['WorkingSet64']);info['cpu_counter_last_s']=item['CPU']
dump(a.output/'process-resources.json',dict(processes=processes,limits='Recorded audit PIDs only; no per-sample timestamps, no CPU rate or total-host RAM inference',pid_owners={'9388':'B1 CopterSim','1924':'UE4 engine','4284':'UE wrapper'}))

rows=read(a.input/'B2/rgb/camera.jsonl')
camera=next(x for x in rows if x['kind']=='actual_camera')
body=next(x for x in rows if x['kind']=='simulator_body_truth')
dump(a.output/'mount-diagnostic.json',dict(camera=camera,body=body,raw_position_difference=[x-y for x,y in zip(camera['native_position'],body['position_map_ned_m'])],requested_mount_translation_FRD_m=[.3,0,0],interpretation='initial stationary receiver-near raw coordinates suggest additional -0.15 vertical origin offset; axes/clock/extrinsic calibration unverified',cause='model/actor origin or other transform hypotheses unresolved, no repair/retest'))
