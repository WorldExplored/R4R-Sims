import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {Presentation,PresentationFile} from '@oai/artifact-tool';
const root='/Users/srreyanshsethi/Downloads/AL/R4R-Sims-grad-nav';
const workspace='/private/tmp/gradnav-decision-deck';
const skill=process.env.SKILL_DIR;
const {finalizePresentation}=await import(pathToFileURL(path.join(skill,'container_tools/artifact_tool_utils.mjs')).href);
const P=Presentation.create({slideSize:{width:1280,height:720}}),family='Helvetica Neue';
const ink='#17313E',muted='#506774',accent='#187C88',alert='#A84E35';
function text(s,v,x,y,w,h,size=28,color=ink,bold=false){let n=s.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});n.text=v;n.text.style={typeface:family,fontSize:size,color,bold,autoFit:'none'};return n;}
function slide(title,notes){let s=P.slides.add();s.background.fill='#F8FAFB';text(s,title,64,42,1152,100,42,ink,true);text(s,'AirLab / 8 October 2026 / training-view diagnostic',64,670,1000,30,18,muted);text(s,String(P.slides.items.length),1180,670,40,30,18,muted);s.speakerNotes.textFrame.setText(notes);return s;}
function lines(s,a){a.forEach((v,i)=>text(s,v,64,185+i*99,1140,85,29));}
const evidence='https://github.com/WorldExplored/R4R-Sims/tree/audit/grad-nav';
const cite=`${evidence}/docs/grad-nav/camera-correspondence.md; runs20261009T033353Z-correspondence-23ce26 and20261009T033735Z-correspondence-6bf320. Source and full hashes retained. No new model/scene training.`;
let s=slide('GRaD-Nav usability decision',cite);
text(s,'NO-GO for calibrated R4R camera replay\nwith this released gate_mid package',64,205,1140,155,44,alert,true);
text(s,'Native rendering and dynamics work as research components.\nCapture/checkpoint correspondence remains unresolved.',64,425,1140,105,30);
text(s,'One controlled version comparison. Original weights unchanged.',64,580,1140,60,26,muted);
s=slide('Inputs, outputs and E2E scope',cite);
lines(s,['Scene config + Gaussian checkpoint + camera pose/K → RGB, depth, alpha','Body rates + normalized thrust + state → next simulated state','PD controller → dynamics → achieved camera → native images/video','Original learned visual policy → actions/outcomes: blocked by weights']);
text(s,'The demonstrated controller consumes height/velocity, not rendered images. Calibrated replay, visual autonomy and outdoor fidelity are separate gates.',64,586,1140,70,24,alert,true);
s=slide('Checkpoint restoration and camera corrections',`${cite} Strict load hooks record missing/unexpected keys. All saved tensors and named parameters checked. SO3xR3 apply_to_camera called only for corresponding training index; model always evaluation-mode.`);
lines(s,['Strict loading: no missing keys and no unexpected keys in either version','All six Gaussian arrays and all saved model tensors restored exactly','270 saved pose corrections; median translation 0.01597 scene units','Maximum correction: 0.04156 scene units; rotation tangent 0.01827 rad']);
text(s,'Every learned parameter hash is unchanged after rendering. Zero training steps and optimizer updates. The checkpoint does not embed the original filename order.',64,585,1140,74,24,muted);
const rid='20261009T033353Z-correspondence-23ce26';
const report=JSON.parse(await fs.readFile(path.join(root,'results/grad-nav',rid,'diagnostics.json'),'utf8'));
async function image(s,rel,x,y,w,h,alt){s.images.add({blob:new Uint8Array(await fs.readFile(path.join(root,rel))),contentType:'image/png',alt,fit:'contain',position:{left:x,top:y,width:w,height:h}});}
for(const idx of [0,134,269]){
 const rec=report.camera_records.find(r=>r.training_index===idx),m=report.metrics.filter(r=>r.training_index===idx);
 s=slide(`Training camera ${idx}: ${path.basename(rec.image_filename)}`,`${cite} Deterministic selection[0,floor((Ntrain-1)/2),Ntrain-1] ->0,134,269. Source is canonical OpenCV-undistorted ROI-cropped1279x719, uint8/255. Right saved-correction render uses upstream CameraOptimizer.apply_to_camera for this exact training index. No color/exposure fit. Figures are observed outputs; not held-out fidelity.`);
 await image(s,`artifacts/grad-nav/${rid}/frames/${String(idx).padStart(3,'0')}-source-preprocessed.png`,64,160,555,312,'Canonical preprocessed training source');
 await image(s,`artifacts/grad-nav/${rid}/frames/${String(idx).padStart(3,'0')}-saved-correction.png`,661,160,555,312,'Observed render with saved correction');
 text(s,'Preprocessed source',64,485,555,45,25,muted);text(s,'Render with saved pose correction',661,485,555,45,25,muted);
 text(s,`PSNR: canonical ${m[0].psnr_db.toFixed(4)} dB; corrected ${m[1].psnr_db.toFixed(4)} dB.\nSaved corrections do not recover the source scene structure.`,64,552,1140,100,28,alert,true);
}
s=slide('Controlled Nerfstudio version comparison',`${cite} Actual module paths/hashes and pip-check recorded. NS1.1.4 overlay shares baseline dependencies read-only. Runtime OpenCV changed from4.8 to4.10; baseline has duplicate distributions. Every RGB/depth/alpha array is bit-identical across versions. No broad search or guessed scene transform.`);
lines(s,['1.1.3 baseline retained; 1.1.4 installed in a separate environment','Torch 2.1.2/cu118 and gsplat 1.0.0 retained exactly','Required changes only: OpenCV 4.10.0.84, viser 0.2.3, tensorly 0.9.0','Dependency check passes; all 18 RGB/depth/alpha arrays are identical']);
text(s,'This version change did not resolve correspondence. No Gaussian restoration or optimizer-update failure was found.',64,585,1140,74,26,alert,true);
s=slide('Direct usefulness for Real4Real',cite);
const values=[['Use case','Decision','Evidence or missing gate'],['Dynamics API / native integration','Usable component','B state feedback and D camera/video'],['Calibrated camera replay','NO-GO now','Training captures not reproduced'],['Original visual-policy E2E','Blocked','Compatible learned package absent'],['Outdoor sparse views / racing fidelity','Not established','Calibration, held-out inputs and task tests missing']];
const table=s.tables.add({rows:5,columns:3,left:64,top:172,width:1152,height:375,columnWidths:[330,245,577],values});
for(let r=0;r<5;r++)for(let c=0;c<3;c++){let cell=table.getCell(r,c);cell.text.style={typeface:family,fontSize:r===0?26:24,color:r===0?'#FFFFFF':ink,bold:r===0};cell.fill=r===0?accent:'#F8FAFB';}
table.borders.assign({fill:'#CCD8DD',width:1,style:'solid'});
text(s,'Splats can supply appearance; collision geometry, calibrated physics and verified camera registration remain separate requirements.',64,579,1140,74,26,muted);
s=slide('Information needed from the authors',`${cite} Surviving hypotheses are explicitly hypotheses: post-training scene transform, mixed asset revision or historical preprocessing/order. Do not infer original experiment failure. Four older shared-host logs were transferred and checksum-verified; no termination.`);
lines(s,['Matching checkpoint/config/captures bundle with hashes and reference renders','Every world transform and scale baked into the Gaussians or camera poses','Original 270-image training order, split and preprocessing steps','Exact training environment; original compatible navigation checkpoint']);
text(s,'Until that provenance is supplied, do not use this bundle as a calibrated R4R baseline. No outdoor fidelity or real-transfer claim follows from these diagnostics.',64,585,1140,74,26,alert,true);
await fs.mkdir(path.join(workspace,'build'),{recursive:true});await fs.mkdir(path.join(workspace,'output'),{recursive:true});
const draft=path.join(workspace,'build/decision.pptx');await(await PresentationFile.exportPptx(P)).save(draft);
const final=path.join(workspace,'output/GRaD-Nav_Correspondence_Decision.pptx');
const receipt=await finalizePresentation({workspaceDir:workspace,candidatePath:draft,finalPath:final,pythonExecutable:process.env.RUNTIME_PYTHON,integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-heading-fit','--require-native-table-slide','8'],requiredNativeTableOwnerSlides:[8],fontPolicy:{basis:'reference',families:[family],referencePath:path.join(root,'docs/grad-nav/GRaD-Nav_R4R_Audit-v4.pptx'),referenceSha256:'6f484df5ff453a6ba2b46188a92fbea11678cc1de82505a88d3b8cf835bc366a'},verifyArtifactToolImport:true,receiptPath:path.join(workspace,'build/validation.json')});
for(let i=0;i<P.slides.items.length;i++){const png=await P.export({slide:P.slides.items[i],format:'png',scale:1});await fs.writeFile(path.join(workspace,'build',`slide-${String(i+1).padStart(2,'0')}.png`),new Uint8Array(await png.arrayBuffer()));}
console.log(JSON.stringify({slides:P.slides.items.length,path:final,status:receipt.packageIntegrity?.status}));
