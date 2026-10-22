# Verification Status

This file separates three kinds of evidence. Read the section that matches the claim you are making.

1. **Historical verification** (§A): what was measured for the 0.4.0 clean-room rebuild on 2026-10-16. It describes that snapshot only. Its counts (59 tests, 79 skills, 21 schemas) are **not** current.
2. **Current code-level checks** (§B): what was re-measured for the `upgrade/audit-health-version` branch on 2026-10-22, with the command and outcome for each.
3. **Unverified external integrations** (§C): capabilities that require hardware, services, or host applications this repository's CI cannot provide. Nothing in §C is claimed as passing.

---

## §A. Historical: 0.4.0 clean-room rebuild (2026-10-16)

The following section is preserved from the 0.4.0 release. Every statement in it refers to that snapshot.


**Verification date:** 2026-10-16  
**Scope:** source repository, optional integration interfaces, public wheel packaging, and documentation/schema contracts. This report is distinct from the historical test logs contained in the submitted archive.

### Reproducible checks performed in the 0.4.0 rebuild environment

| Check | Result | Evidence / boundary |
|---|---|---|
| Full Python test suite | **59 passed** | `python -m pytest -q`; no filters or deselection |
| Exact public source ZIP | **Passed** | 276 file entries; ZIP CRC clean; 276/276 per-file hashes verified against the adjacent manifest; extracted ZIP independently passed 59/59 tests |
| Source compilation | **Passed** | `python -m compileall -q src tools tests` |
| Capability register parity / schema validation | **Passed** | Static register matches the runtime registry and validates against the capability-register schema |
| Z-Image workflow contract | **Passed** | Builder node types, model filenames, seed and input guards are tested against the documented ComfyUI workflow shape |
| Repository JSON schemas | **Passed** | Tests validate Draft 2020-12 schema syntax and ensure bundled schemas equal their source counterparts |
| Required document / skill contracts | **Passed** | Tests confirm required agent, jam, animation, asset, research and security documents exist; 79 skill entries load and parse |
| Release-packager security tests | **Passed** | Tests cover secrets, local state, model weights, Python build metadata, overwrite guard, symlink rejection, output-in-source rejection, integrity and blocker reporting |
| CLI from source tree | **Passed** | `PYTHONPATH=src python -m vated_studio.cli --help`; doctor reports `ready` in a temporary workspace |
| Wheel build | **Passed** | `pip wheel --no-build-isolation --no-deps .` created `11vatedtech_ai_game_studio-0.4.0-py3-none-any.whl` |
| Isolated wheel install | **Passed** | Installed into a fresh virtual environment with `--no-deps`; discovered **79 skills** and **21 schemas**, status returned correctly |
| Installed CLI smoke checks | **Passed** | `ags --version`, `ags init`, `ags doctor`, skill search, and jam profiles in isolated installation |
| Installed MCP stdio smoke check | **Passed** | Three JSON-RPC exchanges: initialize, tools/list and ags_status; five tools advertised |
| HTTP auth/protocol tests | **Passed** | Automated local-server tests cover health, unauthorized access, authenticated status/command and malformed JSON |
| Working-tree secret scan | **Passed** | No `.env` besides `.env.example`, no token/db/private-key files found at scan time |

## Source package and knowledge-base checks

- 79 specialist `SKILL.md` files exist in the root `skills/` library; a regression test verifies every bundled runtime skill file is byte-identical to its authoritative root counterpart.
- The 79 bundled runtime skill files under `src/vated_studio/data/skills/` are byte-identical to the root source skill files at verification time.
- 21 root JSON Schemas exist and are bundled byte-equivalently under `src/vated_studio/data/schemas/`.
- Repository source includes the canonical operating standard, 24-hour/72-hour/14-day game-jam workflows, research source register, animation production standard, and asset production standard.
- The public build contains software and workflow recipes, not model weights, a local `.env`, a virtual environment, build metadata, local SQLite data or duplicated WebAssembly game exports.

## Research basis

The source register in `docs/research/source-register.json` records public primary sources. Important implementation references include:

