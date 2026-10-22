# The Unwriter’s Almanac — Design Specification

**Status:** Concept and core mechanic approved; visual direction reviewed; full design spec awaits Founder review. No game implementation authorized yet.  
**Date:** 2026-10-16  
**Project:** New isolated browser-first game; Neon Blasters remains untouched.  
**Design benchmark:** Neon Blasters simulation timing was measured separately; see the conversation summary.  
**Target:** Desktop web, pointer plus keyboard; first slice one compact illustrated puzzle page.

## 1. Intent and distinctive premise

A mischievous living ink-creature has escaped from an unfinished naturalist’s almanac. It crosses each impossible page by drawing a single continuous stroke. The stroke is not merely a grappling hook: once inked, its shape becomes a local law of gravity and a traversable ridge. It can redirect drifting pigment, catch an otherwise unreachable mote, and give the creature a new surface to cling to.

**Creative thesis:** A puzzle page becomes editable physics: the player draws one continuous rail, watches the world’s gravity and drifting ink bend around its geometry, then guides an expressive ink-being through the result.

**Player fantasy:** “I am writing a rule into the page, and this little living mark trusts my line enough to follow it.”

**Audience:** Players who enjoy compact environmental puzzles, legible traversal challenges, and worlds whose material appearance communicates their rules.

**Emotional shape:** Curiosity at the creature’s first movement; experimentation with the stroke; a visible, understandable physical consequence; delight at the creature’s traversal; a quiet moment of authored completion.

## 2. Core puzzle mechanic — one stroke, many laws

The player has one editable, continuous stroke per puzzle page. The player presses/holds a drawing input and drags within the page’s safe drawing region, then releases. The stroke receives a small configurable control-point budget and visible endpoints. After release, the stroke becomes an ink rail. Its local tangent changes the direction of the drifting pigment mote’s attraction/flow and becomes walkable/clingable terrain for the ink creature. A closed loop or graceful arc can redirect the mote; the creature traverses the same curve under its own gravity/orientation state. The player can redraw or erase the stroke until the page is solved.

This is deliberately not arbitrary world painting. One stroke, one clearly visible result, a bounded shape budget, and a single named objective keep puzzle causality inspectable. The exact mapping between rail tangent, local gravity direction, and pigment movement must be tuned in the first playable slice and be visible before the player commits the stroke. If input strokes need smoothing, render both live preview and committed rail identically to avoid hidden geometry.

## 3. Smallest compelling loop

1. **Notice:** An ink-being idles on a paper ledge; a bright vermilion pigment mote drifts beyond a gap; the exit mark sits visibly on the opposite page edge.
2. **Infer:** Sparse marginal annotations and motion preview show that drawn ink becomes a surface and guides nearby floating pigment.
3. **Draw:** The player sketches one connected stroke that bridges, hooks, or loops across the gap.
4. **Commit:** On release, the stroke dries into a raised ink rail; the mote curves along/around it; the creature anticipates, jumps, clings, and traverses it.
5. **Adjust:** If the geometry fails, erase/replace the rail without losing progress or triggering a death penalty.
6. **Solve:** Bring the mote into the folio seal / exit mark. The creature reaches the page gutter and the page transforms into a completed print.
7. **Recover:** A clear restart restores the puzzle, stroke budget, creature, mote, and completion state deterministically.

## 4. Player verbs and controls

- `move`: arrow keys / A-D or optional pointer-directed movement, depending on final control proof.
- `jump / spring`: Space or W / Up. Jump input has a small buffer and coyote allowance so traversal failure feels attributable.
- `draw rail`: hold primary pointer and drag in the page area; release to commit. Keyboard alternative uses a simple start/extend/commit path if it can remain comprehensible.
- `erase / redraw`: right-click or E clears the current rail while unsolved; a visible action label and keyboard focus are required.
- `pause`: Escape / P; freezes simulation and animation clocks coherently.
- `restart`: R or a clearly visible menu action.
- **Accessibility:** avoid color-only signaling; visible line, endpoint and attraction preview; keyboard alternative to drawing; reduced motion setting; no flashing; clear contrast and UI-readable objective text.

