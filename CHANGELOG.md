# Changelog

## 0.5.0 — agent-first creative production

- Added the agent-first creative production contract, animation execution runbook, creative-tooling architecture, resource-aware job orchestration guidance, and MCP/local-tool catalog. Routine art, rigging, animation, integration and iteration are assigned to the executing agent; human approval and rights review stay separate, factual gates.
- Added eight specialist skills (agent capability discovery, production director, AI asset pipeline, full-stack animation, action design, rigging/retargeting, combat VFX/audio, visual gameplay validation), mirrored into package data; the skill library is now 87 skills.
- Added a bounded stdlib creative MCP server (`tools/creative_mcp_server.py`) exposing preflight, animation-sequence and pose-spec validation, Blender scene inventory, bounded review rendering and pose-spec action authoring over stdio, with workspace-contained paths, symlink refusal, argument bounds, fixed bundled scripts and `--disable-autoexec` Blender subprocesses.
- Added semantic animation contracts (`animation-sequence-v2`, `blender-pose-spec-v1`) and validators that reject static-image pulse/transform gimmicks and missing action phases.
- Added read-only creative preflight and `ags readiness`, which report detected tools, loopback services, RAM/GPU/disk headroom and host MCP configuration without guessing unknown values.
- Fixed MCP protocol negotiation in both stdio servers: supported revisions are negotiated with the client instead of echoing the host-rejected `2025-11-25`.
- Added Blender background scripts for scene inventory, action authoring from a validated pose spec, and bounded review-frame rendering.
- Added asset-method and MCP-tool registries with schemas, plus overlay contract and readiness tests.
- Repository hygiene: the secret-file scan now fails only for secrets Git would actually publish, the Godot adapter resolves PATH/bundled candidates deterministically, and the docs generator no longer drops curated source-register entries.
- Known limits are unchanged in kind: Blender-backed tools were exercised on one machine (see `docs/studio/LOCAL_CREATIVE_UPGRADE_VERIFICATION_2026-10-20.md`), third-party MCPs remain researched rather than installed, and no human art or legal approval is claimed.

## 0.4.0 — clean-room consolidated rebuild

- Introduced the `src/vated_studio` package boundary and new command service.
- Consolidated local ComfyUI and SD WebUI adapters, FLUX.2 Klein/Z-Image recipes, Godot/Blender/RIFE probes, safe path handling, workflow state, SQLite run/event/asset/feedback state, jam planning, schema validation, asset image operations, animation assembly/audit, atlas packing, authenticated HTTP, MCP stdio, and release packaging/audit.
- Added a canonical agent contract, specialist workflow library, structured project contracts, researched source register, jam operating profiles, and release/security guidance.
- Explicitly excluded secrets, virtual environments, local database state, model weights, and copied engine exports from public source packaging.
- This version is a rebuilt foundation; real model/engine runtime checks still depend on the machine where those optional tools are installed.
