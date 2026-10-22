# The Unwriter’s Almanac — Implementation Plan

**Status:** Draft for Founder review; implementation has not started.  
**Design authority:** [2026-10-16-the-unwriters-almanac-design.md](../specs/2026-10-16-the-unwriters-almanac-design.md)  
**Project root:** `projects/the-unwriters-almanac/` (new, isolated; do not modify Neon Blasters or Prismatic Creature Battler).  
**Target:** desktop web browser, static local app, Canvas2D with semantic DOM UI.  
**Planning profile:** 24-hour elapsed game-jam envelope, with 25% protected release reserve (360 minutes). No jam deadline/rules or human-review availability were supplied; treat this only as a planning model, not a submission commitment.

## 1. Objective and completion criteria

Implement one playable original page in which an ink creature uses one editable continuous line as both traversable terrain and a force that redirects a pigment mote into an exit seal. Provide a clear start-to-solve-to-restart loop, authored animation, graceful failure/recovery, and a coherent reviewed watercolor/ink-wash visual grammar.

**Definition of done for the vertical slice:**
- In a real browser, start → play → draw/commit → successful route → page solved → restart all operate without console/network errors.
- One drawn stroke visibly previews and deterministically commits; bounds/smoothing are predictable; erase/redraw is safe.
- Stroke geometry acts as collision/traversal and changes mote movement; one deterministic authored solution reaches the goal. Solution must not depend on renderer state.
- The ink-being displays distinct idle, look/anticipate, launch/traverse, contact/land, fall/recover, and solve behavior with stable identity anchors, inspected in playback at game scale.
- Pointer coordinate mapping survives CSS/high-DPI resize; pointer loss, blur, visibility changes cancel an uncommitted stroke; pause freezes simulation and character/wash animation clocks; page reset is reliable.
- DOM controls provide accessible instructions, objective, pause/reset/restart, keyboard movement/jump and a keyboard path to create/commit or select a bounded stroke if freehand is not accessible.
- Desktop and narrow viewport rendering have no overflow or collision/visual divergence that hides the objective.
- Automated tests cover deterministic replay, stroke sanitization/bounds, pointer lifecycle, fixed-step hitch cap, rail attachment/collision, mote redirection, solve/reset/restart and pause.
- Browser screenshots/recording, accessibility snapshot and clean console/network evidence are retained; actual human puzzle comprehension remains a clearly labeled open gate if no playtester participates.
- Build/source paths are isolated; no AI-generated runtime art is assumed. Any optional concept-only model output has exact lineage and rights state recorded; unknown rights block distribution.
- Measure actual representative update/render timing and stroke/particle bounds; do not infer this game’s FPS from the unrelated Neon Blasters simulation benchmark.

## 2. Constraints, approvals, and scope cuts

- Design spec is approved by Founder; this plan itself still awaits Founder approval before implementation.
- The existing git branch is `main`. To avoid working directly on the protected/default branch, request plan approval and use a new task branch/worktree after approval. Never switch or create branches without explicit applicable authorization in this shared checkout; if a clean isolated worktree cannot be made safely, ask the Founder before coding.
- Do not alter root `.env`, prior untracked paths, existing game projects, or user data. Use only new project-specific paths and the spec/plan artifacts.
- Reuse available Node/browser and project conventions; no new dependencies/services, no network runtime, no paid APIs, no deployment or publishing.
- The one-stroke physics mapping is the largest design risk. Prove it in the first playable graybox, not after illustration production.
- Local ComfyUI generation is not required. If a concept candidate is later justified, recheck GPU queue/memory, exact model file and license provenance, generate sequentially and preserve raw candidates; candidates remain reference-only until reviewed.
- Cut optional audio first, then concept generation, extra page ornaments, nonessential pose variants, tutorial copy variants. Preserve the causal puzzle loop, readable character/rail/mote/goal, accessibility alternatives, restart and browser validation.

## 3. Isolated project shape

