#!/usr/bin/env python3
"""Validate a Blender bone-pose action spec without requiring Blender."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
from typing import Any

EVENT_KINDS={"hitbox_on","hitbox_off","impact","sound","vfx","combo_open","combo_close","cancel_open","root_motion","marker","other"}
ATTACK_PHASES={"anticipation","contact","follow_through","recovery"}

def validate_pose_spec(data: dict[str, Any]) -> list[str]:
    errors=[]
    required=("schema_version","spec_id","armature_object","action_name","action_kind","fps","frame_start","frame_end","poses","events")
    for key in required:
        if key not in data: errors.append(f"Missing required field: {key}")
    if errors:return errors
    if data.get("schema_version")!="1.0":errors.append("schema_version must be '1.0'.")
    if not isinstance(data.get("fps"),(int,float)) or not (0<float(data["fps"])<=120): errors.append("fps must be >0 and <=120.")
    start,end=data.get("frame_start"),data.get("frame_end")
    if not isinstance(start,int) or not isinstance(end,int) or start<0 or end<=start: errors.append("frame_start/frame_end must define an increasing nonnegative range.")
    poses=data.get("poses",[])
    if not isinstance(poses,list) or len(poses)<2: errors.append("At least two key poses are required."); poses=[]
    seen_frames=set(); bone_sets=[]; channel_maps=[]; phase_names=set()
    for i,pose in enumerate(poses):
        if not isinstance(pose,dict): errors.append(f"poses[{i}] must be an object."); continue
        frame=pose.get("frame")
        if not isinstance(frame,int): errors.append(f"poses[{i}].frame must be an integer.")
        elif frame in seen_frames: errors.append(f"Duplicate pose frame: {frame}.")
        else: seen_frames.add(frame)
        if isinstance(start,int) and isinstance(end,int) and isinstance(frame,int) and not start<=frame<=end: errors.append(f"Pose frame {frame} lies outside frame range.")
        if not pose.get("name"): errors.append(f"poses[{i}] requires a name.")
        if pose.get("purpose"): phase_names.add(str(pose["purpose"]).lower().replace(" ","_"))
        bones=pose.get("bones")
        if not isinstance(bones,dict) or not bones: errors.append(f"poses[{i}].bones must be a non-empty object."); continue
        bone_sets.append(set(bones)); channels={}
        for bone_name, transform in bones.items():
            if not isinstance(transform,dict): errors.append(f"Pose {pose.get('name')}: transform for {bone_name} must be object."); continue
            keys=set(transform)
            if not keys or not keys.issubset({"rotation_degrees","location"}): errors.append(f"Pose {pose.get('name')}: {bone_name} supports only rotation_degrees and location.")
            if not keys.intersection({"rotation_degrees","location"}): errors.append(f"Pose {pose.get('name')}: {bone_name} has no transform channel.")
            channels[bone_name]=keys
            for field in keys:
                vec=transform[field]
                if not isinstance(vec,list) or len(vec)!=3 or any(not isinstance(x,(int,float)) for x in vec): errors.append(f"Pose {pose.get('name')}: {bone_name}.{field} must be 3 numbers.")
        channel_maps.append(channels)
    if len(bone_sets)>1 and any(b!=bone_sets[0] for b in bone_sets[1:]): errors.append("Every key pose must address the same set of bones; omit no critical bone across poses.")
    if len(channel_maps)>1 and any(m!=channel_maps[0] for m in channel_maps[1:]): errors.append("Every key pose must use the same transform channels per bone.")
    events=data.get("events",[])
    if not isinstance(events,list): errors.append("events must be an array."); events=[]
    event_kinds=set()
    for i,event in enumerate(events):
        if not isinstance(event,dict): errors.append(f"events[{i}] must be an object."); continue
        f=event.get("frame"); kind=event.get("kind")
        if not isinstance(f,int) or (isinstance(start,int) and isinstance(end,int) and not start<=f<=end): errors.append(f"events[{i}] frame outside range.")
        if kind not in EVENT_KINDS: errors.append(f"events[{i}] invalid kind {kind!r}.")
        event_kinds.add(kind)
        if not event.get("name"): errors.append(f"events[{i}] requires a name.")
    if data.get("action_kind") in {"attack","heavy_attack","combo"}:
        missing=ATTACK_PHASES-phase_names
        if missing: errors.append("Attack action requires pose purpose phases: "+", ".join(sorted(missing))+".")
        for expected in ("hitbox_on","hitbox_off","impact"):
            if expected not in event_kinds: errors.append(f"Attack action requires event kind '{expected}'.")
    return errors

def main()->int:
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("spec",type=Path);p.add_argument("--json",action="store_true");a=p.parse_args()
    try:d=json.loads(a.spec.read_text(encoding="utf-8"))
    except Exception as exc: print(json.dumps({"valid":False,"errors":[str(exc)]},indent=2));return 2
    errors=validate_pose_spec(d) if isinstance(d,dict) else ["Root must be a JSON object."]
    print(json.dumps({"valid":not errors,"errors":errors,"spec_id":d.get("spec_id") if isinstance(d,dict) else None,"note":"Structural validation does not prove good choreography or a successful Blender run."},indent=2))
    return 0 if not errors else 2
if __name__=="__main__":raise SystemExit(main())
