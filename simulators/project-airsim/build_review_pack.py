#!/usr/bin/env python3
"""Assemble a local-only, checksummed Project AirSim review pack from preserved evidence."""
import csv
import hashlib
import json
import math
import re
import shutil
import subprocess
import sys
import zipfile
from bisect import bisect_left
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

RUNS = [
    '20261009T002738Z-pose-1', '20261009T002820Z-pose-2',
    '20261009T002844Z-smoke-1', '20261009T002933Z-smoke-2',
    '20261009T003251Z-smoke-repair', '20261009T003453Z-flight-1',
    '20261009T003606Z-flight-2', '20261009T003933Z-pose-corrected',
]
A_RUNS = [RUNS[0], RUNS[1], RUNS[7]]
B_RUNS = [RUNS[5], RUNS[6]]
RUN_LABELS = {RUNS[0]:'A1',RUNS[1]:'A2',RUNS[7]:'A corrected',RUNS[5]:'B1',RUNS[6]:'B2'}
PYC = '/Users/srreyanshsethi/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3'


def rows(p):
    return [json.loads(s) for s in p.read_text().splitlines() if s.strip()] if p.is_file() else []


def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def verify_manifest(repo, path):
    missing, mismatch = [], []
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        expected, rel = line.split('  ', 1)
        p = repo / rel
        if not p.is_file():
            missing.append(rel)
        elif sha(p) != expected:
            mismatch.append(rel)
    return missing, mismatch


def copy(src, dst):
    if not src.is_file():
        raise FileNotFoundError(src)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def nearest(records, tick):
    times = [x['wall_monotonic_ns'] for x in records]
    i = bisect_left(times, tick)
    j = min((max(0, min(len(times) - 1, k)) for k in (i-1, i)), key=lambda k: abs(times[k]-tick))
    return records[j]


def xyz(x):
    p = x['native']['position']
    return [p[k] for k in 'xyz']


def heading(x):
    q = x['native']['orientation']
    return math.degrees(math.atan2(2*(q['w']*q['z']+q['x']*q['y']), 1-2*(q['y']**2+q['z']**2)))


def read_font(size):
    for f in ('/System/Library/Fonts/Supplemental/Arial.ttf', '/System/Library/Fonts/Helvetica.ttc'):
        if Path(f).is_file():
            return ImageFont.truetype(f, size)
    return ImageFont.load_default()


def depth_preview(arr):
    a = np.asarray(arr, dtype=np.float32)
    clipped = np.clip(a, 0, 20) / 20
    pix = np.stack([55 + 120*clipped, 80 + 100*clipped, 150 + 85*clipped], axis=-1).astype(np.uint8)
    pix[a == 65504] = (221, 40, 153)  # max finite half; meaning unresolved
    pix[~np.isfinite(a)] = (240, 210, 35)
    return Image.fromarray(pix, 'RGB')


def contact(items, kind, out):
    w, h = 430, 285
    canvas = Image.new('RGB', (w*3, h*math.ceil(len(items)/3)+28), 'white')
    d = ImageDraw.Draw(canvas)
    bold, small = read_font(17), read_font(13)
    for j, item in enumerate(items):
        x, y = (j%3)*w, (j//3)*h
        im = Image.open(item['rgb']) if kind == 'RGB' else depth_preview(np.load(item['depth']))
        im = im.convert('RGB').resize((400, 225))
        canvas.paste(im, (x+15, y+32))
        label=item['label'].replace('horizontal_plus_2m','horizontal +2 m').replace('vertical_up_1m','vertical +1 m').replace('heading_plus_30deg','heading +30°').replace('yaw_plus_30','yaw +30°')
        d.text((x+15, y+7), f"{RUN_LABELS[item['run']]}: {label} [{item['camera']}]", fill=(20,45,58), font=bold)
        d.text((x+15, y+260), f"sim ns {item['timestamp']} | {kind}", fill=(35,65,72), font=small)
    if kind != 'RGB':
        # Legend is a preview convention, not a claim about scene semantics.
        d.text((10, canvas.height-22), 'Blue = 0–20 m preview stretch (clipped). Magenta = 65504 max finite float16, meaning unresolved. Yellow = nonfinite.', fill=(30,30,30), font=small)
    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out, optimize=True)