- [FLUX.2 official model matrix](https://github.com/black-forest-labs/flux2): capabilities and license distinctions are model-variant-specific; the current repository identifies Klein 4B under Apache-2.0 and 9B / dev variants under non-commercial terms. Recheck the exact file before adoption.
- [ComfyUI official docs](https://docs.comfy.org/) and [official API specification](https://github.com/Comfy-Org/ComfyUI/blob/master/openapi.yaml): workflows are installation/node-version sensitive. The [official Z-Image Turbo template](https://github.com/Comfy-Org/workflow_templates/blob/main/templates/image_z_image_turbo.json) grounds the Z-Image builder node graph. The [Tongyi-MAI model card](https://huggingface.co/Tongyi-MAI/Z-Image-Turbo/tree/main) currently lists Apache-2.0; verify the exact downloaded file and terms before adoption.
- [Godot sprite animation](https://docs.godotengine.org/en/stable/tutorials/2d/2d_sprite_animation.html) and [AnimationTree](https://docs.godotengine.org/en/stable/tutorials/animation/animation_tree.html): engine animation methods and transitions.
- [Blender animation features](https://www.blender.org/features/animation/), [RIFE ncnn-vulkan](https://github.com/nihui/rife-ncnn-vulkan), and [Pixar in a Box](https://www.khanacademy.org/computing/pixar): public animation/rigging/interpolation/creative-development references; no claim is made about confidential studio pipelines.
- [GitHub Actions secure-use guidance](https://docs.github.com/en/actions/reference/security/secure-use): CI actions in the included workflow are pinned to full SHAs and permissions are limited to repository contents read.

## Not verified here

This container does **not** contain the founder's actual Windows GPU environment and did not rerun ComfyUI generations, FLUX.2 Klein/SD checkpoint inference, RIFE interpolation, actual Godot project export, a browser gameplay session, Blender rendering, or any game-specific end-to-end production. Historical GPU timings and Ember Warden/Lumen Hollow results are described in the research as inherited evidence, not as tests for this clean-room repository.

The capability registry normalizes and tests dependency/verification/limitation fields as complete strings; this caught and fixed a one-element serialization defect during isolated package validation. A successful wheel, test suite, API response, or generated image does not certify high artistic quality, a coherent animation, a complete playable game, commercial rights, human art-direction approval, or success in a game jam. Those require their own evidence and, where appropriate, genuine human review.

### Historical local re-verification (0.4.0)

```bash
python -m pip install -e ".[dev]"
python -m pytest -q
ags doctor
ags capabilities
ags skills search "character identity animation"
ags jam profiles
```

For external integration proof, configure the real local services and run the relevant `ags` commands against their installed versions. Check the actual generated files, engine output and target build before promoting a capability status.

---

## §B. Current code-level checks (branch `upgrade/audit-health-version`, 2026-10-22)

Measured in an execution sandbox (Linux, Python 3.13, no GPU, no PyPI access). Counts below were read from the tree at the time of writing, not inherited.

| Check | Command | Result |
|---|---|---|
| Stdlib-runnable test modules | `PYTHONPATH=src:tests python3 -m unittest <modules>` | **67 run: 66 passed, 1 skipped** (modules listed in the audit document) |
| Full pytest suite, Python 3.11 / 3.12 / 3.13 | GitHub Actions `Studio Core CI`, job step `python -m pytest -q` | Passed on the audit commit (run `39874316027`) and on the personal-path remediation commit (run `39874671518`), step conclusion `success` on every version. Exact pass/skip counts are **not captured** here; the workflow log was not retrievable from the sandbox. |
| Source compilation | `python -m compileall -q src tools tests` | Passed |
| Skill inventory | `find skills -name SKILL.md` | **87** skills; all 87 bundled copies under `src/vated_studio/data/skills/` are byte-identical to root copies |
| Schema inventory | `ls schemas` | **25** JSON Schemas; bundled copies are byte-identical |
| Recorded hash integrity | custom check over repo JSON `{path, sha256}` pairs | 157 resolvable matches, **2 pre-existing mismatches** in `evidence/the-unwriters-almanac/source-manifest.json` (`projects/.../asset-manifest.json`, `task-graph.json`). These predate this branch and are not corrected here. |

Notes on the inventory:

- `skills/index.json` exists only at the repository root. It is the generated catalog written by `tools/build_skills.py`; runtime discovery reads the `SKILL.md` files directly, so it is intentionally not bundled.
- The historical 0.4.0 figures (79 skills, 21 schemas, 59 tests) are superseded by the counts above.

## §C. Unverified external integrations

These capabilities are **not verified** by this repository's CI or by the checks in §B. A green CI run does not establish any of them.

| Capability | Why not verified | What would be required |
|---|---|---|
| ComfyUI generation (Klein, Z-Image) | No GPU and no ComfyUI service in CI | A machine with the model files installed and the `ags` ComfyUI adapter pointed at it |
| SD WebUI adapter | Same | Same class of environment |
| Blender scene authoring and rendering | Blender not installed in CI | Blender binary, run through `tools/blender` |
| Godot project validation, export, and runtime | Godot not installed in CI | Godot binary; headless run and target-runtime playtest |
| RIFE interpolation | Binary and models absent | Local RIFE install |
| GPU VRAM behavior | No GPU | Measurement on the target GPU |
| Freebuff / Claude / other MCP host integration | Protocol tests use a simulated client, which is not a host | Live host configuration and an observed tool call |
| Visual or artistic quality of generated assets | Requires human or agent visual review | Recorded review against the art direction |
| Commercial rights for models and assets | Requires legal review | Per-asset license review |

## Local re-verification

```bash
python -m pip install -e ".[dev]"
python -m pytest -q
python -m compileall -q src tools tests
ags doctor
ags capabilities
```

For external proof, run the relevant `ags` commands against the real installed services and record the generated files, engine output and target build before changing any capability status.
