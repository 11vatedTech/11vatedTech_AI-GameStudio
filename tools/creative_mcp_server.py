#!/usr/bin/env python3
"""Bounded stdlib MCP server for creative preflight, animation contracts and Blender actions.

The server is stdio-only. It does not expose a network listener and only accepts paths
under AGS_WORKSPACE (or the process current directory). Blender work runs as explicit
subprocesses with --disable-autoexec and fixed bundled scripts, never arbitrary user code.
"""
from __future__ import annotations
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path, PureWindowsPath
from typing import Any

# Protocol negotiation: echo a version the client requested when this server
# implements it, otherwise answer with the newest version verified against the
# installed Freebuff host. 2025-11-25 is deliberately absent because that host
# rejects it; add a version only after a real connector test passes.
SUPPORTED_PROTOCOL_VERSIONS = (
    "2025-06-18",
    "2025-03-26",
    "2024-11-05",
)
LATEST_SUPPORTED_PROTOCOL_VERSION = SUPPORTED_PROTOCOL_VERSIONS[0]
COMPATIBILITY_PROTOCOL_VERSION = LATEST_SUPPORTED_PROTOCOL_VERSION
SERVER_VERSION = "0.3.0"

TOOLS = [
    {"name":"ags_creative_preflight","description":"Read-only discovery of local creative executables, loopback services, GPU/RAM/disk state and conservative generation policy. Unknown measurements are not guessed.","inputSchema":{"type":"object","properties":{}}},
    {"name":"ags_validate_animation_sequence","description":"Validate semantic phases, identity invariants, hitbox/impact event markers, review state and evidence requirements. Rejects static-image pulse/transform gimmicks as character animation.","inputSchema":{"type":"object","required":["manifest_path"],"properties":{"manifest_path":{"type":"string","description":"Workspace-relative JSON manifest path."},"check_files":{"type":"boolean","default":False}}}},
    {"name":"ags_validate_blender_pose_spec","description":"Validate a bone-pose action spec without launching Blender. Checks consistent bone/channel sets, timeline and attack event markers.","inputSchema":{"type":"object","required":["pose_spec_path"],"properties":{"pose_spec_path":{"type":"string"}}}},
    {"name":"ags_blender_scene_inventory","description":"Run a bounded, read-only Blender background scene inventory: objects, armatures, bones, actions, frame range and camera. Writes only a new JSON report inside the workspace.","inputSchema":{"type":"object","required":["blend_path","output_path"],"properties":{"blend_path":{"type":"string"},"output_path":{"type":"string"},"overwrite":{"type":"boolean","default":False},"timeout_seconds":{"type":"integer","minimum":5,"maximum":300,"default":90}}}},
    {"name":"ags_blender_render_action_review","description":"Render frames of an existing named Blender Action for inspection. Uses the loaded file and writes PNG frames into an empty/new workspace-relative folder; it does not save the .blend file.","inputSchema":{"type":"object","required":["blend_path","armature_name","action_name","output_dir"],"properties":{"blend_path":{"type":"string"},"armature_name":{"type":"string"},"action_name":{"type":"string"},"output_dir":{"type":"string"},"start_frame":{"type":"integer","minimum":0},"end_frame":{"type":"integer","minimum":0},"step":{"type":"integer","minimum":1,"maximum":12,"default":1},"resolution_scale":{"type":"integer","minimum":10,"maximum":100,"default":60},"timeout_seconds":{"type":"integer","minimum":5,"maximum":600,"default":180}}}},
    {"name":"ags_blender_author_action","description":"Create a named, transform-keyed Action from a validated pose-spec on an existing rig and save it to a new .blend output. Never overwrite the source .blend; output overwrite is opt-in.","inputSchema":{"type":"object","required":["source_blend_path","pose_spec_path","output_blend_path"],"properties":{"source_blend_path":{"type":"string"},"pose_spec_path":{"type":"string"},"output_blend_path":{"type":"string"},"overwrite_output":{"type":"boolean","default":False},"timeout_seconds":{"type":"integer","minimum":5,"maximum":600,"default":180}}}}
]

