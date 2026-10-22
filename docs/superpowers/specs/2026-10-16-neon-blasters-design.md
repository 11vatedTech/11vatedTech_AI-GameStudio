# Neon Blasters — Design Specification

**Status:** Approved concept; design spec for Founder review before implementation planning  
**Date:** 2026-10-16  
**Project:** Neon Blasters (new game; keep The Prismatic Creature Battler benched)  
**Platform:** Desktop browser, mouse and keyboard  
**Primary rendering:** Browser-native 2D/2.5D, WebGL2 for post-processing and high-volume luminous effects

## 1. Product intent

Build an arcade survival shooter in which the cursor feels like a precise, immediate blaster rather than a pointer. The player tracks drifting neon targets, holds fire to send instant laser hits, and converts well-aimed shots into tactile impacts, crystalline fractures, luminous debris, and cascading explosions. A run ends when uncleared targets overwhelm the arena. The intended pleasure curve is immediate shot satisfaction, rising precision/combo mastery, then a controlled escalation into spectacular screen-filling chain destruction.

## 2. Audience and player fantasy

**Audience:** Players drawn to short-session arcade survival, expressive input feedback, score chasing, and readable high-energy VFX.

**Player fantasy:** “My hand is the weapon: every movement aims, every press fires now, and a precise shot can turn one crystal into a chain of neon fireworks.”

## 3. Creative thesis and distinction

**Thesis:** Neon Blasters makes aim itself the instrument: a mouse-held, zero-travel-time laser rewards deliberate color targeting, then renders destruction as physical, varied source-colored fragments whose chain reactions make precision visibly more powerful than indiscriminate firing.

The signature is the causal sequence **aim → instant beam → exact contact → fracture → fragments → chain reaction → reward**, not generic continuous glow or a projectile that merely disappears on collision.

## 4. Core loop and run structure

1. **Acquire:** Read target motion, target family, durability, color, and volatile links.
2. **Aim:** Cursor reticle and restrained trail communicate current aim without masking target silhouettes.
3. **Fire:** Mouse hold emits instant hits at a controlled rate; each hit terminates at the actual target surface.
4. **Choose:** Cycle cyan, magenta, or amber with a keyboard key (default `Q`) to match crystal spectra. A matching hit deals a precision reward and advances the combo more efficiently.
5. **React:** Crystals split beams; Chainlight links consecutive kills; volatile cores detonate neighbors; Overdrive converts combo charge into a large-area pixel fireworks blast.
6. **Collect/adapt:** Power-up cores grant temporary multishot, piercing, explosive rounds, time dilation, or one supernova. Between escalation beats, choose one blaster upgrade from a small randomized-but-seeded set.
7. **Survive:** Spawn cadence, target variety, and approach patterns escalate. Run ends when arena occupancy crosses its overload limit for a short grace interval; a brief warning communicates imminent failure.
8. **Review/retry:** Show score, survival time, best combo, color accuracy, destruction/chain stats, then offer immediate restart.

There are no permanent progression advantages in the initial scope. Run upgrades reset between runs; best score may persist locally.

## 5. Inputs and accessibility requirements

- **Mouse move:** Aim the weapon reticle. The beam originates from a clearly visible fixed emitter at the lower center of the playfield and points at the cursor.
- **Left mouse hold:** Fire at the configured repeat cadence. First hit begins immediately on press; no projectile travel or input buffer is allowed for the standard beam.
- **Q / right-click:** Cycle the three beam spectra; HUD always displays selected color and a keyboard alternative is available.
- **Space:** Trigger Overdrive when charged; otherwise no effect, with a clear charge indicator.
- **Escape/P:** Pause, with firing and simulation time stopped together.
- **Touch/mobile:** Out of first release scope; input architecture should avoid preventing a later touch-aim adapter.
- Provide reduced-flash mode, limit screen shake, preserve high-contrast target telegraphs, and do not communicate matching solely by color (pair color with shape/icon/pattern).

## 6. Target families and readable behavior

- **Neon Blocks (core):** Geometric cubes with color-coded durability and clear hit states. Repeated hits create combo value; destruction emits varied small cubic fragments.
- **Prismatic Crystals (high-value):** Faceted, multi-layer silhouettes with a visible color/core. Matching laser colors accelerate fracture. A destroyed crystal splits the beam toward nearby eligible targets (Prismatic Splitter), subject to a bounded number of branches per event.
- **Power-Up Cores (temporary ability):** Recognizable capsule silhouette; collected/destroyed to grant one of multishot, piercing, explosive rounds, time dilation, or supernova. Communicate effect and remaining duration in HUD.
- **Volatile Cores (chain reaction):** Distinct warning pulse and fuse state. A hit creates a radial damage pulse and can arm/detonate nearby volatile cores, bounded by a chain-depth/time safety cap to protect performance and avoid runaway simulation.

