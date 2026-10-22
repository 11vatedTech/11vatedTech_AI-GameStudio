# Release Report — v0.5.0 "Agent-First Creative Production" (2026-10-22)

This report records what was audited, consolidated, validated and published. It separates automated tests, agent inspection, and unverified external dependencies on purpose. Read it with [the verification record of 2026-10-20](LOCAL_CREATIVE_UPGRADE_VERIFICATION_2026-10-20.md), which documents the original local overlay work.

## 1. Release summary

The local repository contained a large body of uncommitted creative-production work on top of the published v0.4.0 clean-room rebuild. This release consolidates that work into the public repository:

- an agent-first creative production contract and supporting runbooks;
- eight new specialist skills (87 total, mirrored into package data);
- a bounded creative-tool MCP server plus Blender authoring/review scripts;
- semantic animation contracts (`animation-sequence-v2`, `blender-pose-spec-v1`) and validators;
- read-only creative preflight and `ags readiness`;
- asset-method and MCP-tool registries with schemas;
- fixes for MCP protocol negotiation, documentation-generator drift, and repository hygiene checks.

Version moved to `0.5.0` because new public interfaces (`ags readiness`, creative MCP tools, new schemas) were added.

## 2. Starting state

- Branch `work/unwriters-almanac` at `0da7804`, identical to `main` and `origin/main`; no upstream configured.
- 762 working-tree changes (13 modified, 749 untracked), including ~108 MB of regenerated engine/web exports, local `.state/` evidence and duplicate generated files.
- Baseline suite: **115 passed, 3 skipped** (16.08 s) on Python 3.12.10, Windows.

## 3. Files and subsystems changed

Subsystems: creative MCP server (`tools/creative_mcp_server.py`), Blender scripts (`tools/blender/`), animation validation (`tools/animation/validate_sequence.py`), preflight (`tools/preflight/creative_preflight.py`), readiness (`src/vated_studio/readiness.py`), CLI, Godot adapter, capability registry, MCP negotiation, docs generator, schemas, skills, registries, case-study projects and curated evidence.

Corrections made during consolidation (cause first, then the change):

| Problem found | Correction |
| --- | --- |
| `tools/build_docs.py` rebuilt `docs/research/source-register.json` without four curated entries (Z-Image model card, ComfyUI Z-Image template, Godot AnimationTree, Blender animation), silently deleting provenance on every run. | The generator template now emits all 19 entries; rerunning it reproduces the tracked file byte-for-byte. |
| The package MCP server (`ags-mcp`) echoed any requested protocol version and defaulted to `2025-11-25`, the revision the installed Freebuff host rejects. | Both stdio servers negotiate only implemented revisions (`2025-06-18`, `2025-03-26`, `2024-11-05`) and answer unknown requests with the newest verified one. Tests cover echo, fallback and the rejected revision. |
| The creative MCP server advertised a single hard-coded version string. | Same negotiation policy, with the unsupported-version list documented in code and exercised by tests. |
| `assets/refined/creatures-atlas.json` stored absolute `C:\Users\...` source paths. | Atlas manifests now record a repository-relative `source` when the input is under the working directory; the committed manifest was rewritten (hashes unchanged and re-verified). |
| Capability register could not describe the new tools. | Four capabilities added in `capabilities.py` and the snapshot regenerated; `docs/capability-register.json` again equals the runtime registry and validates against its schema. |
| Generated exports, duplicate ComfyUI output and runtime copies were untracked but publishable. | `.gitignore` now excludes `builds/`, `**/.state-*/`, `*.zip`, skill-index backups and the byte-identical ComfyUI `generation-output/` mirror. |
| A local absolute host path appeared in a published verification doc. | Replaced with `%USERPROFILE%/.agents/mcp.json`; `.state/` evidence links are now described as local-only instead of dead links. |

## 4. Validation results

All commands ran on Windows 11, Python 3.12.10, from the repository root, on 2026-10-22.

