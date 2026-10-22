#!/usr/bin/env python3
"""Validate a semantic animation sequence manifest (not visual quality itself)."""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path
from typing import Any

STATIC_GIMMICKS = {"static_pulse", "image_pulse", "static_image_pulse", "scale_pulse", "rotate_static_image", "shake_static_image", "camera_only", "static_image_transform", "ui_pulse", "still_image_tween", "static_image_tween"}
PHASE_REQUIREMENTS = {
 "walk": {"contact", "passing", "push_off"}, "run": {"contact", "passing", "push_off"},
 "dodge": {"anticipation", "evasion", "recovery"}, "jump": {"anticipation", "takeoff", "airborne", "landing"},
 "hit_reaction": {"impact", "recoil", "recovery"}, "attack": {"anticipation", "contact", "follow_through", "recovery"},
 "heavy_attack": {"anticipation", "contact", "follow_through", "recovery"},
 "combo": {"anticipation", "contact", "follow_through", "recovery"},
 "spellcast": {"anticipation", "release", "follow_through", "recovery"},
 "death": {"impact", "collapse"},
}
REQUIRED_IDENTITY = {"hair", "outfit", "weapon", "grip", "camera"}


def _validate_assembled_animation(data: dict[str, Any], base_dir: Path | None, check_files: bool) -> dict[str, Any]:
    """Validate the existing v1.0 assembled-frame manifest contract.

    This status means the assembly metadata is structurally valid only; it does
    not certify semantic choreography or visual quality.
    """
    errors: list[str] = []
    warnings: list[str] = []
    required = ["schema_version", "animation_id", "fps", "frame_count", "frame_size", "anchor", "status"]
    for key in required:
        if key not in data:
            errors.append(f"Missing required field: {key}")
    if errors:
        return {"valid": False, "errors": errors, "warnings": warnings, "status": "rejected"}
    if data.get("schema_version") != "1.0":
        errors.append("schema_version must be '1.0' for assembled animation manifests.")
    fps = data.get("fps")
    if isinstance(fps, bool) or not isinstance(fps, (int, float)) or not 1 <= fps <= 120:
        errors.append("fps must be a number from 1 through 120.")
    frame_count = data.get("frame_count")
    if isinstance(frame_count, bool) or not isinstance(frame_count, int) or frame_count < 1:
        errors.append("frame_count must be an integer >=1.")
    frame_size = data.get("frame_size")
    if not isinstance(frame_size, list) or len(frame_size) != 2 or any(isinstance(v, bool) or not isinstance(v, int) or v < 1 for v in frame_size):
        errors.append("frame_size must contain two positive integers.")
    if not isinstance(data.get("animation_id"), str) or not data["animation_id"].strip():
        errors.append("animation_id must be a non-empty string.")
    source_frames = data.get("source_frames")
    if not isinstance(source_frames, list) or len(source_frames) != frame_count:
        errors.append("source_frames must contain exactly frame_count entries.")
    else:
        for index, frame in enumerate(source_frames):
            if not isinstance(frame, dict) or not isinstance(frame.get("path"), str) or not frame.get("path", "").strip():
                errors.append(f"source_frames[{index}] requires a non-empty path string.")
                continue
            digest = frame.get("sha256")
            if not isinstance(digest, str) or not re.fullmatch(r"[a-f0-9]{64}", digest):
                errors.append(f"source_frames[{index}] sha256 must be a 64-character lowercase hexadecimal digest.")
            if "index" in frame and (isinstance(frame["index"], bool) or not isinstance(frame["index"], int) or frame["index"] != index):
                errors.append(f"source_frames[{index}].index must equal its zero-based position.")
        if isinstance(frame_count, int) and not isinstance(frame_count, bool) and len(source_frames) == frame_count:
            indices = [frame.get("index", index) for index, frame in enumerate(source_frames) if isinstance(frame, dict)]
            if indices != list(range(frame_count)):
                errors.append("source_frames entries must be ordered with unique zero-based indices.")
        layout = data.get("layout")
        if layout is not None:
            if not isinstance(layout, list) or len(layout) != frame_count:
                errors.append("layout must contain exactly frame_count entries when present.")
            else:
                for index, position in enumerate(layout):
                    if not isinstance(position, dict):
                        errors.append(f"layout[{index}] must be an object.")
                        continue
                    for field in ("x", "y", "content_width", "content_height"):
                        value = position.get(field)
                        if isinstance(value, bool) or not isinstance(value, int):
                            errors.append(f"layout[{index}].{field} must be an integer.")
                        elif field in {"content_width", "content_height"} and value < 1:
                            errors.append(f"layout[{index}].{field} must be positive.")
        loop = data.get("loop")
        if loop is not None and not isinstance(loop, bool):
            errors.append("loop must be a boolean when present.")
        if not isinstance(data.get("anchor"), str) or not data["anchor"].strip():
            errors.append("anchor must be a non-empty string.")
        if "outputs" in data:
            outputs = data["outputs"]
            if not isinstance(outputs, dict):
                errors.append("outputs must be an object when present.")
            elif any(not isinstance(value, str) or not value.strip() for value in outputs.values()):
                errors.append("outputs values must be non-empty strings.")
        if "frames" in data and not isinstance(data["frames"], list):
            errors.append("frames must be an array when present.")
        elif isinstance(data.get("frames"), list) and data["frames"] and len(data["frames"]) != frame_count:
            errors.append("frames must contain exactly frame_count entries when present.")
        elif isinstance(data.get("frames"), list) and data["frames"]:
            indices = [frame.get("index") for frame in data["frames"] if isinstance(frame, dict)]
            if len(indices) != frame_count or indices != list(range(frame_count)):
                errors.append("frames entries must be ordered with unique zero-based indices.")
            for index, frame in enumerate(data["frames"]):
                if not isinstance(frame, dict):
                    errors.append(f"frames[{index}] must be an object.")
                    continue
                if not isinstance(frame.get("path"), str) or not frame["path"].strip():
                    errors.append(f"frames[{index}].path must be a non-empty string.")
                if not isinstance(frame.get("sha256"), str) or not re.fullmatch(r"[a-f0-9]{64}", frame["sha256"]):
                    errors.append(f"frames[{index}].sha256 must be a 64-character lowercase hexadecimal digest.")
        status_label = data.get("status")
        if status_label == "approved" and not data.get("human_review_id"):
            warnings.append("Manifest status is approved but no human_review_id is recorded; structural validation does not authenticate approval.")
    status = data.get("status")
    if status not in {"assembled", "assembled_requires_visual_review", "requires_visual_review", "approved", "rejected", "blocked"}:
        errors.append("status is not a recognized assembled-animation status.")
    if check_files and base_dir is not None:
        output_names = data.get("outputs", {})
        if isinstance(output_names, dict):
            for key, value in output_names.items():
                if not isinstance(value, str) or not value:
                    continue
                path = (base_dir / value).resolve()
                try:
                    path.relative_to(base_dir.resolve())
                except ValueError:
                    errors.append(f"Output path escapes manifest root: {value}")
                    continue
                if not path.is_file():
                    errors.append(f"Output path does not exist: {value}")
        if isinstance(source_frames, list):
            for index, frame in enumerate(source_frames):
                raw_path = frame.get("path") if isinstance(frame, dict) else None
                if not isinstance(raw_path, str) or not raw_path:
                    continue
                path = Path(raw_path)
                if path.is_absolute():
                    path = path.resolve()
                else:
                    path = (base_dir / path).resolve()
                    try:
                        path.relative_to(base_dir.resolve())
                    except ValueError:
                        errors.append(f"source_frames[{index}] relative path escapes manifest root: {raw_path}")
                        continue
                if not path.is_file():
                    errors.append(f"source_frames[{index}] path does not exist: {raw_path}")
    return {
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "status": "valid-assembled-manifest" if not errors else "rejected",
        "sequence_id": data.get("animation_id"),
        "action_kind": "idle" if "idle" in str(data.get("animation_id", "")).lower() else "unknown",
        "review_status": "requires_visual_review" if status in {"assembled_requires_visual_review", "requires_visual_review"} else status,
        "note": "Assembled-frame manifest validation is structural only. Semantic animation claims still require a v2 sequence manifest and playback review.",
    }