```text
projects/the-unwriters-almanac/
  package.json                 # minimal scripts only; no dependency required
  docs/game-brief.json
  docs/art-bible.json
  docs/task-graph.json
  docs/asset-manifest.json
  src/index.html
  src/styles.css
  src/app.js
  src/simulation.js
  src/input.js
  src/renderer.js
  src/animation.js
  scripts/serve.mjs
  tests/simulation.test.mjs
  tests/input.test.mjs
builds/the-unwriters-almanac/  # only if a distinct built copy is needed
evidence/the-unwriters-almanac/ # QA, captures, manifest, and benchmark evidence
```

Keep source-first deployment static and local. The browser-native Canvas2D/DOM split fits the artwork and deterministic physics. Avoid engine conversion, level-editor scaffolding, assets that are visually generated but semantically unverified, or abstractions for multiple pages.

## 4. Phases and bite-sized tasks

Estimates are provisional planning estimates, not measured productivity. The task estimates total **970 minutes (16 h 10 m)**, leaving the profile’s **360-minute/6-hour (25%) release reserve** unused. The remaining planned work capacity is 110 minutes of slack within the 24-hour envelope. Re-estimate after the loop prototype and protect the full reserve.

### Phase A — Isolated setup, contracts and first page proof (125 min)

**UA-001 — Create project scaffold and runnable local shell (35 min)**
- Add a new minimal project, static-server script, semantic app skeleton and a passing initial `npm test` script.
- Acceptance: local HTTP response serves HTML/CSS/module with correct content types; no changes to existing games; no third-party runtime requests.

**UA-002 — Persist project brief, art bible, task graph, asset/provenance ledger (40 min)**
- Convert approved specification into schema-valid project contracts; record camera, palette, silhouette, animation identity anchors, forbidden styles, responsibilities and human gates.
- Acceptance: all JSON parses and `ags schema validate` reports pass (or required schema validator limitation is reported without claiming pass); every visual asset is labeled authored/code, reference-only generated, integrated or approved truthfully.

**UA-003 — Responsive art proof page (50 min)**
- Port the selected “breathing page” language from the moodboard into a first playable-scale scene comp: rag paper, constrained wash behind crisp contours, vermilion proposed rail, ink-being silhouette, drifting mote and folio seal.
- Acceptance: browser screenshot at desktop and 540px viewport; no overflow; collision candidates align with drawn shapes; a documented critique fixes any key readability defect before gameplay expands.

### Phase B — Deterministic one-stroke gameplay proof (300 min)

**UA-004 — Define deterministic state, geometry and fixed-step contracts (55 min)**
- Model idle/title, playing, paused, solved; creature, mote, one editable rail, goal, seed, ordered command inputs, event types, fixed delta and bounded catch-up.
- Acceptance: repeated seed/command sequence yields identical state/event trace; pause and reset do not leak old rail/timer state.

**UA-005 — Normalize, simplify and preview player drawing (65 min)**
- Map pointer into a logical 16:9 page; capture drag; constrain to permitted zone; resample/simplify under a declared point cap; render identical prospective and committed paths; keyboard-accessible rail construction fallback.
- Acceptance: multiple CSS/device scales preserve coordinates; cancel on lost capture/upstream blur/hidden page without accidentally committing; empty/degenerate strokes produce a safe message.

**UA-006 — Implement traversal rail and pigment-mote guidance (100 min)**
- First prove a stable playable route: rail supports collision/attachment or physically consistent guided traversal; its tangent affects mote drift in a clear visible way; specify any rail intersection/path-follow behavior exactly in code and tests.
- Acceptance: authored solution reaches goal deterministically; a nearly identical but invalid route does not solve; reset/erase always allows recovery; stroke geometry cannot exceed point/length bounds.

**UA-007 — Add solved, pause, erase and restart flows (40 min)**
- Make solved state require the mote at goal; provide pause and explicit page reset/restart; freeze world and animation clocks together.
- Acceptance: repeated resets are idempotent; a solved page does not accept further physics input; restart starts a clean seeded page.