def altitude_plot(run, raw, out):
    states = rows(raw/'actual_vehicle.jsonl')
    acts = rows(raw/'actions.jsonl')
    start = states[0]['wall_monotonic_ns']
    ts = np.array([(s['wall_monotonic_ns']-start)/1e9 for s in states])
    alt = np.array([-s['native']['position']['z'] for s in states])
    W,H = 1500,650; x0,y0,x1,y1 = 100,55,1450,555
    im=Image.new('RGB',(W,H),'white'); d=ImageDraw.Draw(im)
    title,small=read_font(25),read_font(17)
    lo,hi = min(alt.min(),2.2),max(alt.max(),5.2)
    def xx(t): return x0+(x1-x0)*float(t)/max(ts[-1],1)
    def yy(z): return y1-(y1-y0)*(float(z)-lo)/(hi-lo)
    starts={a['phase']:a for a in acts if a.get('event')=='start'}
    for a in acts:
        if a.get('event') not in ('complete','failed') or a['phase'] not in starts: continue
        s=starts[a['phase']]; xa,xb=xx((s['wall_monotonic_ns']-start)/1e9),xx((a['wall_monotonic_ns']-start)/1e9)
        if xb < x0 or xa > x1: continue
        color=(255,235,229) if a.get('result') is False or a.get('event')=='failed' else (238,246,248)
        d.rectangle((max(xa,x0),y0,min(xb,x1),y1),fill=color)
        label=a['phase']+(' FALSE' if a.get('result') is False else ' ERROR' if a.get('event')=='failed' else '')
        d.text((max(xa+3,x0),y0+8),label,fill=(125,49,39) if color[0]==255 else (18,90,110),font=small)
    for z in range(math.ceil(lo),math.floor(hi)+1):
        y=yy(z);d.line((x0,y,x1,y),fill=(225,225,225),width=1);d.text((45,y-10),str(z),fill=(50,50,50),font=small)
    d.line((x0,y0,x0,y1),fill=(40,40,40),width=2);d.line((x0,y1,x1,y1),fill=(40,40,40),width=2)
    for t in range(0,math.floor(ts[-1])+1,5):
        x=xx(t);d.line((x,y1,x,y1+6),fill=(40,40,40),width=2);d.text((x-8,y1+10),str(t),fill=(40,40,40),font=small)
    pts=[(xx(t),yy(z)) for t,z in zip(ts,alt)]
    d.line(pts,fill=(21,104,149),width=3)
    d.text((x0,15),f'{run}: achieved altitude and client command intervals (offline alignment)',fill=(20,45,58),font=title)
    d.text((x0,605),'X: client monotonic wall seconds since first state. Y: altitude (m) = -NED Z. Pink: server false.',fill=(40,45,50),font=small)
    out.parent.mkdir(parents=True,exist_ok=True);im.save(out,optimize=True)


def excerpt(src, spans, dst, repo):
    lines=src.read_text().splitlines()
    with dst.open('w') as f:
        f.write(f'Pinned source 09755454b8d82b0231af7e59fd1ab8f980ff32c5\n{src.relative_to(repo)}\nSHA256 {sha(src)}\n')
        for first,last in spans:
            f.write(f'\n--- lines {first}-{last} ---\n')
            for n in range(first,min(last,len(lines))+1):f.write(f'{n:4} {lines[n-1]}\n')


