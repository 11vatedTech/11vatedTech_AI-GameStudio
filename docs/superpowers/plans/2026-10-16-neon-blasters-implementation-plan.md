# Neon Blasters — Implementation Plan

**Status:** Draft plan for Founder review; no implementation started  
**Design authority:** [2026-10-16-neon-blasters-design.md](../specs/2026-10-16-neon-blasters-design.md)  
**Project:** New browser game; The Prismatic Creature Battler remains benched  
**Target:** Desktop browsers, mouse + keyboard; WebGL2 renderer with Canvas2D fallback  
**Planning profile:** 72-hour production profile, retaining the prescribed ~22% release reserve. This is an elapsed-time planning envelope, not a claim that 56 productive hours are available. Re-estimate using actual availability before execution.  
**Approval boundary:** Founder approval of this plan is required before implementation begins.

## 1. Objective and definition of done

Ship a verified, locally playable Neon Blasters survival prototype that expresses the approved cursor-as-weapon thesis. The game must provide immediate mouse-hold laser fire, exact collision feedback, four legible target families, three-color Spectrum Hunting, Prismatic Splitter, Chainlight, Overdrive, five power-ups, between-beat run upgrades, escalating target patterns, overload failure, results, and restart. Simulation must be deterministic for a fixed run seed/input trace; presentation events must not own game outcomes. Dense effects must remain resource-bounded and measured.

### Release acceptance

- Title → run → overload → results → restart works in an actual browser without console/network errors.
- Pointer aim maps correctly at supported desktop viewports/high-DPI scaling; fire begins on press and stops on release; pointer loss, pause and tab visibility changes cannot leave fire stuck.
- Target-family and beam interaction contract tests cover one-hit semantics, matching/mismatching spectra, split branches, piercing, volatile caps, power-up stacking/expiry, pause, overload and restart.
- Seeded simulation test reproduces results for identical inputs; particles use separate cosmetic randomness.
- WebGL2 path and lower-effect Canvas2D fallback both render; renderer context-loss path recovers or reports a clear fallback state.
- All required visual states are inspected in browser at 1280×720, 1920×1080, and a narrow window; screenshots and browser logs are retained.
- Stress report captures browser/hardware/viewport, simulation/effect counts, p50/p95 frame times, adaptive quality/cap activity, and any limitation. Do not claim 60 FPS unless measurement supports it.
- Build/archive opens; release manifest includes exact commands, versions, checks, artifact hashes, provenance/license status and unresolved human gates. No deployment or publication is included.

## 2. Work contract and constraints

- **Player value:** crisp cursor aim, immediate beam, material-specific impact and satisfying causal destruction.
- **Out of scope:** mobile delivery, online scoreboards, accounts, multiplayer, campaigns/biomes, permanent progression, ads/monetization, paid APIs, and broad multi-weapon systems.
- **Technical constraints:** local-first, no required external service, deterministic gameplay module, fixed-step simulation with capped catch-up, pooled effects, explicit chain and particle ceilings, safe visibility/pointer lifecycle.
- **Creative constraints:** avoid generic cyberpunk-city dressing and unbounded bloom; target telegraphs, overload boundary, aim and score must remain legible through spectacle; pair spectrum colors with non-color cues; provide reduced-flash/effects controls.
- **Rights constraint:** generated art/audio are not automatically commercially cleared. Preserve source lineage and record model/asset/audio license uncertainty before distribution.
- **Current workspace facts:** local ComfyUI and Godot 4.7.2 are available, but the approved game direction is browser-native. SD WebUI is unavailable. No additional art generation or engine integration is assumed in this plan.

## 3. Proposed project layout

Create a new, isolated project at `projects/neon-blasters/`; do not reuse or edit the benched Prismatic Creature Battler. Keep source code, art direction, source assets, build output, and QA evidence distinct:

```text
projects/neon-blasters/
  docs/game-brief.json
  docs/art-bible.json
  docs/task-graph.json
  docs/asset-manifest.json
  src/index.html
  src/styles.css
  src/app.js
  src/input.js
  src/simulation.js
  src/spawn-director.js
  src/events.js
  src/renderer-webgl.js
  src/renderer-canvas2d.js
  src/effects.js
  src/audio.js
  src/config.js
  tests/...
  assets/src/...
  assets/runtime/...
builds/neon-blasters/...
evidence/neon-blasters/...
```