Exact player movement and pointer mapping are a prototype question. Do not require fine motor drawing: snapping/smoothing should make a short gesture usable. Provide a deterministic fallback stroke preview or a small set of editable handles if freehand noise harms puzzle fairness.

## 5. States and data ownership

`BOOT → TITLE → PAGE_INTRO → PLAYING → PAGE_SOLVED → RESULTS/RESTART` with `PAUSED` reachable from `PLAYING`. A puzzle may also have a non-punitive `RESET_PAGE` action.

The puzzle simulation owns page geometry/collision, creature position/velocity/grounded/attachment state, player stroke/control points, mote state, objective and completion. It runs at a fixed timestep with a capped catch-up policy. Rendering owns paper layers, wash, hatching and pose interpolation, but cannot change puzzle outcomes. Typed events communicate `stroke_previewed`, `stroke_committed`, `stroke_erased`, `mote_redirected`, `creature_jumped`, `creature_attached`, `creature_fell`, `creature_landed`, `objective_reached`, `page_solved`, and `page_reset`. A seed and ordered commands reproduce gameplay; cosmetic wash movement uses an independent clock/seed.

## 6. Art direction — “The breathing page”

**Direction selected from three original browser visual studies.** Build on watercolor pigment motion with crisp authored ink geometry for fair interaction.

- **Reference principles, not imitation:** Relief print positive/negative contrast can clarify solid rails (V&A printmaking overview); manuscript creatures can read iconically through silhouette and staged color (Getty bestiary exhibition); different ink/paper responses can distinguish stable structures from fragile washes (Harvard conservation article). The original game is not a historical pastiche. No named artist, specific artwork, manuscript page layout, border, heraldic figure, or source image is copied or shipped.
- **Palette:** cool ivory rag paper `#F1E7CF`; blue-black structure `#182A35`; quiet sage wash `#688A87`; player-authored vermilion `#D96C4D`; warm pigment/gold `#E7B957`; chalk-white highlights `#FAF6E9`.
- **Value hierarchy:** creature, solid collision edge, live stroke, objective and mote are crisp and distinct; diffuse blooms remain low contrast and behind gameplay; endpoint and preview stay visible over any wash.
- **Shape grammar:** Creature has an asymmetrical droplet/blot body, two negative-space eyes, a tapering capillary tail, and one small vermilion seed. Drawn rails have gently irregular but snapped smooth curvature and readable endpoints. Old print-derived ledges are composed as broad negative/positive planes, not a grid of generic platforms. Motes are small saturated pigment beads with restrained halos. Exit seals use original botanical/astral page symbols.
- **Material grammar:** Crisp structural ink holds edges; wet washes bloom, feather, and dry; chalk/graphite annotations stay sparse; vermilion is only for active/player-authored change and its consequences. “Ink physics” is a designed visual rule, not a scientific material simulation claim.
- **Camera/composition:** fixed orthographic page tableau at 16:9 logical resolution, one page in frame, soft paper/parallax layers, generous margin/gutter, stable camera. Page geometry aligns exactly with collision; no decorative ledges imply unsupported walkable surfaces.
- **Typography/UI:** quiet editorial folio numbers and marginal notes; small local/system serif plus restrained mono annotations. Objective, draw/erase instructions, pause, and completion are explicit text, never faux unreadable handwriting. UI is embedded on page-edge labels rather than floating generic cards.
- **Forbidden:** generic distressed sepia/parchment, neon cyberpunk, copied manuscript borders, name-brand imitation, all-over blur, uncontrolled wash behind gameplay, decorative illegible text, primitive circles pretending to be finished animation, or generated sprite sequences accepted without semantic review.

## 7. Animation and signature moments

The character’s visual identity must remain stable across a small authored pose system; no AI-generated multi-frame cycle is assumed consistent.

