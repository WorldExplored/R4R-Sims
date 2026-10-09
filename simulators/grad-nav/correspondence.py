"""Training-view diagnostic: canonical dataset cameras, saved corrections, no updates."""
import argparse,json,copy,hashlib,time,sys
from pathlib import Path
def tensor_hash(x):return hashlib.sha256(x.detach().cpu().contiguous().numpy().tobytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('mode');p.add_argument('--upstream',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 import torch,numpy as np,yaml
 from PIL import Image
 from nerfstudio.utils.eval_utils import eval_setup
 from nerfstudio.models.splatfacto import SplatfactoModel
 torch.manual_seed(0);torch.set_num_threads(2)
 out=a.out;(out/'frames').mkdir(exist_ok=True)
 scene=Path('/home/ubuntu/grad-nav-deps/scenes/gs_data/sv_1007_gate_mid/splatfacto/2024-10-07_145741')
 cfg=yaml.load((scene/'config.yml').read_text(),Loader=yaml.Loader)
 for c in [cfg,cfg.pipeline.datamanager,cfg.pipeline.datamanager.dataparser]:c.data=scene/'data'
 cfg.output_dir=scene.parents[2];resolved=out/'resolved-config.yml';resolved.write_text(yaml.dump(cfg))
 events=[];original=torch.nn.Module.load_state_dict
 def audited(self,state_dict,*args,**kwargs):
  if not isinstance(self,SplatfactoModel):return original(self,state_dict,*args,**kwargs)
  row={'strict':kwargs.get('strict',args[0] if args else True),'input_keys':list(state_dict)}
  try:
   result=original(self,state_dict,*args,**kwargs);row.update(missing_keys=list(result.missing_keys),unexpected_keys=list(result.unexpected_keys),status='loaded');return result
  except Exception as e:row.update(status='error',error=str(e));raise
  finally:events.append(row)
 torch.nn.Module.load_state_dict=audited
 config,pipeline,checkpoint_path,step=eval_setup(resolved,test_mode='inference')
 torch.nn.Module.load_state_dict=original
 pipeline.eval();model=pipeline.model;dm=pipeline.datamanager
 checkpoint=torch.load(checkpoint_path,map_location='cpu');saved=checkpoint['pipeline'];state=model.state_dict()
 comparisons=[]
 for name in ['means','scales','quats','opacities','features_dc','features_rest']:
  key='gauss_params.'+name;ref=saved['_model.'+key];cur=state[key].cpu()
  comparisons.append({'key':key,'saved_shape':list(ref.shape),'loaded_shape':list(cur.shape),'exact_equal':bool(torch.equal(cur,ref)),'max_abs_delta':float((cur-ref).abs().max()),'saved_sha256':tensor_hash(ref),'loaded_sha256':tensor_hash(cur)})
 all_restore=[]
 for key,ref in saved.items():
  if key.startswith('_model.'):
   k=key[7:];cur=state.get(k);all_restore.append({'key':k,'present':cur is not None,'exact_equal':bool(torch.equal(ref,cur.cpu())) if cur is not None else False})
 before={k:tensor_hash(v) for k,v in model.named_parameters()}
 adjustments=model.camera_optimizer.pose_adjustment.detach().cpu();n=len(dm.train_dataset);indices=[0,(n-1)//2,n-1]
 assert len(adjustments)==n
 mapping=[{'training_index':i,'image_filename':str(f),'pose_adjustment_translation_so3':adjustments[i].tolist(),'translation_norm_scene_units':float(adjustments[i,:3].norm()),'rotation_tangent_norm_rad':float(adjustments[i,3:].norm())} for i,f in enumerate(dm.train_dataset.image_filenames)]
 (out/'camera_optimizer_mapping.json').write_text(json.dumps(mapping,indent=2)+'\n')
 cameras_before=copy.deepcopy(dm.train_dataset.cameras)
 # Trigger the canonical loader's undistortion/crop; no optimizer or trainer run.
 cache=dm.cached_train
 dm.train_unseen_cameras=indices.copy()
 metrics=[];records=[]
 with torch.inference_mode():
  for index in indices:
   camera,batch=dm.next_train(0)
   assert camera.metadata['cam_idx']==index and not model.training
   gt=batch['image'].float()/255 if batch['image'].dtype==torch.uint8 else batch['image'].float()
   raw_source=dm.train_dataset.get_data(index,image_type='uint8')['image'].cpu().numpy()
   Image.fromarray(raw_source).save(out/'frames'/f'{index:03d}-source-original.png')
   Image.fromarray((gt.cpu().numpy()*255).round().astype('uint8')).save(out/'frames'/f'{index:03d}-source-preprocessed.png')
   corrected=copy.deepcopy(camera)
   corrected.camera_to_worlds=model.camera_optimizer.apply_to_camera(camera)
   record={'training_index':index,'image_filename':str(dm.train_dataset.image_filenames[index]),'optimizer_mapping_index':index,'source_intrinsics':cameras_before[index].get_intrinsics_matrices().tolist(),'source_distortion':cameras_before[index].distortion_params.tolist(),'loader_intrinsics':camera.get_intrinsics_matrices().cpu().tolist(),'source_dimensions':[int(cameras_before.width[index]),int(cameras_before.height[index])],'loader_dimensions':[int(camera.width.item()),int(camera.height.item())],'canonical_c2w':camera.camera_to_worlds.cpu().tolist(),'corrected_c2w':corrected.camera_to_worlds.cpu().tolist(),'upstream_correction_method':'CameraOptimizer.apply_to_camera; SO3xR3 world translation independent of rotation','pose_adjustment':adjustments[index].tolist(),'model_evaluation_mode':not model.training}
   records.append(record)
   for label,cam in [('canonical',camera),('saved-correction',corrected)]:
    torch.cuda.synchronize();start=time.perf_counter();d=model.get_outputs_for_camera(cam);torch.cuda.synchronize();wall=time.perf_counter()-start
    rgb=d['rgb'];assert rgb.shape==gt.shape
    error=rgb-gt;mse=float((error**2).mean());row={'training_index':index,'variant':label,'mae_rgb_0_1':float(error.abs().mean()),'rmse_rgb_0_1':float(mse**.5),'mse_rgb_0_1':mse,'psnr_db':float(-10*np.log10(mse)) if mse else None,'rgb_range':[float(rgb.min()),float(rgb.max())],'render_wall_s':wall,'dimensions':list(rgb.shape),'comparison':'training-view diagnostic, not held-out fidelity; full preprocessed RGB, no exposure/color fit'}
    metrics.append(row)
    Image.fromarray((rgb.cpu().numpy()*255).round().astype('uint8')).save(out/'frames'/f'{index:03d}-{label}.png')
    Image.fromarray((error.abs().cpu().numpy().clip(0,1)*255).round().astype('uint8')).save(out/'frames'/f'{index:03d}-{label}-absolute-difference.png')
    for key in ['rgb','depth','accumulation']:np.save(out/'frames'/f'{index:03d}-{label}-{key}.npy',d[key].cpu().numpy())
 after={k:tensor_hash(v) for k,v in model.named_parameters()};assert before==after
 assert all(x['exact_equal'] for x in comparisons)
 report={'scene_path':str(scene),'checkpoint_path':str(checkpoint_path),'checkpoint_sha256':hashlib.sha256(Path(checkpoint_path).read_bytes()).hexdigest(),'saved_step':checkpoint['step'],'loaded_model_step':model.step,'loader_events':events,'gaussian_parameters':comparisons,'all_saved_model_tensors':all_restore,'camera_optimizer_mode':config.pipeline.model.camera_optimizer.mode,'camera_optimizer_summary':{'count':n,'translation_norm_min_median_max_scene_units':[float(x) for x in torch.quantile(adjustments[:,:3].norm(dim=1),torch.tensor([0.,.5,1.]))],'rotation_norm_min_median_max_rad':[float(x) for x in torch.quantile(adjustments[:,3:].norm(dim=1),torch.tensor([0.,.5,1.]))]},'selection_rule':'indices[0,floor((Ntrain-1)/2),Ntrain-1] in dataparser training order; no selection using image quality','selected_indices':indices,'train_image_count':n,'eval_image_count':len(dm.eval_dataset),'dataparser_transform':dm.train_dataparser_outputs.dataparser_transform.tolist(),'dataparser_scale':dm.train_dataparser_outputs.dataparser_scale,'downscale_factor':dm.dataparser.downscale_factor,'preprocessing':'upstream FullImageDatamanager.cached_train: OpenCV undistortion, alpha0 optimal K, ROI crop, half-pixel principal-point shift; cached uint8 -> float/255; no extra resize, gamma, pose fit or exposure adjustment','parameter_hashes_before':before,'parameter_hashes_after':after,'parameters_unchanged':before==after,'optimizer_updates':0,'training_steps':0,'camera_records':records,'metrics':metrics,'physical_scale_verified':False,'held_out_fidelity':False}
 (out/'diagnostics.json').write_text(json.dumps(report,indent=2)+'\n');(out/'camera_poses.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in records));(out/'metrics.json').write_text(json.dumps(metrics,indent=2)+'\n')
 print(json.dumps({'selection':indices,'gaussian_restore_exact':all(x['exact_equal'] for x in comparisons),'optimizer_summary':report['camera_optimizer_summary'],'metrics':metrics,'parameters_unchanged':before==after},indent=2),flush=True)
if __name__=='__main__':main()
