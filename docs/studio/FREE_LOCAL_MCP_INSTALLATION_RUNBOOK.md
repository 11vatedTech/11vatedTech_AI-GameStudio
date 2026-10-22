# Free-First Local MCP Installation Runbook (Windows)

**Rule:** add one MCP at a time. Confirm the actual client build and configuration path before editing. Preserve user files and secrets. Never expose unauthenticated local tool sockets to LAN/internet.

## 1. Start with read-only discovery

1. In a PowerShell terminal, record `python --version`, `git --version`, `uvx --version` (if present), `blender --version`, and the configured Studio doctor report.
2. Run `python tools/preflight/creative_preflight.py --json` from the Studio repository root and save the output to a local evidence folder. If `nvidia-smi` is missing, GPU state is **unknown**—do not guess.
3. Open the exact installed Freebuff version's settings or help docs and find the documented MCP/tool-server configuration mechanism. Do not presume it uses Codex's `~/.codex/config.toml`, Claude's JSON format, or any specific path. Search likely app configuration locations only after asking what version/install channel is being used, and never print token values.
4. Back up that config before any change. If format/location is unclear, stop before edit and report the exact unresolved fact.

## 2. MCP for Blender — first candidate

Upstream: https://github.com/ahujasid/mcp-for-blender

It has two components: a Blender add-on that runs a socket server within Blender and a Python MCP server. It can expose scene operations, direct Blender Python execution, multi-view rendering, and animation/rig/action inspection. It is third-party software, not an official Blender Foundation tool.

Security requirements:

- Keep Blender's socket on `localhost` / `127.0.0.1`; do not forward port 9876 to public interfaces.
- Set `BLENDER_MCP_SAFE_MODE=1` for initial use. Safe mode reduces what scripts may do; if a legitimate required operation is blocked, evaluate a dedicated safe wrapper and narrowly scoped allowlist rather than disabling it globally without a review.
- Set `DISABLE_TELEMETRY=true` in the server process and check the add-on's privacy/telemetry toggle in the actual installed version.
- Run on a disposable project first. Keep a source `.blend` backup; generated scripts can still damage a scene.
- Verify exact upstream license/terms/version on install. Premium generation/connectors are outside the free-first baseline.

For Codex CLI only, upstream documents this form (it is an example, not a Freebuff configuration):

```powershell
uvx mcp-for-blender --help
codex mcp add blender -- uvx mcp-for-blender
```

A manually reviewed Codex TOML example is in `config/examples/codex-mcp-blender.toml`. Prefer using the actual MCP host's documented mechanism, include the environment variables above, restart the host, and verify with its MCP list/tool list. Keep a second terminal/log open for errors.

### Blender connection smoke test

1. Open Blender, enable the installed MCP add-on and start its server only on localhost.
2. Confirm the MCP server reports connected and the host lists actual Blender tools.
3. Use read-only tools first: list scene objects, active camera, armatures, bones, actions and frame ranges.
4. In a *copy* of a disposable scene, create one object/material, set one keyframe, render a frame, inspect the image, and verify no source file was overwritten.
5. Record server/package/add-on versions, exact tool names, success/failure and evidence. Only then mark this connection demonstrated.


## 2A. Bundled Studio creative MCP (stdio, no third-party Python dependency)

The overlay includes `tools/creative_mcp_server.py`, a stdlib MCP server that gives the compatible host fixed named tools for: local preflight; semantic animation validation; Blender pose-spec validation; read-only scene inventory; bounded Action frame rendering; and action authoring from validated pose specs. It is separate from the Studio's current `ags-mcp` so it can be smoke-tested without replacing the installed server.

Register the script using the actual agent host's documented stdio MCP configuration. Set `AGS_WORKSPACE` to the root of the installed Studio clone and `BLENDER_BIN` to the actual Blender executable. A Codex-only example with placeholders is in `config/examples/codex-mcp-creative-server.toml`. Do **not** copy it over another host's config.