| Check | Command | Result |
| --- | --- | --- |
| Full test suite | `python -m pytest -q` | **116 passed, 3 skipped** (17.16 s), 0 failed |
| Compilation | `python -m compileall -q src tools tests` | exit 0 |
| Whitespace | `git diff --check` | exit 0 |
| Schema meta-validation, bundled-schema parity, registry/schema conformance | included in the suite (`test_repository_contracts.py`, `test_overlay_contracts.py`) | passed |
| Capability register equals runtime and schema | included in the suite | passed |
| Creative MCP stdio session | initialize → tools/list → valid sequence → `../outside.json` | 6 tools listed; sequence `valid: true`; traversal refused with `path_outside_workspace`; exit 0; empty stderr |
| `ags-mcp` negotiation | initialize with supported/unsupported/missing versions | echoes supported revisions, falls back to `2025-06-18` for `2025-11-25` and malformed input |
| `ags readiness` | `python -m vated_studio.cli readiness` | ran; reported `BLOCKED` overall (quality approval open, environment partial) — the expected honest state, not a failure |
| `ags doctor` | `python -m vated_studio.cli doctor` | Godot 4.7.2, Blender 5.2.0 LTS and RIFE binaries detected; ComfyUI and SD WebUI **not running** at validation time (connection refused) |
| Godot project | `python -m vated_studio.cli godot validate projects/prismatic-creature-battler` | `static_valid: true`, `runtime_validation: passed`, headless editor run exit 0 (5.27 s) |
| Wheel build | `python -m pip wheel --no-deps . --wheel-dir dist-check` | `11vatedtech_ai_game_studio-0.5.0-py3-none-any.whl`, 0.21 MB |
| Wheel contents | inspect archive | 87 `SKILL.md`, 25 schemas, `cli.py`, `readiness.py`, packaged LICENSE |
| Installed-package use | install wheel into a clean `--target`, import from an unrelated directory | loads 87 skills and 21 capabilities without the repository |
| Secret scan | pattern scan over all 676 publishable candidate files | 1 hit: the intentional `local-test-token-long-enough` test fixture; no private-key blocks |
| Large-file audit | largest candidate file | ~38 MB wasm **excluded** with `builds/`; largest published file is 14 MB (Blender review spritesheet) |

The three skips are symlink-creation tests that Windows without developer mode cannot run; they are skipped, not passed, and run on the Linux CI matrix.

## 5. MCP protocol and host integration

- Verified locally on 2026-10-22: the creative server starts over stdio, negotiates `2025-06-18`, lists six tools, validates the example animation sequence, refuses a path outside the workspace, ignores notifications, and exits 0 with no stderr output.
- Host-mediated discovery and one preflight invocation through the connected Freebuff connector were verified on 2026-10-20 (see the linked record). That host verification was **not** repeated in this release; the connector configuration on this machine is machine-local and Git-ignored.
- No third-party MCP (MCP-for-Blender, Comfy MCP, Godot MCP, Krita MCP, Playwright MCP) is installed or claimed as integrated. Registry entries are research status only.

## 6. Blender and Godot verification

Re-executed through the creative MCP tool interface on 2026-10-22, using the previously created disposable rig in the Git-ignored `.state/` workspace:

| Operation | Result |
| --- | --- |
| `ags_blender_scene_inventory` on the source rig | exit 0 in 4.27 s; 24 objects, 1 armature (`TorchSweepRig`, 18 bones), frame range 1–24, camera `ReviewCamera` |
| `ags_blender_author_action` from `torch_sweep.pose.json` | exit 0 in 3.92 s; output `.blend` 139,100 bytes, SHA-256 `ed275fb4e1ad53c36989fb82155db1349bb6f8527068bcfd75eeb8f60cab576c`; source hash unchanged |
| Inventory of the authored file | action `Torch_Sweep_Runtime_Proof`, frames 1–24 present |
| `ags_blender_render_action_review` | exit 0 in 9.48 s; 6 PNG frames at 256×256, all distinct hashes |

Interpretation, stated plainly: this proves the Blender integration runs, preserves the source file, and produces inspectable frames. The rig is an engineering dummy, the action comes from a scripted pose spec, and six downsampled frames are **not** approved character animation. Godot import/playback of the authored glTF was verified on 2026-10-20; it was not repeated in this release.

## 7. Known limitations and deferred work

- Blender-backed tools require a local Blender install and are not exercised in CI; the release branch CI covers preflight, validators, MCP protocol behaviour and path safety only.
- ComfyUI and SD WebUI were unavailable during this validation, so no generation workflow was re-run; historical generation evidence is unchanged and unverified here.
- Character animation quality, rig quality, in-engine combat wiring and human art approval remain open. The Torch: Dominions diagnostic benchmark is a workflow benchmark, not a finished game.
- Third-party creative MCPs remain researched candidates; installing them is a separate, per-tool decision.
- Model/asset rights review is not performed; licensing notes are evidence aids, not legal advice.

## 8. Publication

Strategy: publish from a release branch and merge with a non-destructive merge commit; never force-push. Exact SHAs, branch, remote verification and CI outcome are recorded in the final section below once the push and CI have actually completed.

## 9. Reproduction from a clean checkout

```bash
python -m venv .venv
. .venv/bin/activate            # Windows: .venv\Scripts\activate
python -m pip install -e ".[dev]"
python -m pytest -q
python -m compileall -q src tools tests
ags doctor
ags readiness
python tools/preflight/creative_preflight.py --json
python tools/animation/validate_sequence.py examples/animation/torch_sweep.sequence.example.json
python tools/blender/validate_pose_spec.py examples/blender/torch_sweep_pose_spec.example.json --json
printf '%s\n' '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18"}}' '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}' | python tools/creative_mcp_server.py
```

The creative MCP server needs `AGS_WORKSPACE` set to the repository root; Blender tools additionally need `BLENDER_BIN`.
