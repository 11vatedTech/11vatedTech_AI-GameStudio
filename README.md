# 11vatedTech AI Game Studio

**A local-first, agent-operated game-production operating system.** It equips Freebuff, Claude Code, and compatible coding agents with a canonical workflow, specialist production skills, structured contracts, local creative-tool adapters, asset/animation processing, project scaffolding, persistent evidence, and release gates.

This is a clean-room consolidation based on the submitted 11vatedTech studio archive and its documented experiments. It preserves the lessons of the existing implementation—working ComfyUI/Klein and SD workflows, the `int32` background-distance fix, path containment, SQLite provenance, animation diagnostics, explicit Godot checks, and the observed limitations of independently generated poses and RIFE alpha—while reorganizing them around a new package and one source of truth.

> **Honesty contract:** the repository contains implemented and tested local tooling plus a broad expert workflow library. It does not make every game AAA-quality automatically, guarantee game-jam wins, or certify art or commercial rights from a command exit code. Each capability is labeled by evidence level; human visual review, playtesting, and rights review remain real gates.

## What is inside

- **Canonical production system:** full discover-to-release lifecycle, genre-aware workflow selection, risk management, handoffs, QA gates, learning loop, and 24-hour / 72-hour / 14-day production profiles.
- **Specialist skill library:** game design, genre patterns, art direction, multiple 2D/3D styles, image generation, ComfyUI, character/environment design, asset extraction, animation approaches, Blender/Godot, VFX, audio, accessibility, testing, licensing, marketing, and release engineering.
- **Local agent interfaces:** command-line interface (`ags`), authenticated loopback HTTP API, and MCP stdio server (`ags-mcp`). The agent calls the studio; the studio does not require a paid reasoning API.
- **Creative-tool adapters:** ComfyUI API-format workflows, reference workflow builders for FLUX.2 Klein 4B and Z-Image Turbo, Stable Diffusion WebUI, Godot 4, Blender, and RIFE detection/invocation. External programs and models remain optional local installations.
- **Asset pipeline:** image inspection, conservative edge-connected background removal, trim/color/resize operations, contact sheets, deterministic atlas packing, animation frame audit/assembly, hashes, and provenance records.
- **Production state:** SQLite run/event/asset/feedback log, workflow state machine, validated JSON Schema contracts, capability registry, jam planning with release reserves, release inventory, ZIP integrity verification, and SHA-256 manifests.
- **Public-repository hygiene:** no bundled weights, `.env`, machine-specific database, virtual environment, or repeated WebAssembly releases.

## Requirements

- Python 3.11+ for the core.
- Optional: Pillow + NumPy for image and animation operations.
- Optional: `jsonschema` for complete draft 2020-12 contract validation.
- Optional: local ComfyUI, Stable Diffusion WebUI, Godot 4, Blender, and RIFE executables for the relevant operations.
- No mandatory API keys, subscriptions, Node runtime, or TypeScript build step.

## Install on Windows (PowerShell)

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
ags init
ags doctor
ags status
```

For image/animation operations, install the vision extra (included in `dev`):

```powershell
python -m pip install -e ".[vision,validation]"
```

For macOS/Linux:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[dev]'
ags init
ags doctor
```

No dependency installer downloads model weights. Configure local services via `.env.example` copied to `.env` and edit only the required executable/endpoint paths. **Never commit `.env` or token files.**

## First five commands

```bash
ags doctor
ags capabilities
ags skills search "reference-conditioned character animation"
ags jam profiles
ags project create "My New Game" --slug my-new-game
```

The created Godot project is an **engine/input smoke fixture**, not finished game art. Read its README and replace it with the actual creative direction before claiming production readiness.

## Image generation

Export an API-format workflow from ComfyUI and put it under your workspace, then:

```bash
ags command image.generate.comfy --args '{"workflow":"workflows/my-api-workflow.json","output_dir":"assets/generated"}'
```

The tested FLUX.2 Klein builder uses explicit `fp8_e4m3fn` by default to retain the valid path observed in the submitted experiment:

```bash
ags command image.generate.klein --args '{"prompt":"A distinctive stylized forest guardian, full body, clear silhouette, consistent costume design, no text","width":1024,"height":1024,"seed":1101,"output_dir":"assets/generated/forest-guardian"}'
```

