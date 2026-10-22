# The Unwriter’s Almanac — Ink-Comic and Route-Choice Redesign

**Status:** Design approved by the Founder’s “approvef” response in this thread; implementation plan review is the next gate.  
**Date:** 2026-10-17  
**Project:** Existing browser game at `projects/the-unwriters-almanac/`; preserve the shared checkout and unrelated untracked files.  
**Scope decision:** One expressive ink-comic visual redesign plus one meaningfully redesigned route-choice page.  
**Target:** Local desktop/narrow-browser play; no deployment or distribution authorization.

## 1. Problem and design objective

The running slice has a coherent page palette and reliable browser-native controls, but its environment, character and texture are drawn with Canvas primitives. The asset manifest is empty. The illustration therefore reads like prototype placeholders despite a real local image-generation pipeline being available. The gameplay has the same prototype limitation: a line is accepted mainly for starting near the creature, touching the bead within a generous radius, reaching the seal and satisfying a total-length bound. It does not make the player reason about competing routes.

**Objective:** Make the first page feel like a deliberately illustrated, expressive ink-comic world, and make drawing a line a legible route decision rather than a permissive drawing gesture. Keep collision and active player input crisp, deterministic and independently testable over the illustration.

**Creative thesis:** A living comic is being printed in real time: the player inks one route through a torn page, chooses between a broad safe sweep and a short risky cut, and watches pigment and a mischievous ink-being answer that choice.

**Player fantasy:** “I read the marks, choose how to cross the damaged page, and draw a living line the little ink-being can trust.”

**Audience:** Players who enjoy compact environmental puzzles, readable choices, and distinctive illustrated worlds.

## 2. Approaches considered

1. **Recommended — image-led page plate with deterministic gameplay layers.** Generate original illustrated environmental art and a character-design proof; render the selected scene artwork as a local image while drawing the live rail, seal, bead, hazard boundary, and collision-aligned structural cues as sharp gameplay overlays. Use restrained authored motion rather than generated animation frames. This directly replaces placeholder-looking atmosphere without asking an image model to decide collision.
2. **Art-only refresh.** Add illustrated imagery but keep the current permissive line acceptance. Lower gameplay risk, but leaves the user’s “weakly designed” criticism unanswered.
3. **Mechanics-only refresh.** Add route constraints to the current procedural page. Lower asset-production risk, but leaves the main visual failure intact.

The selected scope is approach 1, limited to a single representative page and its complete browser loop. A full campaign, content framework or mass asset generation is explicitly out of scope.

## 3. Game loop and player choices

1. Inspect a comic page: the ink-being begins on the left, the gold pigment bead and folio seal are visible, and a central ink-eater tears across the direct crossing.
2. Read two strongly staged, visibly different route opportunities around the tear.
3. Draw one continuous line from the creature to the seal. The player may freehand it or use accessible route presets; a line preview shows exact geometry, ink used, hazard clearance and bead contact before commit.
4. Commit only if the route connects start → bead → seal, fits the finite page-ink budget, and clears the ink-eater’s forbidden shape. The same line is the traversable ridge and pigment path.
5. Watch the creature cling/traverse while the bead follows. A bad or eaten route gives an immediate understandable response and permits erase/redraw without losing the page.
6. Reach the seal, deliver a concise comic-panel solve beat, and allow deterministic restart.

### Route choice: one page, two understandable solutions

The first redesigned page, working name **“The Tear in the Current,”** places a fixed ink-eater/no-ink region across the tempting direct route. The player can choose:

- **Wide sweep:** more rail length, generous clearance and less precision; visibly consumes more of the page’s finite ink allowance.
- **Narrow cut:** shorter and more ink-efficient, but threads a smaller safe channel close to the ink-eater; it demands deliberate curve placement and has less clearance margin.

These are design targets for a real geometry puzzle, not pre-approved numeric dimensions. The exact hazard outline, passage widths and ink budget must be tuned against sampled rail lengths, actor footprint, drawing-point limits and actual viewport/game scale before implementation is called playable. Both route classes must have independently tested solutions. Ordinary geometry rules—not hidden preselected stroke identity—must validate them. A cosmetic arc variant that changes no constraint does not count as a meaningful route.

**Fairness rules:** Illustrate the no-ink region with shape/hatching as well as color; show start, bead, seal, both route mouths, and the remaining-ink meter before drawing; overlay a temporary line preview and reject safely with a named reason. No pixel-perfect path is required. Erase remains immediate and non-punitive. The challenge comes from choosing route class and balancing clearance against ink, not from unpredictable physics or opaque failure.

**Mechanic retained:** One continuous stroke has two consequences: the ink-being follows the rail and the gold bead moves along it. The rail itself is the source of truth for simulation; background illustration never supplies hidden collision.

## 4. Expressive ink-comic art direction

**Style name:** *The Living Margin* (proposed replacement for the current watercolor-first direction).

