# MCP and Local Tool Catalog

See [UPSTREAM_CREATIVE_TOOLS_RESEARCH.md](UPSTREAM_CREATIVE_TOOLS_RESEARCH.md) for source/license notes. This document defines the responsibilities of the proposed stack; catalog entries are recommendations, not installed integrations.

| Role | Tool | Agent must be able to do | Fallback |
|---|---|---|---|
| 3D authoring | Blender + MCP for Blender | Inspect scene/rig/actions; create/edit mesh/materials; author keyframes; render review views; export assets | Blender Python scripts in background mode |
| Image generation | Existing local ComfyUI workflows + Comfy MCP | Query live models/nodes; validate graph; launch/watch/cancel job; collect output and logs | Studio ComfyUI API adapter |
| Raster authoring | Krita + Krita MCP if verified | Work with real layers/masks, inspect result, repair edges, export | Krita manual/script/plugin path; Pillow for technical transforms only |
| Game engine | Godot + existing adapter and optional Godot MCP | Build/run, inspect errors, test scene changes | `ags godot validate/export`, executable CLI |
| Browser test | Playwright MCP | Launch build, perform named input scenarios, screenshot, inspect console errors | Playwright direct CLI/script if available |
| Audio | Audacity/available local DAW + optional MCP | Inspect, edit, mix, normalize, export and preserve stems | FFmpeg for deterministic conversion; direct editing tools |
| Motion capture | FreeMoCap / compatible retarget route | Capture/retarget skeleton, map rig, clean foot/hand/weapon contacts | Manually authored Blender action specs or conditioned keyframes |
| Media QA | FFmpeg CLI / optional MCP | Probe metadata, compare frame/audio outputs, extract contact sheets | Python/Pillow tooling |
| Studio state | `ags` and `ags-mcp` | Record projects, capability evidence, jobs, assets, provenance, tests and release data | Durable project manifests if the Studio service is unavailable |
| Creative execution MCP | Bundled `tools/creative_mcp_server.py` | Read-only preflight; validate animation/pose contracts; inspect Blender scenes; create pose-spec Actions to a new blend; render bounded review frames | Direct fixed script CLI tools in `tools/`; the MCP server is stdio-only and must be registered in the actual agent host |

## Required common protocol

Every external tool adapter must offer or document: `doctor/health`, `capabilities`, `run`, `inspect`, `cancel` where jobs are asynchronous, structured error output, version/source identification, workspace-scoped IO, provenance capture, and a safe disposable-project smoke test. Tools without the needed operations may still be used manually but must not be overstated as fully integrated.

## Security boundaries

- Localhost by default; no unauthenticated socket listener on external interfaces.
- Never pass prompt/filename text through shell interpolation. Use argument arrays and explicit paths.
- Generated Python/scripts are untrusted. Inspect before execution and run destructive operations against copies.
- Never automatically install arbitrary custom nodes or model repos. Read install scripts, pin versions, inspect dependencies, then approve the environment change.
- Never expose `.env`, host tokens, browser profiles, project secrets, model caches or private references in public artifacts.
