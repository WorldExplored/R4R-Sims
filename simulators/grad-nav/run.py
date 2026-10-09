"""Bounded subprocess execution, logs, GPU sampling and settled manifest."""
import argparse, datetime, hashlib, json, os, pathlib, subprocess, sys, threading, time, traceback, uuid

def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()

def main():
    p=argparse.ArgumentParser();p.add_argument('mode');p.add_argument('--root',type=pathlib.Path,required=True)
    p.add_argument('--upstream',type=pathlib.Path,required=True);p.add_argument('--timeout',type=int,default=90);a=p.parse_args()
    now=datetime.datetime.now(datetime.timezone.utc);rid=now.strftime('%Y%m%dT%H%M%SZ')+'-'+a.mode+'-'+uuid.uuid4().hex[:6]
    raw=a.root/'artifacts/grad-nav'/rid;small=a.root/'results/grad-nav'/rid
    raw.mkdir(parents=True);small.mkdir(parents=True)
    cmd=[sys.executable,str(a.root/('simulators/grad-nav/render.py' if a.mode in ['a','d'] else 'simulators/grad-nav/probe.py')),a.mode,'--upstream',str(a.upstream),'--out',str(raw)]
    def capture(c):return subprocess.run(c,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT).stdout
    metadata={'run_id':rid,'mode':a.mode,'start_utc':now.isoformat(),'timeout_s':a.timeout,'command':cmd,'cwd':str(pathlib.Path.cwd()),
      'candidate_commit':capture(['git','-C',str(a.root),'rev-parse','HEAD']).strip(),
      'upstream_commit':capture(['git','-C',str(a.upstream),'rev-parse','HEAD']).strip(),
      'upstream_status':capture(['git','-C',str(a.upstream),'status','--short']),
      'input_path':str(a.upstream),'output_path':str(raw),'policy_weights':'none','scene':'gate_mid' if a.mode in ['a','d'] else 'none','seed':0,
      'status':'running','environment_file':'environment.txt','navigation_learned_components_used':False}
    (raw/'run.json').write_text(json.dumps(metadata,indent=2)+'\n')
    (raw/'commands.log').write_text(json.dumps(cmd)+'\n')
    (raw/'environment.txt').write_text(capture(['uname','-a'])+capture([sys.executable,'-m','pip','freeze'])+capture(['nvidia-smi'])+capture(['df','-h',str(a.root)]))
    (raw/'upstream.patch').write_text(capture(['git','-C',str(a.upstream),'diff'])+capture(['git','-C',str(a.upstream),'diff','--staged']))
    stop=threading.Event()
    def monitor():
        with (raw/'gpu.jsonl').open('w') as f:
            while not stop.is_set():
                q=capture(['nvidia-smi','--query-gpu=timestamp,memory.used,memory.total,utilization.gpu','--format=csv,noheader,nounits'])
                f.write(json.dumps({'wall_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sample':q.strip()})+'\n');f.flush();stop.wait(1)
    t=threading.Thread(target=monitor);t.start();start=time.perf_counter()
    with (raw/'console.log').open('w') as log:
        child=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
        try:code=child.wait(timeout=a.timeout)
        except subprocess.TimeoutExpired:
            import signal;os.killpg(child.pid,signal.SIGTERM)
            try:child.wait(timeout=10)
            except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);child.wait()
            code=124
    stop.set();t.join()
    metadata.update(exit_status=code,status='completed' if code==0 else 'failed',wall_s=time.perf_counter()-start,
        end_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),timed_out=code==124)
    (raw/'run.json').write_text(json.dumps(metadata,indent=2)+'\n')
    for name in ['run.json','commands.log','console.log','environment.txt','upstream.patch','config.json','camera_config.json','resolved-config.yml','metrics.json','conversion.json','gpu.jsonl']:
        if (raw/name).exists():(small/name).write_bytes((raw/name).read_bytes())
    manifest=[{'path':str(x.relative_to(raw)),'bytes':x.stat().st_size,'sha256':digest(x)} for x in sorted(raw.rglob('*')) if x.is_file()]
    (raw/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');(small/'manifest.json').write_bytes((raw/'manifest.json').read_bytes())
    print(json.dumps({'run_id':rid,'status':metadata['status'],'exit_status':code,'raw':str(raw),'small':str(small)}),flush=True)
    return code

if __name__=='__main__':sys.exit(main())