- **Idle (gentle 2–3 second loop):** wet body subtly breathes; tail-tip investigates nearby page fibers; occasional slow blink; no perpetual noisy jitter.
- **Draw anticipation/contact:** as the player begins a stroke, the creature tracks the pen tip with its eyes, compresses slightly; at commit it briefly flattens against the page and the tail follows the new ink curve.
- **Jump/traverse:** squash and anticipation, stretch through launch, settle/contact with clear foot/adhesion read; when attached to a rail, body orientation follows local tangent with a small delayed tail follow-through; avoid tumbling without cue.
- **Fall/recovery:** stretched droplet silhouette and tail-up anticipation, a soft page bounce on landing; forgiving reset if stuck.
- **Solve:** the creature reaches toward the exit seal; the vermilion line drains into the gutter, the wash dries, and the completed page quietly acquires a final outline/folio mark.

Animation methods for first slice: authored vector body/eyes/tail/wings-like capillary, plus a small pose/timing state machine. Frame-based or generated art may be explored later but is not a dependency. Inspect all transitions at actual gameplay scale and playback rate; static poses and CSS demo loops do not certify game animation quality.

## 8. Technical architecture and boundaries

- Static browser app with a small module graph; use the existing Node/ES-module local server convention, no added runtime libraries unless proven useful and installed.
- Canvas2D for deterministic playfield rendering, local path geometry, wet-wash masks and sprite/vector composition; DOM for semantic instructions, focusable controls and accessible status. Avoid a 3D engine: the intended artifact is a page illustration, not dimensional realism.
- Modules: `simulation` for deterministic physics and stroke state; `input` for pointer/keyboard coordinate conversion and cancellation; `renderer` for paper/page layers and pose interpolation; `animation` or animation tables for state timing; `app` for menus/HUD/state transitions; `audio` optional and deferred until the visual/action loop works.
- Pointer up, lost capture, blur, visibility change and resize are explicit paths; an incomplete drawing stroke never commits on lost input. Pause freezes puzzle and animation clocks. Reset is idempotent.
- Bound stroke control points, particles/wash emitters, event count, catch-up and any render-layer allocations. No remote API, account, telemetry or network dependency.
- One page and one interaction beat only for the first slice. Keep geometry/data separable enough for a second page later, but do not build a level editor/content framework now.

## 9. Local generation policy and resource constraints

Local ComfyUI is available with FLUX.2 Klein 4B distilled FP8, Qwen 3 4B text encoder, and FLUX2 VAE listed; installed model identifiers were probed through ComfyUI. GPU is an RTX 5070 Ti Laptop GPU with ~12 GiB VRAM; at one inspection 2.7 GiB free in ComfyUI stats and `nvidia-smi` showed a different near-idle moment. These observations vary and do not guarantee a job will fit. Generation must be serialized, begin only after checking current queue and free memory, and stop after a small approved concept set.

ComfyUI shows explicit support for the workflow node names and installed components, but a workflow has not yet been executed for this concept. Exact checkpoint/encoder/VAE license files and redistribution rights are not yet verified; optional generated outputs remain concept-reference-only until checked. Never promise unlimited generations. Do not use generated individual poses as a sprite animation without identity, alpha, anchor, transition and in-game playback review.

First visible artifact uses original inline SVG/Canvas-like authoring so design review is not blocked by image-model availability. If model generation is later approved/needed: sequential, 512-scale concept candidates, reproducible prompt/seed/workflow/component IDs; preserve raw output, prompt and hashes; create a candidate sheet with rejected candidates and honest status. No source/reference images are runtime assets.

## 10. Scope, deliverables, and cuts

**First playable slice:** one designed page; one ink-being; one falling pigment mote; one editable rail; one primary puzzle objective; start/pause/restart/solve states; pointer/keyboard input; at least idle/draw/commit/move/land/solve animation beats; concise instructions and objective cue; original page art; seeded tests.

**Explicit non-goals:** full metroidvania, many levels, enemies/combat, procedural puzzle generation, arbitrary freehand painting, persistent progression, online play, mobile release, remote/paid AI API, voice acting, localized content, 3D, export packaging, publication/deployment. Additional levels and audio wait until the slice proves fun/readable.

If scope grows, cut in this order: optional audio and extra page decoration; alternate character poses beyond the required core actions; optional freehand handles; concept generation; extra tutorial language. Preserve the understandable one-stroke rule, recoverable page, complete solve/restart loop, distinct character silhouette, material readability and actual browser validation.