- **Originality boundary:** Use general ink-comic techniques—expressive line weight, concentrated hatching, asymmetrical panel framing, bold silhouettes, and selective accent color. Do not imitate or name a living or historical artist, reproduce a specific comic, character, panel layout, page, lettering treatment or signature mark.
- **Palette:** retain the project’s distinctive cool ivory `#F1E7CF` and blue-black `#182A35`; make vermilion `#D96C4D` the authored route/impact accent and gold `#E7B957` the bead/objective. Restrained sage `#688A87` may separate distant art from playable foreground. Remove the broad blurry-watercolor-bloom look as the dominant treatment; preserve only small intentional pigment accents where they clarify cause and effect.
- **Value/shape hierarchy:** strong outer ink masses and variable brush contour; broad comic shadows/hatching grouped into readable planes; generous light negative space behind controls and route preview. Creature, bead, goal, hazards and authored line remain crisp above the page illustration. Use hatch direction, silhouette and labels in addition to color to communicate route danger.
- **Character identity:** retain the existing original ink-being concept—one dark asymmetric blot silhouette, two pale eyes, a rooted tapering tail and one vermilion seed—but redesign its final silhouette/expression through an image-led character study. Review distinct idle, attentive/anticipation, stretched/clinging and solved silhouettes at actual game scale. Do not assume a generated multi-frame sprite sheet is coherent.
- **Page composition:** one wide comic-page illustration with a strong left-to-right eye path; the tear and two route choices frame the objective. Keep a quiet gameplay-safe center layer and unambiguous negative space where active lines and physics must read. Do not bake tiny text, controls or exact collision edges into generated art.
- **Typography and UI:** keep semantic DOM controls and legible local-system fonts. Page numbers and short sound-effect lettering can be authored as real text after asset review; generated lettering is not used for instructions or objectives.
- **Avoid:** faux sepia manuscript, watercolor wash as a substitute for scene illustration, generic procedural doodles, neon/glow, stock comic-book imitation, illegible AI text, decorative shapes that look collidable, and polish effects that obscure the path.

## 5. Art asset strategy and image-generation gate

The proposed first proof set is intentionally small:

1. A wide environmental page-plate candidate (no baked-in text, rails, objective glyphs or implied extra platforms) to establish scene composition and ink-comic material.
2. A standalone ink-being character-design candidate emphasizing the required identity anchors and play-scale silhouette.
3. If useful after inspecting the first two, one isolated hazard/ink-eater study. Do not batch-generate a full game or assume each image is runtime-ready.

The proof stage is **selection and review**, not automatic integration. Preserve raw candidates, prompts, seeds, workflow/API-format JSON, generation settings, model and component identifiers, file hashes, and the reason for selection/rejection. Compare candidates full-size and at the actual playfield scale. Founder can reject the direction or candidate before integration. The selected page plate may become local runtime art only after composition/legibility review and exact asset/model provenance is recorded. Keep all model inference local; no runtime API, account, paid service, or network dependency.

### Current machine evidence and limitations

The local ComfyUI endpoint answered successfully. At the inspection time, ComfyUI reported an NVIDIA RTX 5070 Ti Laptop GPU with 12.82 GB total VRAM and 2.71 GB free. Listed model components included `flux-2-klein-4b-fp8.safetensors`, `z_image_turbo_bf16.safetensors`, `qwen_3_4b.safetensors`, `flux2-vae.safetensors`, and `ae.safetensors`; these observations establish availability/names, **not** source revision, file identity, loadability at the requested size, complete component provenance, rights clearance, or output quality. Free VRAM changes over time; recheck queue/memory immediately before any generation and serialize GPU work.

Publisher materials describe FLUX.2 Klein 4B and Z-Image-Turbo weights as Apache 2.0, but local model filenames and separately repacked encoder/VAE assets are not proof of which bits are installed. Before generation, preserve/record component hashes and source URLs/revisions where recoverable; verify applicable weight and component terms. In particular, do not assign a license to generic `ae.safetensors` from its filename. If component provenance cannot be established, do not describe the output as rights-cleared or approve it for distribution. Any eventual distribution still needs human rights review; model-weight licensing does not itself guarantee copyright status of outputs.

**Generation stop conditions:** do not generate before the implementation plan is approved; do not generate if current VRAM headroom/queue is unsafe or the workflow cannot be matched to the installed files; stop after the small proof set; keep uncertain outputs in reference-only status. Never download new models or use a hosted API as an unapproved workaround.

## 6. Gameplay/system boundaries

- Keep the current browser-native ES modules, Canvas2D renderer, semantic DOM, local static server and zero-runtime-dependency posture unless testing shows a concrete blocker.
- Keep deterministic puzzle state authoritative in `simulation.js`; add explicit page geometry for the no-ink region, route corridors, ink allowance and any bead-contact condition. Renderer images cannot determine validity or solve state.
- Preserve a single bounded stroke, explicit preview/commit/erase, fixed-step update, safe pointer-cancel behavior, pause/restart, keyboard-accessible guided routes and reduced-motion support.
- Replace the current broad `start/bead proximity/seal proximity/length` acceptance as the sole challenge with testable continuous geometry rules: endpoints near the intended anchors, bead contact, budget respected, and no intersection with the ink-eater region. Add route-width/clearance checks only where derived from actual creature footprint and fair lane geometry.
- Make ink allowance visible before and during drawing. Report invalid reason (missed anchor, ink over budget, hazard hit, or invalid start/end), retain the drawing for correction where safe, and never silently mutate the line between preview and commit.
- The image page plate is a non-collision background layer. Crisp gameplay annotations remain separate, testable overlays aligned to logical 1280×720 coordinates. Do not add runtime networking, image generation, a level editor, or a multi-page framework.