class CreativeMCPError(Exception):
    def __init__(self, code: str, message: str, details: Any = None):
        super().__init__(message); self.code=code; self.details=details

class CreativeMCPServer:
    def __init__(self, workspace: str | Path | None = None):
        self.workspace=Path(workspace or os.environ.get("AGS_WORKSPACE") or Path.cwd()).expanduser().resolve()
        if not self.workspace.is_dir(): raise ValueError(f"Workspace directory does not exist: {self.workspace}")
        self.python=sys.executable

    def safe_path(self, raw: str, *, must_exist: bool = False, want_dir: bool = False) -> Path:
        if not isinstance(raw,str) or not raw.strip(): raise CreativeMCPError("invalid_path","A non-empty workspace-relative path is required.")
        win=PureWindowsPath(raw)
        p=Path(raw)
        if p.is_absolute() or win.is_absolute() or win.drive or ".." in p.parts or ".." in win.parts:
            raise CreativeMCPError("path_outside_workspace","Paths must be relative to AGS_WORKSPACE and may not contain '..'.",{"path":raw})
        cursor=self.workspace
        for part in p.parts:
            if part in {"", "."}: continue
            cursor=cursor/part
            if cursor.is_symlink(): raise CreativeMCPError("symlink_path_refused","Symlink path components are refused.",{"path":str(cursor)})
        resolved=(self.workspace/p).resolve()
        try: resolved.relative_to(self.workspace)
        except ValueError: raise CreativeMCPError("path_outside_workspace","Resolved path escapes AGS_WORKSPACE.",{"path":raw})
        if must_exist and not resolved.exists(): raise CreativeMCPError("path_not_found","Path does not exist inside workspace.",{"path":raw})
        if must_exist and want_dir and not resolved.is_dir(): raise CreativeMCPError("not_a_directory","Expected a directory.",{"path":raw})
        if must_exist and not want_dir and not resolved.is_file(): raise CreativeMCPError("not_a_file","Expected a file.",{"path":raw})
        return resolved

    @staticmethod
    def bounded_int(value: Any, name: str, low: int, high: int, default: int) -> int:
        if value is None: return default
        if isinstance(value, bool) or not isinstance(value, int) or not low <= value <= high:
            raise CreativeMCPError("invalid_argument", f"{name} must be an integer from {low} to {high}.", {"value": value})
        return value

    def blender_binary(self) -> str:
        configured=os.environ.get("BLENDER_BIN")
        if configured:
            expanded=str(Path(configured).expanduser())
            if Path(expanded).is_file(): return str(Path(expanded).resolve())
            found=shutil.which(configured)
            if found:return found
        found=shutil.which("blender")
        if found:return found
        raise CreativeMCPError("blender_not_found","Blender executable not found. Set BLENDER_BIN to the installed blender.exe path; no installation was attempted.")

    def _sanitize_command(self, command: list[str]) -> list[str]:
        workspace = str(self.workspace.resolve())
        normalized_root = os.path.normcase(os.path.normpath(workspace))
        sanitized = []
        for index, argument in enumerate(command):
            value = str(argument)
            normalized = os.path.normcase(os.path.normpath(value))
            if normalized == normalized_root:
                value = "$WORKSPACE"
            elif normalized.startswith(normalized_root + os.sep) or normalized.startswith(normalized_root + "/") or normalized.startswith(normalized_root + "\\\\"):
                value = "$WORKSPACE"
            elif index == 0:
                value = "<executable>/" + Path(value).name
            elif Path(value).is_absolute() or PureWindowsPath(value).is_absolute():
                value = "<external-path>/" + PureWindowsPath(value).name
            sanitized.append(value)
        return sanitized

    @staticmethod
    def _captured_text(value: Any, limit: int = 12000) -> str:
        if value is None:
            return ""
        if isinstance(value, bytes):
            value = value.decode("utf-8", errors="replace")
        return str(value)[-limit:]

    def _output_records(self, outputs: list[Path] | None, output_dirs: list[Path] | None) -> list[dict[str, Any]]:
        paths = list(outputs or [])
        for directory in output_dirs or []:
            if directory.is_dir():
                paths.extend(sorted(path for path in directory.rglob("*") if path.is_file())[:256])
        records = []
        seen = set()
        for path in paths:
            resolved = path.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            present = resolved.is_file()
            try:
                relative = resolved.relative_to(self.workspace).as_posix()
            except ValueError:
                relative = "<outside-workspace>/" + resolved.name
            records.append({"path": relative, "exists": present,
                            "bytes": resolved.stat().st_size if present else None,
                            "sha256": hashlib.sha256(resolved.read_bytes()).hexdigest() if present else None})
        return records

    def run_bounded(self, command: list[str], timeout: int, *, outputs: list[Path] | None = None,
                    output_dirs: list[Path] | None = None, stage: str = "subprocess", check: bool = True) -> dict[str,Any]:
        started_at = datetime.now(timezone.utc)
        started = time.monotonic()
        sanitized_command = self._sanitize_command(command)
        try:
            proc=subprocess.run(command,cwd=self.workspace,capture_output=True,text=True,timeout=timeout,check=False,shell=False)
        except subprocess.TimeoutExpired as exc:
            finished_at = datetime.now(timezone.utc)
            records = self._output_records(outputs, output_dirs)
            diagnostics = {"stage": stage, "started_at": started_at.isoformat(timespec="milliseconds"),
                "finished_at": finished_at.isoformat(timespec="milliseconds"),
                "elapsed_seconds": round(time.monotonic() - started, 3), "timeout_seconds": timeout,
                "command": sanitized_command, "exit_code": None, "returncode": None, "timed_out": True,
                "stdout": self._captured_text(exc.stdout), "stderr": self._captured_text(exc.stderr),
                "outputs_created": any(item["exists"] for item in records), "outputs": records}
            raise CreativeMCPError("process_timeout",f"Process exceeded {timeout}s timeout during {stage}.",diagnostics) from exc
        except OSError as exc:
            finished_at = datetime.now(timezone.utc)
            records = self._output_records(outputs, output_dirs)
            diagnostics = {"stage": stage, "started_at": started_at.isoformat(timespec="milliseconds"),
                "finished_at": finished_at.isoformat(timespec="milliseconds"),
                "elapsed_seconds": round(time.monotonic() - started, 3), "timeout_seconds": timeout,
                "command": sanitized_command, "exit_code": None, "returncode": None, "timed_out": False,
                "stdout": "", "stderr": str(exc)[-12000:],
                "outputs_created": any(item["exists"] for item in records), "outputs": records}
            raise CreativeMCPError("process_start_failed",str(exc),diagnostics) from exc
        finished_at = datetime.now(timezone.utc)
        records = self._output_records(outputs, output_dirs)
        result={"stage": stage, "started_at": started_at.isoformat(timespec="milliseconds"),
            "finished_at": finished_at.isoformat(timespec="milliseconds"),
            "elapsed_seconds": round(time.monotonic() - started, 3), "timeout_seconds": timeout,
            "command": sanitized_command, "returncode": proc.returncode, "exit_code": proc.returncode,
            "timed_out": False, "stdout": self._captured_text(proc.stdout),
            "stderr": self._captured_text(proc.stderr),
            "outputs_created": any(item["exists"] for item in records), "outputs": records}
        if proc.returncode!=0 and check:
            raise CreativeMCPError("process_failed",f"Process exited with code {proc.returncode} during {stage}.",result)
        return result

    def execute(self, name: str, args: dict[str,Any]) -> dict[str,Any]:
        if not isinstance(args,dict): raise CreativeMCPError("invalid_arguments","Tool arguments must be a JSON object.")
        if name=="ags_creative_preflight":
            script=self.workspace/"tools/preflight/creative_preflight.py"
            if not script.is_file(): raise CreativeMCPError("studio_tool_missing","Preflight script is missing from workspace.",{"path":"tools/preflight/creative_preflight.py"})
            proc=self.run_bounded([self.python,str(script),"--workspace",str(self.workspace),"--json"],60,stage="creative_preflight",check=False)
            try: payload=json.loads(proc.get("stdout",""))
            except Exception: payload={"status":"output_not_json","stdout":proc.get("stdout"),"stderr":proc.get("stderr")}
            return {"status":"preflight-complete","report":payload,"exit_code":proc["returncode"],"note":"Resource status is advisory; workflow-specific headroom is still required."}
        if name=="ags_validate_animation_sequence":
            manifest=self.safe_path(args.get("manifest_path",""),must_exist=True)
            cmd=[self.python,str(self.workspace/"tools/animation/validate_sequence.py"),str(manifest)]
            if args.get("check_files",False):cmd.append("--check-files")
            proc=self.run_bounded(cmd,20,stage="animation_sequence_validation",check=False)
            try: return json.loads(proc["stdout"])
            except Exception: return {"status":"unparsed_validator_output","result":proc}
        if name=="ags_validate_blender_pose_spec":
            spec=self.safe_path(args.get("pose_spec_path",""),must_exist=True)
            script=self.workspace/"tools/blender/validate_pose_spec.py"
            proc=self.run_bounded([self.python,str(script),str(spec),"--json"],20,check=False)
            try: return json.loads(proc["stdout"])
            except Exception: return {"status":"unparsed_validator_output","result":proc}
        if name=="ags_blender_scene_inventory":
            blend=self.safe_path(args.get("blend_path",""),must_exist=True)
            out=self.safe_path(args.get("output_path",""))
            if out == blend: raise CreativeMCPError("input_output_collision","Inventory JSON output must not be the source .blend path.")
            if out.exists() and not args.get("overwrite",False):raise CreativeMCPError("output_exists","Inventory output already exists; pass overwrite=true after checking it.",{"path":str(out.relative_to(self.workspace))})
            blender=self.blender_binary()
            out.parent.mkdir(parents=True,exist_ok=True)
            script=self.workspace/"tools/blender/inspect_animation_scene.py"
            cmd=[blender,"--background","--disable-autoexec",str(blend),"--python",str(script),"--","--output-json",str(out)]
            timeout=self.bounded_int(args.get("timeout_seconds"),"timeout_seconds",5,300,90)
            proc=self.run_bounded(cmd,timeout,outputs=[out],stage="blender_scene_inventory")
            try: report=json.loads(out.read_text(encoding="utf-8"))
            except Exception as exc:raise CreativeMCPError("inventory_invalid_json",f"Blender returned but inventory cannot be parsed: {exc}",proc)
            return {"status":"inventory-produced-not-quality-approved","report":report,"process":proc}
        if name=="ags_blender_render_action_review":
            blend=self.safe_path(args.get("blend_path",""),must_exist=True)
            output_dir=self.safe_path(args.get("output_dir",""))
            if output_dir.exists() and any(output_dir.iterdir()):raise CreativeMCPError("output_dir_not_empty","Refusing to overwrite existing review frames.",{"path":str(output_dir.relative_to(self.workspace))})
            blender=self.blender_binary()
            output_dir.mkdir(parents=True,exist_ok=True)
            step=int(args.get("step",1));scale=int(args.get("resolution_scale",60));start=args.get("start_frame");end=args.get("end_frame")
            if not 1<=step<=12:raise CreativeMCPError("invalid_step","step must be 1..12.")
            if not 10<=scale<=100:raise CreativeMCPError("invalid_resolution_scale","resolution_scale must be 10..100.")
            if start is not None and end is not None and end<start:raise CreativeMCPError("invalid_range","end_frame must be >= start_frame.")
            if start is not None and end is not None and (end-start)//step>240:raise CreativeMCPError("review_frame_limit","A single render review is limited to 241 frames. Split longer reviews intentionally.")
            script=self.workspace/"tools/blender/render_action_review.py"
            cmd=[blender,"--background","--disable-autoexec",str(blend),"--python",str(script),"--","--armature",str(args["armature_name"]),"--action",str(args["action_name"]),"--output-dir",str(output_dir),"--step",str(step),"--resolution-scale",str(scale)]
            if start is not None:cmd += ["--start",str(int(start))]
            if end is not None:cmd += ["--end",str(int(end))]
            timeout=self.bounded_int(args.get("timeout_seconds"),"timeout_seconds",5,600,180)
            proc=self.run_bounded(cmd,timeout,output_dirs=[output_dir],stage="blender_render_action_review")
            frames=sorted(p for p in output_dir.glob("*.png") if p.is_file())
            if not frames:raise CreativeMCPError("render_produced_no_frames","Blender exited successfully but no frame PNGs were found.",proc)
            return {"status":"candidate-render-frames-only-not-animation-approved","output_dir":str(output_dir.relative_to(self.workspace)),"frame_count":len(frames),"frames":[{"path":str(p.relative_to(self.workspace)),"bytes":p.stat().st_size,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()} for p in frames],"process":proc,"note":"Review playback at intended and slow speed; this render operation does not approve motion or integrate it in-engine."}
        if name=="ags_blender_author_action":
            source=self.safe_path(args.get("source_blend_path",""),must_exist=True)
            spec=self.safe_path(args.get("pose_spec_path",""),must_exist=True)
            output=self.safe_path(args.get("output_blend_path",""))
            if output==source:raise CreativeMCPError("source_overwrite_refused","Output must be a different path than the source .blend file.")
            overwrite=bool(args.get("overwrite_output",False))
            if output.exists() and not overwrite:raise CreativeMCPError("output_exists","Action output exists; set overwrite_output=true only after deliberate review.")
            # Validate spec before launching Blender so most bad requests are cheap failures.
            validator=self.workspace/"tools/blender/validate_pose_spec.py"
            valid_run=self.run_bounded([self.python,str(validator),str(spec),"--json"],20,stage="pose_spec_validation",check=False)
            validation=json.loads(valid_run["stdout"])
            if not validation.get("valid"):raise CreativeMCPError("invalid_pose_spec","Pose spec validation failed.",validation)
            blender=self.blender_binary()
            source_hash=hashlib.sha256(source.read_bytes()).hexdigest()
            output.parent.mkdir(parents=True,exist_ok=True)
            script=self.workspace/"tools/blender/author_action_from_pose_spec.py"
            cmd=[blender,"--background","--disable-autoexec",str(source),"--python",str(script),"--","--pose-spec",str(spec),"--output-blend",str(output)]
            if overwrite:cmd.append("--overwrite-output")
            timeout=self.bounded_int(args.get("timeout_seconds"),"timeout_seconds",5,600,180)
            proc=self.run_bounded(cmd,timeout,outputs=[output],stage="blender_action_authoring")
            if hashlib.sha256(source.read_bytes()).hexdigest()!=source_hash:
                raise CreativeMCPError("source_hash_changed","Source .blend hash changed during action creation; investigate before use.",{"source":str(source.relative_to(self.workspace))})
            return {"status":"candidate-action-authored-not-runtime-verified","source_blend":str(source.relative_to(self.workspace)),"source_sha256_unchanged":True,"pose_spec":str(spec.relative_to(self.workspace)),"output":str(output.relative_to(self.workspace)),"process":proc,
                "next_required_steps":["render the action for inspection","review intended-speed and slow playback","export to engine","verify transitions and event timing in game"]}
        raise CreativeMCPError("unknown_tool",f"Unknown creative tool: {name}")

    def handle(self, request: dict[str,Any]) -> dict[str,Any] | None:
        req_id=request.get("id");method=request.get("method");params=request.get("params",{})
        if not isinstance(method,str): return {"jsonrpc":"2.0","id":req_id,"error":{"code":-32600,"message":"Invalid request: method must be a string"}}
        if method.startswith("notifications/") or method=="$/cancelRequest":return None
        if method=="initialize":
            requested_version = params.get("protocolVersion") if isinstance(params, dict) else None
            if requested_version in SUPPORTED_PROTOCOL_VERSIONS:
                negotiated_version = requested_version
            else:
                # Unknown/unsupported request (including the host-rejected
                # 2025-11-25): answer with the newest version verified to work.
                negotiated_version = COMPATIBILITY_PROTOCOL_VERSION
            return {"jsonrpc":"2.0","id":req_id,"result":{"protocolVersion":negotiated_version,"capabilities":{"tools":{"listChanged":False}},"serverInfo":{"name":"11vatedtech-creative-tools","version":SERVER_VERSION},"instructions":"Use ags_creative_preflight first. All file paths are workspace-relative. The Blender server uses bounded fixed scripts with --disable-autoexec, requires a disposable source project, and never claims a render is approved animation. Read the Studio's agent-first creative contract."}}
        if method=="ping":return {"jsonrpc":"2.0","id":req_id,"result":{}}
        if method=="tools/list":return {"jsonrpc":"2.0","id":req_id,"result":{"tools":TOOLS}}
        if method=="tools/call":
            if not isinstance(params,dict):return {"jsonrpc":"2.0","id":req_id,"error":{"code":-32602,"message":"params must be an object"}}
            name=params.get("name");arguments=params.get("arguments",{})
            try:
                output=self.execute(str(name),arguments)
                return {"jsonrpc":"2.0","id":req_id,"result":{"content":[{"type":"text","text":json.dumps(output,ensure_ascii=False,indent=2,default=str)}],"structuredContent":output,"isError":False}}
            except CreativeMCPError as exc:
                payload={"code":exc.code,"message":str(exc),"details":exc.details}
                return {"jsonrpc":"2.0","id":req_id,"result":{"content":[{"type":"text","text":json.dumps(payload,ensure_ascii=False,indent=2,default=str)}],"structuredContent":payload,"isError":True}}
            except (ValueError,TypeError,KeyError,json.JSONDecodeError) as exc:
                payload={"code":"invalid_arguments","message":str(exc)}
                return {"jsonrpc":"2.0","id":req_id,"result":{"content":[{"type":"text","text":json.dumps(payload,indent=2)}],"structuredContent":payload,"isError":True}}
        if method=="resources/list":return {"jsonrpc":"2.0","id":req_id,"result":{"resources":[]}}
        return {"jsonrpc":"2.0","id":req_id,"error":{"code":-32601,"message":f"Method not found: {method}"}}


def main() -> int:
    try: server=CreativeMCPServer()
    except Exception as exc:
        print(f"creative MCP startup error: {exc}",file=sys.stderr);return 2
    for line in sys.stdin:
        if not line.strip():continue
        try:
            request=json.loads(line)
            if not isinstance(request,dict):raise ValueError("request must be an object")
            response=server.handle(request)
            if response is not None:
                sys.stdout.write(json.dumps(response,ensure_ascii=False,separators=(",",":"))+"\n");sys.stdout.flush()
        except Exception as exc:
            sys.stderr.write(f"creative MCP request error: {type(exc).__name__}: {exc}\n");sys.stderr.flush()
            sys.stdout.write(json.dumps({"jsonrpc":"2.0","id":None,"error":{"code":-32600,"message":"Invalid request"}})+"\n");sys.stdout.flush()
    return 0
if __name__=="__main__":raise SystemExit(main())