**UA-008 — First browser play loop and mechanic adjustment (40 min)**
- Operate the actual game in browser; tune only the most consequential stroke-force/input/goal issue based on observed play.
- Acceptance: capture start, drawing, committed rail, mote redirect, character traversal, solved and restarted state; document outcome and defects before moving to visual production.

### Phase C — Animation, atmosphere and accessibility (265 min)

**UA-009 — Implement authored character pose/timing system (85 min)**
- Create a stable original vector creature and coordinated idle, tracking/anticipation, jump/stretch, rail cling, fall/landing, recover and solved beats. Use anchored parts and declarative timing curves/state transitions; no AI sprite cycle assumptions.
- Acceptance: inspect full loop and all important transitions at actual playback speed and small game scale; body silhouette/eyes/tail root/pigment seed stable; ground/rail contact reads. Save a contact sheet or frame strip for review.

**UA-010 — Add layered watercolor wash and authored-page detail (55 min)**
- Use limited parallax paper grain, masked diffuse pigment, sparse botanical/astral page motifs and rail dry/bloom/dissolve sequence. Gameplay stays above washes.
- Acceptance: reduced-motion path; wash and particles bounded; page identity not generic sepia; stroke and goal remain legible at both viewports.

**UA-011 — Add accessible instruction, keyboard input and state feedback (55 min)**
- Clear objective and one-sentence stroke rule; pointer/keyboard alternative; visible help keys; pause/resume/reset/restart; focus order, status announcements, reduced motion.
- Acceptance: keyboard-only play can complete a puzzle route; focus is visible; no required information encoded by color/animation alone; dynamic instructions announce once without repetitive screenreader spam.

**UA-012 — Add concise solve and recovery choreography (35 min)**
- Mote enters seal, vermilion drains to page gutter, creature completes a directional look/reach/settle action; optional reset keeps page state comprehensible.
- Acceptance: solve can only occur on objective event; celebration short, skippable/reduced-motion, and never blocks restart.

**UA-013 — Test coverage for geometry, states, input failure and deterministic events (35 min)**
- Add Node unit tests for stroke sanitization, objective, trajectory redirection, reset, pause/fixed-step, and pointer lifecycle; use deterministic seeded fixtures.
- Acceptance: tests fail on injected wrong coordinates, stale input or out-of-bounds stroke and pass for corrected behavior; no suppressed failures.

### Phase D — Integration, adversarial QA and evidence (280 min)

**UA-014 — Fixed-step app/render integration and dev smoke (45 min)**
- Connect app, input, simulation, render and animation; instrument step/draw/frame and bounded actor/point counts. Handle resize/context/device-pixel scaling.
- Acceptance: render cannot modify simulation; hitch drops are capped/recorded; no unbounded objects in a representative session.

**UA-015 — Adversarial actual-browser traversal testing (80 min)**
- Test draw start/end/cancel, erase/recommit, keyboard fallback, jump/traverse, goal, pause, reset, resize, visibility interruption, and stalled-frame recovery.
- Acceptance: every failure path is recoverable; capture screen and update defect notes; no console errors/network requests outside same-origin local app.

**UA-016 — Visual and accessibility review at desktop + narrow layout (55 min)**
- Inspect title/intro, active puzzle with live preview and committed stroke, paused, page solved, restart, reduced motion, keyboard path. Review tab order, labels, contrast, focus, overflow and game/text hierarchy.
- Acceptance: screenshots and accessibility tree retained; fix first-order composition or gameplay readability issues rather than cosmetic polish only.

**UA-017 — Measure representative CPU/render timings and resource bounds (35 min)**
- On named machine/browser, fixed seeded run of at least 25 repetitions after warm-up; report median/p95 update/render frame or clearly state if GPU render timing not exposed. Report actual geometry/particle caps and occupancy.
- Acceptance: raw output retained; distinguish development harness and browser; no unsupported 60 FPS promise; repeat a changed source/build after any performance fix.