## 7. Acceptance criteria

1. **Art proof:** the reviewed proof set has consistent expressive ink-comic material, a distinctive stable character design, a legible wide scene composition, no imitated source work, and no critical generated typography. Proof candidates are explicitly labeled concept/reference or selected runtime candidate.
2. **Meaningful choice:** the same puzzle has at least two geometrically distinct valid route solutions with visibly different ink-cost/clearance trade-offs: wide/long/easier and narrow/shorter/closer to the ink-eater. Automated simulation tests accept both and reject the direct hazard-crossing route and an over-budget route. A plain curve variation that evades no constraint is not a pass.
3. **Clear feedback/fairness:** the player sees both route options, finite ink budget, start/bead/seal and hatched no-ink hazard before committing; failed routes identify the reason and can be erased/redrawn without a softlock.
4. **Causal integrity:** the committed preview is exactly the rail used by simulation; the bead and character visibly follow it; a rendered background cannot create or remove collision.
5. **Character:** silhouette/eyes/tail/seed remain identifiable across the small authored motion set; inspect pose changes and transitions at gameplay scale and playback speed. Do not label generated stills as animation proof.
6. **Browser interaction:** pointer and keyboard/guided controls, start, draw, commit, invalid correction, both route solutions, erase, pause/resume, solve and restart work in the served browser at desktop and narrow sizes. Record screenshots/evidence and inspect accessibility tree, console/network and horizontal overflow.
7. **Regression:** run the existing game tests before changes and all project tests after changes; add deterministic tests for the two route classes, ink budget, hazard rejection, correction/retry, reset and seed replay. Rerun relevant checks after the final source edit.
8. **Provenance:** update the project art bible and asset manifest; document per-file source/model/workflow/hash/prompt/review state. Distinguish generated reference art, selected/integrated files, agent visual inspection, Founder art-direction decision, and human rights review.
9. **Bounded delivery:** one page, small proof set, local static browser artifact only. No deployment, publication, commercial-release assertion, or claiming a human playtest occurred.

## 8. Risks and decisions

- **Generated page composition competes with gameplay:** generate environment art as a background plate with reserved space; draw rails/hazards/anchors separately; inspect at target play scale before acceptance.
- **Generated creature identity drifts:** retain explicit anatomy anchors; use selected still as design authority and author only a few controlled poses; reject inconsistent candidates rather than building a low-quality atlas.
- **Route choices are cosmetic:** require two valid route families with tested clearance/ink costs and a rejected direct route; review in a playable browser, not only in diagrams.
- **Hazard feels arbitrary:** communicate forbidden shape through in-world hatching, route mouths and immediate explained failure; no invisible precision traps.
- **Model or component rights are uncertain:** preserve hashes/source provenance, keep candidates local and reference-only, and leave rights clearance open for a qualified human review.
- **Performance/image size:** bound local image dimensions and decoded memory; load same-origin assets only; measure actual browser frame/render behavior after integration.
- **Existing untracked user files:** add only the spec at this checkpoint; do not clean, overwrite, stage, or commit unrelated files.

## 9. Work contract and value gate

- **Global capability value:** exercise a verifiable local image-generation-to-browser-art workflow rather than relying on primitive placeholders.
- **Project value:** improve the two currently weak pillars—visual authorship and meaningful choice—without expanding beyond one page.
- **Learning value:** compare a small image-led scene/character proof against the actual browser composition and determine whether route-budget/clearance constraints create a legible choice.
- **Cost/opportunity cost:** local GPU time and review effort are variable; no paid API, new dependency, broad model download, campaign, or mass generation is authorized. Preserve a bounded proof set and the 24-hour jam profile’s six-hour release reserve as a planning constraint, not a claimed deadline.
- **Current milestone:** review the implementation plan; after its approval, separately review the first generated proof set before gameplay-art integration.
- **Non-goals:** full game, multiple pages, combat/enemies beyond the single static ink-eater hazard, procedural level generation, remote/paid image generation, generated animation sequences, deployment, publication and commercial-clearance claims.
- **Stop conditions:** if rights/provenance or adequate GPU headroom cannot be verified, pause generated-art work rather than disguising authored procedural art as generated or quietly switching to a hosted provider. If the first proof does not outperform the current visual hierarchy at actual game scale, revise the composition/prompt before integrating it.

## 10. Approval boundary

The Founder approved this ink-comic plus route-choice-page design. This approval authorizes planning, not image generation, game changes, contract updates, or commits. The implementation plan is the next review gate. Image generation remains separately gated by exact model/component provenance, rights and VRAM preflight; selected proof assets must be reviewed before gameplay-art integration.
