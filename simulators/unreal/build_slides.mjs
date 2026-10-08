/** Build the evidence-based Unreal audit deck from verified local run artifacts. */
import fs from 'node:fs/promises';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
const root = path.resolve(import.meta.dirname, '../..');
const evidence = process.env.UNREAL_ARTIFACT_ROOT || path.join(root, 'artifacts/unreal');
const skillDir = process.env.SKILL_DIR;
const python = process.env.RUNTIME_PYTHON;
const runtimeNodeModules = process.env.RUNTIME_NODE_MODULES;
if (!skillDir || !python || !runtimeNodeModules) throw new Error('Set SKILL_DIR, RUNTIME_PYTHON and RUNTIME_NODE_MODULES from bundled presentation runtime');
const build = path.join(root, '.codex-unreal-closeout-deck-build');
const output = path.join(root, 'docs/unreal/Unreal_R4R_Audit_2026-10-08_v3.pptx');
await fs.mkdir(build, {recursive:true});
const { Presentation, PresentationFile } = await import(pathToFileURL(path.join(runtimeNodeModules,'@oai/artifact-tool/dist/artifact_tool.mjs')).href);
const { finalizePresentation } = await import(pathToFileURL(path.join(skillDir,'container_tools/artifact_tool_utils.mjs')).href);
const p = Presentation.create({slideSize:{width:1280,height:720}});
const C = {ink:'#182C3A', blue:'#125C78', muted:'#536875', light:'#E4EAED', white:'#FFFFFF', red:'#9A332F', green:'#176D5A'};
const font='Arial';
function slide(title, note='') {
  const s=p.slides.add(); s.background.fill=C.white;
  if (title) tx(s,title,62,40,1150,72,36,C.ink,true);
  if (note) s.speakerNotes.textFrame.setText(note);
  return s;
}
function tx(s,text,left,top,width,height,size=23,color=C.ink,bold=false) {
  const sh=s.shapes.add({geometry:'textbox',position:{left,top,width,height},fill:'none',line:{fill:'none',width:0}});
  sh.text=text; sh.text.style={typeface:font,fontSize:size,bold,color,autoFit:'shrinkText'};return sh;
}
async function img(s,file,left,top,width,height,alt) {
  s.images.add({blob:new Uint8Array(await fs.readFile(file)),contentType:'image/png',alt,fit:'contain',position:{left,top,width,height}});
}
const a='ue-20261008T215319Z-a-5fe9b7c3';
const b='ue-20261008T220451Z-b-a3d4be49';
const aDir=path.join(evidence,a), bDir=path.join(evidence,b);
const sControl='ue-20261008T232833Z-s-light-573e44a0';
const sDir=path.join(evidence,sControl);
const yawDir=path.join(evidence,'ue-20261008T232215Z-yaw-6b9a9962');
const focused=path.join(root,'results/unreal/focused-validation-20261008T232000Z');
const recovery=JSON.parse(await fs.readFile(path.join(root,'results/unreal/closeout-20261008/recovery.json'),'utf8'));