**UA-018 — Provenance, rights and local build/evidence audit (35 min)**
- Record local asset file hashes, authorship/method, any model/workflow/prompt/license information, test/runtime commands and open human gates. Create package only if the project's delivery requires it; no deployment.
- Acceptance: no `.env`, model weights, cache or unrelated files in game source/build; every delivered artifact traces to a source or is clearly marked; human playtest and rights approval remain open until obtained.

**UA-019 — Final regression and handoff record (30 min)**
- Run project automated tests, syntax checks, JSON/schema checks if installed, HTTP checks, browser completion loop, `git diff --check`, and source/status inspection.
- Acceptance: exact final command results and limitations documented; tests rerun after last change; no claim of “visual masterpiece” or human-approved art without human review.

### Planned budget

| Phase | Estimate |
|---|---:|
| A: Setup/contracts/first visual proof | 125 min |
| B: Playable one-stroke loop | 300 min |
| C: Animation/visual/accessibility | 265 min |
| D: Integration/verification/evidence | 280 min |
| **Planned work** | **970 min / 16 h 10 m** |
| 24 h profile release reserve (25%) | **360 min / 6 h** |
| Extra planning slack | **110 min / 1 h 50 m** |

## 5. Dependency graph

```text
UA-001 → UA-002 → UA-003
   └──────→ UA-004 → UA-005 → UA-006 → UA-007 → UA-008
                                      ├→ UA-009 ─┐
                                      ├→ UA-010 ─┼→ UA-012
                                      └→ UA-011 ─┘
UA-004..UA-012 → UA-013 → UA-014 → UA-015 → UA-016 → UA-017 → UA-018 → UA-019
```

Do not run GPU generation in parallel with another GPU-heavy job. Other model may research references or inspect independent artifacts but may not edit the same source files. One integrator owns final changes, browser test and project handoff.

## 6. Risks and gates

| Risk | Countermeasure / evidence gate |
|---|---|
| “Drawing a line” feels like generic grappling | Same rail must move mote and support creature; prove paired consequence in UA-006/008 |
| Arbitrary freehand rail impossible to tune | Explicit point count/curvature/tangent model; visible preview and forgiving erase; no mandatory pixel precision |
| Gravity metaphor and collision disagree | Prototype behavior before wash art; exact collision paths correspond to visible path |
| Cute character lacks weight or stable identity | Authored pose transitions/anchors; inspect frame contact sheet and live playback |
| Palette washes obscure play | Reserve high-contrast contours/endpoints and measure at narrow viewport |
| App works only for developer machine | Local Node static server, zero remote dependencies, clean new project |
| Plan estimates hide work/time risk | Run jam planner, re-estimate after first browser loop and keep 6 h reserve |
| Rights of model output uncertain | No model output required for play; any generation remains reference-only pending file/license audit |
| Existing untracked user files risk contamination | Create only in new scoped project paths; never broad-stage or remove unrelated files |

## 7. Jam planner estimate check

The approved jam profile is only a budget model: no actual jam rules, submission constraints, or deadline were provided.


`ags jam plan --profile 24h --tasks evidence/unwriter-almanac-planner-tasks.json` was run with 970 total mandatory estimate minutes and explicit dependencies. It planned all 19 tasks, deferred none, preserved the 360-minute release reserve, and reported 110 minutes remaining capacity. The full command result is in `evidence/unwriter-almanac-jam-plan.json`; the planner input is in `evidence/unwriter-almanac-planner-tasks.json`. The planner is advisory/greedy, not a critical-path oracle. Any cut of a mandatory task blocks approval of this schedule; the plan must then be rebalanced without taking time from the reserve. No actual jam rules/deadline are known, so this is only a scope worksheet.

## 8. Approval boundary

This plan converts the Founder-approved design into isolated implementation tasks and acceptance evidence. **It is a proposal, not authorization to modify the game project. Do not scaffold or implement the new game until the Founder explicitly approves this plan.**