## 11. Acceptance criteria and verification

1. **Conceptual comprehension:** the player can state from the in-game cue that a drawn stroke becomes a rail and redirects the mote before committing a puzzle-critical stroke; verify in a short human playtest when available, otherwise mark comprehension as unapproved.
2. **Drawing:** stroke begins only inside drawing-safe region, ends on release, maps correctly through CSS scale/high-DPI resizing, is continuous, bounded and replaceable; lost pointer/blur/visibility cancels safely.
3. **Puzzle causality:** changing the line changes mote route and traversal surface deterministically; no hidden renderer-only gameplay; a valid authored solution reaches the objective and triggers completion.
4. **Character:** idle, anticipation/draw, jump/rail traverse, landing/recovery, and solve response all have observable temporal motion with identity anchors preserved; inspect playback at viewport and in-game scale.
5. **Recoverability:** pause freezes game and animations; page reset and restart return to a clean deterministic state; unreachable/reset conditions cannot softlock.
6. **Readable visual hierarchy:** playable rails, endpoints, creature, mote and objective remain legible over wash at desktop and narrow viewport; reduced motion preserves feedback.
7. **Automated coverage:** seeded replay equivalence; stroke cap/smoothing; input cancellation; fixed-step/hitch cap; rail collision/attachment; redirected mote; invalid/valid solution; pause/reset/restart; objective transitions.
8. **Actual browser proof:** serve the game, operate draw/erase/move/jump/pause/solve/restart in the actual browser; inspect accessibility tree, console/network, screenshots or recording, and relevant viewports. A unit test or static illustration is not runtime proof.
9. **Budget/performance:** measure representative CPU/update/draw timings and bounded allocation counts; report environment, viewport and run count; no full-game FPS claim from the earlier Neon Blasters simulation-only benchmark.
10. **Rights/provenance:** distinguish authored SVG/code and concept-only model candidates; record hashes/workflow/model/terms status when generated assets exist; no shipping or commercial clearance claim without review.

## 12. Risks, failure modes, and mitigations

- **The line feels like a standard drawing puzzle:** make the same physical rail support the creature while it also redirects a visibly moving pigment mote; the two consequences must be simultaneous and legible.
- **Gravity rule is opaque:** preview a small directional/current cue around the stroke before commit; show post-commit physical behavior immediately; consider one safe reversible intro.
- **Freehand drawing creates unfair collisions:** clamp to safe region, bound point count, simplify deterministically, expose final geometry before commitment, and allow no-penalty erase.
- **Watery image washes hide platform edges:** keep collision contours and active stroke high contrast; constrain wash masks behind play; preserve value separation at narrow viewports.
- **Pose changes break identity or feet contact:** keep immutable body silhouette/eye count/tail root/seed; use authored vector rig/table, stable anchors and playback review.
- **Generation consumes GPU or yields inconsistent images:** first pixel does not require generation; query queue/VRAM, generate sequentially only after license review, preserve all candidates and stop if unusable.
- **Scope balloons to an elaborate illustrated book:** ship one perfect page-sized loop, no campaign or editor until playtest says otherwise.
- **Benchmark confusion:** report Neon Blasters’ separate Node simulation-only timings as such; do not conflate them with graphics or this game’s browser performance.

## 13. Human review gates

Founder approves the design spec before planning/code. Founder selects/revises the direction from this moodboard. A genuine human playtester assesses rule comprehension and puzzle satisfaction. Visual/art-direction and animation identity remain agent-assessed until explicitly human reviewed. A qualified rights reviewer must verify exact model files/terms before any generated content is distributed. No jam deadline/rules were provided; the project is a local experiment, not a jam submission.

## 14. Approval boundary

The original concept, “clever page puzzles” gameplay, and “one stroke, many laws” interaction are decisions from the Founder. “The breathing page” is the selected visual grammar from the browser board. This specification binds scope and success evidence, but still awaits Founder’s review. **Do not write implementation code, generate game assets, or build a vertical slice until the Founder explicitly approves this design spec.**