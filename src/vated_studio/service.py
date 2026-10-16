from __future__ import annotations

from pathlib import Path
from typing import Any, Callable
import hashlib
import json
import platform
import sys
import time
import uuid

from . import __version__
from .adapters.blender import BlenderAdapter
from .adapters.comfyui import ComfyUIClient, load_api_workflow
from .adapters.godot import GodotAdapter
from .adapters.rife import RIFEAdapter
from .adapters.sd_webui import SDWebUIClient
from .assets.animation import assemble_animation, audit_frames
from .assets.atlas import pack_atlas
from .assets.images import build_contact_sheet, inspect_image, process_image
from .capabilities import CapabilityRegistry
from .config import StudioConfig
from .errors import StudioError
from .jsonio import atomic_write_json, read_json, sha256_file
from .paths import ensure_inside, require_file, slugify
from .planner import load_profiles, plan_jam
from .projects import ProjectFactory
from .qa.release_audit import audit_release, package_release
from .schemas import list_schemas, validate_document
from .store import StudioStore
from .workflow import ProjectWorkflow, Stage


class StudioService:
    """Shared application services. No hidden model calls; operations are explicit and auditable."""

    def __init__(self, config: StudioConfig):
        self.config = config
        self.workspace = config.workspace.expanduser().resolve()
        self.workspace.mkdir(parents=True, exist_ok=True)
        for directory in ("assets", "projects", "builds", "evidence", ".state"):
            (self.workspace / directory).mkdir(parents=True, exist_ok=True)
        self.store = StudioStore(self.workspace)
        self.projects = ProjectFactory(self.workspace)
        self.comfy = ComfyUIClient(config.comfyui_url, timeout=config.request_timeout_seconds)
        self.sd = SDWebUIClient(config.sd_webui_url, timeout=config.request_timeout_seconds)
        self.godot = GodotAdapter(config.godot_bin, timeout=config.request_timeout_seconds)
        self.blender = BlenderAdapter(config.blender_bin, timeout=config.request_timeout_seconds)
        self.rife = RIFEAdapter(config.rife_bin, timeout=min(config.request_timeout_seconds, 180))
        self.capabilities = CapabilityRegistry()
        self._commands: dict[str, Callable[[dict[str, Any]], Any]] = {
            "status": self.status,
            "doctor": self.doctor,
            "capabilities.list": self.capabilities_list,
            "jam.profiles": self.jam_profiles,
            "jam.plan": self.jam_plan,
            "schema.list": self.schema_list,
            "schema.validate": self.schema_validate,
            "skills.list": self.skills_list,
            "skills.search": self.skills_search,
            "skills.read": self.skills_read,
            "project.create": self.project_create,
            "project.validate": self.project_validate,
            "project.workflow.create": self.project_workflow_create,
            "project.workflow.advance": self.project_workflow_advance,
            "godot.doctor": self.godot_doctor,
            "godot.validate": self.godot_validate,
            "godot.export": self.godot_export,
            "blender.doctor": self.blender_doctor,
            "rife.doctor": self.rife_doctor,
            "asset.import": self.asset_import,
            "asset.inspect": self.asset_inspect,
            "asset.process": self.asset_process,
            "asset.contact_sheet": self.asset_contact_sheet,
            "asset.atlas": self.asset_atlas,
            "animation.audit": self.animation_audit,
            "animation.build": self.animation_build,
            "image.generate.comfy": self.image_generate_comfy,
            "image.generate.klein": self.image_generate_klein,
            "image.generate.zimage": self.image_generate_zimage,
            "image.generate.sd_webui": self.image_generate_sd,
            "release.audit": self.release_audit,
            "release.package": self.release_package,
            "feedback.add": self.feedback_add,
            "runs.list": self.runs_list,
        }

    @property
    def command_names(self) -> list[str]:
        return sorted(self._commands)

    def execute(self, command: str, args: dict[str, Any] | None = None) -> dict[str, Any]:
        if not isinstance(command, str) or not command.strip():
            raise StudioError("Command is required", code="missing_command")
        if args is None:
            args = {}
        if not isinstance(args, dict):
            raise StudioError("Command arguments must be an object", code="invalid_arguments")
        handler = self._commands.get(command)
        if handler is None:
            raise StudioError("Unknown studio command", code="unknown_command", details={"command": command, "available_commands": self.command_names}, http_status=404)
        run_id = uuid.uuid4().hex
        self.store.start_run(run_id, command, args)
        start = time.monotonic()
        try:
            result = handler(args)
            status = self._classify_result(result)
            duration = round((time.monotonic() - start) * 1000, 2)
            envelope = {"run_id": run_id, "command": command, "duration_ms": duration, "status": status, "result": result}
            self.store.finish_run(run_id, status, result=envelope)
            self.store.event("command_completed", {"run_id": run_id, "command": command, "status": status, "duration_ms": duration})
            return envelope
        except StudioError as exc:
            self.store.finish_run(run_id, "blocked" if exc.http_status in (409, 503, 504) else "failed", error=exc.as_dict())
            raise
        except Exception as exc:
            self.store.finish_run(run_id, "failed", error={"code": "internal_error", "type": type(exc).__name__, "message": str(exc)})
            raise StudioError("Studio command failed unexpectedly", code="internal_error",
                              details={"run_id": run_id, "exception_type": type(exc).__name__, "reason": str(exc)}, http_status=500) from exc

    @staticmethod
    def _classify_result(result: Any) -> str:
        if isinstance(result, dict):
            if result.get("status") in {"blocked", "failed", "review_required", "generated_requires_review", "assembled_requires_visual_review"}:
                return "blocked" if result.get("status") == "blocked" else str(result["status"])
            if result.get("runtime_validation") == "blocked":
                return "blocked"
        return "succeeded"

    def status(self, _: dict[str, Any]) -> dict[str, Any]:
        return {"name": "11vatedTech AI Game Studio", "version": __version__, "workspace": str(self.workspace),
                "python": sys.version.split()[0], "platform": platform.platform(), "counts": self.store.counts(),
                "commands": self.command_names, "safety": {"http_default_loopback": True, "provider_remote_opt_in": self.config.allow_remote_providers},
                "claim_boundary": "Command execution success is not evidence of artistic quality, commercial rights, or a complete playable game."}

    def doctor(self, _: dict[str, Any]) -> dict[str, Any]:
        return {"workspace_exists": self.workspace.is_dir(), "workspace_writable": self._writable_probe(),
                "database": self.store.path.is_file(), "comfyui": self.comfy.health(), "sd_webui": self.sd.health(),
                "godot": self.godot.doctor(), "blender": self.blender.doctor(), "rife": self.rife.doctor(),
                "optional_vision": self._vision_available(), "schema_validator": self._jsonschema_available(),
                "overall": "ready" if self.workspace.is_dir() and self._writable_probe() and self.store.path.is_file() else "degraded",
                "note": "Optional tool unavailability blocks only operations that require that tool. Image generation availability does not imply model-license or output-quality approval."}

    def _writable_probe(self) -> bool:
        path = self.workspace / f".write-probe-{uuid.uuid4().hex}"
        try:
            path.write_text("ok", encoding="utf-8")
            path.unlink()
            return True
        except OSError:
            return False

    @staticmethod
    def _vision_available() -> bool:
        try:
            import PIL, numpy  # noqa: F401
            return True
        except ImportError:
            return False

    @staticmethod
    def _jsonschema_available() -> bool:
        try:
            import jsonschema  # noqa: F401
            return True
        except ImportError:
            return False

    def capabilities_list(self, _: dict[str, Any]) -> dict[str, Any]:
        return {"capabilities": self.capabilities.list(), "count": len(self.capabilities.list()),
                "statuses": {"implemented+tested": "code has automated tests", "tested-with-mocks": "protocol logic exercised with simulated HTTP; external runtime not proved", "implemented": "implementation exists, may require manual/external verification", "documented": "described but not demonstrated"}}

    def jam_profiles(self, _: dict[str, Any]) -> dict[str, Any]:
        return {"profiles": load_profiles(), "units": {"hours": "elapsed budget, not guaranteed productive time", "fractions": "planning allocations not fixed contracts"}}

    def jam_plan(self, args: dict[str, Any]) -> dict[str, Any]:
        profile = str(args.get("profile", "24h"))
        tasks = args.get("tasks", [])
        if isinstance(tasks, str):
            tasks = json.loads(tasks)
        measured = args.get("measured_tasks", {})
        if not isinstance(measured, dict):
            raise StudioError("measured_tasks must be an object", code="invalid_measured_tasks")
        return plan_jam(profile, tasks, elapsed_minutes=int(args.get("elapsed_minutes", 0)), measured_tasks=measured)

    def schema_list(self, _: dict[str, Any]) -> dict[str, Any]:
        return {"schemas": self._schema_names()}

    def _schema_names(self) -> list[str]:
        repo_schemas = Path(__file__).resolve().parents[2] / "schemas"
        if repo_schemas.is_dir():
            return list_schemas(repo_schemas)
        bundled = Path(__file__).resolve().parent / "data" / "schemas"
        return list_schemas(bundled)

    def schema_validate(self, args: dict[str, Any]) -> dict[str, Any]:
        schema = args.get("schema")
        document_path = args.get("document")
        if not isinstance(schema, str) or not isinstance(document_path, str):
            raise StudioError("schema and document are required", code="missing_schema_arguments")
        path = ensure_inside(self.workspace, document_path)
        document = read_json(path)
        repo_schemas = Path(__file__).resolve().parents[2] / "schemas"
        base = repo_schemas if repo_schemas.is_dir() else Path(__file__).resolve().parent / "data" / "schemas"
        return {"document": str(path), **validate_document(document, schema, base)}

    def skills_list(self, args: dict[str, Any]) -> dict[str, Any]:
        query = str(args.get("query", "")).strip().lower()
        skills = self._load_skills()
        if query:
            skills = [skill for skill in skills if query in skill["id"].lower() or query in skill["title"].lower() or query in skill["summary"].lower() or any(query in tag.lower() for tag in skill["tags"])]
        return {"skills": skills, "count": len(skills)}

    def skills_search(self, args: dict[str, Any]) -> dict[str, Any]:
        query = str(args.get("query", "")).strip()
        if not query:
            raise StudioError("Search query is required", code="missing_query")
        tokens = {t for t in query.lower().split() if len(t) > 2}
        ranked = []
        for skill in self._load_skills():
            blob = f"{skill['id']} {skill['title']} {skill['summary']} {' '.join(skill['tags'])}".lower()
            score = sum(3 if token in skill["id"].lower() else 2 if token in skill["title"].lower() else 1 for token in tokens if token in blob)
            if score:
                ranked.append((score, skill))
        ranked.sort(key=lambda pair: (-pair[0], pair[1]["id"]))
        return {"query": query, "results": [{**skill, "match_score": score} for score, skill in ranked[:int(args.get("limit", 10))]], "count": len(ranked)}

    def skills_read(self, args: dict[str, Any]) -> dict[str, Any]:
        skill_id = str(args.get("id", "")).strip()
        if not skill_id or "/" in skill_id or "\\" in skill_id or ".." in skill_id:
            raise StudioError("A skill basename is required", code="invalid_skill_id")
        path = self._skills_root() / skill_id / "SKILL.md"
        if not path.is_file():
            raise StudioError("Skill not found", code="skill_not_found", details={"id": skill_id}, http_status=404)
        return {"id": skill_id, "path": str(path), "content": path.read_text(encoding="utf-8")}

    def _skills_root(self) -> Path:
        # Prefer the repository library during development, then bundled package data.
        candidates = [
            Path(__file__).resolve().parents[2] / "skills",
            Path(__file__).resolve().parent / "data" / "skills",
            Path.cwd() / "skills",
        ]
        return next((candidate for candidate in candidates if candidate.is_dir()), candidates[0])

    def _load_skills(self) -> list[dict[str, Any]]:
        root = self._skills_root()
        rows = []
        if not root.is_dir():
            return rows
        for path in sorted(root.glob("*/SKILL.md")):
            text = path.read_text(encoding="utf-8")
            title = path.parent.name.replace("-", " ").title()
            summary = ""
            tags: list[str] = []
            for line in text.splitlines():
                if line.startswith("# "):
                    title = line[2:].strip()
                if line.startswith("Summary:"):
                    summary = line.split(":", 1)[1].strip()
                if line.startswith("Tags:"):
                    tags = [tag.strip() for tag in line.split(":", 1)[1].split(",") if tag.strip()]
            rows.append({"id": path.parent.name, "title": title, "summary": summary, "tags": tags, "path": path.relative_to(root.parent).as_posix()})
        return rows

    def project_create(self, args: dict[str, Any]) -> dict[str, Any]:
        title = str(args.get("title", "")).strip()
        if not title:
            raise StudioError("Project title is required", code="missing_title")
        return self.projects.create_godot_2d(title, slug=args.get("slug"))

    def project_validate(self, args: dict[str, Any]) -> dict[str, Any]:
        path = ensure_inside(self.workspace, str(args.get("path", "")))
        result = self.godot.validate_project(path, run_engine=bool(args.get("run_engine", False)))
        result["project_root"] = str(path)
        return result

    def project_workflow_create(self, args: dict[str, Any]) -> dict[str, Any]:
        workflow = ProjectWorkflow.create(str(args.get("title", "")), args.get("project_id"))
        rel = Path("projects") / workflow.project_id / "studio-workflow.json"
        dest = ensure_inside(self.workspace, rel)
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists():
            raise StudioError("Workflow already exists", code="workflow_exists", http_status=409)
        atomic_write_json(dest, workflow.to_dict())
        return {"path": str(dest), "workflow": workflow.to_dict()}

    def project_workflow_advance(self, args: dict[str, Any]) -> dict[str, Any]:
        project_id = slugify(str(args.get("project_id", "")), fallback="")
        if not project_id:
            raise StudioError("project_id is required", code="missing_project_id")
        path = ensure_inside(self.workspace, Path("projects") / project_id / "studio-workflow.json")
        if not path.is_file():
            raise StudioError("Workflow record not found", code="workflow_not_found", http_status=404)
        data = read_json(path)
        workflow = ProjectWorkflow(data["project_id"], data["title"], Stage(data["current_stage"]))
        # Persist prior history only; transitions must never erase prior events.
        from .workflow import StageEvent
        workflow.history = [StageEvent(h["stage"], h["occurred_at"], h.get("evidence", []), h.get("note", "")) for h in data.get("history", [])]
        workflow.advance(str(args.get("stage", "")), evidence=args.get("evidence", []), note=str(args.get("note", "")))
        atomic_write_json(path, workflow.to_dict())
        return {"path": str(path), "workflow": workflow.to_dict()}

    def godot_doctor(self, _: dict[str, Any]) -> dict[str, Any]:
        return self.godot.doctor()

    def godot_validate(self, args: dict[str, Any]) -> dict[str, Any]:
        path = ensure_inside(self.workspace, str(args.get("project", "")))
        return self.godot.validate_project(path, run_engine=bool(args.get("run_engine", True)))

    def godot_export(self, args: dict[str, Any]) -> dict[str, Any]:
        project = ensure_inside(self.workspace, str(args.get("project", "")))
        output = ensure_inside(self.workspace, str(args.get("output", "builds/export.bin")))
        if output.exists() and not bool(args.get("overwrite", False)):
            raise StudioError("Export output exists; set overwrite=true only after verifying the target", code="output_exists", details={"output": str(output)}, http_status=409)
        return self.godot.export(project, str(args.get("preset", "")), output)

    def blender_doctor(self, _: dict[str, Any]) -> dict[str, Any]:
        return self.blender.doctor()

    def rife_doctor(self, _: dict[str, Any]) -> dict[str, Any]:
        return self.rife.doctor()

    def asset_import(self, args: dict[str, Any]) -> dict[str, Any]:
        source = Path(str(args.get("source", ""))).expanduser()
        if not source.is_file() or source.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"}:
            raise StudioError("Source must be an existing supported image file", code="invalid_image_source", details={"source": str(source)})
        asset_id = uuid.uuid4().hex
        destination = ensure_inside(self.workspace, Path("assets") / f"{asset_id}{source.suffix.lower()}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(source.read_bytes())
        digest = sha256_file(destination)
        metadata = {"source_name": source.name, "imported_from": str(source.resolve()), "provenance": "user_import", "license_status": str(args.get("license_status", "not_recorded"))}
        self.store.record_asset(asset_id=asset_id, project_id=args.get("project_id"), kind=str(args.get("kind", "imported")), relative_path=destination.relative_to(self.workspace).as_posix(), sha256=digest, metadata=metadata)
        inspection = inspect_image(destination) if self._vision_available() else {"status": "not_run", "reason": "Install vision extra"}
        return {"asset_id": asset_id, "path": str(destination), "sha256": digest, "metadata": metadata, "inspection": inspection}

    def asset_inspect(self, args: dict[str, Any]) -> dict[str, Any]:
        path = ensure_inside(self.workspace, str(args.get("path", "")))
        return inspect_image(path)

    def asset_process(self, args: dict[str, Any]) -> dict[str, Any]:
        source = ensure_inside(self.workspace, str(args.get("source", "")))
        destination = ensure_inside(self.workspace, str(args.get("destination", "")))
        if destination.exists() and not bool(args.get("overwrite", False)):
            raise StudioError("Destination exists; pass overwrite=true only when replacement is intended", code="output_exists", http_status=409)
        return process_image(source, destination, args.get("operations", {}))

    def asset_contact_sheet(self, args: dict[str, Any]) -> dict[str, Any]:
        paths = args.get("paths", [])
        if not isinstance(paths, list) or not paths:
            raise StudioError("paths must be a non-empty array", code="invalid_paths")
        safe_paths = [ensure_inside(self.workspace, value) for value in paths]
        output = ensure_inside(self.workspace, str(args.get("output", "evidence/contact-sheet.png")))
        return build_contact_sheet(safe_paths, output, cell_size=tuple(args.get("cell_size", [320, 320])), columns=int(args.get("columns", 3)), labels=args.get("labels"))

    def asset_atlas(self, args: dict[str, Any]) -> dict[str, Any]:
        paths = args.get("paths", [])
        if not isinstance(paths, list) or not paths:
            raise StudioError("paths must be a non-empty array", code="invalid_paths")
        safe_paths = [ensure_inside(self.workspace, value) for value in paths]
        output = ensure_inside(self.workspace, str(args.get("output", "assets/atlas.png")))
        if output.exists() and not bool(args.get("overwrite", False)):
            raise StudioError("Atlas output already exists", code="output_exists", http_status=409)
        return pack_atlas(safe_paths, output, max_width=int(args.get("max_width", 2048)), padding=int(args.get("padding", 2)))

    def animation_audit(self, args: dict[str, Any]) -> dict[str, Any]:
        frames = args.get("frames", [])
        if not isinstance(frames, list):
            raise StudioError("frames must be an array", code="invalid_frames")
        safe = [ensure_inside(self.workspace, value) for value in frames]
        return audit_frames(safe, anchor=str(args.get("anchor", "bottom-center")), drift_warning_px=float(args.get("drift_warning_px", 6)))

    def animation_build(self, args: dict[str, Any]) -> dict[str, Any]:
        frames = args.get("frames", [])
        if not isinstance(frames, list):
            raise StudioError("frames must be an array", code="invalid_frames")
        safe = [ensure_inside(self.workspace, value) for value in frames]
        output_stem = ensure_inside(self.workspace, str(args.get("output_stem", "builds/animation")))
        outputs = [output_stem.with_suffix(".gif"), output_stem.with_name(output_stem.name + "_spritesheet.png"), output_stem.with_name(output_stem.name + "_animation.json")]
        if any(path.exists() for path in outputs) and not bool(args.get("overwrite", False)):
            raise StudioError("Animation output exists; set overwrite=true to replace it intentionally", code="output_exists", details={"outputs": [str(p) for p in outputs]}, http_status=409)
        return assemble_animation(safe, output_stem, fps=float(args.get("fps", 10)), anchor=str(args.get("anchor", "bottom-center")), padding=int(args.get("padding", 4)))

    def image_generate_comfy(self, args: dict[str, Any]) -> dict[str, Any]:
        workflow_data = args.get("workflow")
        if isinstance(workflow_data, str):
            workflow_path = ensure_inside(self.workspace, workflow_data)
            workflow = load_api_workflow(workflow_path)
        elif isinstance(workflow_data, dict):
            from .adapters.comfyui import validate_api_workflow
            workflow = validate_api_workflow(workflow_data)
        else:
            raise StudioError("workflow must be an API-format workflow object or workspace-relative JSON path", code="missing_workflow")
        output = ensure_inside(self.workspace, str(args.get("output_dir", "assets/generated")))
        return self.comfy.generate_from_workflow(workflow, output, timeout=float(args.get("timeout_seconds", self.config.request_timeout_seconds)))

    def image_generate_klein(self, args: dict[str, Any]) -> dict[str, Any]:
        from .adapters.klein_workflows import make_klein_txt2img
        output = ensure_inside(self.workspace, str(args.get("output_dir", "assets/generated")))
        workflow = make_klein_txt2img(prompt=str(args.get("prompt", "")), width=int(args.get("width", 1024)),
                                      height=int(args.get("height", 1024)), seed=int(args.get("seed", 1)),
                                      steps=args.get("steps"), cfg=args.get("cfg"),
                                      distilled=bool(args.get("distilled", True)),
                                      weight_dtype=str(args.get("weight_dtype", "fp8_e4m3fn")))
        result = self.comfy.generate_from_workflow(workflow, output, timeout=float(args.get("timeout_seconds", self.config.request_timeout_seconds)))
        result["workflow_recipe"] = "flux2-klein-4b-distilled-fp8"
        result["requested_seed"] = int(args.get("seed", 1))
        result["review_required"] = True
        return result

    def image_generate_zimage(self, args: dict[str, Any]) -> dict[str, Any]:
        from .adapters.zimage_workflows import make_zimage_txt2img
        output = ensure_inside(self.workspace, str(args.get("output_dir", "assets/generated")))
        workflow = make_zimage_txt2img(prompt=str(args.get("prompt", "")), width=int(args.get("width", 512)),
                                       height=int(args.get("height", 512)), seed=int(args.get("seed", 1)),
                                       steps=int(args.get("steps", 8)), cfg=float(args.get("cfg", 1.0)))
        result = self.comfy.generate_from_workflow(workflow, output, timeout=float(args.get("timeout_seconds", self.config.request_timeout_seconds)))
        result["workflow_recipe"] = "z-image-turbo-bf16"
        result["requested_seed"] = int(args.get("seed", 1))
        result["review_required"] = True
        return result

    def image_generate_sd(self, args: dict[str, Any]) -> dict[str, Any]:
        output = ensure_inside(self.workspace, str(args.get("output_dir", "assets/generated")))
        return self.sd.generate(prompt=str(args.get("prompt", "")), negative_prompt=str(args.get("negative_prompt", "")),
                                width=int(args.get("width", 512)), height=int(args.get("height", 512)), steps=int(args.get("steps", 24)),
                                cfg_scale=float(args.get("cfg_scale", 6.0)), seed=int(args.get("seed", -1)),
                                sampler_name=args.get("sampler_name"), output_dir=output)

    def release_audit(self, args: dict[str, Any]) -> dict[str, Any]:
        target = str(args.get("release_dir", ""))
        if not target:
            raise StudioError("release_dir is required", code="missing_release_dir")
        return audit_release(self.workspace, target, required_files=args.get("required_files", []))

    def release_package(self, args: dict[str, Any]) -> dict[str, Any]:
        source = str(args.get("source_dir", ""))
        output = str(args.get("archive", ""))
        if not source or not output:
            raise StudioError("source_dir and archive are required", code="missing_package_arguments")
        return package_release(self.workspace, source, output, overwrite=bool(args.get("overwrite", False)))

    def feedback_add(self, args: dict[str, Any]) -> dict[str, Any]:
        category = str(args.get("category", "")).strip()
        notes = str(args.get("notes", "")).strip()
        reviewer_type = str(args.get("reviewer_type", "agent"))
        if not category or not notes or reviewer_type not in {"human", "agent", "automated"}:
            raise StudioError("category, notes, and a valid reviewer_type are required", code="invalid_feedback")
        rating = args.get("rating")
        if rating is not None and (not isinstance(rating, int) or not 1 <= rating <= 5):
            raise StudioError("rating must be an integer in 1..5", code="invalid_rating")
        feedback_id = uuid.uuid4().hex
        self.store.add_feedback(feedback_id=feedback_id, project_id=args.get("project_id"), artifact_id=args.get("artifact_id"),
                                category=category, rating=rating, notes=notes, reviewer_type=reviewer_type,
                                context=args.get("context", {}) if isinstance(args.get("context", {}), dict) else {})
        return {"feedback_id": feedback_id, "reviewer_type": reviewer_type, "status": "recorded"}

    def runs_list(self, args: dict[str, Any]) -> dict[str, Any]:
        return {"runs": self.store.runs(int(args.get("limit", 50)))}


def load_api_workflow(path: Path) -> dict[str, Any]:
    return load_api_workflow_impl(path)


# Alias kept here for a single explicit file-workflow loading path.
from .adapters.comfyui import load_api_workflow as load_api_workflow_impl