On hardware with the submitted RTX 5070 Ti report, Klein generation peaked near 11.1 GB of 12.2 GB reported VRAM. **Run sequentially.** This measurement comes from prior evidence and is not guaranteed for another workflow/model revision. The Z-Image recipe is optional and may run near the memory limit; do not run two GPU generations concurrently.

A finished generation is a **candidate**. It still needs technical inspection, art-direction review, refinement, engine integration, and an in-game inspection. `seed` is not an identity-lock mechanism.

## Image and animation examples

```bash
ags asset inspect assets/generated/candidate.png
ags asset process assets/generated/candidate.png assets/refined/candidate.png --operations '{"remove_background":{"color":"#102030","tolerance":18},"trim":{"threshold":0,"padding":8}}'
ags asset contact-sheet --paths assets/refined/a.png assets/refined/b.png --output evidence/candidates.png
ags animation audit --frames assets/anim/f0.png assets/anim/f1.png assets/anim/f2.png --anchor bottom-center
ags animation build --frames assets/anim/f0.png assets/anim/f1.png assets/anim/f2.png --output-stem builds/walk --fps 8
```

Background removal only clears regions connected to the image edge that fall within the chosen color tolerance. It is not semantic segmentation or professional alpha matting. Animation metrics detect dimensional/anchor/duplicate signals; they do not judge whether movement looks good. Playback review is mandatory. RIFE is an interpolator, not a semantic animation generator, and must be rejected when it damages silhouette, timing, or alpha.

## Godot integration

```bash
ags godot doctor
ags godot validate projects/my-new-game
ags godot export projects/my-new-game --preset Web --output builds/my-new-game.html
```

Export requires a matching preset in `export_presets.cfg`, a compatible Godot executable, and installed export templates. The adapter checks that the output exists and is nonempty; it does not prove the game plays correctly. Run the actual output in the target browser/device and capture evidence.

## Agent entrypoints

- `AGENTS.md` — canonical instructions, required by every compatible repository agent.
- `FREEBUFF.md`, `CLAUDE.md`, `GEMINI.md` — thin host-specific entrypoints that defer to the shared canon.
- `skills/*/SKILL.md` — specialist workflow modules with triggers, inputs, procedures, acceptance criteria, failure modes, evidence, and sources.
- `docs/studio/11vatedtech-game-production-canon.md` — authoritative production lifecycle.
- `docs/workflows/game-jam-24h.md`, `game-jam-72h.md`, `game-jam-14d.md` — time-budgeted operating systems.
- `schemas/*.schema.json` — project, art, asset, animation, audio, task, license, review, QA, and release contracts.

## MCP server

Configure a compatible MCP host to run `ags-mcp` from the repository's virtual environment. The server exposes `ags_status`, `ags_doctor`, `ags_capabilities`, `ags_skill_search`, and `ags_command`. It uses standard JSON-RPC over stdio and emits logs to stderr so stdout remains protocol-clean. Test it in the actual agent host after installation; a protocol smoke test alone does not prove host configuration.

## Local HTTP API

```bash
ags serve
```

The API binds to loopback by default. On first run it creates `.state/api-token`; requests to `/v1/command` require `Authorization: Bearer <token>`. `/health` is the only unauthenticated endpoint. Do not expose this service directly to the public internet. Provider URLs are restricted to loopback unless `AGS_ALLOW_REMOTE_PROVIDERS=true` is set intentionally.

## Tests

```bash
python -m pytest -q
```

Current-rebuild verification is recorded in `VERIFICATION.md`. Tests use simulated provider responses where appropriate; they cannot prove that the user's real GPU, ComfyUI node packs, checkpoints, Godot export templates, browser, or licenses are available. Run `ags doctor` and relevant external integration tests on the target machine.

## Public-release policy

This Git repository contains software, workflow recipes, schemas, documentation, and tests—not pretrained model weights. Every model/license entry is model-specific. The code's MIT license does not change upstream model, checkpoint, font, audio, texture, or generated-content licensing. Do not state that a game is commercially cleared until the actual source materials and applicable terms have been reviewed.

## Vision and limitations

The goal is to amplify the operator's agent, not replace creative judgment with a rigid pipeline. The studio makes strong practices available and testable; a game is still only as strong as the design, art direction, implementation, integration, iteration, and actual playtest that went into it. The roadmap in `docs/ROADMAP.md` marks planned or experimental capabilities separately from implemented functions.