Spawn director uses authored patterns and escalation bands, not unconstrained random placement. Spawn rules must preserve a readable aiming corridor and avoid untelegraphed instant overload.

## 7. Signature mechanics

- **Spectrum Hunting:** Manually switch among three beam colors. Matching crystal color rewards precision with a defined damage/score/combo bonus. A mismatch still damages, preventing hard locks.
- **Prismatic Splitter:** Crystal destruction emits a limited number of secondary instant beams toward nearby targets, respecting line-of-sight, max branching, and one-hit-per-target-per-event protections.
- **Chainlight:** Consecutive kills establish a visible link sequence; maintaining it escalates score/energy, while a miss or timeout resets the chain with clear feedback.
- **Overdrive:** Combo-earned charge enables a deliberate player-triggered blast. It damages/destroys a bounded target set, creates a large but time-limited burst, and cannot obscure the overload warning or make later survival state ambiguous.

## 8. Game states and data ownership

`BOOT → TITLE → RUNNING ↔ PAUSED → RUN_OVER → TITLE/RESTART`.

The **simulation** owns target identity, position, velocity, health, family, spectrum, volatile state, damage, combo timers, power-up duration, spawn schedule, overload occupancy, score, run seed, and result. Rendering and audio consume typed combat events (`shot_fired`, `hit`, `fracture`, `destroyed`, `split`, `chain_advanced`, `powerup_collected`, `overload_warning`, `run_over`) and cannot mutate gameplay outcomes. A run seed plus ordered player inputs should reproduce simulation outcomes for tests/debugging; cosmetic particle randomness may use a separate seed.

## 9. Technical architecture

- **Application shell:** DOM/Canvas UI for title, pause, HUD, upgrade choice, overload warning, results, and accessibility controls.
- **Simulation module:** Fixed-step deterministic state update, spawn director, target movement/collision, beam hit resolution, damage/chain/power-up logic, score, overload and run state. Use stable IDs and bounded event output.
- **Input adapter:** Normalize pointer coordinates to logical playfield coordinates, pointer capture while firing, keyboard color/Overdrive/pause controls, and visibility-loss safety (release fire/pause simulation).
- **Renderer:** WebGL2 for additive laser layers, bloom, impact rings, fracture flashes, and batched debris. Canvas 2D fallback may preserve the game loop with lower effect density if WebGL2 is unavailable. HUD text remains DOM/Canvas crisp and non-blooming.
- **Effect system:** Object pools for beams, impacts, shards, sparks, score pops, and trails; per-frame and per-chain particle ceilings; quality tiers and reduced-effects option.
- **Audio:** Local procedural synthesis and/or explicitly licensed local files. Layer a short laser transient, material-specific break, chain accent, and low-frequency volatile/supernova hit; master mix must not become an undifferentiated wall. Audio must respect mute and pause.
- **Persistence:** Minimal local best score and settings only. No account, cloud service, ads, or telemetry in the first release.

Logical coordinate scaling should support common desktop aspect ratios and high-DPI displays without coupling simulation coordinates to CSS pixels.

## 10. Art direction and VFX grammar

**Style:** Focused luminous arcade instrument panel, not generic cyberpunk city dressing. The field is near-black with sparse environmental linework and strong negative space; the cursor/weapon emitter, target silhouettes, and overload boundary carry the hierarchy.

**Palette:** Cyan, magenta, amber are the three player spectra. Targets use distinct value/material roles: cool electric block glass, refractive multi-face crystal, isolated power capsule, and volatile hot-core fracture. White-hot beam core is reserved for direct contact/maximum energy. Use a small number of non-combat background accents.

**Shape/material grammar:** Blocks are orthogonal and pixel-fracturing; crystals are faceted and refractive with crack paths; power-ups are smooth capsules with clear glyphs; volatile cores have unstable seams and a pulsing fuse ring. Particle size, speed, brightness, spin, and lifetime vary by material and inherit its source color. Fragments inherit a component of impact direction and energy.

**Impact choreography:** 0–30 ms white contact spark and brief surface flash; 30–140 ms directional fracture lines / ring; 100–450 ms fragment ejection with varied velocities; 300 ms+ differentiated afterglow/trails. Timing is tunable and verified in browser at real playback speed. Effects may not cover player reticle, target warning state, overload boundary, or score-critical UI.

## 11. Performance and safety budgets

