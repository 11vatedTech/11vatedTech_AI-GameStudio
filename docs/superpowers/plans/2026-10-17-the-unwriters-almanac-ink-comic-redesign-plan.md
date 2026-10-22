# The Unwriter’s Almanac — Ink-Comic Redesign Implementation Plan

**Status:** Draft for Founder review; plan approval required before implementation.  
**Design authority:** [2026-10-17-the-unwriters-almanac-ink-comic-redesign.md](../specs/2026-10-17-the-unwriters-almanac-ink-comic-redesign.md)  
**Existing project:** `projects/the-unwriters-almanac/` (already contains a local playable browser prototype).  
**Target:** Existing ES-module/Canvas2D local browser game, desktop and narrow viewports.  
**Delivery boundary:** One redesigned playable page; no deployment, publication, or rights clearance assertion.

## 1. Objective and definition of done

Replace the prototype-looking Canvas-only page with a reviewed, image-led expressive ink-comic environment/character direction, and make its one-page line puzzle demand a real, fair choice between a wide safer route and a short tighter route. Keep the rail, hazard, endpoint, bead and collision logic crisp, authored/testable overlays. The same committed line must guide both character and bead.

**Plan exit criteria:**

- A small local image-generation proof set exists with raw source, prompts, reproducible workflow/settings and hashes; selected proof candidate(s) receive Founder review before integration.
- The game has two independently solved geometrically distinct route families with an explicitly visible ink budget/clearance tradeoff; a direct hazard-crossing and over-budget route reject with useful feedback.
- Pointer/guided keyboard interaction, correction, erase, pause, solve/restart, reduced motion and accessibility behavior remain operational.
- Tests pass, the local server runs, and the actual browser is inspected at desktop and narrow size with no uncaught errors or remote runtime requests.
- Asset/provenance and verification records distinguish candidate vs integrated art, technical checks, agent inspection, human approval and open rights/playtest gates.
- Re-check code/tests after final source edits; make no unsupported performance or commercial-clearance claims.

## 2. Constraints, approvals and workspace safety

- The design spec was approved by “approvef.” **This plan itself is now the review gate:** do not generate images, modify gameplay/project files or update the game’s art/gameplay contracts until the Founder explicitly approves this plan.
- No commit is requested. Do not stage, commit, push, deploy or publish.
- Existing branch is `work/unwriters-almanac`. The checkout contains untracked `assets/`, `builds/`, `docs/superpowers/`, `evidence/` and `projects/` paths from this ongoing work. Preserve all existing files and make targeted edits only after approval. Do not switch branches or create a worktree without user authorization; if isolation is required for a later implementation, ask first rather than silently changing branch/worktree state.
- Existing source is an operational prototype, not a new-project scaffold. Preserve its start/solve/restart, seeded fixed-step sim, bounded drawing and accessible semantic controls; do not replace the project wholesale.
- No new dependencies, hosted model, runtime network calls, model download, deployment, multiple levels or broad content architecture.
- At the prior inspection, ComfyUI was available but VRAM showed only ~2.7 GB free; recheck queue and memory at generation time and serialize GPU use. Model/component filenames alone are not provenance or rights review.
- Generated content remains concept-only until selected. Any integration is local, same-origin, size-bounded and subject to asset review; no AI-generated frame sequence is assumed identity-consistent.

## 3. Existing system baseline (before execution)

- App: static ES modules; Canvas2D playfield and semantic DOM controls; no project runtime dependencies.
- Simulation: `src/simulation.js`; line acceptance currently checks approximate start, bead and goal distances plus broad total length; committed rail carries the actor and bead along the same polyline.
- Geometry/input: `src/geometry.js`, `src/input.js`; 1280×720 logical page, clamped/resampled stroke and pointer cancellation paths.
- Renderer: `src/renderer.js`; paper texture, page scene, creature, bead and effects are drawn as Canvas primitives. `docs/asset-manifest.json` currently has no runtime image asset records.
- Existing validation command: `cd projects/the-unwriters-almanac && npm test`; last recorded run before plan drafting: **16 passed, 0 failed**. At implementation start, verify current branch/status, inspect relevant current files and rerun this baseline because the shared checkout may have changed.

