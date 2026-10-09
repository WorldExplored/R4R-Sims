"""Executed over SSH on the user-authorized A5000 only. No process termination."""
import hashlib,json,os,shutil,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path

PLAN = {'instance': '63.141.33.148:22134', 'gpu': 'RTX A5000', 'remove_paths': ['/root/R4R-Sims-unreal-audit', '/root/R4R-Sims', '/workspace/r4r_assets', '/tmp/r4r-strace-apt.log', '/tmp/r4r-vulkan.stdout', '/tmp/r4r-vulkan.stderr', '/tmp/r4r-vulkan.strace', '/tmp/r4r-libegl-apt.log', '/tmp/r4r-blocks-smoke.log', '/tmp/r4r-ue-home', '/tmp/r4r-ue-assets', '/tmp/Blocks', '/tmp/r4r-pip.log', '/tmp/r4r-pip-deps.log', '/tmp/r4r-pip-airsim.log', '/tmp/r4r-pip-wheel.log', '/tmp/r4r-pip-repin.log', '/tmp/r4r-rpc-parent.pid', '/tmp/r4r-rpc-smoke.log', '/tmp/r4r-preflight.json', '/tmp/r4r-current-a-id', '/tmp/r4r-tmux-apt.log', '/tmp/ue-20261008T215142Z-a-f0246d36-launch.log', '/tmp/ue-20261008T215142Z-a-f0246d36-supervisor.log', '/tmp/r4r-pull.log', '/tmp/ue-20261008T215319Z-a-5fe9b7c3-launch.log', '/tmp/ue-20261008T215319Z-a-5fe9b7c3-supervisor.log', '/tmp/r4r-plugin-clone.log', '/tmp/r4r-current-b-id', '/tmp/ue-20261008T215415Z-b-e868ec1c-launch.log', '/tmp/ue-20261008T215415Z-b-e868ec1c-supervisor.log', '/tmp/r4r-rsync-apt.log', '/tmp/ue-20261008T215611Z-b-d415e2e7-launch.log', '/tmp/ue-20261008T215611Z-b-d415e2e7-supervisor.log', '/tmp/ue-20261008T215758Z-b-33710b89-launch.log', '/tmp/ue-20261008T215758Z-b-33710b89-supervisor.log', '/tmp/r4r-matplotlib-pip.log', '/tmp/r4r-analysis-separate.log', '/tmp/r4r-analysis-pip.log', '/tmp/r4r-ffmpeg-apt.log', '/tmp/r4r-final-b-id', '/tmp/ue-20261008T220223Z-b-eddeea80-launch.log', '/tmp/ue-20261008T220223Z-b-eddeea80-supervisor.log', '/tmp/r4r-landing-check-id', '/tmp/ue-20261008T220451Z-b-a3d4be49-launch.log', '/tmp/ue-20261008T220451Z-b-a3d4be49-supervisor.log', '/tmp/unzip-install.log', '/tmp/r4r-ue55-installed', '/tmp/r4r-splat-build.sh', '/tmp/r4r-splat-active-id', '/tmp/r4r-splat-output-ue-20261008T224031Z-s-fe9a3ea3', '/tmp/r4r-splat-capture-ue-20261008T224031Z-s-fe9a3ea3.py', '/tmp/r4r-splat-control-launch.sh', '/tmp/r4r-splat-home-ue-20261008T224031Z-s-fe9a3ea3', '/tmp/Zen_12529_Startup', '/tmp/r4r-splat-control.py', '/tmp/UnrealBuildTool', '/tmp/uba_shm_locks', '/tmp/r4r-splat-render.sh', '/tmp/r4r-splat-project', '/tmp/r4r-splat-output', '/tmp/r4r-splat-home', '/tmp/r4r-splat-capture.py', '/tmp/r4r-vase.ply', '/tmp/UnrealEditor-Cmd', '/tmp/Zen_9390_Startup', '/tmp/zen_8558', '/tmp/Zen_17499_Startup', '/tmp/ShaderCompileWorker', '/tmp/r4r-splat-gpu.sh', '/tmp/r4r-splat-render-retry.sh', '/tmp/r4r-splat-capture-fixed.py', '/tmp/r4r-splat-launch-retry.sh', '/tmp/r4r-splat-project-ue-20261008T223559Z-s-8c7e26a7', '/tmp/r4r-splat-output-ue-20261008T223559Z-s-8c7e26a7', '/tmp/r4r-splat-home-ue-20261008T223559Z-s-8c7e26a7', '/tmp/r4r-splat-capture-ue-20261008T223559Z-s-8c7e26a7.py', '/tmp/r4r-vase-ue-20261008T223559Z-s-8c7e26a7.ply', '/tmp/Zen_10934_Startup', '/tmp/r4r-splat-launch-third.sh', '/tmp/r4r-splat-project-ue-20261008T224031Z-s-fe9a3ea3', '/tmp/r4r-vase-ue-20261008T224031Z-s-fe9a3ea3.ply', '/tmp/r4r-splat-control-active-id', '/tmp/r4r-splat-control-output-ue-20261008T224552Z-s-control-10f8cdbd', '/tmp/Zen_14121_Startup', '/tmp/r4r-splat-tick-control.py', '/tmp/r4r-splat-tick-launch.sh', '/tmp/r4r-splat-tick-active-id', '/tmp/r4r-splat-tick-output-ue-20261008T224847Z-s-control-83b490d9', '/tmp/Zen_15000_Startup', '/tmp/r4r-splat-channel-control.py', '/tmp/r4r-splat-channel-launch.sh', '/tmp/r4r-splat-channel-active-id', '/tmp/r4r-splat-channel-output-ue-20261008T225105Z-s-control-e488bef0', '/tmp/Zen_15938_Startup', '/tmp/r4r-focused-camera-id', '/tmp/Zen_18994_Startup', '/tmp/r4r-validation-home-ue-20261008T232215Z-yaw-6b9a9962', '/tmp/r4r-focused-landing-id', '/tmp/r4r-validation-home-ue-20261008T232324Z-land-isolated-a3227c9a', '/tmp/splat_light_control.py', '/tmp/r4r-splat-light-launch.sh', '/tmp/r4r-splat-light-control.py', '/tmp/r4r-splat-light-active-id', '/tmp/r4r-splat-light-output-ue-20261008T232449Z-s-light-1f298556', '/tmp/r4r-focused-landing-settled-id', '/tmp/r4r-validation-home-ue-20261008T232549Z-land-settled-04b41479', '/tmp/r4r-focused-landing-observed-id', '/tmp/r4r-validation-home-ue-20261008T232723Z-land-observed-c1f84706', '/tmp/r4r-splat-light-output-ue-20261008T232833Z-s-light-573e44a0', '/tmp/r4r_assets', '/workspace/unreal-final-backup-20261008'], 'backup_dir': '/workspace/unreal-final-backup-20261008', 'preserve': ['running instance', 'SSH service and keys', 'NVIDIA driver and GPU runtime', 'system packages'], 'excluded_reproducible_content': ['expanded engine and Blocks archives already locally SHA-256 verified', 'compiled plugin already locally source-manifest verified', 'Python venvs reproducible from recorded package versions', 'derived-data/shader caches and editor trace stores'], 'backup_local_path': '/Users/srreyanshsethi/Downloads/AL/R4R-Sims/artifacts/unreal/unreal-final-backup-20261008', 'expected_backup_manifest_sha256': '9a79eb23140bf3affc152829d821fd32e60ee7e9cb77bb7c75029bcf330d3b88', 'local_source_manifest_verified_files': 95, 'local_source_manifest_verified_bytes': 6321206, 'published_audit_commit': '4d07033ebf2a9e58d37687f837849dc9c88962ad', 'expected_published_code_sha256': {'/root/R4R-Sims/simulators/unreal/analyze.py': '7f136320a50b93f937f4c5b8ed127618ebf4aaeef686e52cec82595efcf0ee8e', '/root/R4R-Sims/simulators/unreal/manifest.py': 'eda17f074ab56fb686043281174d50ed0f08cedbc8fae4b7ff737cebf46134c2', '/root/R4R-Sims-unreal-audit/simulators/unreal/focused_analyze.py': '0fd44d97824501ddc144bbec9d9d5f417e3e86c345b83f830ef9edef72915638', '/root/R4R-Sims-unreal-audit/simulators/unreal/focused_validation.py': '0365b28c7b3c486edcfb48f1b7d8f5e432a4315658f3842d962dd4cddcfc2472'}}
def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
gpu=subprocess.check_output(['nvidia-smi','--query-gpu=name','--format=csv,noheader'],text=True).strip()
assert gpu=='NVIDIA RTX A5000', 'Wrong GPU host; cleanup refused'
processes=subprocess.check_output(['ps','-eo','comm='],text=True).splitlines()
assert not any(p.strip() in {'Blocks','UnrealEditor','UnrealEditor-Cmd','ShaderCompileWorker'} for p in processes), 'An Unreal process is active'
backup=Path(PLAN['backup_dir'])
assert digest(backup/'source-manifest.json')==PLAN['expected_backup_manifest_sha256'], 'Backup manifest changed'
for path,expected in PLAN['expected_published_code_sha256'].items():
    assert digest(path)==expected, 'Unpublished code change: '+path