Adapt file names to existing repository idioms during implementation setup; preserve module boundaries and keep the simulation independent of DOM/WebGL. Avoid adding dependencies unless already installed or explicitly justified. A static HTML/CSS/ES-module app needs no backend or package dependency.

## 4. Dependency-ordered phases and task cards

Estimates below are planning estimates, not calibrated measurements. Validate through `ags jam plan` with an explicit task file before committing to a calendar. GPU-heavy generation is serialized. Reserve time is not scheduled as feature capacity.

### Phase 0 — Workspace/release safety and first visible proof (3 h planned)

**NB-001. Create isolated Neon Blasters project scaffold**
- Inputs: approved design spec, existing studio conventions, current git state.
- Outputs: project folder, initial brief/art bible/task graph, separate source/build/evidence roots.
- Acceptance: project validates; no benched-project files changed; browser opens a placeholder title and arena shell.
- Evidence: initial project manifest, git diff/status, HTTP smoke evidence.

**NB-002. Routing, art direction and proof-set gate**
- Set concept/resource/craft plan to the approved neon arcade thesis; define target viewport, target silhouettes, weapon origin, palette, shape/material grammar, type/HUD hierarchy, VFX limits, reduced-flash direction.
- Inspect or create one target hero, one impact/shatter proof, one field/background and one HUD sample before batch assets.
- Acceptance: sample communicates block/crystal/volatile distinctions and weapon action at play scale; source lineage recorded; visual QA findings logged; no mass generation before selection.

### Phase 1 — Deterministic playable loop with primitive/blockout content (10 h planned)

**NB-003. Define simulation contracts and fixed-step clock**
- Data contracts: run state, target, weapon, upgrade, power-up, run seed, typed event payload; simulation config separated from renderer.
- Fixed-step update, capped catch-up, stable target IDs, deterministic PRNG and input command queue.
- Acceptance: unit tests verify seeded reproduction, pause/resume, no negative health, stable event ordering, bounded delta catch-up.

**NB-004. Build mouse/keyboard input adapter**
- Normalize pointer against logical viewport; fixed bottom-center emitter; pointer capture while firing; first hit immediately on pointerdown, cadence-controlled repeat; stop instantly on release/lost capture/blur; Q/right-click color cycle; Space Overdrive; Escape/P pause.
- Acceptance: browser interaction tests assert aim coordinate mapping, immediate first shot, firing cadence tolerance, release stop, no stuck input after visibility loss, pause freezes simulation.

**NB-005. Implement core target simulation and collision**
- Spawned blocks and crystals with movement, health, spectrum, durability, arena occupancy, swept/raycast beam endpoint, stable collision resolution and single-hit event protection.
- Acceptance: collision contract tests for multiple targets along beam, beam surface endpoint, edge cases, damage exactly once, target removal not tied to visuals.

**NB-006. Implement survival run state, spawn director, overload and restart**
- Authored spawn patterns/escalation bands, safe aiming corridors, visible overload occupancy and grace interval, run-over result, restart reset.
- Acceptance: deterministic seeded run ends via overload without untelegraphed spawns; start→play→fail→restart is playable in browser.

**NB-007. First feel vertical slice and adversarial input review**
- Wire blockout graphics/audio and exact beam/hit/fragment sequence; inspect actual pointer feel and target legibility before more systems.
- Acceptance: real browser run observed; screenshot/recording retained; no console errors; first-shot onset, beam endpoint and release response confirmed. Revise control parameters before expanding.

### Phase 2 — Signature combat, target families and progression (15 h planned)

**NB-008. Add Spectrum Hunting and color-readable targeting**
- Three beam spectra, crystal matching bonus, mismatch damage, icon/pattern redundancies and HUD state.
- Acceptance: matching/mismatch test cases and screenshot show readable cues independent of color alone.

**NB-009. Add material-specific break events and pooled effects**
- Typed impact/fracture/destroy events; per-family fragment profile; impact direction inheritance; varied sizes/speed/brightness/spin/lifetime; pools and strict budget counters.
- Acceptance: gameplay state unaffected by effect pool exhaustion; different target families yield distinct, source-colored destruction; profile captures active pool peaks.

