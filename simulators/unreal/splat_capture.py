"""Run inside UE 5.5.4 Editor; import author PLY and export eight SceneCapture RGBs.

Environment: R4R_SPLAT_PLY, R4R_SPLAT_RUN. This is a static level-A object test.
"""
import hashlib
import json
import math
import os
from pathlib import Path
import time

import unreal


def digest(path):
    h = hashlib.sha256()
    with open(path, "rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def main():
    ply = Path(os.environ["R4R_SPLAT_PLY"]).resolve(strict=True)
    run = Path(os.environ["R4R_SPLAT_RUN"]).resolve()
    frames = run / "frames"
    frames.mkdir(parents=True, exist_ok=True)
    target_map = "/Game/Maps/VaseSmoke"
    if not unreal.EditorLevelLibrary.new_level(target_map):
        raise RuntimeError("Unable to create empty smoke-test level")
    task = unreal.AssetImportTask()
    task.set_editor_property("filename", str(ply))
    task.set_editor_property("destination_path", "/Game/Gaussians")
    task.set_editor_property("destination_name", "chinese_vase")
    task.set_editor_property("automated", True)
    task.set_editor_property("save", True)
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    imported = list(task.get_editor_property("imported_object_paths"))
    if len(imported) != 1:
        raise RuntimeError("Expected one imported Gaussian asset, got " + repr(imported))
    asset = unreal.EditorAssetLibrary.load_asset(imported[0])
    if asset is None:
        raise RuntimeError("Imported asset did not load")
    actor = unreal.EditorLevelLibrary.spawn_actor_from_object(asset, unreal.Vector(0, 0, 0))
    if actor is None:
        raise RuntimeError("Point cloud asset did not spawn a render actor")
    niagara = actor.get_editor_property("niagara_component")
    if niagara is None:
        raise RuntimeError("Imported actor has no Niagara component")
    world = unreal.EditorLevelLibrary.get_editor_world()
    capture = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SceneCapture2D, unreal.Vector(900, 0, 0))
    component = capture.get_editor_property("capture_component2d")
    target = unreal.RenderingLibrary.create_render_target2d(
        world, 640, 480, unreal.TextureRenderTargetFormat.RTF_RGBA8)
    component.set_editor_property("texture_target", target)
    component.set_editor_property("capture_source", unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
    component.set_editor_property("fov_angle", 60.0)
    component.set_editor_property("capture_every_frame", False)
    component.set_editor_property("capture_on_movement", False)
    if not unreal.EditorLevelLibrary.save_current_level():
        raise RuntimeError("Could not save smoke-test map")
    niagara.set_editor_property("wait_for_compilation_on_activate", True)
    niagara.activate(True)
    niagara.advance_simulation(12, 1.0 / 30.0)
    write_json(run / "scene.json", {
        "source_ply": str(ply), "source_ply_sha256": digest(ply),
        "asset_path": imported[0], "actor_class": actor.get_class().get_name(),
        "map": target_map, "niagara_system": niagara.get_asset().get_path_name(),
        "niagara_active_after_warmup": bool(niagara.is_active()),
        "niagara_pointcloud_data_interface_present": niagara.get_data_interface("PointCloud") is not None,
        "niagara_warmup": {"ticks": 12, "delta_seconds": 1.0 / 30.0},
        "frame": "UE left-handed +Z up, centimetres; camera looks +X locally",
        "ply_to_ue_position_cm": "100*(X,-Z,-Y) per importer source",
        "resolution": [640, 480], "horizontal_fov_deg": 60,
        "intrinsics_assumed_px": {"fx": 640 / (2 * math.tan(math.radians(30))),
                                  "fy": 640 / (2 * math.tan(math.radians(30))),
                                  "cx": 320, "cy": 240},
        "policy_weights": "none", "simulation_time": "not recorded for static editor replay",
        "depth": "not captured; imported splat depth unvalidated",
    })
    positions = [(900, 0, 0), (900, 80, 0), (900, -80, 0), (900, 0, 80),
                 (900, 0, -80), (850, 80, 60), (850, -80, 60), (900, 0, 0)]
    with (run / "reference_route.json").open("w") as stream:
        json.dump({"frame": "UE left-handed centimetres", "camera_centres_cm": positions}, stream, indent=2)
    with (run / "camera.jsonl").open("w", buffering=1) as stream:
        for index, (x, y, z) in enumerate(positions):
            dx, dy, dz = -x, -y, -z
            yaw = math.degrees(math.atan2(dy, dx))
            pitch = math.degrees(math.atan2(dz, math.hypot(dx, dy)))
            capture.set_actor_location(unreal.Vector(x, y, z), False, False)
            capture.set_actor_rotation(unreal.Rotator(roll=0, pitch=pitch, yaw=yaw), False)
            capture_start = time.time()
            component.capture_scene()
            name = f"frame_{index:04d}"
            unreal.RenderingLibrary.export_render_target(world, target, str(frames), name + ".png")
            output = frames / (name + ".png")
            if not output.is_file():
                raise RuntimeError("SceneCapture PNG missing: " + str(output))
            location = capture.get_actor_location()
            rotation = capture.get_actor_rotation()
            row = {"index": index, "wall_unix_s": time.time(),
                   "target_cm": [x, y, z],
                   "target_pitch_yaw_roll_deg": [pitch, yaw, 0],
                   "actual_cm": [location.x, location.y, location.z],
                   "actual_forward_ue": [capture.get_actor_forward_vector().x,
                                         capture.get_actor_forward_vector().y,
                                         capture.get_actor_forward_vector().z],
                   "capture_request_wall_unix_s": capture_start,
                   "export_done_wall_unix_s": time.time(),
                   "rotation_pitch_yaw_roll_deg": [rotation.pitch, rotation.yaw, rotation.roll],
                   "image": str(output), "bytes": output.stat().st_size,
                   "sha256": digest(output), "source": "SceneCapture2D render target export"}
            stream.write(json.dumps(row, sort_keys=True) + "\n")
            unreal.log("R4R_SPLAT_FRAME " + json.dumps(row, sort_keys=True))
    write_json(run / "status.json", {"status": "camera_exported_unvalidated",
                                     "frames": len(positions),
                                     "note": "Pixel content and splat visibility require post-run validation"})


main()
