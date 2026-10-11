import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {Presentation,PresentationFile} from '@oai/artifact-tool';
const workspaceDir=path.resolve(process.argv[2] ?? '.');
const contentPath=path.resolve(process.argv[3] ?? 'deck-content.json');
const requestedFinalPath=path.resolve(process.argv[4] ?? 'rflysim-preparation.pptx');
const SKILL_DIR=process.env.PRESENTATION_SKILL_DIR;
if (!SKILL_DIR) throw new Error('PRESENTATION_SKILL_DIR required');
const RUNTIME_PYTHON=process.env.RUNTIME_PYTHON;
if (!RUNTIME_PYTHON) throw new Error('RUNTIME_PYTHON required');
await fs.mkdir(path.join(workspaceDir,'deck-build'),{recursive:true});
await fs.mkdir(path.dirname(requestedFinalPath),{recursive:true});
const {finalizePresentation,resolvePresentationFont}=await import(pathToFileURL(path.join(SKILL_DIR,'container_tools/artifact_tool_utils.mjs')).href);
const content=JSON.parse(await fs.readFile(contentPath,'utf8'));
const family=resolvePresentationFont({fontFamily:'Arial'});
const presentation=Presentation.create({slideSize:{width:1280,height:720}});
function text(slide,t,left,top,width,height,size,color,bold=false){
 const s=slide.shapes.add({geometry:'textbox',position:{left,top,width,height},fill:'none',line:{fill:'none',width:0}});
 s.text=t;s.text.style={typeface:family,fontSize:size,color,bold,autoFit:'none'};
 return s;
}
for(let i=0;i<content.length;i++){
 const c=content[i];const slide=presentation.slides.add();slide.background.fill='#FFFFFF';
 text(slide,c.title,72,50,1136,86,i===0?60:44,'#102D3B',true);
 if(c.image){
  const bytes=await fs.readFile(path.resolve(path.dirname(contentPath),c.image));
  const isPlot=/trajectory|tracking-timing|capture-timing|gpu/.test(c.image);
  slide.images.add({blob:bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength),contentType:'image/png',alt:c.title,fit:'contain',position:isPlot?{left:72,top:145,width:1136,height:340}:{left:610,top:175,width:598,height:450}});
  c.paragraphs.forEach((p,j)=>text(slide,p,72,isPlot?500+j*50:175+j*145,isPlot?1136:490,isPlot?48:132,isPlot?20:25,j===0?'#102D3B':'#344955'));
 }else{
  c.paragraphs.forEach((p,j)=>text(slide,p,72,175+j*128,1136,112,i===0?32:28,j===0?'#102D3B':'#344955'));
 }
 text(slide,`${c.footer ?? 'Preparation only · no measured simulator results'}   ${i+1} / ${content.length}`,72,667,1136,28,17,'#606C75');
 slide.speakerNotes.textFrame.setText(c.notes);
}
const candidatePath=path.join(workspaceDir,'deck-build/candidate.pptx');
await (await PresentationFile.exportPptx(presentation)).save(candidatePath);
const finalPath=requestedFinalPath;
const result=await finalizePresentation({workspaceDir,candidatePath,finalPath,pythonExecutable:RUNTIME_PYTHON,
 integrityValidatorPath:path.join(SKILL_DIR,'container_tools/inspect_presentation_package_integrity.py'),
 layoutValidatorPath:path.join(SKILL_DIR,'container_tools/inspect_presentation_layout_geometry.py'),
 layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-heading-fit'],
 explicitTotalSlideCount:content.length,fontPolicy:{basis:'design',families:[family]},verifyArtifactToolImport:true,
 receiptPath:path.join(workspaceDir,'deck-build/validation.json')});
await fs.writeFile(path.join(workspaceDir,'deck-build/build-result.json'),JSON.stringify(result,null,2));
console.log(JSON.stringify({finalPath,font:family,slides:content.length}));

await fs.mkdir(path.join(workspaceDir,'previews'),{recursive:true});
for (const [index,slide] of presentation.slides.items.entries()) {
 const png=await presentation.export({slide,format:'png',scale:1});
 await fs.writeFile(path.join(workspaceDir,'previews',`slide-${String(index+1).padStart(2,'0')}.png`),new Uint8Array(await png.arrayBuffer()));
}
