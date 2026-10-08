"""One UE5 final-color mesh gate after correcting light direction and saturation."""
import hashlib
import json
import math
import os
from pathlib import Path
import time
import traceback
import unreal

out=Path(os.environ["R4R_SPLAT_RUN"])
if not unreal.EditorLevelLibrary.load_level("/Game/Maps/VaseSmoke"):
    raise RuntimeError("Saved map did not load")
world=unreal.EditorLevelLibrary.get_editor_world()
actors=unreal.EditorLevelLibrary.get_all_level_actors()
splat=next(a for a in actors if a.get_class().get_name()=="GaussianSplattingPointCloudActor")
niagara=splat.get_editor_property("niagara_component")
niagara.set_editor_property("allow_scalability",False)
niagara.activate(True)
cube=unreal.EditorLevelLibrary.spawn_actor_from_object(
    unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Cube.Cube"),unreal.Vector(0,0,0))
cube.set_actor_scale3d(unreal.Vector(3,3,3))
light=unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.DirectionalLight,unreal.Vector(0,0,500))
# Prior control used yaw 0: rays point toward +X, away from the camera-visible +X face.
light.set_actor_rotation(unreal.Rotator(roll=0,pitch=-45,yaw=180),False)
lc=light.get_component_by_class(unreal.DirectionalLightComponent)
lc.set_editor_property("intensity",10.0)
camera=unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SceneCapture2D,unreal.Vector(900,0,0))
camera.set_actor_rotation(unreal.Rotator(roll=0,pitch=0,yaw=180),False)
component=camera.get_editor_property("capture_component2d")
target=unreal.RenderingLibrary.create_render_target2d(world,640,480,unreal.TextureRenderTargetFormat.RTF_RGBA8)
component.set_editor_property("texture_target",target)
component.set_editor_property("fov_angle",60.0)
component.set_editor_property("capture_every_frame",False)
component.set_editor_property("capture_on_movement",False)
component.set_editor_property("capture_source",unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
state={"tick_count":0,"editor_delta_sum_seconds":0,"frames":{},"error":None,
    "hypothesis":"Reversed light made final color nonblack but 100000 intensity saturated the control; reduce to 10",
    "changed_configuration":{"directional_light_intensity":{"prior":100000,"new":10},
        "directional_light_yaw_deg":{"prior":180,"new":180}},
    "light_mobility":str(lc.get_editor_property("mobility")),
    "light_forward_ue":[light.get_actor_forward_vector().x,light.get_actor_forward_vector().y,light.get_actor_forward_vector().z],
    "requested_camera":{"position_cm":[900,0,0],"pitch_yaw_roll_deg":[0,180,0]},
    "intrinsics_assumed":{"width":640,"height":480,"fx":640/(2*math.tan(math.radians(30))),
        "fy":640/(2*math.tan(math.radians(30))),"cx":320,"cy":240,"hfov_deg":60},
    "frame":"UE left-handed Z-up cm, camera local +X; PLY importer 100*(X,-Z,-Y)",
    "policy_weights":"none","cube_gate_passed":False,"splat_attempted":False}
handle=None

def export(name):
    unreal.RenderingLibrary.export_render_target(world,target,str(out),name)
    path=out/name
    loc=camera.get_actor_location(); rot=camera.get_actor_rotation()
    row={"wall_unix_s":time.time(),"tick":state["tick_count"],"bytes":path.stat().st_size,
        "sha256":hashlib.sha256(path.read_bytes()).hexdigest(),"actual_camera_position_cm":[loc.x,loc.y,loc.z],
        "actual_rotation_pitch_yaw_roll_deg":[rot.pitch,rot.yaw,rot.roll],
        "capture_source":"SCS_FINAL_COLOR_LDR","render_target":"RTF_RGBA8"}
    state["frames"][name]=row
    (out/"camera.jsonl").open("a").write(json.dumps({"image":name,**row})+"\n")

def done():
    global handle
    state["niagara_active_final"]=bool(niagara.is_active())
    (out/"diagnostics.json").write_text(json.dumps(state,indent=2,sort_keys=True)+"\n")
    if handle is not None: unreal.unregister_slate_post_tick_callback(handle); handle=None
    unreal.EditorPythonScripting.set_keep_python_script_alive(False)

def tick(delta):
    try:
        state["tick_count"]+=1; state["editor_delta_sum_seconds"]+=float(delta)
        n=state["tick_count"]
        if n==20:
            state["cube_capture_request_wall_unix_s"]=time.time(); component.capture_scene()
        elif n==22:
            export("cube_final.png")
            center=unreal.RenderingLibrary.read_render_target_pixel(world,target,320,240)
            background=unreal.RenderingLibrary.read_render_target_pixel(world,target,10,10)
            state["cube_center_rgba"]=[center.r,center.g,center.b,center.a]
            state["cube_background_rgba"]=[background.r,background.g,background.b,background.a]
            state["cube_gate_passed"]=max(center.r,center.g,center.b)>20 and max(background.r,background.g,background.b)<200 and max(
                abs(center.r-background.r),abs(center.g-background.g),abs(center.b-background.b))>20
            if not state["cube_gate_passed"]: done()
        elif n==24 and state["cube_gate_passed"]:
            cube.set_actor_hidden_in_game(True)
            state["splat_attempted"]=True
            state["splat_capture_request_wall_unix_s"]=time.time(); component.capture_scene()
        elif n==26:
            export("splat_final.png"); done()
    except Exception:
        state["error"]=traceback.format_exc(); unreal.log_error(state["error"]); done()

unreal.EditorPythonScripting.set_keep_python_script_alive(True)
handle=unreal.register_slate_post_tick_callback(tick)