{
  const s=p.slides.add();s.background.fill=C.ink;
  tx(s,'Unreal Engine in the Real4Real audit',66,118,1130,130,53,C.white,true);
  tx(s,'Camera checks pass. Flight acceptance and splat appearance remain unresolved.',70,300,1080,100,29,'#C9DCE4');
  tx(s,'8 October 2026  ·  Focused validation included  ·  Complete R4R workflow unproven',70,578,1080,60,21,'#C9DCE4');
  s.speakerNotes.textFrame.setText('Updated from preserved v2. Sources: original runs, focused-validation.md and closeout recovery/dependency records. No additional GPU experiment was started for this update.');
}
{
  const s=slide('Real4Real question and experiment scope','Internal project context: docs/r4r-audit-context.md, 2026-10-08. No approved AirLab dataset was supplied.');
  tx(s,'Small real outdoor capture',70,156,500,54,29,C.blue,true);
  tx(s,'Reconstruct one site, then render trustworthy observations for NEW drone camera routes in residential, suburban and campus scenes below 100 m.',70,218,1050,122,27);
  tx(s,'Capture at 15 m → render at 50 m',70,388,720,56,27,C.red,true);
  tx(s,'Open research goal. Blocks cannot answer it.',70,449,850,48,25);
  tx(s,'A: pose replay    B: scripted closed loop    C: released learned policy    S: UE Gaussian splat',70,577,1110,52,22,C.muted);
}
{
  const s=slide('Native Blocks system path','Microsoft AirSim source commit 96235148a332fe7cb3d3525a0720e26faaca99e0; Linux Blocks v1.8.1 release ZIP SHA-256 563e1da1b5d7303b9405c8736243ea92ab0a011b96a561f26f17563d105a404f. See docs/unreal/sources.md.');
  tx(s,'A  Target poses → ComputerVision pose RPC → UE scene → RGB + planar depth',70,170,1110,80,26,C.blue);
  tx(s,'B  Estimated position → P velocity script → SimpleFlight → FastPhysicsEngine',70,280,1110,80,26,C.blue);
  tx(s,'    UE supplies rendered camera views and scene collision; AirSim logs state.',70,360,1090,65,25);
  tx(s,'C  No compatible released policy weights or task interface in Blocks.',70,490,1090,70,25,C.red);
  tx(s,'Scene: stock FlyingExampleMap. No real capture, common splat scene or held-out split.',70,604,1090,50,22,C.muted);
}
{
  const s=slide('A: eight camera poses produced eight RGB images',`Run ${a}; source-manifested local artifacts. 640x480; requested/actual rig and response camera centers matched to recorded precision. Image contact: figures/rgb-contact.png. A is not flight.`);
  await img(s,path.join(aDir,'figures/rgb-contact.png'),56,142,1168,492,'Contact sheet of eight actual Blocks camera images');
  tx(s,'NED route: 0–1 m horizontal at z = −2 m; 0.25 s pose settling',72,645,1100,38,22,C.muted);
}
{
  const s=slide('Camera sanity passed across four yaw directions','Run ue-20261008T232215Z-yaw-6b9a9962. NED fixed center (0,0,-2) m. Five actual RGB/depth pairs. Max orientation error 0.0000136604 degrees, zero position error. Adjacent distinct-yaw RGB mean absolute differences 31.29–43.08/255. Repeat-zero mean difference 0.968/255. RGB/depth timestamps differ 5.249–8.051 ms. Original eight-frame replay retained.');
  await img(s,path.join(yawDir,'yaw-contact.png'),75,140,1130,490,'Actual fixed-position yaw 0, 90, 180, minus 90 and repeat-zero images');
  tx(s,'Scene directions visibly change. Recorded centers match. RGB/depth times differ by 5–8 ms.',70,642,1110,48,22,C.muted);
}
{
  const s=slide('A: planar depth is present for all eight views',`Run ${a}; all 8 float32 480x640 arrays opened. DepthPlanar is optical-axis distance in metres. Display clipped at 50 m. First frame wall 23.09375 m; ground 6.0195 m; far/sky 13456 m. RGB timestamp only, depth timestamp not recorded.`);
  await img(s,path.join(aDir,'figures/depth-grid.png'),58,141,1164,490,'Eight measured DepthPlanar maps, displayed with 50 metre clip');
  tx(s,'First-frame wall edge matched at five tested columns; depth timestamp remains unmeasured.',70,648,1120,40,21,C.muted);
}
{
  const s=slide('B: scripted flight reached the five square waypoints',`Run ${b}, five waypoint_reached events at 0.228–0.248 m error; full run failed the final landing-state check. Actual track from vehicle_trajectory.jsonl. Baseline Ground_6 collision is recorded separately.`);
  await img(s,path.join(bDir,'figures/trajectory-xy.png'),48,156,660,506,'Measured reference versus actual XY vehicle trajectory');
  tx(s,'Reference',738,180,470,45,27,C.blue,true);
  tx(s,'1 m square; NED z = −2 m',738,225,470,54,25);
  tx(s,'Controller',738,308,470,45,27,C.blue,true);
  tx(s,'P gain 0.7; velocity clip ±0.7 m/s; 0.2 s commands; SimpleFlight inner loop',738,352,470,126,23);
  tx(s,'Five waypoint events met 0.25 m tolerance. Landing state did not confirm.',738,531,470,95,23,C.red);
}
{
  const s=slide('B still fails acceptance without route or image waits','Run ue-20261008T232723Z-land-observed-c1f84706. 177 state samples, descent median polling 4.912 Hz. Ground-relative hover 1.51–1.54 m, downward speed up to 0.290 m/s. New Ground_6 contact at 28.068 s. land RPC true at 28.152 s. Flying persisted through 38.446 s with zero velocity. takeoff RPC false despite observed airborne movement. First isolated apparent pass was rejected because no flight occurred.');
  await img(s,path.join(focused,'isolated-descent.png'),56,135,750,550,'Recorded height, vertical velocity and LandedState throughout the isolated test');
  tx(s,'Airborne hover observed',835,174,385,62,25,C.blue,true);
  tx(s,'Takeoff returned False despite achieved height.',835,248,385,86,23,C.red);
  tx(s,'Landing returned True after floor contact.',835,369,385,86,23);
  tx(s,'LandedState stayed Flying for 10 s at zero velocity.',835,493,385,112,23,C.red,true);
}
{
  const s=slide('Measured rates and resource use',`Analysis from ${b}/analysis.json, camera.jsonl, actions.jsonl, run.json and GPU JSONL. Sampled GPU usage is whole-GPU nvidia-smi, not process peak. Renderer GPU timing and policy latency were not measured.`);
  tx(s,'Native B landing-check run',72,154,1090,44,27,C.blue,true);
  const rows=[
    ['Image RPC median','3.210 s  (acquisition, transport, encoding)'],
    ['Image interval median','5.355 s  ≈ 0.187 captured images/s'],
    ['Velocity command rate','4.696 Hz median interval; 2.007 Hz over action span'],
    ['GPU memory','769 MiB sampled whole-GPU peak'],
    ['Wall / simulation time','64.75 s run / 48.83 s first-to-last state'],
    ['Video','2 FPS encoded playback; renderer throughput unmeasured']
  ];
  let y=218;for(const [k,v] of rows){tx(s,k,73,y,380,51,22,C.ink,true);tx(s,v,458,y,730,51,22,C.ink);y+=69;}
}
{
  const s=slide('Failures retained under separate run IDs','All IDs and error details are in results/unreal/ and local source-manifested artifacts. Preflight-only failure has a local supervisor log but no remote run directory/source manifest. The landing-check run had new Ground_6 contact after the spawn baseline, so landing cannot be called successful.');
  tx(s,'A startup RPC race',72,160,560,44,27,C.red,true);tx(s,'first attempt failed; next A run completed',72,204,1100,44,23);
  tx(s,'B occupied RPC port',72,286,560,44,27,C.red,true);tx(s,'supervisor output retained; process ownership fixed',72,330,1100,44,23);
  tx(s,'B spawn Ground_6 baseline',72,412,650,44,27,C.red,true);tx(s,'subsequent route checks compare collision timestamps',72,456,1100,44,23);
  tx(s,'Landing-state failure reproduced',72,538,750,44,27,C.red,true);tx(s,'Isolated airborne descent ended at contact with LandedState still Flying.',72,582,1100,65,23);
}
{
  const s=slide('Final-color capture works. Splat appearance is unvalidated',`Focused control ${sControl}, same author PLY/imported project. Corrected directional light yaw 180, intensity 10. SCS_FINAL_COLOR_LDR, RTF_RGBA8, actual camera (900,0,0) cm yaw180, HFOV60, 640x480. Mesh RGB max226, no saturation. Single splat frame max113, 0.322% pixels above10. These raw PNGs have no brightness enhancement. Initial black and saturated attempts retained. This is one-frame integration evidence, no fidelity metric.`);
  tx(s,'Corrected light direction and saturation',70,136,1120,50,27,C.blue,true);
  await img(s,path.join(sDir,'cube_final.png'),63,225,545,300,'Actual corrected final-color mesh image');
  await img(s,path.join(sDir,'splat_final.png'),672,225,545,300,'Single actual dark red splat frame without brightness enhancement');
  tx(s,'Usable mesh control, RGB max 226',70,535,530,52,22,C.green,true);
  tx(s,'Visible splat detail, RGB max 113',673,535,535,52,22,C.blue,true);
  tx(s,'Dark appearance remains unexplained. Useful fidelity, depth and collision remain unproven.',70,615,1110,60,21,C.ink);
}
{
  const s=slide('The selected importer drops higher-order SH','Pinned Italink commit 411f879985719ce69eaaf15d58152c551e2719b1. GaussianSplattingPointCloud.cpp lines204–216 collects/validates f_rest indices. Lines263–271 stores DC-derived color after sRGB-to-linear conversion. GaussianSplattingPointCloud.h lines18–55 has one Color field and no higher-order SH storage. Source URLs: https://github.com/Italink/GaussianSplattingForUnrealEngine/blob/411f879985719ce69eaaf15d58152c551e2719b1/Source/GaussianSplattingRuntime/Private/GaussianSplattingPointCloud.cpp#L204-L271 and Public/GaussianSplattingPointCloud.h#L18-L55. This is static inspection of the selected import path, not a diagnosis of the dark frame.');
  tx(s,'PLY includes higher-order appearance coefficients',70,157,1110,54,28,C.blue,true);
  tx(s,'The importer checks their fields, but stores only DC-derived color. Its point structure has no place for the higher-order coefficients.',70,231,1110,122,26);
  tx(s,'Viewing-direction appearance is lost on this path',70,402,1110,55,28,C.red,true);
  tx(s,'This limits a faithful R4R baseline when the input model uses those coefficients. It does not explain the dark red frame by itself.',70,478,1110,112,25);
  tx(s,'Next comparison: the same PLY and matched cameras, with color conversion and exposure checked.',70,626,1110,53,21,C.muted);
}
{
  const s=slide('Three ways to replace UE visuals','Architecture assessment based on source inspection and current native run. No external sensor adapter or complete UE replacement was built. UE4.27 Blocks is a packaged binary and cannot be edited as the UE5.5 splat project.');
  tx(s,'1  Splats inside UE',72,160,560,43,29,C.blue,true);
  tx(s,'Replace chosen object appearance. UE keeps world time, rendering/compositing and collision. UE5 drone layer and accurate collision geometry remain to build.',72,208,1100,88,23);
  tx(s,'2  External splat observations',72,325,650,43,29,C.blue,true);
  tx(s,'Retain AirSim/UE dynamics, SimpleFlight, collisions and other sensors. Build a synchronized pose/intrinsics, axes/scale and image-return adapter.',72,373,1100,88,23);
  tx(s,'3  UE removed',72,492,560,43,29,C.blue,true);
  tx(s,'Another simulator must own dynamics, controller, sensors, clocks, collision, logging and task evaluation. A splat renderer supplies appearance only.',72,540,1100,91,23);
}
{
  const s=slide('Applicability to R4R tasks','User scope and docs/r4r-audit-context.md. Blocks supports integration only. Outdoor scene coverage, novel views, moving objects, depth and collision are separate tests. No policy score or real drone transfer was measured.');
  tx(s,'Indoor navigation',72,162,500,43,29,C.blue,true);tx(s,'API and collision plumbing demonstrated; realistic obstacles and task thresholds absent.',72,208,1080,54,24);
  tx(s,'Outdoor navigation, sparse scenes',72,306,750,43,29,C.blue,true);tx(s,'No real reconstruction, vegetation, capture coverage or altitude extrapolation evidence.',72,352,1080,65,24);
  tx(s,'Racing',72,452,500,43,29,C.blue,true);tx(s,'No gates, racing policy or high-rate vision benchmark; captured images averaged about 0.19 Hz in flight.',72,498,1080,65,24);
  tx(s,'Complete R4R workflow remains unproven. Native integration and one splat frame leave the real-scene questions open.',72,602,1100,75,22,C.ink,true);
}
{
  const s=slide('A5000 host, storage and practical limits','Host: user-supplied RunPod Ubuntu 22.04.5, RTX A5000 24 GB, driver 580.178.04, 50 GB cgroup RAM, 120 GB root disk. Epic Linux requirements: https://dev.epicgames.com/documentation/en-us/unreal-engine/linux-development-requirements-for-unreal-engine. Source ZIP and editor sizes are in docs/unreal/assets.md. $0.30/hour was displayed by provider UI, not independently billed.');
  tx(s,'GPU experiments are paused',72,158,1080,46,29,C.blue,true);
  tx(s,'The supplied Ubuntu 22.04 A5000 proved Vulkan and offscreen rendering. Its 24 GB VRAM is headroom. Future experiments need a specific hypothesis before provisioning.',72,207,1100,95,24);
  tx(s,'Space and installation',72,336,750,46,29,C.blue,true);
  tx(s,'UE 5.5.4 archive 27.09 GB; ZIP entry sum 65.30 GB expanded. Blocks ZIP 142.5 MB / 281.3 MB expanded. Preserve about 30 GB project/cache headroom after editor extraction.',72,387,1100,103,24);
  tx(s,'Cheaper option and limits',72,524,750,46,29,C.blue,true);
  tx(s,'An 8 GB VRAM NVIDIA Vulkan VM may run packaged Blocks, consistent with Epic editor guidance, but is untested here. Original 3DGS training VRAM does not size rendering.',72,574,1100,89,23);
}
{
  const s=slide('Next scientific gate and evidence handoff','Internal R4R context; see docs/unreal/handoff.md and sources.md. Source-manifested A/B files reside under ~/Downloads/AL/R4R-Sims/artifacts/unreal/. Public source URLs and commits are in sources.md.');
  tx(s,'Same-PLY rendering comparison first',72,155,1000,47,30,C.blue,true);
  tx(s,'Reference splat renderer and UE at matched poses, intrinsics and resolution. Check retained attributes, color conversion and exposure before another scene.',72,205,1100,112,24);
  tx(s,'Calibrated outdoor holdout afterward',72,350,1000,47,30,C.blue,true);
  tx(s,'Approved real training capture and separate held-out views, including sparse regions and new altitude. Capture at 15 m and render at 50 m remains unresolved.',72,400,1100,105,24);
  tx(s,'Flight-stack diagnosis is separate',72,542,1000,47,30,C.ink,true);
  tx(s,'Landing RPC and SimpleFlight LandedState use different predicates. Instrument their inputs if this control stack is retained. No condition failure is identified yet.',72,590,1100,82,23);
}
{
  const s=slide('Local recovery verified. No other audit uses this host','Closeout recovery.json rechecks VM-source manifests, archive hashes, compiled plugin and imported project assets. Instance-dependencies.json records a read-only host process/GPU snapshot and inspected task records. TRAVELUAV is active on separate A6000 host 209.137.198.205. RFLY SIM, GRADNAV and AIRSIM are idle phase-1 work. No simulator or GPU consumer was observed on 63.141.33.148:22134. This is an observed dependency check, not a provider-wide guarantee. Instance remains running.');
  tx(s,`${recovery.runs.length} run folders matched VM-created manifests`,72,160,1100,50,28,C.green,true);
  tx(s,'Blocks and sample ZIPs, full UE 5.5.4 archive, compiled plugin, imported map and point-cloud asset are recoverable locally.',72,230,1100,104,25);
  tx(s,'TRAVELUAV uses a separate A6000 instance',72,385,1100,50,28,C.blue,true);
  tx(s,'Other listed audits are idle preparation tasks. This A5000 has no simulator or GPU process running. No dependency on it was found.',72,455,1100,105,25);
  tx(s,'v2 and earlier evidence remain preserved. The instance has not been terminated.',72,620,1100,53,22,C.muted);
}

const candidate=path.join(build,'candidate.pptx');
await (await PresentationFile.exportPptx(p)).save(candidate);
const result=await finalizePresentation({workspaceDir:root,candidatePath:candidate,finalPath:output,
  pythonExecutable:python,
  integrityValidatorPath:path.join(skillDir,'container_tools/inspect_presentation_package_integrity.py'),
  layoutValidatorPath:path.join(skillDir,'container_tools/inspect_presentation_layout_geometry.py'),
  layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-heading-fit'],
  fontPolicy:{basis:'design',families:[font]},verifyArtifactToolImport:true,
  receiptPath:path.join(build,'validation.json')});
console.log(JSON.stringify({output,result}));
