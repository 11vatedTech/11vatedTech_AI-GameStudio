# Local creative-upgrade verification — 2026-10-20

## Outcome

The v0.2 creative-production overlay is **applied locally** and the bundled creative MCP is **connected to Freebuff and verified through the host-mediated tool path**. Freebuff discovered all six tools and a preflight invocation returned a structured result. Its stdio protocol was also exercised directly. Blender 5.2 authored a real keyframed Action from a rig-specific pose spec, rendered review frames, and the exported glTF was imported and played by Godot 4.7.2 in a disposable project scene.

Test counts in this record are the ones observed on 2026-10-20; current counts and the public-release verification are in [RELEASE_REPORT_2026-10-22.md](RELEASE_REPORT_2026-10-22.md).

This is not a claim that the Studio or every proposed third-party MCP is fully installed/production-ready. No third-party Blender MCP was installed, the sample technical dummy is not finished hero art, and no human art/legal review was performed.

## Why the earlier message mentioned human art

Earlier canon and quality-gate docs said “human art-direction sign-off” and “human review mandatory” without clearly separating *human creative ownership* from *honest approval/status tracking*. That could sound like production work was the operator's responsibility. The current instructions now explicitly assign routine art, rigging, animation, repair, integration, and iteration to the agent; human approval and rights status remain separate, factual gates only where required. See [the agent-first production contract](AGENT_FIRST_CREATIVE_PRODUCTION_CONTRACT.md), [production-director skill](../../skills/production-director/SKILL.md), and [canonical agent instructions](../../AGENTS.md).

## Overlay, tests, and workspace

> **Publication note:** this is a dated local verification record. Paths under `.state/` are Git-ignored local evidence and are **not** part of the public repository, so those links only resolve on the machine where the work was executed. Published artifacts are the source, docs, skills, schemas, registries and project files.

- Installer report: `.state/agent-first-overlay-install-report.json` (local): applied, 51 overlay files created, one skill index merged, optional AGENTS insertion not applied.
- Added the production contract, animation execution runbook, eight specialist skills mirrored into package data, four schemas, method/tool registries, Blender scripts, resource preflight, and a bounded stdlib creative MCP server.
- Initial full-suite run found an ignored local root `.env`, causing the repository hygiene check to false-fail despite it not being publishable. Without reading the file, the test was corrected to fail only when sensitive-named files are not Git-ignored; the root `.env` remains ignored and untouched.
- Final full suite after protocol negotiation and tests: **88 passed, 3 skipped in 14.25s**, no failures. The three skips are symlink tests unavailable on this host.
- Focused creative-MCP suite: **10 passed, 1 skipped**, no failures; the skip is a symlink test unavailable on this host.
- Final compile check: `python -m compileall -q tools tests` passed.
- Documentation-generator check from the preceding verification remains recorded; its unrelated generated files were restored. The current protocol fix did not change documentation generation.
- `ags doctor`: Blender 5.2.0 and Godot 4.7.2 available; ComfyUI responsive on `127.0.0.1:8188`; SD WebUI unavailable on `127.0.0.1:7860`; overall `ready` does not certify any particular model/workflow.
- The optional `AGENTS.md` insertion was reviewed and integrated in a concise canonical form. Recoverable pre-change copies of `AGENTS.md`, the production canon, and quality gates are stored in ignored `.state/backups/`; no upstream GitHub changes were made.
- Git is substantially dirty with the overlay, prior workspace state, and new project fixture; do not commit/push without reconciling ownership.

## Freebuff connector state

The installed Freebuff bundle loads `~/.agents/mcp.json`. Trust/consent state is separate; config presence alone is not proof of a connected or usable server.

- The host MCP config (`%USERPROFILE%/.agents/mcp.json`, machine-local and never committed) contains `11vatedtech-creative-tools` with the local Python 3.12 executable, Studio root, `AGS_WORKSPACE`, and Blender 5.2 path. SHA-256 at inspection: `48e193c3ec3290e483e807bfe5ce4b5d6915ffe94bda6c0c7b34a501e08d00e7`.
- Connector troubleshooting on 2026-10-20: Freebuff Desktop 0.0.182 initially reported `Server's protocol version is not supported: 2025-11-25`. The server was changed to negotiate the verified compatible `2025-06-18` version; a regression test covers a client requesting `2025-11-25`.
- **Host-mediated verification now passed:** Freebuff discovered all six tools from `11vatedtech-creative-tools`; `ags_creative_preflight` was invoked through the connected MCP tool and returned a structured report. This confirms the connector starts, negotiates protocol, exposes tools, and executes an invocation through Freebuff. It does not imply the preflight itself approved heavy generation.
- Latest preflight: overall tool call returned normally (`isError: false`), but the report's generation policy is `pause-heavy-generation` because only 951,386,112 bytes (~0.89 GiB) RAM was available, below the 2 GiB safety threshold. Blender and ComfyUI were responding; GPU reported 11,920 MiB free. Do not run heavy generation until a later preflight shows safe headroom. Godot was not detected in this invocation's environment; treat that as environment discovery, not a change to the prior separate Godot 4.7.2 runtime evidence.
- Direct MCP smoke after the user toggled Enabled, using the configured command/environment without modifying configuration: initialize with client version `2025-06-18` returned the matching version; tool discovery returned all six tools; example sequence and pose specs validated; `../outside.json` was refused with `path_outside_workspace`; server exited 0 with empty stderr. Preflight returned a normal MCP result but its subprocess exit was `2` with policy `pause-heavy-generation`; this is a valid safety warning, not a preflight pass for heavy generation. A previous successful preflight reported `sequential-low-memory-only`; resource headroom is dynamic and this latest more restrictive status should govern until remeasured.
- The web researcher agent was unavailable because its session had expired; no third-party MCP install or package install was attempted.

