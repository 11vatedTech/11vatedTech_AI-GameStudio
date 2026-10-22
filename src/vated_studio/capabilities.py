from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any
import json


@dataclass(frozen=True, slots=True)
class Capability:
    id: str
    label: str
    status: str
    interface: str
    purpose: str
    dependencies: tuple[str, ...] = ()
    verification: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()
    evidence_level: str = "implemented"

    def __post_init__(self) -> None:
        # Guard against accidental one-item tuple literals written as ("value").
        # Capability contracts must expose lists of complete strings, never characters.
        for field_name in ("dependencies", "verification", "limitations"):
            value = getattr(self, field_name)
            if isinstance(value, str):
                object.__setattr__(self, field_name, (value,))
            elif not isinstance(value, tuple) or not all(isinstance(item, str) for item in value):
                raise TypeError(f"{field_name} must be a tuple of strings")

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        for key in ("dependencies", "verification", "limitations"):
            data[key] = list(data[key])
        return data



# Verification paths refer to real tests in this repository. External model and
# engine claims are kept separate from tests that use protocol fixtures/mocks.
_BUILTIN = [
    Capability("workspace-state", "Workspace, configuration and evidence store", "implemented+tested", "ags init/status/doctor; SQLite run/event/asset/feedback store", "Initialize a workspace, inspect local prerequisites, and persist command outcomes and feedback.", ("Python >=3.11", "SQLite in Python standard library"), ("tests/test_config_paths.py", "tests/test_store_service.py"), ("Doctor readiness does not mean optional image models or game engines are installed."), "tested"),
    Capability("jam-planner", "Time-boxed production planner", "implemented+tested", "ags jam profiles; ags jam plan", "Plan 24-hour, 72-hour, and 14-day work within a release reserve while respecting dependencies and reporting cuts.", (), ("tests/test_planner_workflow.py",), ("A deterministic greedy planner is not a full critical-path or resource-constrained scheduler; estimates require calibration."), "tested"),
    Capability("skill-library", "Searchable specialist skill library", "implemented+tested", "ags skills list/search/read; MCP ags_skill_search", "Load 87 production skills covering design, genres, art styles, assets, animation, rigging, engineering, QA, and release.", ("Bundled SKILL.md package data"), ("tests/test_repository_contracts.py", "tests/test_store_service.py"), ("A skill is guidance, not proof that the described tool or outcome has been tested."), "tested"),
    Capability("project-factory", "Godot 2D project factory", "implemented+tested", "ags project create; project.create", "Create a clearly labeled Godot 4 starter fixture with safe slugging and scoped output paths.", ("Bundled Godot starter template"), ("tests/test_store_service.py",), ("Starter fixture is not a finished game and still requires actual design, content, and engine validation."), "tested"),
    Capability("schema-contracts", "JSON Schema contract library", "implemented+tested", "ags schema list/validate", "Provide machine-readable project, art, asset, animation, task, license, review, QA, and release contracts.", ("jsonschema optional extra for full validation"), ("tests/test_repository_contracts.py", "tests/test_store_service.py"), ("Schema syntax validation does not prove a project's creative or gameplay quality."), "tested"),
    Capability("comfyui-api", "ComfyUI API workflow execution", "implemented+tested", "vated_studio.adapters.comfyui.ComfyUIClient; image.generate.comfy", "Validate API-format workflows, submit jobs, poll history, download outputs, and record output hashes.", ("Compatible local ComfyUI service, nodes and models"), ("tests/test_adapters.py",), ("Automated tests use a local protocol fixture. They do not prove a particular real checkpoint/node graph runs on the target GPU."), "tested-with-mocks"),
    Capability("image-generation-recipes", "Model-specific Klein and Z-Image workflow builders", "implemented+tested", "image.generate.klein; image.generate.zimage", "Build explicit API-format workflow graphs for supported model variants and generation settings.", ("Compatible workflow nodes and exact model assets in local ComfyUI"), ("tests/test_adapters.py",), ("Builder validity is not live-generation proof. Model files, node versions, VRAM, licensing and output quality must be checked on the target machine."), "tested-with-mocks"),
    Capability("sd-webui-api", "Stable Diffusion WebUI API", "implemented+tested", "vated_studio.adapters.sd_webui.SDWebUIClient; image.generate.sd_webui", "Call a compatible local WebUI API and save returned image outputs.", ("Compatible local WebUI with API enabled and a loaded model"), ("tests/test_adapters.py",), ("Endpoint behavior and supported fields vary by WebUI distribution/version; local model quality is not inferred."), "tested-with-mocks"),
    Capability("image-processing", "Image inspection and deterministic refinement", "implemented+tested", "ags asset inspect/process/contact-sheet", "Inspect dimensions, alpha, occupancy and hashes; trim, resize, conservative edge-background removal, and create contact sheets.", ("Pillow and NumPy optional vision extras"), ("tests/test_asset_pipeline.py",), ("Edge-color removal is not semantic matting. Numeric signals are not aesthetic-quality scores."), "tested"),
    Capability("animation-assembly", "Animation frame audit and assembly", "implemented+tested", "ags animation audit/build", "Normalize frame canvas/anchors and create preview GIF, spritesheet, manifest, and measurable diagnostic signals.", ("Pillow and NumPy optional vision extras"), ("tests/test_asset_pipeline.py",), ("Diagnostics cannot judge semantic motion, weight, timing, or expressive readability; playback inspection is required."), "tested"),
    Capability("atlas-packing", "Deterministic sprite atlas packing", "implemented+tested", "asset.atlas; pack_atlas", "Pack images into an atlas with metadata and padding suitable for downstream engine integration.", ("Pillow optional vision extra"), ("tests/test_asset_pipeline.py",), ("Target-engine import and edge-bleed checks remain project-specific."), "tested"),
    Capability("godot-integration", "Godot project validation and guarded export", "implemented+tested", "ags godot doctor/validate/export", "Check project structure, invoke selected Godot validation/export commands with timeouts, and inspect output existence.", ("Godot 4 executable; export templates and named preset for export"), ("tests/test_store_service.py",), ("A command exit code or nonempty export does not prove the game plays correctly. External engine execution was not run in this container."), "tested-with-mocks"),
    Capability("blender-probe", "Blender availability probe", "implemented", "ags doctor; vated_studio.adapters.blender.BlenderAdapter", "Discover a local Blender executable and read its version without forcing a Blender install.", ("Optional local Blender executable"), (), ("No Blender animation/render was executed in this clean-room validation."), "implemented"),
    Capability("rife-runner", "Optional RIFE interpolation wrapper", "implemented", "ags doctor; vated_studio.adapters.rife.RIFEAdapter", "Run a configured RIFE ncnn-vulkan interpolation process and inspect basic output/alpha signals.", ("Optional RIFE binary and compatible model"), (), ("Interpolation does not invent semantic motion; output alpha/silhouette and playback must be reviewed. No RIFE invocation occurred in this container."), "implemented"),
    Capability("local-http", "Authenticated local HTTP API", "implemented+tested", "ags serve; /health; /v1/status; /v1/command", "Expose a bearer-authenticated command surface with request-size bounds, structured errors and loopback-first config.", ("Python standard library"), ("tests/test_config_paths.py", "tests/test_mcp_http.py"), ("Designed for a local trusted workflow, not an internet-facing multi-user service."), "tested"),
    Capability("mcp-stdio", "MCP JSON-RPC stdio server", "implemented+tested", "ags-mcp; MCP ags_status/ags_doctor/ags_capabilities/ags_skill_search/ags_command", "Expose discoverable local studio tools over protocol-clean stdio.", ("Python standard library", "Compatible MCP host"), ("tests/test_mcp_http.py",), ("Protocol tests and local smoke tests do not verify every external coding agent's configuration."), "tested"),
    Capability("release-packager", "Public-release audit and source packaging", "implemented+tested", "ags release audit/package", "Inventory and hash release files; exclude secrets, local state, caches and common model-weight formats; refuse unsafe symlinks and accidental overwrite.", ("Python standard library"), ("tests/test_release_security.py",), ("The tool does not certify copyright, commercial model rights, game quality, or human approval."), "tested"),
    Capability("animation-action-contracts", "Semantic animation action and pose-spec contracts", "implemented+tested", "schemas/animation-sequence-v2.schema.json; schemas/blender-pose-spec-v1.schema.json; tools/animation/validate_sequence.py; tools/blender/validate_pose_spec.py", "Validate action phases, identity invariants, root/prop continuity, gameplay event markers and review state before any engine integration, and reject static-image pulse/transform gimmicks as character animation.", ("Python standard library", "jsonschema optional extra for full schema validation"), ("tests/test_animation_sequence.py", "tests/test_blender_pose_spec.py", "tests/test_overlay_contracts.py"), ("Structural validation cannot judge silhouette, weight, arcs, contact or readability; playback and in-engine review remain required."), "tested"),
    Capability("creative-preflight", "Read-only creative resource preflight", "implemented+tested", "ags readiness; tools/preflight/creative_preflight.py; MCP ags_creative_preflight", "Discover local creative executables and loopback services, measure RAM/GPU/disk headroom, and emit a conservative generation policy without guessing unknown values.", ("Python standard library"), ("tests/test_creative_preflight.py", "tests/test_readiness.py"), ("Advisory only: a passing preflight does not approve a specific model/workflow or guarantee a generation will fit."), "tested"),
    Capability("creative-mcp-server", "Bounded creative-tool MCP server", "implemented+tested", "python tools/creative_mcp_server.py; MCP ags_creative_preflight/ags_validate_animation_sequence/ags_validate_blender_pose_spec/ags_blender_scene_inventory/ags_blender_render_action_review/ags_blender_author_action", "Expose preflight, animation contract validation and Blender authoring/render tools over stdio with workspace-contained paths, argument bounds and fixed bundled scripts.", ("Python standard library", "Local Blender executable for Blender-backed tools"), ("tests/test_creative_mcp_server.py",), ("Automated tests cover path containment, protocol negotiation and process bounding; Blender-backed tools require a local Blender installation and were exercised on one machine, not in CI."), "tested-with-mocks"),
    Capability("blender-action-authoring", "Blender Action authoring and review renders", "implemented", "tools/blender/author_action_from_pose_spec.py; tools/blender/inspect_animation_scene.py; tools/blender/render_action_review.py", "Create or inspect transform-keyed Blender Actions from a validated pose spec, render review frames and verify the source .blend stays unchanged.", ("Blender 4.x/5.x executable; disposable source project"), ("tests/test_blender_pose_spec.py",), ("Executed on one Windows machine with Blender 5.2 as recorded in docs/studio/LOCAL_CREATIVE_UPGRADE_VERIFICATION_2026-10-20.md; not executed in CI, and rendered frames are review candidates rather than approved animation."), "demonstrated"),
]


class CapabilityRegistry:
    def __init__(self, additional: list[dict[str, Any]] | None = None):
        self._items = {item.id: item for item in _BUILTIN}
        for row in additional or []:
            capability = Capability(
                id=row["id"], label=row["label"], status=row["status"], interface=row["interface"], purpose=row["purpose"],
                dependencies=tuple(row.get("dependencies", [])), verification=tuple(row.get("verification", [])),
                limitations=tuple(row.get("limitations", [])), evidence_level=row.get("evidence_level", "documented"))
            self._items[capability.id] = capability

    def list(self, status: str | None = None) -> list[dict[str, Any]]:
        items = sorted(self._items.values(), key=lambda cap: cap.id)
        if status:
            items = [item for item in items if item.status == status]
        return [item.to_dict() for item in items]

    def get(self, capability_id: str) -> dict[str, Any] | None:
        item = self._items.get(capability_id)
        return item.to_dict() if item else None

    def write_snapshot(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"schema_version": "1.0", "capabilities": self.list()}, indent=2), encoding="utf-8")