## 4. Small, ordered implementation phases

The sequence separates proof review from integration. Estimates are planning estimates, not measured latency or promises; re-estimate at the route-feasibility spike. Protect the 24-hour profile’s six-hour release reserve as a planning constraint. There is no supplied jam deadline.

### Phase A — Plan approval, baseline and geometry feasibility (estimate: 90–130 minutes)

**IC-001 — Record approved scope and baseline (15 min)**
- Confirm approval of this plan; inspect `git status`, current branch, relevant project contracts and existing source; run current `npm test`.
- Acceptance: record exact baseline command/result and preserve every pre-existing untracked path. No source modification during baseline.

**IC-002 — Prove the route puzzle is feasible before tuning art/gameplay (45–75 min)**
- In a disposable test/design calculation (not yet production source), compare candidate polylines against start, bead and goal positions, DRAW_BOUNDS, minimum/maximum length, point count, a candidate ink-eater polygon/region and two route clearance targets. Document a concrete wide-sweep and narrow-cut candidate, a direct hazard-crossing candidate, and an over-budget candidate.
- Acceptance: the two valid paths satisfy all shared constraints but have distinct length/clearance costs; invalid paths fail for the intended reasons; each path remains representable after `sanitizeStroke`. If no fair pair exists, return to design before implementing mechanic/UI.

### Phase B — Local model/provenance preflight and proof generation (estimate: 60–180+ minutes; VRAM/job latency is variable)

**IC-003 — Verify installed workflow/model/component identity and rights status (20–45 min)**
- Recheck ComfyUI `/system_stats`, queue, and supported node metadata. Hash the installed diffusion checkpoint, text encoder and VAE component files without copying/altering them. Match exact identities to authoritative publisher/repack source and license terms where possible. Distinguish weight license from code license and generated-output rights.
- Acceptance: record hashes, recoverable source URLs/revisions, applicable component license status and VRAM snapshot; keep any unresolved component identity/rights explicitly `unclear`/`human_review_required`. Do not generate using an unidentifiable or unsafe workflow/component set.

**IC-004 — Create a bounded original ink-comic proof set (40–120+ min)**
- After preflight only, run one generation at a time, with current headroom checked immediately before submit. Generate one wide background plate candidate and one ink-being design candidate; only add one isolated ink-eater study if those demonstrate a clear need. No baked-in instructional text or collision geometry. Preserve prompts, seeds, workflow JSON/version, model/component identifiers/hashes, raw outputs and failed/rejected outputs; do not overwrite.
- Acceptance: originals are stored in a dedicated project/evidence candidate directory, named with stable IDs, hash recorded, and marked reference/candidate—not silently integrated. Stop at this set.

**IC-005 — Review candidates at actual play scale and request human art-direction choice (20–40 min)**
- Inspect source-size and 1280×720 playfield-scale candidates; verify character anchors, negative space for puzzle, separation of hazard and route overlay, and no misleading collision cues. Record agent review and rejected alternatives. Present candidate preview for Founder review.
- Acceptance: do not proceed to game-art integration until the Founder explicitly selects or requests revisions. If no suitable candidate, revise prompt/composition once per visible defect or stop and report.

### Phase C — Integrate image-led ink-comic art (estimate: 100–160 minutes, only after proof selection)

**IC-006 — Update art bible, asset manifest and provenance records (25–40 min)**
- Change the old watercolor-first visual canon to the approved ink-comic direction. Add only selected asset records; preserve candidate/rejected state and per-file hashes/prompt/seed/workflow/model/component/license status/review ID. Do not label candidate art approved or commercially cleared.
- Acceptance: JSON/schema checks pass, manifest references actual files with matching SHA-256, and unresolved rights/human review remains visible.

