from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from . import __version__
from .api.http_server import serve
from .config import StudioConfig
from .errors import StudioError
from .mcp_server import run as run_mcp
from .service import StudioService


def _json_arg(value: str) -> dict[str, Any]:
    if value.startswith("@"):
        raw = json.loads(Path(value[1:]).expanduser().read_text(encoding="utf-8"))
    else:
        raw = json.loads(value)
    if not isinstance(raw, dict):
        raise ValueError("Arguments must decode to a JSON object")
    return raw


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ags", description="11vatedTech AI Game Studio — agent-operated local game-production tools")
    parser.add_argument("--version", action="version", version=f"ags {__version__}")
    parser.add_argument("--workspace", type=Path, default=None, help="Workspace root (default: AGS_WORKSPACE or current directory)")
    sub = parser.add_subparsers(dest="action", required=True)
    sub.add_parser("init", help="Initialize the workspace directories and database")
    sub.add_parser("status", help="Show workspace state and command list")
    sub.add_parser("doctor", help="Probe configured local tools and providers")
    sub.add_parser("capabilities", help="List implemented capabilities and limitations")
    sub.add_parser("commands", help="List available command identifiers")
    serve_parser = sub.add_parser("serve", help="Start the authenticated local HTTP command API")
    serve_parser.add_argument("--host", default=None)
    serve_parser.add_argument("--port", type=int, default=None)
    serve_parser.add_argument("--token", default=None, help="Optional token; otherwise securely generated in workspace state")
    sub.add_parser("mcp", help="Run the MCP stdio server")
    command = sub.add_parser("command", help="Invoke any documented studio command with JSON arguments")
    command.add_argument("name")
    command.add_argument("--args", default="{}", help='JSON object or @path to a JSON file, e.g. @args.json')
    skill = sub.add_parser("skills", help="Search and inspect the production skill library")
    skill_sub = skill.add_subparsers(dest="skills_action", required=True)
    search = skill_sub.add_parser("search")
    search.add_argument("query")
    search.add_argument("--limit", type=int, default=10)
    skill_sub.add_parser("list")
    read = skill_sub.add_parser("read")
    read.add_argument("id")
    jam = sub.add_parser("jam", help="Timeboxed production planning")
    jam_sub = jam.add_subparsers(dest="jam_action", required=True)
    jam_sub.add_parser("profiles")
    plan = jam_sub.add_parser("plan")
    plan.add_argument("--profile", choices=("24h", "72h", "14d"), default="24h")
    plan.add_argument("--tasks", required=True, help="JSON file with an array of task objects")
    plan.add_argument("--elapsed-minutes", type=int, default=0)
    schema = sub.add_parser("schema", help="List schemas and validate project contracts")
    schema_sub = schema.add_subparsers(dest="schema_action", required=True)
    schema_sub.add_parser("list")
    schema_val = schema_sub.add_parser("validate")
    schema_val.add_argument("--schema", required=True)
    schema_val.add_argument("--document", required=True)
    proj = sub.add_parser("project", help="Create or validate Godot projects")
    proj_sub = proj.add_subparsers(dest="project_action", required=True)
    create = proj_sub.add_parser("create")
    create.add_argument("title")
    create.add_argument("--slug")
    validate = proj_sub.add_parser("validate")
    validate.add_argument("path")
    validate.add_argument("--run-engine", action="store_true")
    asset = sub.add_parser("asset", help="Inspect, refine, atlas, or review assets")
    asset_sub = asset.add_subparsers(dest="asset_action", required=True)
    inspect = asset_sub.add_parser("inspect")
    inspect.add_argument("path")
    sheet = asset_sub.add_parser("contact-sheet")
    sheet.add_argument("--paths", nargs="+", required=True)
    sheet.add_argument("--output", default="evidence/contact-sheet.png")
    sheet.add_argument("--columns", type=int, default=3)
    process = asset_sub.add_parser("process")
    process.add_argument("source")
    process.add_argument("destination")
    process.add_argument("--operations", required=True, help="JSON object or @path to operation config")
    animate = sub.add_parser("animation", help="Animation frame assembly and diagnostics")
    anim_sub = animate.add_subparsers(dest="animation_action", required=True)
    audit = anim_sub.add_parser("audit")
    audit.add_argument("--frames", nargs="+", required=True)
    audit.add_argument("--anchor", default="bottom-center", choices=("bottom-center", "center", "top-center"))
    build = anim_sub.add_parser("build")
    build.add_argument("--frames", nargs="+", required=True)
    build.add_argument("--output-stem", required=True)
    build.add_argument("--fps", type=float, default=10.0)
    build.add_argument("--anchor", default="bottom-center", choices=("bottom-center", "center", "top-center"))
    godot = sub.add_parser("godot", help="Godot runtime and export")
    godot_sub = godot.add_subparsers(dest="godot_action", required=True)
    godot_sub.add_parser("doctor")
    godot_validate = godot_sub.add_parser("validate")
    godot_validate.add_argument("project")
    godot_validate.add_argument("--static-only", action="store_true")
    export = godot_sub.add_parser("export")
    export.add_argument("project")
    export.add_argument("--preset", required=True)
    export.add_argument("--output", required=True)
    release = sub.add_parser("release", help="Audit or package a release tree")
    release_sub = release.add_subparsers(dest="release_action", required=True)
    ra = release_sub.add_parser("audit")
    ra.add_argument("release_dir")
    ra.add_argument("--required-files", nargs="*", default=[])
    rp = release_sub.add_parser("package")
    rp.add_argument("source_dir")
    rp.add_argument("archive")
    rp.add_argument("--overwrite", action="store_true", help="Replace an existing archive intentionally")
    return parser


