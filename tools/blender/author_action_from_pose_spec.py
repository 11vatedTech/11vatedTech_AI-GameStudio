"""Author a transform-keyed Blender Action from a validated bone-pose spec.

Run on a disposable source .blend and write to a different output .blend. Example:
  blender -b source_copy.blend -P tools/blender/author_action_from_pose_spec.py -- --pose-spec examples/blender/torch_sweep_pose_spec.example.json --output-blend builds/Torch_Sweep_candidate.blend
This automates key placement, not the artistic judgment that makes choreography convincing.
"""
import bpy, argparse, json, math, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from validate_pose_spec import validate_pose_spec

def parse():
 argv=sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
 p=argparse.ArgumentParser();p.add_argument("--pose-spec",required=True,type=Path);p.add_argument("--output-blend",required=True,type=Path);p.add_argument("--overwrite-output",action="store_true")
 return p.parse_args(argv)

def main():
 a=parse();source=Path(bpy.data.filepath).resolve() if bpy.data.filepath else None;out=a.output_blend.expanduser().resolve();spec_path=a.pose_spec.expanduser().resolve()
 if source is None:raise SystemExit("No source .blend is loaded. Open a saved source project copy first.")
 if out==source:raise SystemExit("Refusing to overwrite the source .blend. Choose a distinct output path.")
 if out.exists() and not a.overwrite_output:raise SystemExit(f"Output exists: {out}; pass --overwrite-output only if deliberate.")
 data=json.loads(spec_path.read_text(encoding="utf-8"));errors=validate_pose_spec(data)
 if errors:raise SystemExit("Invalid pose spec:\n- "+"\n- ".join(errors))
 arm=bpy.data.objects.get(data["armature_object"])
 if arm is None or arm.type!="ARMATURE":raise SystemExit(f"Armature object not found: {data['armature_object']}")
 missing=sorted({bone for pose in data["poses"] for bone in pose["bones"] if arm.pose.bones.get(bone) is None})
 if missing:raise SystemExit("Pose spec references missing pose bones: "+", ".join(missing))
 scene=bpy.context.scene;scene.render.fps=round(float(data["fps"]));scene.frame_start=int(data["frame_start"]);scene.frame_end=int(data["frame_end"])
 arm.animation_data_create();arm.animation_data.action=None
 action=bpy.data.actions.new(data["action_name"]);arm.animation_data.action=action
 # Blender 4.4+ Actions use slots/layers. Create and bind a slot explicitly when available.
 if hasattr(action, "slots"):
  slot = arm.animation_data.action_slot
  if slot is None:
   slot = action.slots.new(arm.id_type, arm.name)
   arm.animation_data.action_slot = slot
 for pose in sorted(data["poses"],key=lambda x:x["frame"]):
  scene.frame_set(int(pose["frame"]))
  for bone_name,transform in pose["bones"].items():
   bone=arm.pose.bones[bone_name]
   if "rotation_degrees" in transform:
    bone.rotation_mode="XYZ";bone.rotation_euler=tuple(math.radians(float(v)) for v in transform["rotation_degrees"])
    bone.keyframe_insert(data_path="rotation_euler",frame=int(pose["frame"]),group=bone_name)
   if "location" in transform:
    bone.location=tuple(float(v) for v in transform["location"])
    bone.keyframe_insert(data_path="location",frame=int(pose["frame"]),group=bone_name)
 # Set interpolation on legacy Actions and Blender 4.4+ layered Actions. Do not
 # silently treat an API mismatch as success when the requested curve edit failed.
 interpolation=data.get("interpolation","BEZIER")
 curves=[]
 try:
  curves=list(action.fcurves)
 except (AttributeError, TypeError, RuntimeError):
  slot = arm.animation_data.action_slot if hasattr(action, "slots") else None
  if slot is not None:
   for layer in action.layers:
    for strip in layer.strips:
     if getattr(strip, "type", "KEYFRAME") != "KEYFRAME":
      continue
     try: bag=strip.channelbag(slot)
     except (TypeError, RuntimeError): bag=None
     if bag is not None: curves.extend(list(bag.fcurves))
 if not curves: raise RuntimeError("No Action F-curves were created; inspect the rig/action-slot API before using this output.")
 for curve in curves:
  for kp in curve.keyframe_points:kp.interpolation=interpolation
 for event in data["events"]:
  scene.timeline_markers.new(f"[{event['kind']}] {event['name']}",frame=int(event["frame"]))
 out.parent.mkdir(parents=True,exist_ok=True);bpy.ops.wm.save_as_mainfile(filepath=str(out))
 print(json.dumps({"status":"candidate-action-authored","source_blend":str(source),"output_blend":str(out),"action":action.name,
  "armature":arm.name,"pose_count":len(data["poses"]),"keyed_bones":sorted({b for pose in data["poses"] for b in pose["bones"]}),
  "event_count":len(data["events"]),"source_overwritten":False,"runtime_verified":False,
  "warning":"This script creates keys and markers from supplied transforms. It does not prove animation quality; render and review the action, then export and test in the engine."},indent=2))
if __name__=="__main__":main()