**IC-007 — Add local scene-plate and character integration layer (45–75 min)**
- Load selected local same-origin page-plate art in the existing Canvas renderer as a non-collision backdrop. Keep player line, points/endpoints, bead, seal, ink-eater hatch/hurt region and any collision cue crisp and separately drawn. Prefer current authored pose code on top of selected character reference until selected artwork can be integrated with a safe identity-stable approach; never pass baked-in art shapes off as collision.
- Bound pixel dimensions/decoded allocation; handle image load error with an explicit fallback/error state, not a blank canvas. Test all references through the project static server.
- Acceptance: image and simulation coordinates remain aligned at logical and CSS-resized canvas sizes; art does not cover essential cues; no remote image source.

**IC-008 — Responsive composition, interaction overlay and accessibility (30–45 min)**
- Present start, gold bead, seal, two route corridors, hatched no-ink region, finite ink meter, line preview/validity cues and named feedback. Recompose labels/controls at narrow viewport; keep focus/ARIA/reduced motion behavior and keyboard-guided route selection.
- Acceptance: key information is never color-only or baked into generated text; no horizontal overflow; visual/state cues remain legible at play scale.

### Phase D — Implement and validate route-choice mechanic (estimate: 130–220 minutes)

**IC-009 — Add explicit route geometry and validity query (45–75 min)**
- Add deterministic page rules to simulation/domain code: start and goal anchors; bead-intersection/nearest distance; finite ink budget; ink-eater forbidden shape; any lane clearance derived from creature radius and fair visible corridors. Keep geometry tests independent of renderer.
- Acceptance: preview and commit call the same pure validation function against the same sanitized points; no hidden guided-preset identifiers; failure reasons are deterministic. Seeded replay remains identical.

**IC-010 — Add playable wide and narrow route examples and accessible presets (25–45 min)**
- Replace the three equivalent guided curves with the reviewed wide-sweep and narrow-cut paths plus a clearly named direct invalid example only in tests/dev evidence, not a misleading player “choice.” Keep actual pointer freehand input.
- Acceptance: both selected routes can be previewed and committed under ordinary constraints; the wide option has more hazard clearance but consumes more ink; the narrow option consumes less ink and has a demonstrably smaller clearance margin. If these properties cannot be shown in actual geometry, revise the model before calling it a choice.

**IC-011 — Explain rejection, ink cost and correction (25–45 min)**
- Display remaining/used ink continuously while drawing and before commit; draw clearance/blocked overlap feedback with shape plus text; preserve failed drawing until retry or provide one-action erase. Ensure invalid commit doesn’t accidentally clear a player stroke or stale guided-selection state.
- Acceptance: direct hazard crossing, ink-over-budget, missed bead and invalid endpoints each yield appropriate feedback; erase/retry works without restart.

**IC-012 — Add tests for route classes, bounds and recovery (35–55 min)**
- Extend simulation tests for both valid path families, direct path blocked by ink-eater, over-budget path, clearance distinction, identical preview/commit sanitized geometry, reason mapping, seed reproducibility, erase/retry and existing solve/pause/reset behavior.
- Acceptance: tests assert underlying geometric conditions and event/state outcomes, not only labels; keep prior coverage; do not weaken or skip tests.

### Phase E — Browser integration, QA, measurement, handoff (estimate: 140–220 minutes)

**IC-013 — Run actual browser gameplay on both routes and failure paths (45–75 min)**
- Start/reuse the project server after checking the listener; inspect DOM, game canvas, actual pointer drag, each route preset, successful solve, invalid route, erase/retry, pause/resume/restart and reduced-motion states at desktop and narrow viewport.
- Acceptance: actual browser UI responds correctly; route choice is comprehensible from artwork/visible costs; no console exceptions, failed local assets or external requests. Preserve screenshots/accessibility snapshots; human comprehension remains open until a human playtest occurs.

**IC-014 — Visual/performance/accessibility critique and iteration (35–70 min)**
- Inspect scene/candidate at 1440×960 desktop and 390×844 narrow; assess playfield reading at rendered size, focus order, keyboard path, text alternatives, contrast, overflow, image loading and state transitions. Measure representative renderer CPU timings and image dimensions/decoded-size upper bound; report data/method, not a frame-rate assertion.
- Acceptance: fix first-order composition/readability/cause-and-effect issues, rerun browser and relevant checks after fixes, and keep reduced motion usable.