Its safety boundaries are deliberate: only relative paths within `AGS_WORKSPACE`, symlink-path refusal, fixed bundled scripts (no arbitrary shell command argument), bounded timeouts, Blender `--disable-autoexec`, distinct output `.blend`, source hash check, and no network listener. `ags_blender_author_action` produces transform-keyed candidate motion from the provided bone pose spec; it cannot invent good choreography without rig-specific pose design. Rendered PNGs are review evidence, not an approved animation.

Smoke test without Blender first: connect the MCP host, list tools, call `ags_creative_preflight`, validate `examples/animation/torch_sweep.sequence.example.json`, and validate `examples/blender/torch_sweep_pose_spec.example.json`. Then test the Blender tools against a copied rig file only. If the installed Freebuff host's MCP configuration is unknown, stop before touching any config and determine the correct mechanism from that build.

## 3. Comfy MCP — local generation orchestration

Upstream: https://github.com/Comfy-Org/comfy-mcp

This is a separate MCP route from the Studio's existing ComfyUI API adapter. It can run/monitor/cancel jobs and inspect the models, nodes and templates installed in the live ComfyUI instance. Respect its source license and dependencies; use the local server mode, not Comfy Cloud. Avoid installing into the same Python environment that holds a carefully configured ComfyUI stack unless upstream specifically supports it. Use a separately pinned environment and record the exact version. Do not install custom nodes blindly.

## 4. Godot MCP — runtime feedback

Upstream: https://github.com/Coding-Solo/godot-mcp

Use as an optional agent interface for launch/run/debug-output workflows after reading the current upstream requirements (the published project uses Node). Keep the Studio's own Godot validate/export commands available as an independent fallback. Actual browser game acceptance still requires a browser run, controls, objective completion/restart and console/error review.

## 5. Krita MCP — raster/layer editing

Upstream: https://github.com/SanSaSane/krita-mcp

Use as an optional route for layered painting, inpainting cleanup, mask/alpha work, compositing and export. Confirm plugin/API compatibility with the installed Krita version before relying on it. Do not confuse MCP project license with Krita's license or model/asset licenses.

## 6. Browser MCP

Upstream: https://github.com/microsoft/playwright-mcp

Useful for opening the real HTML/Web export, sending mouse/keyboard input, capturing screenshots and inspecting browser console/network errors. Pin/review the version. Browser automation verifies technical paths, not subjective game feel by itself. Add named repeatable scenarios rather than random unrecorded clicks.

## 7. Audio workflow

Prefer native CLI/automation first if present; otherwise evaluate Audacity MCP (https://github.com/xDarkzx/Audacity-MCP) for local clip inspection/editing. Use a compatible local tool to author/record/mix SFX/music. FFmpeg is useful for audio/video probing, resampling, codec conversion and frame extraction. Verify the binary build and codec/legal terms for redistributed outputs. Keep all sources, stems, sample rates, loudness targets and asset rights records.

## 8. Motion capture and retargeting

FreeMoCap is a free/open-source markerless capture option: https://github.com/freemocap/freemocap. Its project is AGPL-3.0 and the published release is alpha; evaluate deployment/licensing/quality before making it a dependency. Capture motion for a specific action, inspect skeleton fit, retarget to the actual game rig, repair hand/weapon contact and feet/root, then export and review. Do not treat unretargeted skeleton coordinates as final animation.

## 9. Installation and update safety

- Keep separate environments for ComfyUI, Blender MCP and auxiliary Python packages where dependency overlap could break CUDA/PyTorch.
- Pin versions/commit SHAs in the local tool registry; periodically re-audit upstream license/security/telemetry notes.
- Never commit user-specific MCP config, tokens, absolute paths, model weights or logs containing private content.
- Make a one-tool-per-change diff and retain a rollback copy.
- If a host does not support the requested MCP feature or its config mechanism is unknown, mark `blocked_dependency` and preserve the information needed to continue—not a fabricated success.
