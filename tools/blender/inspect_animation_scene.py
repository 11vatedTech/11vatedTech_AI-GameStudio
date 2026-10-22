"""Run inside Blender using `blender -b project.blend -P inspect_animation_scene.py -- --output-json report.json`.
Read-only scene inventory. Does not save or modify the source blend file.
"""
import bpy, json, argparse, sys
from pathlib import Path

def args_after_separator():
    argv=sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
    p=argparse.ArgumentParser();p.add_argument("--output-json",required=True);return p.parse_args(argv)

def main():
    a=args_after_separator()
    objects=[]; armatures=[]; actions=[]; cameras=[]
    for obj in bpy.context.scene.objects:
        objects.append({"name":obj.name,"type":obj.type,"location":list(obj.location),"dimensions":list(obj.dimensions),"visible":not obj.hide_render})
        if obj.type=="ARMATURE":
            armatures.append({"name":obj.name,"bones":[{"name":b.name,"parent":b.parent.name if b.parent else None,"use_deform":b.use_deform} for b in obj.data.bones],
                "active_action":obj.animation_data.action.name if obj.animation_data and obj.animation_data.action else None})
        if obj.type=="CAMERA": cameras.append({"name":obj.name,"type":obj.data.type,"lens":obj.data.lens})
    for action in bpy.data.actions:
        # Blender 4.4+ uses layered Actions; older versions expose action.fcurves.
        curves = 0
        curves_known = False
        try:
            curves = len(action.fcurves)
            curves_known = True
        except (AttributeError, TypeError, RuntimeError):
            try:
                for layer in action.layers:
                    for strip in layer.strips:
                        if getattr(strip, "type", "KEYFRAME") != "KEYFRAME":
                            continue
                        for slot in action.slots:
                            try:
                                bag = strip.channelbag(slot)
                            except (TypeError, RuntimeError):
                                bag = None
                            if bag is not None:
                                curves += len(bag.fcurves)
                curves_known = True
            except (AttributeError, TypeError, RuntimeError):
                curves_known = False
        actions.append({"name":action.name,"frame_range":[float(action.frame_range[0]),float(action.frame_range[1])],"fcurve_count":curves if curves_known else None})
    scene=bpy.context.scene
    report={"status":"read-only-inventory","blender_version":bpy.app.version_string,"blend_file":bpy.data.filepath,
        "render_engine":scene.render.engine,"fps":scene.render.fps,"frame_range":[scene.frame_start,scene.frame_end],
        "active_camera":scene.camera.name if scene.camera else None,"cameras":cameras,"object_count":len(objects),"objects":objects,
        "armatures":armatures,"actions":actions,"note":"This report inventories scene data; it does not certify rig quality or animation quality."}
    out=Path(a.output_json).expanduser().resolve();out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,indent=2),encoding="utf-8")
    print(json.dumps({"written":str(out),"armatures":len(armatures),"actions":len(actions),"camera":report["active_camera"]},indent=2))
if __name__=="__main__":main()