def validate_sequence(data: dict[str, Any], base_dir: Path | None = None, check_files: bool = False) -> dict[str, Any]:
    """Validate either a semantic v2 sequence or a supported legacy v1 assembly.

    Legacy v1 reports are explicitly identified as assembly metadata and are not
    promoted to semantic-animation or visual-quality approval.
    """
    if isinstance(data, dict) and data.get("schema_version") == "1.0" and "animation_id" in data:
        return _validate_assembled_animation(data, base_dir, check_files)

    errors: list[str] = []; warnings: list[str] = []
    required = ["schema_version", "sequence_id", "action_kind", "method", "frame_rate", "frame_count", "phases", "identity_invariants", "events", "review", "artifacts"]
    for key in required:
        if key not in data: errors.append(f"Missing required field: {key}")
    if errors: return {"valid":False,"errors":errors,"warnings":warnings,"status":"rejected"}
    if data.get("schema_version") != "2.0": errors.append("schema_version must be '2.0'.")
    method = str(data.get("method", "")).strip().lower().replace("-", "_").replace(" ", "_")
    if method in STATIC_GIMMICKS:
        errors.append(f"Method '{method}' is static-image gimmick motion, not authored character animation.")
    if not isinstance(data.get("frame_rate"), (int,float)) or not (0 < float(data["frame_rate"]) <= 120): errors.append("frame_rate must be >0 and <=120.")
    if not isinstance(data.get("frame_count"), int) or data["frame_count"] < 2: errors.append("frame_count must be an integer >=2.")
    frame_count = data.get("frame_count", 0)
    kind = data.get("action_kind")
    phases=data.get("phases",[])
    phase_names=set()
    previous_start=-1
    for i,p in enumerate(phases):
        if not isinstance(p,dict): errors.append(f"phases[{i}] must be an object."); continue
        name=str(p.get("name", "")).strip().lower().replace(" ", "_")
        if not name: errors.append(f"phases[{i}] requires a name.")
        phase_names.add(name)
        start,end=p.get("start_frame"),p.get("end_frame")
        if not isinstance(start,int) or not isinstance(end,int) or start < 0 or end < start: errors.append(f"Phase '{name}' has an invalid frame range."); continue
        if end >= frame_count: errors.append(f"Phase '{name}' ends outside frame_count ({frame_count}).")
        if start < previous_start: warnings.append("Phase list is not ordered by start frame.")
        previous_start=start
    needed=PHASE_REQUIREMENTS.get(kind,set())
    missing=needed-phase_names
    if missing: errors.append(f"{kind} sequence missing semantic phases: {', '.join(sorted(missing))}.")
    inv={str(v).lower().replace(" ","_") for v in data.get("identity_invariants",[]) if isinstance(v,str)}
    missing_inv=REQUIRED_IDENTITY-inv
    if missing_inv: errors.append(f"identity_invariants missing: {', '.join(sorted(missing_inv))}.")
    events=data.get("events",[])
    event_pairs={(e.get("kind"),e.get("frame")) for e in events if isinstance(e,dict)}
    for i,e in enumerate(events):
        if not isinstance(e,dict): errors.append(f"events[{i}] must be an object."); continue
        if not isinstance(e.get("frame"),int) or not 0 <= e.get("frame",-1) < frame_count: errors.append(f"events[{i}] frame is outside the clip.")
    if kind in {"attack","heavy_attack","combo"}:
        event_kinds={e.get("kind") for e in events if isinstance(e,dict)}
        if "hitbox_on" not in event_kinds: errors.append("Attack must define a hitbox_on event.")
        if "hitbox_off" not in event_kinds: errors.append("Attack must define a hitbox_off event.")
        if "impact" not in event_kinds: errors.append("Attack must define an impact event synchronized to contact.")
    review=data.get("review",{}); artifacts=data.get("artifacts",{})
    if not isinstance(review,dict) or not isinstance(artifacts,dict): errors.append("review and artifacts must be objects.")
    else:
        for field in ("source","review_frame_strip"):
            if not artifacts.get(field): errors.append(f"artifacts.{field} is required.")
        for field in ("intended_speed_reviewed","slow_reviewed","identity_checked","prop_contact_checked","notes"):
            if field not in review: errors.append(f"review.{field} is required.")
        status=review.get("status","candidate")
        if status in {"motion-valid","integrated","runtime-verified","agent-approved","operator-approved","rights-cleared"}:
            if not review.get("intended_speed_reviewed"): errors.append(f"status '{status}' requires intended-speed review.")
            if not review.get("slow_reviewed"): errors.append(f"status '{status}' requires slow review.")
            if not review.get("identity_checked"): errors.append(f"status '{status}' requires identity review.")
            if not review.get("prop_contact_checked"): errors.append(f"status '{status}' requires prop/contact review.")
        if status in {"integrated","runtime-verified","agent-approved","operator-approved","rights-cleared"} and not review.get("integrated"):
            errors.append(f"status '{status}' requires integrated=true.")
        if status in {"runtime-verified","agent-approved","operator-approved","rights-cleared"}:
            if not review.get("runtime_observed") or not artifacts.get("engine_capture") or not artifacts.get("engine_log"):
                errors.append(f"status '{status}' requires runtime_observed plus engine_capture and engine_log artifacts.")
        if status == "operator-approved" and not review.get("operator_approval_reference"):
            errors.append("operator-approved status requires operator_approval_reference.")
        if check_files and base_dir:
            for k,v in artifacts.items():
                values=v if isinstance(v,list) else [v]
                for value in values:
                    if not value or not isinstance(value,str): continue
                    p=(base_dir/value).resolve()
                    try: p.relative_to(base_dir.resolve())
                    except ValueError: errors.append(f"Artifact path escapes manifest root: {value}"); continue
                    if not p.is_file(): errors.append(f"Artifact path does not exist: {value}")
    return {"valid":not errors,"errors":errors,"warnings":warnings,"status":"valid-manifest" if not errors else "rejected",
            "sequence_id":data.get("sequence_id"),"action_kind":kind,"review_status":review.get("status") if isinstance(review,dict) else None,
            "note":"This validator enforces declared sequence structure and evidence. It cannot judge motion quality; playback and target-engine inspection remain required."}


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest",type=Path); parser.add_argument("--check-files",action="store_true"); parser.add_argument("--json",action="store_true")
    args=parser.parse_args()
    try: data=json.loads(args.manifest.read_text(encoding="utf-8"))
    except Exception as exc: print(json.dumps({"valid":False,"errors":[f"Cannot read JSON: {exc}"]},indent=2)); return 2
    if not isinstance(data,dict): print(json.dumps({"valid":False,"errors":["Manifest root must be an object."]},indent=2)); return 2
    result=validate_sequence(data,args.manifest.resolve().parent,args.check_files); print(json.dumps(result,indent=2,ensure_ascii=False)); return 0 if result["valid"] else 2
if __name__ == "__main__": raise SystemExit(main())
