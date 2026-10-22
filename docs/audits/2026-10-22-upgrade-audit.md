# Upgrade Audit — 2026-10-22 (execution session, public-baseline pass)

Scope: the published `main` at `cecd6a6` (pyproject 0.5.0), cloned into a sandbox.
The founder's local OneDrive tree (`...\11vatedtech-ai-game-studio-v0.4.0`) was **not reachable** from the
execution sandbox (Linux, no access to `C:\`), so local-only work was not reconciled. This is a blocker for
Phase I/II reconciliation and is recorded below.

## Environment (measured, not inherited)

| Item | Measured here | Mandate's expected machine |
|---|---|---|
| OS / Python | Linux, Python 3.13.17 (`/usr/bin/python3`), 3.12 and 3.11 also present | Windows, Python 3.12.10 |
| CPU / RAM | 2 vCPU, 7 GB RAM | Core Ultra 9 275HX, 32 GB |
| GPU | none (`nvidia-smi` absent) | RTX 5070 Ti laptop, ~12 GB VRAM |
| Disk free | 30 GB | — |
| PyPI / npm | **unreachable** (DNS fails for pypi.org, files.pythonhosted.org; registry.npmjs.org unresolved) | — |
| pytest | **not installed; not installable** | required by `pyproject` dev extra |
| GitHub | public clone works; push needed repo attachment (granted) | — |

Consequences: ComfyUI, Blender, Godot, SD WebUI, RIFE and any GPU job **cannot be exercised here**. Eight of
fifteen test modules import pytest and **could not be run**.

## Baseline test results

- Stdlib-compatible modules (7 files, unittest): **46 passed, 1 skipped** (`python3 -m unittest`, `PYTHONPATH=src:tests`).
- Pytest-dependent modules (8 files, including `conftest.py`, `test_adapters`, `test_asset_pipeline`,
  `test_config_paths`, `test_planner_workflow`, `test_release_security`, `test_repository_contracts`,
  `test_store_service`): **not run** — blocked by missing pytest. VERIFICATION.md's "59 passed" is a
  historical 0.4.0 claim and is not reproduced here.
- `python3 -m compileall -q src tools tests`: **passed**.

## Findings

| # | Sev | Finding | Evidence | Status |
|---|---|---|---|---|
| F1 | Medium | `/health` returned hardcoded `"version": "0.4.0"` while the package is `0.5.0`. Single-source-of-truth violation; clients checking health would see a stale version. | `src/vated_studio/api/http_server.py:55` | **Fixed** on `upgrade/audit-health-version` (commit `d74f226`); regression test `tests/test_http_health_version.py` fails before, passes after. |
| F2 | Low | Committed fixture `tests/fixtures/anim/tempest-wyrm_idle_animation.json` contains absolute machine paths including the founder's Windows username and OneDrive path. Violates "no arbitrary hardcoded machine paths"; leaks local layout into a public repo. | `tests/fixtures/anim/tempest-wyrm_idle_animation.json:98,114,130,146` | Open. Not changed: rewriting fixture paths without running the pytest suite could break the fixture-dependent tests. |
| F3 | Low | Documentation drift: `VERIFICATION.md` reports 79 skills / 21 schemas / 59 tests for 0.4.0; the tree has 87 skill directories and 25 schemas. `ROADMAP.md` says 87 skills (matches). | `VERIFICATION.md:20`, `ls skills`, `ls schemas` | Open. VERIFICATION is labeled as a historical 0.4.0 report; it should be explicitly marked superseded. |
| F4 | Info | Test infrastructure: 8 of 15 modules require pytest, which is not declared as an installable offline dependency and cannot be installed without a PyPI route. Five test files therefore cannot be verified in restricted environments. | `tests/*.py` grep; `pyproject.toml` dev extra | Open; environment blocker. |
| F5 | Info | Two-clone risk: local OneDrive tree (v0.4.0 label) may hold unpublished work that differs from `main`. Not reconciled. | Mandate §2 vs. sandbox access | Blocker. Requires the founder's machine or an attached copy. |

## Not verified (explicit)

- No ComfyUI, Blender, Godot, SD WebUI, RIFE, or GPU run. No VRAM measurement.
- No pytest-based regression run; no CI run; no wheel build or isolated install in this session.
- No MCP host (Freebuff/Claude) integration test.
- No game build or playtest; `projects/` were not exercised.

## Not done in this pass (scope honesty)

The mandate's Phase IV (job orchestration, identity review, animation pipeline, engine validation) requires the
founder's GPU/Windows environment and the local tree. Those are deferred, not claimed.

## Resolution status (continuation pass)

| Finding | Status | Evidence |
|---|---|---|
| F1 health version | **Resolved** | `d74f226`; regression test `tests/test_http_health_version.py`; CI run `39874316027` (audit commit) and `39874671518` both `success` on 3.11/3.12/3.13 |
| F2 personal machine paths | **Resolved, wider than first recorded** — 16 tracked files (fixture, `evidence/`, `projects/Torch_Dominions-Game-jam-5/visual-proof/`) rewritten to repo-relative paths or `<COMFYUI_SHARED>`/`<USER_HOME>` placeholders. The initial scan under-counted. | `876e6dc`; `tests/test_no_personal_paths.py` fails on the original fixture and passes now; no recorded hash changed; CI `39874671518` `success` |
| F3 historical docs | **Resolved** — `VERIFICATION.md` split into §A historical / §B current measured / §C unverified external | see `VERIFICATION.md` |
| F4 test environment | **Resolved via CI** — pytest is declared in `pyproject.toml` `[dev]`; CI installs it and runs `python -m pytest -q` on 3.11–3.13. Sandbox still cannot run pytest (no PyPI); that is an environment limit, not a project defect. Exact CI pass/skip counts not captured (log blob not retrievable from sandbox). | `.github/workflows/ci.yml`; runs above |
| F5 local vs published | **Open (blocker)** — the Windows tree is unreachable from the execution sandbox. Synchronization procedure: from the founder's machine, `git -C <local> status`, then copy any unpublished files onto `upgrade/audit-health-version` in a separate commit, never overwriting published content without a diff review. | — |

## New finding from the continuation pass

| # | Sev | Finding | Evidence |
|---|---|---|---|
| F6 | Medium | Synchronous `StudioService.execute` runs can leave rows in `status=running` forever after a crash; nothing reconciles them. Addressed for queue-managed jobs only. | `src/vated_studio/service.py:103-117` (`start_run` with no matching finish on crash) |
| F7 | Low | Pre-existing: `StudioStore._init` and connection helper leave SQLite connections open (`with connect()` commits but does not close). | `src/vated_studio/store.py` |
| F8 | Low | Pre-existing unexplained mismatch: 2 recorded hashes in `evidence/the-unwriters-almanac/source-manifest.json` no longer match the files they point to. Not corrected: changing a recorded hash without knowing why the file changed would hide drift. | integrity check, see `VERIFICATION.md` §B |

## Job queue (implementation)

`src/vated_studio/jobs.py` extends the existing `runs` table (no second task system) with: fencing-token leases, claim-time recovery of expired leases, bounded retry with backoff, cooperative cancellation, permanent idempotency keys, a one-at-a-time `gpu` resource, and progress records. Tests: `tests/test_job_queue.py` (19 deterministic tests, incl. a real 8-thread contention test and a legacy-schema migration test). Mutation check: removing fencing, GPU serialization, or claim-time reconciliation each makes the suite fail. Not yet wired into the CLI, HTTP, or ComfyUI paths.