for repo,expected in [('/root/R4R-Sims',{' M simulators/unreal/analyze.py','?? simulators/unreal/manifest.py'}),('/root/R4R-Sims-unreal-audit',{'?? results/unreal/focused-validation-20261008T232000Z/','?? simulators/unreal/focused_analyze.py','?? simulators/unreal/focused_validation.py'})]:
    actual=set(subprocess.check_output(['git','-C',repo,'status','--short'],text=True).splitlines())
    assert actual==expected, 'Unexpected checkout changes; cleanup refused: '+repo
top={'/root/R4R-Sims','/root/R4R-Sims-unreal-audit','/workspace/r4r_assets',PLAN['backup_dir']}
temp_exact={'r4r_assets','Blocks','ShaderCompileWorker','UnrealBuildTool','UnrealEditor-Cmd','zen_8558','uba_shm_locks','splat_light_control.py','unzip-install.log'}
for raw in PLAN['remove_paths']:
    p=Path(raw)
    assert raw==os.path.normpath(raw)
    assert raw in top or (p.parent==Path('/tmp') and (p.name.startswith(('r4r-','ue-20261008','Zen_')) or p.name in temp_exact)), 'Path outside cleanup scope: '+raw
def space():
    return {p:{'total_bytes':shutil.disk_usage(p).total,'free_bytes':shutil.disk_usage(p).free} for p in ['/root','/workspace']}
report={'instance':PLAN['instance'],'gpu':gpu,'started_utc':datetime.now(timezone.utc).isoformat(),'disk_before':space(),'removed_paths':[],'already_absent':[],'errors':[],'instance_terminated':False,'processes_stopped':False,'ssh_or_driver_configuration_changed':False}
for raw in PLAN['remove_paths']:
    p=Path(raw)
    try:
        if p.is_symlink():p.unlink()
        elif p.is_dir():shutil.rmtree(p)
        elif p.exists():p.unlink()
        else:report['already_absent'].append(raw);continue
        report['removed_paths'].append(raw)
    except Exception as e:report['errors'].append({'path':raw,'error':repr(e)})
os.sync()
report['remaining_paths']=[p for p in PLAN['remove_paths'] if os.path.lexists(p)]
report['disk_after']=space();report['finished_utc']=datetime.now(timezone.utc).isoformat()
report['status']='completed' if not report['errors'] and not report['remaining_paths'] else 'partial_failure'
print(json.dumps(report,indent=2),flush=True)
sys.exit(0 if report['status']=='completed' else 1)
