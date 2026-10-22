"""Render stills for a named Blender Action without saving changes to the input .blend.
Example: blender -b hero.blend -P tools/blender/render_action_review.py -- --armature HeroRig --action Torch_Sweep --output-dir evidence/Torch_Sweep --step 2
"""
import bpy, argparse, json, sys, re
from pathlib import Path

def parse():
 argv=sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
 p=argparse.ArgumentParser();p.add_argument("--armature",required=True);p.add_argument("--action",required=True);p.add_argument("--output-dir",required=True,type=Path);p.add_argument("--start",type=int,default=None);p.add_argument("--end",type=int,default=None);p.add_argument("--step",type=int,default=1);p.add_argument("--resolution-scale",type=int,default=100)
 a=p.parse_args(argv)
 if a.step<1: p.error("--step must be >=1")
 if not 10<=a.resolution_scale<=100:p.error("--resolution-scale must be 10..100")
 return a

def main():
 a=parse();arm=bpy.data.objects.get(a.armature);action=bpy.data.actions.get(a.action)
 if arm is None or arm.type!="ARMATURE":raise SystemExit(f"Armature not found or wrong type: {a.armature}")
 if action is None:raise SystemExit(f"Action not found: {a.action}")
 scene=bpy.context.scene
 if scene.camera is None:raise SystemExit("Scene has no active camera. Assign an inspectable camera before rendering review frames.")
 arm.animation_data_create()
 old_action=arm.animation_data.action
 old_slot=getattr(arm.animation_data,"action_slot",None)
 arm.animation_data.action=action
 fr=float(action.frame_range[0]);to=float(action.frame_range[1]);start=a.start if a.start is not None else int(fr);end=a.end if a.end is not None else int(to)
 if start<0 or end<start:raise SystemExit("Invalid frame range")
 if (end-start)//a.step>240:raise SystemExit("Review render is limited to 241 frames per invocation; split longer actions intentionally.")
 out=a.output_dir.expanduser().resolve();out.mkdir(parents=True,exist_ok=True)
 old_frame=scene.frame_current;old_path=scene.render.filepath;old_scale=scene.render.resolution_percentage;written=[]
 scene.render.resolution_percentage=a.resolution_scale
 safe_action=re.sub(r"[^A-Za-z0-9_.-]+", "_", a.action).strip("._") or "action"
 try:
  for f in range(start,end+1,a.step):
   scene.frame_set(f);scene.render.filepath=str(out/f"{safe_action}_{f:04d}.png")
   bpy.ops.render.render(write_still=True);written.append(scene.render.filepath)
 finally:
  scene.frame_set(old_frame);scene.render.filepath=old_path;scene.render.resolution_percentage=old_scale
  arm.animation_data.action=old_action
  if old_action is not None and old_slot is not None and hasattr(arm.animation_data,"action_slot"):
   arm.animation_data.action_slot=old_slot
 # Do not save the blend file. The prior action binding is restored in memory.
 print(json.dumps({"status":"rendered-review-frames","source_blend":bpy.data.filepath,"armature":arm.name,"action":action.name,"frames":written,"saved_blend":False,"note":"Rendered frames are review evidence only, not animation approval or runtime integration."},indent=2))
if __name__=="__main__":main()
