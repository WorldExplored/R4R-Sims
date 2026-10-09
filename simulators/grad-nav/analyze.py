"""Verify transferred evidence and derive figures from actual records."""
import argparse,hashlib,json,pathlib

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()

def main():
    p=argparse.ArgumentParser();p.add_argument('root',type=pathlib.Path);a=p.parse_args();r=a.root
    import numpy as np
    from PIL import Image
    raw=r/'artifacts/grad-nav';errors=[];checks=[];runs=[]
    for folder in sorted(raw.glob('20*')):
        if not folder.is_dir():continue
        manifest=folder/'manifest.json'
        if not manifest.exists():errors.append(f'{folder}:missing manifest');continue
        items=json.loads(manifest.read_text())
        for item in items:
            f=folder/item['path']
            if not f.exists() or f.stat().st_size!=item['bytes'] or sha(f)!=item['sha256']:
                errors.append(str(f)+':checksum mismatch');continue
            if f.suffix=='.json':json.loads(f.read_text())
            elif f.suffix=='.jsonl':
                for line in f.read_text().splitlines():json.loads(line)
            elif f.suffix=='.png':
                with Image.open(f) as im:im.load()
            elif f.suffix=='.npy':
                x=np.load(f,allow_pickle=False)
                if not np.isfinite(x).all():errors.append(str(f)+':nonfinite depth')
        run=json.loads((folder/'run.json').read_text());runs.append(run)
        checks.append({'run_id':folder.name,'files':len(items),'bytes':sum(x['bytes'] for x in items),'verified':True})
        small=r/'results/grad-nav'/folder.name;small.mkdir(parents=True,exist_ok=True)
        if run['status']=='completed' and run['mode'] in ['force','smoke','recovery']:
            states=[json.loads(s) for s in (folder/'state.jsonl').read_text().splitlines()]
            xs=[s['sim_time_s'] for s in states];ys=[s['position_m'][2] for s in states]
            (small/'height-series.json').write_text(json.dumps({'simulation_time_s':xs,'height_m':ys,'setpoint_m':1.25},indent=2)+'\n')
        if run['status']=='completed' and run['mode'] in ['a','d']:
            pattern='*-author.png' if run['mode']=='a' else '*-coupled.png'
            paths=sorted((folder/'frames').glob(pattern));selected=paths if run['mode']=='a' else [paths[0],paths[len(paths)//2],paths[-1]]
            if selected:
                imgs=[Image.open(f).convert('RGB') for f in selected]
                contact=Image.new('RGB',(sum(x.width for x in imgs),max(x.height for x in imgs)))
                x=0
                for im in imgs:contact.paste(im,(x,0));x+=im.width;im.close()
                contact.save(small/'preview.png')
    scientific=raw/'preflight/scientific-manifest.json'
    sci_count=sci_bytes=0
    if scientific.exists():
        for item in json.loads(scientific.read_text()):
            f=raw/'scientific-inputs'/item['path']
            if not f.exists() or f.stat().st_size!=item['bytes'] or sha(f)!=item['sha256']:errors.append(str(f)+':scientific input checksum mismatch');continue
            if f.suffix=='.png':
                with Image.open(f) as im:im.load()
            sci_count+=1;sci_bytes+=item['bytes']
    report={'runs':checks,'scientific_files_verified':sci_count,'scientific_bytes':sci_bytes,'errors':errors,
        'local_root':str(r.resolve()),'remote_deleted':False,'instance_terminated':False}
    (r/'docs/grad-nav/preservation.json').write_text(json.dumps(report,indent=2)+'\n')
    (r/'docs/grad-nav/run-index.json').write_text(json.dumps(runs,indent=2)+'\n')
    print(json.dumps(report,indent=2))
    if errors:raise SystemExit(1)

if __name__=='__main__':main()