- Primary target: 60 FPS on a representative modern desktop browser at 1080p; measure rather than assert.
- Simulation uses fixed timestep and capped catch-up steps to prevent spiral-of-death after tab stalls.
- Use pooled render/effect objects, bounded chain depth, capped active targets and particles, and an adaptive effect tier.
- Instrument frame time (CPU update and GPU render where available), target count, active particles, active beams, and dropped/capped effects. Run an explicit dense-chain stress scenario and report p50/p95 frame duration and cap behavior.
- Pause or safely release firing on tab hide, context loss, or lost pointer capture. Rebuild renderer resources on recoverable WebGL context restore where feasible.
- Avoid flashing patterns exceeding safe short transient usage; offer reduced-flash and reduced-effects settings.

## 12. Failure and recovery

- Overload has a telegraphed threshold and grace interval; failure must not be caused by an invisible target or UI overlap.
- Pause stops spawn, simulation, weapon, audio layers, and effect lifetimes coherently.
- WebGL2 unavailable/context lost: switch to reduced Canvas 2D renderer or show a clear supported-browser message; never leave a broken black screen.
- Visibility change clears held-fire state and pauses. Restart creates fresh simulation state, clears event/effect pools, and resets all temporary upgrades.
- Power-up stacking rules are explicit; duplicate ability pickups refresh duration or convert to score/charge deterministically.

## 13. First release scope / exclusions

**Included:** one survival arena; the four target families; three manual spectra and matching rewards; all four signature mechanics; five temporary power-up effects; a bounded between-beat upgrade set; escalating patterns; overload-based run end; result screen and restart; mouse and keyboard controls; adaptive effects and accessibility settings.

**Excluded:** mobile release, online leaderboard, accounts/cloud saves, multiplayer, multiple arenas/biomes, campaign narrative, permanent skill tree, monetization, generated assets requiring paid APIs, and multi-weapon progression beyond run upgrades.

The scope is intentionally broad per Founder direction. If production threatens the release reserve, preserve the core aim/fire/impact/destruction/run loop, then cut content according to this order: extra upgrade variety → optional power-up variants → secondary spawn patterns → nonessential background decoration. Do not cut shot responsiveness, clear impact/damage feedback, overload readability, restart, or performance caps.

## 14. Verification and acceptance criteria

1. In a real browser, pointer movement visibly controls aim; mouse press fires the first beam within the same input frame; held fire follows configured cadence; release stops firing immediately.
2. Beam endpoints match actual target surface intersections; damage applies once per beam-target event; piercing/split semantics are explicit and covered by tests.
3. All four families have distinct telegraphs, damage/break behavior, and destruction event outputs; volatile chains obey a bounded deterministic chain rule.
4. Spectrum matching rewards correct color but mismatches remain playable; all target communication has non-color cues.
5. Overdrive and each power-up have observable start, active, and expiry/consumption states; pause freezes their timers.
6. Run reaches overload, displays a clear game-over result, allows restart, and produces reproducible simulation results for the same seed and input trace.
7. Browser tests cover aim/fire/release/pause/visibility loss, target collision, chain caps, upgrade selection, overload, result and restart; simulation unit tests cover deterministic damage/score/upgrade paths.
8. Dense-chain benchmark records hardware/browser/viewport, target and particle counts, p50/p95 frame times, and adaptive cap activation. No performance improvement claim without measurements.
9. Inspect the actual rendered desktop browser at 1280×720 and 1920×1080, plus a narrow window fallback; review title, active play, power-up, overload warning, pause, and run-over states. Preserve screenshots and console/network results.
10. Asset and audio provenance/licensing review is a release gate; technical success is not human art or legal approval.

## 15. Risks and mitigations

- **Input feels ordinary:** prioritize zero-latency first-shot onset, exact cursor beam endpoint, impact directionality, and per-material hit feedback; evaluate in a real browser before adding content.
- **Spectacle hides information:** reserve high-energy colors/white flash for impacts; cap effects and keep target silhouettes, color shape language, reticle, and overload warning legible.
- **Full feature scope diffuses polish:** deliver layered milestones, keep a release reserve, and cut optional variety before core feel.
- **Chain performance spikes:** cap target/particle counts, chain depth, split beams, and supernova workloads; benchmark stress cases.
- **Spectrum is inaccessible:** pair hues with icons/patterns and provide adjustable high-contrast/reduced-flash options.
- **WebGL portability:** maintain tested Canvas 2D fallback and verify actual browser behavior; do not infer compatibility from compilation.
- **Audio rights/harshness:** use procedural or explicitly licensed local sources, provide mute/volume controls, and mix against a target loudness ceiling.

## 16. Open decisions intentionally deferred

- Exact run duration and spawn escalation curve: tune after hands-on playtests.
- Exact beam cadence, target durability, combo timeout, upgrade magnitudes, overload threshold, and particle counts: expose as data and tune through instrumented playtests.
- Final sound palette and target hardware matrix: select after the visual/audio first-artifact review.

## 17. Approval boundary

This document records the approved concept direction and design proposal. It does not authorize implementation automatically. Founder must review this file and approve it before implementation planning or code changes begin.
