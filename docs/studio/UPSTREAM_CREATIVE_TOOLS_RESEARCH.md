# Upstream Creative Tool Research Register

Review snapshot: 2026-10-20. Upstream versions and licensing can change; validate current tags, commits, terms and dependencies before each installation. “Free” below means no mandatory paid cloud service for the described local path; it does not automatically grant commercial rights to model weights or outputs.

## Highest priority integrations

### MCP for Blender — https://github.com/ahujasid/mcp-for-blender

- **Fit:** scene inspection and construction, materials, render views, rig/action inspection, live Blender execution; helps turn Blender from a detected executable into a directly operated production tool.
- **Upstream license:** source project lists MIT; review its separate terms/privacy and the actual version before installation.
- **Security:** the add-on socket has no authentication/encryption. Keep it localhost-only. Use `BLENDER_MCP_SAFE_MODE=1`, disable telemetry, execute against copies, and never accept generated Python without inspecting effects on files/processes/network.
- **Free-first scope:** core Blender authoring/inspection/rendering. Treat premium/cloud 3D generation as optional and out-of-scope.
- **Gate:** scene inventory + one disposable rig action + render frame, all versioned and evidenced.

### Comfy MCP — https://github.com/Comfy-Org/comfy-mcp

- **Fit:** direct agent access to the installed local ComfyUI setup, including models/nodes/templates discovery and generation-job start/wait/cancel/failure diagnosis.
- **License:** upstream identifies AGPL terms and separate comfy-cli terms; comply with applicable distribution requirements. Do not assume a local-use process and public distribution have identical obligations.
- **Gate:** introspect actual installed workflow capabilities, run a tiny known workflow in the existing ComfyUI installation, cancel a test job, verify saved output/hash, and compare with current Studio API adapter.

### Godot MCP — https://github.com/Coding-Solo/godot-mcp

- **Fit:** agent-run engine, project execution, debug output and iterative validation.
- **License:** repository lists MIT. Its tooling stack has Node requirements; verify current runtime requirement and compatibility with the installed Godot version.
- **Gate:** launch a disposable project, capture errors, exercise one input-driven interaction and terminate cleanly. Keep Studio Godot adapter as fallback.

### Playwright MCP — https://github.com/microsoft/playwright-mcp

- **Fit:** browser-level screenshots, mouse/keyboard interactions, console/network checks, reproducible test paths for exported HTML/Web builds.
- **License:** Apache-2.0 repository. Browser and downloaded browser distributions have their own terms.
- **Gate:** open exported build, start/restart a named gameplay scenario, capture output and errors; test at least one alternate viewport.

### Krita MCP — https://github.com/SanSaSane/krita-mcp

- **Fit:** an AI agent has an actual raster editor for layers, masks, visual repair, paint-over, compositing and export instead of approximating serious art with SVG/canvas.
- **License:** upstream repo identifies CC0 for the server; verify current license and plugin compatibility. Krita, any bundled plugin and source/model licenses remain separate.
- **Gate:** open a copy of a project, modify a test layer, inspect exported result, verify source remains intact, and record exact API/plugin version.

## Additional specialist route

### TripoSR — https://github.com/VAST-AI-Research/TripoSR

Single-image-to-3D reconstruction can provide static meshes and block out selected props. Upstream says MIT covers code and pretrained models. Published inference reports around 6 GiB VRAM per image; verify local peak, mesh topology/material quality and export. It does not automatically create a clean rigged hero asset, retopology, UVs, animation or a game-ready mesh.

### FreeMoCap — https://github.com/freemocap/freemocap

Local markerless motion-capture source route for actor-performed movement. The project lists AGPL-3.0 and its desktop release has been described as alpha. It introduces setup and retargeting cost; use only after a controlled test that proves capture accuracy for the intended action, with source video/capture permission recorded.

### Rokoko Studio Live Blender add-on — https://github.com/Rokoko/rokoko-studio-live-blender

Potential retarget/streaming bridge. Validate current license, supported version, service/hardware requirements, and whether its useful path works without a paid account. Do not make it a required dependency before an offline fallback is proven.

### Audacity MCP — https://github.com/xDarkzx/Audacity-MCP

Potential local sound-editing integration. Validate current upstream state, compatible Audacity version, command schema and actual output. If unstable, use Audacity's own available automation/CLI or FFmpeg for deterministic technical processing while keeping compositional decisions explicit.

### FFmpeg MCP — https://github.com/none-stack-developer/ffmpeg-mcp

Experimental convenience wrapper. FFmpeg's own CLI is a mature fallback for media probing, extraction, conversion, resampling and batch assembly. Inspect the wrapper before installing; the build's included codecs have separate licensing considerations.

## Recommended stack order

1. **P0:** Blender MCP (real modeling/rigging/animation/render inspection); existing ComfyUI + Comfy MCP (live capabilities and job control); resource preflight.
2. **P1:** Godot MCP and Playwright MCP for run/inspect/repair/test loops; Krita MCP for layer-based raster reconstruction/refinement.
3. **P2:** local motion capture/retargeting and audio tool integration after dependency/license checks.
4. **P3:** single-image 3D reconstruction and experimental wrappers as bounded specialist tools, never the sole hero asset path.

## Policy

The studio owns the orchestration contract even if third-party MCPs come and go. Keep a versioned machine-readable registry with source, license, security, configuration location, health signal, real smoke test, backup/rollback and last audit. Do not advertise a tool as integrated until the target agent host lists it and an end-to-end operation has been recorded.