def main(repo):
    repo=repo.resolve(); root=repo/'artifacts/project-airsim/review-pack'
    if root.exists():
        raise SystemExit(f'preserving existing pack: {root}')
    manifests=[repo/'results/project-airsim'/r/'manifest.sha256' for r in RUNS]
    manifests += [repo/p for p in ('results/project-airsim/previews/SHA256SUMS','artifacts/project-airsim/host-setup/SHA256SUMS','artifacts/project-airsim/source-pinned/SHA256SUMS','artifacts/project-airsim/deliverables/SHA256SUMS')]
    problems=[]
    for mf in manifests:
        missing,bad=verify_manifest(repo,mf)
        problems += [f'MISSING {x}' for x in missing]+[f'MISMATCH {x}' for x in bad]
    if problems:
        raise SystemExit('Local manifests failed:\n'+'\n'.join(problems))
    root.mkdir(parents=True)
    for r in RUNS:
        src=repo/'artifacts/project-airsim'/r; dst=root/'evidence/runs'/r
        for p in src.iterdir():
            if p.is_file():copy(p,dst/p.name)
        result=repo/'results/project-airsim'/r
        for p in result.iterdir():
            if p.is_file():copy(p,root/'evidence/run-records'/r/p.name)
    for p in (repo/'artifacts/project-airsim/host-setup').iterdir():
        if p.is_file():copy(p,root/'evidence/host-setup'/p.name)
    for p in (repo/'docs/project-airsim').iterdir():
        if p.name in ('findings.md','source-investigation.md','frozen-route.md'):
            copy(p,root/'evidence/docs'/p.name)
    for p in (repo/'simulators/project-airsim').iterdir():
        if p.name in ('audit.py','analyze.py','README.md','run_one.sh','setup_linux.sh','preflight_linux.sh','launch_linux.sh','collect_linux.sh'):
            copy(p,root/'evidence/code/current'/p.name)
    for p in (repo/'simulators/project-airsim/config').glob('*.json'):
        copy(p,root/'evidence/code/current/config'/p.name)
    for r in RUNS:
        rev=(repo/'results/project-airsim'/r/'code-revision.txt').read_text().strip().split()[0]
        for name in ('audit.py','analyze.py'):
            hist=subprocess.run(['git','show',f'{rev}:simulators/project-airsim/{name}'],cwd=repo,capture_output=True)
            if hist.returncode==0:
                out=root/'evidence/code/historical'/rev/name;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(hist.stdout)
    srcbase=repo/'artifacts/project-airsim/source-pinned'
    sources={
      'completion.txt': ('vehicle_apis/multirotor_api/src/multirotor_api_base.cpp',[(265,290),(800,845),(900,947),(1260,1295)]),
      'timeout.txt': ('vehicle_apis/include/common/function_caller.hpp',[(20,78)]),
      'client-timeout.txt': ('client/python/projectairsim/src/projectairsim/client.py',[(280,310),(395,425)]),
      'camera-pose.txt': ('core_sim/src/message/image_message.cpp',[(75,105),(241,258)]),
      'camera-transform.txt': ('unreal/Blocks/Plugins/ProjectAirSim/Source/ProjectAirSim/Private/Sensors/UnrealCamera.cpp',[(296,306),(338,349),(774,800)]),
      'intrinsics.txt': ('core_sim/src/sensors/camera.cpp',[(953,970)]),
      'depth-packing.txt': ('unreal/Blocks/Plugins/ProjectAirSim/Source/ProjectAirSim/Private/Sensors/ImagePackingAsyncTask.cpp',[(20,110)]),
      'build-hash.txt': ('core_sim/src/simulator.cpp',[(233,244)]),
      'build-hash-cmake.txt': ('core_sim/src/CMakeLists.txt',[(119,128)]),
    }
    (root/'evidence/source-excerpts').mkdir(parents=True)
    for name,(rel,spans) in sources.items(): excerpt(srcbase/rel,spans,root/'evidence/source-excerpts'/name,repo)
    copy(Path(__file__),root/'analysis/build_review_pack.py')
    for name in ('R4R_Project_AirSim_Audit_Revised.pptx','R4R_Project_AirSim_Audit_Revised.pdf'):
        copy(repo/'artifacts/project-airsim/deliverables'/name,root/'slides'/name)
    copy(repo/'results/project-airsim/previews/trajectory_horizontal.png',root/'analysis/trajectory_horizontal_B1.png')
    copy(repo/'results/project-airsim/previews/trajectory_vertical.png',root/'analysis/trajectory_vertical_B1.png')
    for r in B_RUNS:
        raw=repo/'artifacts/project-airsim'/r
        for axis in ('horizontal','vertical'):
            copy(raw/'analysis'/f'trajectory_{axis}.png',root/'analysis'/f'trajectory_{axis}_{r}.png')
        altitude_plot(r,raw,root/'analysis'/f'altitude_commands_{r}.png')
    selected=[]
    def add_pair(run,cam,label,rgb,depth,rationale,vehicle):
        src=repo/'artifacts/project-airsim'/run
        assert rgb['camera']==cam and depth['camera']==cam and rgb['time_stamp']==depth['time_stamp']
        dest=root/'media'/run/label
        rp=dest/Path(rgb['path']).name;dp=dest/Path(depth['path']).name
        copy(src/rgb['path'],rp);copy(src/depth['path'],dp)
        arr=np.load(dp)
        selected.append(dict(run=run,label=label,camera=cam,rgb=str(rp.relative_to(root)),depth=str(dp.relative_to(root)),timestamp=rgb['time_stamp'],
          camera_pose={k:rgb[k] for k in ('pos_x','pos_y','pos_z','rot_w','rot_x','rot_y','rot_z')},vehicle_pose=vehicle,
          dtype=str(arr.dtype),units='meters, Depth Planar',shape=list(arr.shape),max_finite_half_count=int(np.count_nonzero(arr==65504)),nonfinite_count=int(np.count_nonzero(~np.isfinite(arr))),vehicle_pose_source='achieved_ground_truth_by_phase' if run in A_RUNS else 'nearest_state_by_client_monotonic_wall',
          rationale=rationale,rgb_file=rgb['path'],depth_file=depth['path'],rgb_sha256=sha(src/rgb['path']),depth_sha256=sha(src/depth['path'])))
    for run,cam,phases in [(RUNS[0],'DownCamera',['base']),(RUNS[1],'DownCamera',['base']),(RUNS[7],'DownCamera',['base','horizontal_plus_2m','vertical_up_1m','heading_plus_30deg']),(RUNS[7],'ForwardCamera',['base'])]:
        raw=repo/'artifacts/project-airsim'/run
        requests=rows(raw/'requests.jsonl'); images=rows(raw/'images.jsonl'); vehicles=rows(raw/'actual_vehicle.jsonl')
        phase_ach={x['phase']:x['achieved'] for x in vehicles}
        for phase in phases:
            def pick(kind):
                req=[x for x in requests if x['camera']==cam and x['kind']==kind and x['phase']==phase]
                assert len(req)==1,(run,cam,phase,kind)
                candidates=[x for x in images if x['camera']==cam and x['image_type']==(0 if kind=='rgb' else 1)]
                return min(candidates,key=lambda x:abs(x['wall_monotonic_ns']-req[0]['request_end']['wall_monotonic_ns']))
            add_pair(run,cam,phase,pick('rgb'),pick('depth'),
              'Original tilted mount comparison' if run in RUNS[:2] else 'Forward max-finite-depth and edge-structure inspection' if cam=='ForwardCamera' else 'Corrected downward pose sequence phase',phase_ach[phase])
    for run in B_RUNS:
        raw=repo/'artifacts/project-airsim'/run; acts=rows(raw/'actions.jsonl'); images=rows(raw/'images.jsonl');states=rows(raw/'actual_vehicle.jsonl')
        starts={x['phase']:x for x in acts if x.get('event')=='start'}
        ends={x['phase']:x for x in acts if x.get('event')=='complete'}
        base_rgb=min((x for x in images if x['camera']=='ForwardCamera' and x['image_type']==0),key=lambda x:x['wall_monotonic_ns'])
        base_depth=next(x for x in images if x['camera']=='ForwardCamera' and x['image_type']==1 and x['time_stamp']==base_rgb['time_stamp'])
        add_pair(run,'ForwardCamera','base',base_rgb,base_depth,'B spawn/base camera before takeoff',nearest(states,base_rgb['wall_monotonic_ns'])['native'])
        for phase in ('horizontal','vertical_up','yaw_plus_30'):
            tick=(starts[phase]['wall_monotonic_ns']+ends[phase]['wall_monotonic_ns'])//2
            candidates=[x for x in images if x['camera']=='ForwardCamera' and x['image_type']==0 and starts[phase]['wall_monotonic_ns']<=x['wall_monotonic_ns']<=ends[phase]['wall_monotonic_ns']]
            rgb=min(candidates,key=lambda x:abs(x['wall_monotonic_ns']-tick))
            depth=next(x for x in images if x['camera']=='ForwardCamera' and x['image_type']==1 and x['time_stamp']==rgb['time_stamp'])
            state=nearest(states,rgb['wall_monotonic_ns'])
            add_pair(run,'ForwardCamera',phase,rgb,depth,'Representative frame within recorded B command interval',state['native'])
    # Do not put path objects or derived previews in the metadata file.
    for item in selected:
        item['rgb_path']=item.pop('rgb');item['depth_path']=item.pop('depth')
    (root/'media/selection.json').write_text(json.dumps(selected,indent=2)+'\n')
    items=[]
    for item in selected:
        x=dict(item);x['rgb']=root/item['rgb_path'];x['depth']=root/item['depth_path'];items.append(x)
    contact(items,'RGB',root/'media/contact_rgb.png')
    contact(items,'Depth Planar preview',root/'media/contact_depth.png')
    command_rows=[]
    for run in B_RUNS:
        raw=repo/'artifacts/project-airsim'/run
        acts=rows(raw/'actions.jsonl');states=rows(raw/'actual_vehicle.jsonl');route=rows(raw/'reference_route.jsonl');collisions=rows(raw/'collisions.jsonl')
        starts={x['phase']:x for x in acts if x.get('event')=='start'}
        targets={x['phase']:x for x in route}
        for a in acts:
            if a.get('event') not in ('complete','failed'):continue
            start=starts[a['phase']]; lo=start['wall_monotonic_ns'];hi=a['wall_monotonic_ns'];n0=nearest(states,lo);n1=nearest(states,hi)
            target=targets.get(a['phase'],{}).get('ned_m');pos=xyz(n1)
            err=math.dist(target,pos) if target else None
            yaw_err=abs((heading(n1)+15+180)%360-180) if a['phase']=='yaw_plus_30' else None
            command_rows.append(dict(run=run,phase=a['phase'],result=a.get('result'),exception=a.get('error'),wall_start_monotonic_ns=lo,wall_end_monotonic_ns=hi,
              wall_interval_s=round((hi-lo)/1e9,6),sampled_sim_start_ns=n0['native']['time_stamp'],sampled_sim_end_ns=n1['native']['time_stamp'],
              sampled_sim_interval_s=round((n1['native']['time_stamp']-n0['native']['time_stamp'])/1e9,6),requested_ned_m=target,
              achieved_endpoint_ned_m=pos,endpoint_error_m=err,heading_error_deg=yaw_err,
              collision_events_in_wall_interval=sum(lo<=c['wall_monotonic_ns']<=hi for c in collisions),
              nearest_end_state_offset_ms=round((n1['wall_monotonic_ns']-hi)/1e6,3)))
    (root/'analysis/commands.json').write_text(json.dumps(command_rows,indent=2)+'\n')
    with (root/'analysis/commands.csv').open('w',newline='') as f:
        fields=list(command_rows[0]);w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(command_rows)
    summaries=[]
    for run in RUNS:
        raw=repo/'artifacts/project-airsim'/run;result=repo/'results/project-airsim'/run
        count=json.loads((raw/'counts.json').read_text()) if (raw/'counts.json').is_file() else {}
        status=json.loads((raw/'run.json').read_text())
        images=rows(raw/'images.jsonl');states=rows(raw/'actual_vehicle.jsonl')
        gpu=[]
        gp=result/'gpu-timeseries.csv'
        if gp.is_file():
            for row in list(csv.DictReader(gp.open())):
                try:gpu.append((float(re.search(r'[\d.]+',row.get(' memory.used [MiB]','')).group()),float(re.search(r'[\d.]+',row.get(' utilization.gpu [%]','')).group())))
                except (AttributeError,ValueError):pass
        summaries.append(dict(run=run,status=status.get('status'),reason=status.get('reason'),received_rgb=count.get('received_rgb'),saved_rgb=count.get('saved_rgb'),
          received_depth=count.get('received_depth'),saved_depth=count.get('saved_depth'),received_state=count.get('state'),
          collisions=count.get('collision'),queue_drops=count.get('dropped_queue'),images_metadata=len(images),state_records=len(states),
          wall_state_span_s=round((states[-1]['wall_monotonic_ns']-states[0]['wall_monotonic_ns'])/1e9,3) if len(states)>1 and 'native' in states[0] else None,
          sim_state_span_s=round((states[-1]['native']['time_stamp']-states[0]['native']['time_stamp'])/1e9,3) if len(states)>1 and 'native' in states[0] else None,
          gpu_samples=len(gpu),gpu_memory_peak_mib=max((x[0] for x in gpu),default=None),gpu_util_peak_percent=max((x[1] for x in gpu),default=None)))
    (root/'analysis/run_summary.json').write_text(json.dumps(summaries,indent=2)+'\n')
    make_review(root,summaries,selected,command_rows)
    # The size manifest is checksummed by the conventional SHA256 manifest.
    paths=sorted(p for p in root.rglob('*') if p.is_file() and p.name not in ('MANIFEST.sha256','MANIFEST.tsv','review-pack.zip'))
    (root/'MANIFEST.tsv').write_text('path\tbytes\tsha256\n'+''.join(f'{p.relative_to(root)}\t{p.stat().st_size}\t{sha(p)}\n' for p in paths))
    paths.append(root/'MANIFEST.tsv')
    paths.sort()
    (root/'MANIFEST.sha256').write_text(''.join(f'{sha(p)}  {p.relative_to(root)}\n' for p in paths))
    archive=root/'review-pack.zip'
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in sorted(x for x in root.rglob('*') if x.is_file() and x!=archive):
            z.write(p,p.relative_to(root))
    print(json.dumps({'pack':str(root),'files':len(paths)+1,'archive_bytes':archive.stat().st_size,'archive_sha256':sha(archive),'media_pairs':len(selected)},indent=2))