**NB-010. Add Prismatic Crystals and bounded Prismatic Splitter**
- Crystal facets/core, crack state, match response, line-of-sight split beams and max branching/hit-once guards.
- Acceptance: split geometry, eligible targets, bounds and deterministic outcomes covered by tests.

**NB-011. Add Volatile Cores and safe chain reactions**
- Fuse warning, radial damage, secondary volatile activation with chain-depth/time cap and stable event queue.
- Acceptance: full chain is deterministic and bounded, warning precedes detonation, stress test records cap behavior.

**NB-012. Add Chainlight combo and Overdrive charge/activation**
- Visible kill link, combo timeout/reset, score/energy scaling, intentional Space activation, capped blast target set and warning-safe presentation.
- Acceptance: tests cover combo increment, reset, charge, activation cost, blast bounds, pause behavior and no unintended repeated activation.

**NB-013. Add Power-Up Core and all five temporary effects**
- Multishot, piercing, explosive rounds, time dilation, supernova; explicit start/expiry/consumption; duplicate policy (refresh or score/charge) as approved in design.
- Acceptance: each power-up has unit/integration coverage and observable HUD state; pause suspends timers; targets do not receive duplicate invalid damage.

**NB-014. Add between-beat upgrade choice set**
- Seeded upgrade offer and deterministic application/reset, bounded power and clear active build summary.
- Acceptance: choices are repeatable for same seed, cannot make failure state ambiguous, reset removes run-only bonuses.

**NB-015. Integrate run HUD, pause/title/results and score summary**
- HUD for selected spectrum, score/combo, Overdrive, power-up durations, overload warning, pause/settings, result stats and restart.
- Acceptance: keyboard/pointer focus order and text labels usable; all states observed; no HUD overlaps critical aim/targets at narrow width.

### Phase 3 — Visual identity, audio, adaptive rendering and content proof (12 h planned)

**NB-016. Approve minimal cohesive visual proof set**
- Final-style block, crystal, power-up, volatile core, weapon/emitter, arena, impact and break effect samples. Preserve candidates/rejections and provenance.
- Acceptance: art bible and asset manifest complete enough to identify source, processing, license status and runtime role; review at actual play scale.

**NB-017. Build WebGL2 effect renderer and Canvas2D fallback**
- Additive beam core/glow, restrained bloom, impact rings, crack flashes, batched particles; fallback renderer degrades effect quality without changing simulation.
- Acceptance: feature/visual parity sufficient for play; WebGL2 unavailable/context loss handled; no gameplay dependency on GPU event timing.

**NB-018. Audio feedback and accessibility controls**
- Procedural/licensed laser, material breaks, chains, volatile/supernova; mute/levels, reduced flash/shake/effects, high contrast.
- Acceptance: pause/mute/reduced motion verified; rights status explicit; no sound dependency for required combat information.

**NB-019. Art integration and visual QA pass**
- Replace blockout selectively with approved assets; validate dimensions and draw cost; inspect title, active run, chain, power-up, warning, pause and result.
- Acceptance: findings logged by severity and resolved/accepted; screenshots at 1280×720, 1920×1080 and narrow window; agent visual judgment separated from Founder/human art approval.

### Phase 4 — Performance, failure paths, final QA and packaging (16 h planned; release reserve is separate)

**NB-020. Instrument and stress-test dense destruction**
- Measure simulation CPU frame, renderer/GPU frame where available, target/effect counts, chain depth, and adaptive quality; use fixed stress scenario plus representative manual run.
- Acceptance: report browser/hardware/viewport, p50/p95 timing, peak counts and cap activation. Investigate regressions; only claim target performance when observed.

**NB-021. Browser integration/regression/failure suite**
- Start/pause/resume, pointer lost, tab hidden, canvas resize/high DPI, WebGL context failure, Canvas fallback, full upgrade/power-up run, overload, result/restart, long-run resource bounds.
- Acceptance: automated tests plus actual browser execution pass; failures recorded and corrected; clean console/network log.

**NB-022. Release audit, provenance, package and hashes**
- Freeze source snapshot, collect asset/audio rights status and external dependency inventory, test packaged copy, create release manifest and checksums.
- Acceptance: archive opens and runs from a clean extracted copy; test logs and hashes match; package contains no secrets/caches; unresolved human gates explicit.