def _run(args: argparse.Namespace) -> Any:
    config = StudioConfig.from_env(args.workspace)
    if args.action == "serve":
        from dataclasses import replace
        if args.host is not None:
            config = replace(config, host=args.host)
        if args.port is not None:
            config = replace(config, port=args.port)
        if args.token is not None:
            config = replace(config, token=args.token)
        serve(config)
        return {"status": "stopped"}
    if args.action == "mcp":
        run_mcp(config)
        return {"status": "stopped"}
    service = StudioService(config)
    if args.action == "init":
        return {"status": "initialized", "workspace": str(config.workspace), "directories": ["assets", "projects", "builds", "evidence", ".state"], "database": str(service.store.path)}
    if args.action == "status":
        return service.execute("status", {})
    if args.action == "doctor":
        return service.execute("doctor", {})
    if args.action == "capabilities":
        return service.execute("capabilities.list", {})
    if args.action == "commands":
        return {"commands": service.command_names}
    if args.action == "command":
        return service.execute(args.name, _json_arg(args.args))
    if args.action == "skills":
        if args.skills_action == "search":
            return service.execute("skills.search", {"query": args.query, "limit": args.limit})
        if args.skills_action == "list":
            return service.execute("skills.list", {})
        return service.execute("skills.read", {"id": args.id})
    if args.action == "jam":
        if args.jam_action == "profiles":
            return service.execute("jam.profiles", {})
        tasks = json.loads(Path(args.tasks).expanduser().read_text(encoding="utf-8"))
        return service.execute("jam.plan", {"profile": args.profile, "tasks": tasks, "elapsed_minutes": args.elapsed_minutes})
    if args.action == "schema":
        if args.schema_action == "list":
            return service.execute("schema.list", {})
        return service.execute("schema.validate", {"schema": args.schema, "document": args.document})
    if args.action == "project":
        if args.project_action == "create":
            return service.execute("project.create", {"title": args.title, "slug": args.slug})
        return service.execute("project.validate", {"path": args.path, "run_engine": args.run_engine})
    if args.action == "asset":
        if args.asset_action == "inspect":
            return service.execute("asset.inspect", {"path": args.path})
        if args.asset_action == "contact-sheet":
            return service.execute("asset.contact_sheet", {"paths": args.paths, "output": args.output, "columns": args.columns})
        return service.execute("asset.process", {"source": args.source, "destination": args.destination, "operations": _json_arg(args.operations)})
    if args.action == "animation":
        if args.animation_action == "audit":
            return service.execute("animation.audit", {"frames": args.frames, "anchor": args.anchor})
        return service.execute("animation.build", {"frames": args.frames, "output_stem": args.output_stem, "fps": args.fps, "anchor": args.anchor})
    if args.action == "godot":
        if args.godot_action == "doctor":
            return service.execute("godot.doctor", {})
        if args.godot_action == "validate":
            return service.execute("godot.validate", {"project": args.project, "run_engine": not args.static_only})
        return service.execute("godot.export", {"project": args.project, "preset": args.preset, "output": args.output})
    if args.action == "release":
        if args.release_action == "audit":
            return service.execute("release.audit", {"release_dir": args.release_dir, "required_files": args.required_files})
        return service.execute("release.package", {"source_dir": args.source_dir, "archive": args.archive, "overwrite": args.overwrite})
    raise ValueError(f"Unsupported action {args.action}")


def main() -> None:
    parser = _parser()
    args = parser.parse_args()
    try:
        result = _run(args)
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    except StudioError as exc:
        print(json.dumps({"ok": False, "error": exc.as_dict()}, ensure_ascii=False, indent=2), file=sys.stderr)
        raise SystemExit(2)
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"ok": False, "error": {"code": type(exc).__name__, "message": str(exc)}}, ensure_ascii=False, indent=2), file=sys.stderr)
        raise SystemExit(2)


if __name__ == "__main__":
    main()