**IC-015 — Final regression, provenance and handoff evidence (45–75 min)**
- Run `npm test`, syntax checks for changed modules, JSON/schema validation for changed docs/manifests, local HTTP/content-type checks, browser flow, git diff check and source manifest/hash refresh for only in-scope files. Read back every final modified file/artifact path.
- Acceptance: all executed checks report true command exit statuses; exact paths/results/failures/open human/legal gates are recorded; no unrelated files overwritten/staged/committed.

### Estimated effort and release reserve

The 15 task estimates total **710 minutes (11 h 50 m)**. GPU latency and route tuning are not calibrated by the planner, so the working estimate may rise; use **910 minutes (15 h 10 m)** as the current contingency ceiling, not as measured production time. Against a 24-hour profile, preserve the 360-minute release reserve, leaving 1,080 minutes of planned work capacity; the contingency ceiling leaves 170 minutes of slack. Re-estimate after IC-002 and IC-004; if the route prototype or generation threatens the reserve, cut the optional hazard study, surface micro-detail and extra animation variants before reducing QA or the release reserve. No actual jam deadline is known.

## 5. Dependency sequence

```text
plan approval
   ↓
IC-001 baseline → IC-002 route-feasibility spike
   ↓                              ↓
IC-003 identity/license/VRAM preflight → IC-004 bounded generation → IC-005 Founder candidate review
                                                                     ↓
                                                           IC-006 manifest/canon
                                                                     ↓
                                                           IC-007 art integration → IC-008 responsive/accessible overlays
                                                                                           ↓
IC-009 deterministic route validation → IC-010 route presets → IC-011 feedback → IC-012 tests
                                                                                                  ↓
                                                                              IC-013 actual browser route validation
                                                                                                  ↓
                                                                              IC-014 visual/perf critique
                                                                                                  ↓
                                                                              IC-015 final regression/handoff
```

GPU-heavy jobs are sequential. Route-feasibility work and source review can proceed while provenance is researched, but no gameplay/art contract changes or candidate integration should happen before their explicit gates. One integrator owns final source/manifest edits.

## 6. Risks, blockers and contingency

| Risk | Response |
|---|---|
| The selected proofs look good full size but fail at game scale | Use small-scale/contact-sheet and rendered playfield review before Founder selection or integration |
| The short and wide paths cannot both satisfy constraints | Stop at IC-002; change page geometry/budget/hazard shape and retest, rather than fabricate a route-choice claim |
| Local VRAM is too low or another GPU job occupies it | Wait/stop; no parallel generation and no hosted-provider substitution |
| Exact local weights/components cannot be matched to upstream licenses | Keep candidates ungenerated or strictly local/reference-only; record unresolved rights; do not claim clearance |
| Generated character art cannot maintain identity in motion | Treat it as a design reference; use selected still with authored conservative pose shapes; reject incoherent generated frames |
| Image suggests fake collision or masks active path | Keep collision/rail/hazard as sharp gameplay overlays and adjust plate/negative space; no collision from raster art |
| “Two routes” are merely three cosmetic preset curves | Require objective cost and clearance differences validated geometrically and in actual play; otherwise revise design |
| Shared workspace already has untracked output | Preserve all current untracked paths and add only reviewed in-scope files; no broad cleanup |
| Plan effort exceeds capacity | Re-estimate after feasibility/generation; cut optional decoration/study first, preserve regression and reserve |

## 7. Approval gates

1. **This plan:** Founder approval before implementation or image generation.
2. **Generation preflight:** exact available components/workflow, source/license records, current GPU headroom and queue reviewed before submit.
3. **Proof selection:** Founder reviews generated page/character proof before any selected game art is integrated.
4. **Gameplay verification:** both route solutions and rejected cases proven in tests and the actual local browser.
5. **Human gates:** rule comprehension/satisfaction, final art direction, commercial-rights review, and release approval remain unclaimed until authorized humans perform them.

**Current request:** review the plan and request edits or approve it. Plan approval does not imply selection/approval of generated imagery, commercial rights, or authorization to deploy/release.