**Schedule arithmetic:** The five phase estimates total 56 task-hours (3 + 10 + 15 + 12 + 16). A 72-hour elapsed profile leaves 16 hours for release reserve, which is 22.2% of elapsed time and aligns with the profile’s ~22% guidance. These are estimates, not measured productive time; if actual available capacity or task estimates grow, reduce optional scope before drawing down the reserve.

**Release reserve:** Protect the final ~16 hours for integration failures, fresh build/export, recovery, packaging and human review. If capacity is insufficient, cut in this order: extra upgrade variety, optional power-up variants, secondary spawn patterns, background ornament. Preserve a complete core run and test reserve.

## 5. Critical dependency graph

```text
NB-001 ──> NB-002 ──> NB-016
   │                     │
   └──> NB-003 ──> NB-004 ──> NB-005 ──> NB-006 ──> NB-007
                                      │                 │
                                      ├──> NB-008 ──────┤
                                      ├──> NB-009 ──────┤
                                      ├──> NB-010 ──────┤
                                      ├──> NB-011 ──────┤
                                      ├──> NB-012 ──────┤
                                      ├──> NB-013 ──────┤
                                      └──> NB-014 ──────┤
                                                        └──> NB-015
NB-016 + NB-009 ──> NB-017 ──> NB-018 ──> NB-019
NB-005..NB-019 ──> NB-020 ──> NB-021 ──> NB-022
```

Parallelize independent artwork research/candidate reviews and test design only. Serialize GPU generation and shared renderer/module edits. Integrator owns final merge and package.

## 6. Risks and countermeasures

| Risk | Impact | Countermeasure / exit evidence |
|---|---|---|
| Immediate input still feels delayed | Core fantasy fails | Implement same-input-frame first hit and exact endpoint in NB-004/007; browser timing/interaction proof before adding content |
| Full feature breadth reduces polish | Low clarity/unfinished loop | Playable loop by NB-007; dependency gates; release-reserve scope cuts |
| Particle bursts cause frame spikes | Input/visual response degrades | Pools, ceilings, adaptive tier, bounded chains; NB-020 stress report |
| Effects hide overload/target state | Unfair deaths | Reserved value/color hierarchy and reduced-effects option; target-state visual QA in NB-019 |
| WebGL2 incompatibility/context loss | Blank/broken game | Canvas2D fallback; inject context failure and test in NB-021 |
| Spectrum color inaccessible | Players miss core mechanic | Shape/icon/pattern redundant cues, high-contrast mode; visual check and test in NB-008/015 |
| Generated audio/art rights unclear | Release risk | Local-first/procedural or licensed only; provenance/status register in NB-016/018/022 |
| Scope exceeds available time | Release reserve consumed | Re-estimate after NB-007; drop optional content per cut order; maintain 72h plan reserve |
| Unbounded volatile chain or duplicate split hit | Determinism/overload risk | Stable event queue, per-event target guard, explicit depth/time ceilings; contract tests NB-010/011 |

## 7. Evidence ledger expected

- Design authority: `docs/superpowers/specs/2026-10-16-neon-blasters-design.md`.
- Brief, art bible, dependency/task graph, asset manifest and rights register under the isolated project.
- First feel build, actual browser recording/screenshots, viewport and input observations.
- Unit, deterministic, contract, browser, stress and package-integrity reports with commands/exit status.
- Performance results include measured environment and raw summary; no invented benchmark values.
- Release package hash and clean extracted-copy run.
- Human gates: game-feel, visual/art direction, audio mix and legal/rights review remain labeled until a reviewer actually completes them.

## 8. Self-review

- Scope matches approved desktop-browser, broad-showcase Neon Blasters design; no other game's files are touched.
- Inputs, firing, spectrum, four target families, four signature mechanics, five power-ups, upgrades, overload, pause, result/restart, renderer fallback, performance, verification, and release concerns all have implementation tasks and acceptance evidence.
- No exact tuning constants are invented where the design intentionally defers them; they are parameterized and tuned after playtest.
- The 72-hour profile is a planning recommendation, not an asserted Founder deadline; the 56 task-hour estimate plus 16-hour reserve arithmetic is internally consistent, but actual productive availability and estimates must be recalibrated before execution.
- This plan is for review only. Do not execute, create the project, generate assets, install dependencies, or edit game code until Founder approves the plan.
