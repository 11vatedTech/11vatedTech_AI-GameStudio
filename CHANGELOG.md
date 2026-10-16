# Changelog

## 0.4.0 — clean-room consolidated rebuild

- Introduced the `src/vated_studio` package boundary and new command service.
- Consolidated local ComfyUI and SD WebUI adapters, FLUX.2 Klein/Z-Image recipes, Godot/Blender/RIFE probes, safe path handling, workflow state, SQLite run/event/asset/feedback state, jam planning, schema validation, asset image operations, animation assembly/audit, atlas packing, authenticated HTTP, MCP stdio, and release packaging/audit.
- Added a canonical agent contract, specialist workflow library, structured project contracts, researched source register, jam operating profiles, and release/security guidance.
- Explicitly excluded secrets, virtual environments, local database state, model weights, and copied engine exports from public source packaging.
- This version is a rebuilt foundation; real model/engine runtime checks still depend on the machine where those optional tools are installed.