## Actual Blender authoring and render

All proof artifacts are under the local, Git-ignored `.state/creative-mcp-smoke/vertical-slice/`. This neutral technical dummy proves a workflow, not finished character art or artistic acceptance.

- Blender `5.2.0 LTS`; constructed an 18-bone articulated test rig with weighted mesh pieces, torch, flame, camera and lights.
- Pose spec contains 9 semantic poses (anticipation, initiation, acceleration, contact, follow-through, recovery), tracks 10 bones at each pose, and defines 6 hitbox/impact/audio/VFX/combo markers. Structural validation passed.
- The creative MCP authored `Torch_Sweep_Runtime_Proof` to a new `.blend`. Inspection: **60 F-curves, 540 keyframes**, frames 1–24 at 24 fps, plus the expected event markers. Source hash remained unchanged.
- MCP render produced 12 PNGs (every other source frame) at 50% of 512×512. Blender render logs spanned approximately 9.5 seconds; the MCP output includes hashes for each frame. Local-only artifacts: `contact-sheet.png`, `torch-sweep-24fps.gif`, `action-audit.json`, `torch_sweep.pose.json`. No human semantic/art review was performed. The pose-spec format is reproducible from [the example](../../examples/blender/torch_sweep_pose_spec.example.json).
- `.blend` SHA-256: source `1dbdf14e3714cd5ad66ea4fdfb48d268b1417f1c0bdb4a39d54f17034aa40dc6`; candidate with review camera `a87892ea4f0723bd8c3b3492060bf724a4f954b4820e85a49b580a3b7594c354`.

## Godot import and playback

Exported a GLB candidate and imported it into the existing Godot project in dedicated review-only files. Godot 4.7.2 headless import succeeded; the test scene played the imported Action and reported `ACTION_RUNTIME_PLAYING name=Torch_Sweep_Runtime_Proof duration=1.000 tracks=11`, exit code 0. Import/runtime logs are local-only under `.state/creative-mcp-smoke/vertical-slice/`; the published, reproducible files are [review scene](../../projects/prismatic-creature-battler/scenes/torch_sweep_review.tscn) and [script](../../projects/prismatic-creature-battler/scripts/torch_sweep_review.gd).

This verifies file import and engine-side playback initiation/track existence headlessly. It does **not** prove visual play-scale quality, complete player controls, opponent/contact gameplay, marker-to-hitbox wiring, or human approval. No target body or combat system was integrated.

A review page is available in the shared Preview tab at `http://127.0.0.1:8769/`. Its accessibility snapshot and console/network log were clean, but screenshot capture failed because the preview webview produced no frames.

## Ranked remaining work

1. **Keep tool approval current.** The host-mediated discovery and invocation are verified. If the server's tool manifest changes, re-review Connectors → Choose tools and invoke a smoke test again; do not equate connector health with approval of every future tool.
2. **Quality-gate the animation.** Replace the engineering dummy with a designed hero mesh/rig; author action-specific choreography with feet/root/IK/grip constraints; inspect normal/slow playback and contact poses; fix defects. Wire event markers to gameplay and test hit/contact transitions before acceptance.
3. **Keep repository hygiene robust across developer machines.** The hygiene check now verifies Git ignore status without reading `.env` contents; preserve clean-CI detection of unignored secret files and avoid moving or disclosing local secrets.
4. **Add third-party MCPs one at a time.** Review upstream license, source, compatibility and dependencies. For MCP for Blender use disposable data, localhost-only socket, safe mode, telemetry off; then prove an actual operation through the host UI. Follow with live ComfyUI job/model/node control, Godot debugging, raster-layer editing and browser scenario testing. Catalog entries are recommendations, not installed integrations.
5. **Deepen production automation.** Durable job queues/cancel/retry/resume, versioned candidate promotion, rig/spec-aware validation, review evidence, higher-fidelity character creation, gameplay marker integration and cross-tool regression coverage remain substantial gaps.

## Canonical ownership clarification

The [canonical agent instructions](../../AGENTS.md), [game production canon](11vatedtech-game-production-canon.md), and [quality gates](quality-gates-and-evidence.md) now say unambiguously: agents own routine creative production and asset iteration; primitive/vector/procedural substitutes and static-image motion cannot masquerade as designed final art/character animation; human approvals are separate status gates, not instructions to make the operator create the work. Their pre-change copies are recoverable under ignored `.state/backups/`.

## Completion state

**Completed:** overlay applied; canonical agent-first ownership/policy clarified; direct creative-MCP stdio operations; protocol negotiation/fallback and Freebuff-host-mediated discovery and preflight invocation verified; actual Blender action authoring and frame rendering; actual Godot glTF import and headless action playback; `.blend` source preservation; focused creative-MCP suite (10 passed, 1 skipped); final full suite (88 passed, 3 skipped).

**Open:** third-party MCP installation; production-quality hero art; human art/legal approval; combat/hitbox integration; and screenshot capture (preview compositor unavailable). Freebuff-mediated tool discovery and preflight invocation are now verified. Latest preflight reports `pause-heavy-generation` due to low available RAM; do not run heavy generation until a later preflight shows safe headroom and workflow-specific requirements are checked.