def make_review(root,summaries,selected,commands):
    def rel(run,name):return f'evidence/runs/{run}/{name}'
    lines=[
      '# Project AirSim local evidence pack',
      '',
      'This pack contains preserved 2026-10-09 UTC run evidence and analysis computed locally afterward. No simulator was launched to make this pack. Original run records under `evidence/runs/` and `evidence/run-records/`, preserved logs, and raw `.npy` arrays under `media/` are copied byte for byte. Derived tables, plots and contact sheets are labeled analysis.',
      '',
      '## Tested inputs and data flow',
      '',
      '- Official Project AirSim v1.0.1 `Blocks-Linux-1.0.1.zip`, SHA256 `4a0c7b6de27ed32bdf4de1c31c222c19b796500108b654382b5d76b4ba000040`; indoor UE 5.2.1 packaged Blocks. Python `projectairsim==1.0.2` (no separate client build hash was recorded). Server reported build hash `deff6aa11dd8961ae5de05ea64630995a12bbf67`; pinned public source commit `09755454b8d82b0231af7e59fd1ab8f980ff32c5`. The source commit is not proof of the packaged binary build inputs. [B1 run metadata]('+rel(B_RUNS[0],'run.json')+'), [source notes](evidence/docs/source-investigation.md).',
      '- A used `non-physics`, `set_pose`, ground-truth vehicle pose and next-capture RGB/depth requests. Explicit absolute NED poses: (-1,8,-4), (1,8,-4), (1,8,-5), yaw -45° to -15°, then base. [A route]('+rel(A_RUNS[0],'reference_route.jsonl')+'), [A config]('+rel(A_RUNS[0],'resolved_config.json')+').',
      '- B used waypoint commands → Simple Flight → Fast Physics → vehicle state and native camera messages. RGB was recorded beside the route; the built-in waypoint controller did not consume it. Route: settled spawn near (-1,8,-2.693), hover, (1.5,8,-4), (1.5,8,-5), yaw -15°, hover, return (-1,8,-4), land. [Frozen route](evidence/docs/frozen-route.md), [B1 actions]('+rel(B_RUNS[0],'actions.jsonl')+').',
      '- Cameras: 400×225, horizontal 90° FOV; native K `[[200,0,200],[0,200,112.5],[0,0,1]]` pixels, pinhole/no-distortion interpretation. Capture interval 0.1 simulator seconds. Scene RGB type 0, decoded PNG; Depth Planar type 1, raw `16FC1` float16 meters. Original A DownCamera mount `(0,0,0.5)` m and pitch -11.46°; corrected A/B mount `(0,0,0)` m and pitch -90°. ForwardCamera at vehicle frame origin. [Original config]('+rel(A_RUNS[0],'resolved_config.json')+'), [corrected config]('+rel(A_RUNS[2],'resolved_config.json')+'), [camera metadata]('+rel(A_RUNS[2],'camera_info.jsonl')+'), [pinned mount transform source](evidence/source-excerpts/camera-transform.txt).',
      '- Image timestamps and state timestamps are simulator nanoseconds; `wall_monotonic_ns` is client monotonic wall time. Request round trip and callback-to-save intervals are client observations, not one-way latency or renderer time. Simulator time and wall time must not be combined. [Image metadata]('+rel(B_RUNS[0],'images.jsonl')+'), [state trace]('+rel(B_RUNS[0],'actual_vehicle.jsonl')+').',
      '',
      '## Run inventory',
      '',
      '| Run | Category and actual outcome | Received/saved RGB | Received/saved depth | State records | Collision events |',
      '| --- | --- | ---: | ---: | ---: | ---: |',
    ]
    labels={RUNS[0]:'Original A; tilted mount; pose sequence passed',RUNS[1]:'Repeated A; same tilted mount; pose sequence passed',RUNS[2]:'First smoke; blocked before capture by launch-2 crash',RUNS[3]:'Smoke retry; false tasks, landing NNG timeout',RUNS[4]:'Smoke diagnosed repair; same timeout',RUNS[5]:'Measured B1; mixed booleans, landed; full criteria failed',RUNS[6]:'Measured B2; mixed booleans, landed; full criteria failed',RUNS[7]:'Corrected A; single -90° mount run; no corrected repeat'}
    for s in summaries:
        count=lambda k:'not recorded' if s[k] is None else str(s[k])
        lines.append(f"| [{s['run']}]({rel(s['run'],'run.json')}) | {labels[s['run']]} | {count('received_rgb')}/{count('saved_rgb')} | {count('received_depth')}/{count('saved_depth')} | {count('state_records')} | {count('collisions')} |")
    lines += ['', 'The `completed` status in measured B `run.json` means the Python wrapper reached its end. It does not mean all controller commands passed. [Recorded counts](evidence/run-records/'+B_RUNS[0]+'/counts.json) and [offline inventory](analysis/run_summary.json) are separate.', '',
      '## Failure interpretation', '',
      '| Finding | Confirmed from evidence | Hypothesis or unresolved measurement |', '| --- | --- | --- |',
      '| False takeoff/vertical/return | B1/B2 action records contain server-returned `false` booleans after vehicle motion, well before the requested 25 s on sampled simulator time. No movement-phase collision event was recorded. [Command table](analysis/commands.csv), [B1 collisions]('+rel(B_RUNS[0],'collisions.jsonl')+'). | Pinned controller source allows false on movement/timeout/cancellation/incomplete path, but the packaged binary completion branch was not logged. Need server-side reason, start clock, velocity and cancel flag. [Source excerpts](evidence/source-excerpts/completion.txt), [timeout source](evidence/source-excerpts/timeout.txt). |',
      '| Runner continuation | `task_done` returned false and `flight` issued subsequent commands; both measured runs completed wrapper execution but failed full criteria. [Historical B runner](evidence/code/historical/df28a7602c72cc84f6b966708e479f8de7150893/audit.py), [B2 actions]('+rel(B_RUNS[1],'actions.jsonl')+'). | Later trajectory cannot be assigned solely to a preceding false command. |',
      '| Smoke landing timeout | Both smoke error files contain `pynng.exceptions.Timeout` tracebacks. [Smoke 2](evidence/runs/'+RUNS[3]+'/errors.jsonl), [smoke repair](evidence/runs/'+RUNS[4]+'/errors.jsonl). | No server boolean was received; server-side outcome unrecorded. The tracebacks do not show a Python `asyncio.TimeoutError`. |',
      '| SIGSEGV | Launch 2 logged Signal 11 and missing symbol file. [Full launch log](evidence/host-setup/launch2.log). | No preserved symbolized stack or core identifies the cause. A2 request causation is unproven. |',
      '| Camera mount | Original and corrected configs and direct image camera poses show the +0.5 m/-11.46° versus zero/-90° change. [Original A images]('+rel(A_RUNS[0],'images.jsonl')+'), [corrected A images]('+rel(A_RUNS[2],'images.jsonl')+'). | Corrected sequence ran once. Independent optical calibration and corrected repeatability remain unmeasured. |',
      '| Depth 65504/self-visibility | The [selected forward pair](media/selection.json) retains 65504 as raw float16. Edge RGB structures are visible. Pinned packing source copies half-float bits. [Packer excerpt](evidence/source-excerpts/depth-packing.txt). | 65504 is max finite float16, not a validated no-hit label. Material, far-range and geometry causes remain unresolved; segmentation or render-target pre-pack values were not recorded. |',
      '| Build hash | [B1 run metadata]('+rel(B_RUNS[0],'run.json')+') reports `deff6aa…`; pinned source returns a compile-time macro. [Source excerpt](evidence/source-excerpts/build-hash.txt). | Exact tested binary source/build provenance needs an attestation. Different source and server hashes alone do not prove incompatibility. |',
      '', '## Command and sensor review', '',
      'The [command table](analysis/commands.csv) aligns each B command start/end to nearest recorded vehicle samples, lists wall and sampled simulator intervals, requested target, achieved endpoint, error, and collision events whose client wall timestamp falls within the interval. It is newly computed analysis. Native [B1](evidence/runs/'+B_RUNS[0]+'/actions.jsonl) and [B2](evidence/runs/'+B_RUNS[1]+'/actions.jsonl) actions remain authoritative. Requested targets for takeoff, hover, yaw and land are commands rather than recorded Cartesian waypoint coordinates; no coordinate was invented for them.',
      '', 'Original [horizontal](analysis/trajectory_horizontal_'+B_RUNS[0]+'.png) and [vertical](analysis/trajectory_vertical_'+B_RUNS[0]+'.png) plots are copied. New [B1](analysis/altitude_commands_'+B_RUNS[0]+'.png) and [B2](analysis/altitude_commands_'+B_RUNS[1]+'.png) altitude plots align native pose to recorded client command intervals. Altitude uses `-NED Z` and wall monotonic alignment, not simulator frame stepping.',
      '', 'Measured B `errors.jsonl` is absent because those wrappers recorded no exception; a boolean `false` appears in `actions.jsonl` instead. The first smoke has no native capture trace.',
      '', 'The [RGB contact sheet](media/contact_rgb.png) and [depth contact sheet](media/contact_depth.png) preview selected raw pairs. Magenta identifies exactly 65504 in the preview; its scene meaning is unresolved. `media/selection.json` lists camera ID, filenames, timestamp, direct camera pose, nearest or achieved vehicle pose, dtype, metric planar semantics, original SHA256 and rationale for each selection. The copied `.npy` arrays remain authoritative.',
      '', '## Timing, resources and limits', '',
      '| Run | Wall / simulator state span | Saved RGB / depth | GPU peak (sampled) |', '| --- | ---: | ---: | ---: |',
    ]
    for s in summaries:
        if s['run'] not in B_RUNS:continue
        lines.append(f"| {s['run']} | {s['wall_state_span_s']} / {s['sim_state_span_s']} s | {s['saved_rgb']} / {s['saved_depth']} | {s['gpu_memory_peak_mib']} MiB, {s['gpu_util_peak_percent']}% from {s['gpu_samples']} samples |")
    lines += ['', 'The recorded host had an RTX A5000, proprietary driver 580.178.04, 503 GiB RAM and a 120 GiB overlay disk. CPU utilization was not sampled as a comparable time series. [Static memory](evidence/run-records/20261009T003453Z-flight-1/memory.txt), [disk](evidence/run-records/20261009T003453Z-flight-1/disk.txt), [GPU](evidence/run-records/20261009T003453Z-flight-1/gpu.txt). GPU samples were recorded about once per second and may miss peaks. Delivery/save rate is not pure renderer FPS. The native engine did not expose a dropped-capture count or one-way sensor latency; received and saved counts cannot establish expected capture count. [Original GPU CSV](evidence/run-records/'+B_RUNS[0]+'/gpu-timeseries.csv), [counts](evidence/run-records/'+B_RUNS[0]+'/counts.json), [offline summary](analysis/run_summary.json).',]
    lines += ['', '## Record-level evidence locators', '',
      '| Claim | Exact record or interval |', '| --- | --- |',
      '| Original mount and corrected mount | Original A1 `resolved_config.json` DownCamera `origin`; A1 `images.jsonl` DownCamera base RGB `time_stamp=266181773434002`, `pos_z=-3.5`; corrected A `resolved_config.json` DownCamera `origin`; corrected base RGB `time_stamp=266896914973047`, `pos_z=-4.0`. [Original](evidence/runs/'+A_RUNS[0]+'/images.jsonl), [corrected](evidence/runs/'+A_RUNS[2]+'/images.jsonl). |',
      '| Pose replay/freshness | `phase=base`, `horizontal_plus_2m`, `vertical_up_1m`, `heading_plus_30deg`, `return_base` in each A `reference_route.jsonl` and `actual_vehicle.jsonl`; per-camera `freshness.jsonl` records have matching phase and timestamp. [Corrected freshness](evidence/runs/'+A_RUNS[2]+'/freshness.jsonl). |',
      '| SIGSEGV | [Full launch2.log](evidence/host-setup/launch2.log), lines 4–10: Signal 11, missing `.sym`, segmentation fault. No stack included. |',
      '| 65504 and possible self-visibility | Corrected A ForwardCamera base RGB/depth both `time_stamp=266897316466777`; `media/selection.json` records original filenames, camera pose and pixel count. [Raw pair](media/20261009T003933Z-pose-corrected/base/ForwardCamera_0001.npy). |',
      '| Package/build | B1 `run.json` keys `server_commit`, `source_commit`, `client_version`; [package acquisition](evidence/host-setup/download.log) and [recorded config hashes](evidence/run-records/'+B_RUNS[0]+'/config-sha256.txt). |',
    ]
    for c in commands:
        if c['result'] is False:
            lines.append(f"| {c['run']} `{c['phase']}` server `false` | [actions]({rel(c['run'],'actions.jsonl')}) client monotonic `{c['wall_start_monotonic_ns']}–{c['wall_end_monotonic_ns']}` ns; nearest [state]({rel(c['run'],'actual_vehicle.jsonl')}) simulator `{c['sampled_sim_start_ns']}–{c['sampled_sim_end_ns']}` ns; [collisions]({rel(c['run'],'collisions.jsonl')}). |")
    lines += ['', '## Provenance, reproduction and missing evidence', '',
      '- Each `evidence/run-records/<run>/` contains the historical revision, command, package freeze, config hashes and original manifest. `evidence/runs/<run>/resolved_config.json` is the exact resolved runtime configuration where a run started. The first smoke has no runtime records because it was blocked before launch. [Runner notes](evidence/code/current/README.md).',
      '- To regenerate the pack from the complete verified local worktree: `python3 analysis/build_review_pack.py /path/to/R4R-Sims-worktree` in an empty output slot. The script refuses to overwrite an existing pack. This command is offline only.',
      '- Historical runner revisions are copied under `evidence/code/historical/<commit>/`; the current runner and analyzer are under `evidence/code/current/`. Source excerpts identify pinned source paths, lines and original file hashes. They support possible mechanisms, not an assertion that the packaged binary followed a particular branch.',
      '- This pack can reproduce **offline analysis** from preserved records. Run `python3 evidence/code/current/analyze.py <full-raw-run-dir> <output-dir>` only in a separate output directory with its original Python requirements. The pack contains selected raw images, not full capture sequences, so video reconstruction from the pack alone is unavailable. To check integrity: `sha256sum -c MANIFEST.sha256` from the extracted pack root (or `shasum -a 256 -c MANIFEST.sha256` on macOS).',
      '- Never recorded: a symbolized SIGSEGV stack/core, server-side command completion reason and matched request timeline, pre-pack depth render-target values or segmentation for selected pixels, independently calibrated real camera/dynamics, approved real reconstruction/held-out imagery and policy task assets. The cleared rental instance cannot recover these. A future targeted run could instrument one command and depth/segmentation pixels; none was performed here.',
      '', '## Slides', '',
      '[Revised PPTX](slides/R4R_Project_AirSim_Audit_Revised.pptx) and [revised PDF](slides/R4R_Project_AirSim_Audit_Revised.pdf) are preserved from the prior analysis. Their review does not constitute new simulator verification.',
      '', 'The [size and hash manifest](MANIFEST.tsv) lists bytes and SHA256 for every evidence file. The [SHA256 verification list](MANIFEST.sha256) also covers that size manifest. The archive is an uploadable copy of this expanded pack.',
    ]
    (root/'review.md').write_text('\n'.join(lines)+'\n')


if __name__=='__main__':
    if len(sys.argv)!=2:raise SystemExit('usage: build_review_pack.py /path/to/R4R-Sims-worktree')
    main(Path(sys.argv[1]))
