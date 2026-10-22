# 11vatedTech — Torch RPG
## Game Design Document (GDD) v0.1 — Vision and Vertical-Slice Plan

**Status:** Concept baseline for collaborative review; not yet an implementation specification  
**Working title:** Untitled Torch RPG (name deliberately not locked)  
**Studio:** 11vatedTech  
**Target release:** AI Browser Game Jam 5, October 2026  
**Primary target:** Desktop browser, mouse and keyboard  
**Secondary target:** Touch/browser compatibility where it does not compromise the core experience  
**Production rule:** AI-generated visual, animation, audio, and written assets are the intended production source; no primitive/procedural art may stand in for hero content.

---

## 1. Executive vision

Build a visually distinctive fantasy action-RPG vertical slice about **torches that embody different kinds of fire, each with its own physical behavior and combat philosophy**. At character creation, the player answers three reflective questions. Their answers influence three starting torches offered by the game; the player chooses one and begins exploring a dangerous, interconnected region. They fight with the torch as a physical weapon and cast its dominion abilities, discover other flames, learn unexpected interactions, and uncover evidence that a secret order has learned to eat the essence of fire and transform into monstrous flame-bearing beings.

The jam release must not pretend to contain an entire open-world RPG. It must deliver one convincing, beautifully art-directed region, a complete short adventure, several genuinely distinct combat interactions, one memorable mystery reveal, and enough world texture to make the larger game feel imaginable.

### One-sentence pitch

**A torch is a weapon, a magic discipline, and a reflection of the person wielding it—until a forbidden order begins devouring flames and turning their powers into living monstrosities.**

### Player fantasy

“I discover a flame that fits how I see myself, learn to wield it creatively, explore a world shaped by strange fires, and face enemies who have broken the fundamental laws of flame.”

### Creative thesis

Fire is not a palette swap. Every dominion must change what the player does, how the battlefield behaves, and what new possibilities appear during exploration. The visual spectacle must communicate gameplay clearly while feeling authored, coherent, and premium.

---

## 2. Product definition and scope contract

### 2.1 Full-game ambition

The larger game is an interconnected open-world fantasy action RPG featuring:

- Ten flame dominions with distinct identity, torch designs, combat behavior, environmental interactions, and lore.
- Character creation and a three-question identity ritual that influences the three torches initially offered.
- Collectible torches, discoveries, enemies, creatures, secrets, environmental puzzles, and faction encounters.
- Physical torch combat joined to dominion casting, with cross-flame combinations and player experimentation.
- A concealed order that consumes fire essence and manifests it as unstable monster transformations.
- A world history and moral conflict around identity, ownership, corruption, healing, and the consequences of consuming another being's flame.

### 2.2 Jam vertical slice

The jam build demonstrates the core of that promise in one carefully composed region. It is a **finished slice, not a fake open world**.

**Required player-facing content (provisional target):**

- A title/menu screen and short opening sequence.
- A three-question character ritual; answers produce three available starter torches with explainable affinity logic.
- Three fully playable dominions: Orange/Hearthfire, Blue/Jetfire, and Purple/Haze Fire. These are provisional slice picks, selected for their distinct combat verbs.
- One contiguous explorable region with a clear route, optional detours, secrets, environmental interaction, and a strong distant landmark.
- At least three enemy roles plus a unique flame-eater encounter/boss.
- Physical torch strikes, defensive/movement response, signature abilities, readable status effects, and at least three authored cross-effect combos.
- At least one meaningful white/spirit-fire story interaction and a black/abyss-fire corruption encounter, even if those dominions are not player-selectable in the slice.
- A short narrative arc that ends with a memorable reveal of the forbidden technique.
- Collectible or discoverable torch lore; one meaningful upgrade or reward; save/restart behavior appropriate to scope.
- Original or properly licensed sound effects, music, UI, typography, and visual assets.
- A browser export launched and tested in the target browser, with evidence captured from the real build.

**Target session:** approximately 12–20 minutes on a first playthrough, with a shorter repeat run. This is a design target, not a promise until measured in playtests.

### 2.3 Deliberately out of scope for the jam

- A vast seamless open world, multiple complete biomes, multiplayer, online economies, procedural quest generation, branching campaign, crafting trees, housing, or extensive progression.
- Ten production-complete, player-selectable dominions if doing so would reduce the polish of the core three.
- Cinematic dialogue systems or extensive voice acting.
- Endless enemy variants and a large equipment inventory.
- Monetization, accounts, servers, paid APIs, or any feature that makes a free browser submission dependent on an external paid service.

The full ten-dominion plan remains canonical for future development. The jam slice will not misrepresent unimplemented powers as finished content.

---

## 3. Design pillars

### Pillar A — Ten flames, ten ways to play

Each dominion has a distinct silhouette, sound, movement grammar, hit response, battlefield role, and exploration utility. If changing a flame's color is the only difference, that flame has failed design review.

### Pillar B — The torch is a weapon, not a wand skin

Every torch supports physical strikes, timing, reach, momentum, and a close-range identity. Its spellcasting should feel like an extension of the torch's material, motion, and flame—not a detached list of generic projectiles.

### Pillar C — Mastery comes from combinations

Combat rewards setup, positioning, timing, and reading the environment. The strongest moments emerge from linking dominion properties rather than selecting the biggest damage number.

### Pillar D — Identity is interpreted, not assigned permanently

The three questions produce meaningful starting offers but do not diagnose, stereotype, or lock a player into a personality. Every starting choice must be viable. Discovery can expand the player's identity beyond the initial result.

### Pillar E — The world is worth entering even between fights

The art direction, landmarks, ambient creatures, ruins, soundscape, secrets, and environmental storytelling create a place to explore rather than a series of combat rooms.

### Pillar F — AI production must result in authored assets

Generations are raw candidates. The approved game contains visually consistent, technically cleaned, deliberately composed, engine-integrated assets—not uncurated model output or placeholder geometry.

---

## 4. Audience, platform, and camera

### Intended audience

Players who enjoy stylized fantasy action, expressive elemental combat, character build identity, anime-scale enemy reveals, exploration, collectible weapons, and experimentation. The tone can be intense without relying on graphic gore.

### Target platform

A free, no-download desktop browser game for AI Browser Game Jam 5. The export must be tested on the current desktop browsers available to the team. Keyboard/mouse are the baseline. Touch support is a stretch objective only if it can be implemented and tested without risking desktop quality.

### Recommended camera / presentation

**Provisional recommendation: stylized 2.5D, three-quarter top-down action-adventure presentation.** The camera should keep the player, torch arcs, enemies, hazards, and status effects readable while showing enough layered scenery to create depth. World navigation should be continuous within the slice region; the game can use connected sub-areas hidden by natural transitions rather than pretending the whole campaign is seamless.

This camera is not yet locked. Before production art is generated at scale, a one-screen benchmark must compare (a) three-quarter 2D/2.5D action view and (b) side-on cinematic action view. The winning approach is the one that best combines legible combat, consistent AI-generated character animation, convincing environment depth, and a feasible browser pipeline. No mass content generation until that proof is approved.

### Visual target

Original **mythic dark fantasy with anime-scale emotional readability and painterly cinematic environment art**. Saturated flame colors are the visual signatures against restrained, atmospheric environments. The result should feel premium and art-directed, not like generic asset-store fantasy, flat mobile-game iconography, pixel-art by default, or an unedited image-generation collage.

---

## 5. World and narrative foundation

### World principle

Flame is a force of identity and transformation. Different fires are not simply chemical or elemental variants: cultures, creatures, and factions interpret them differently. Torches act as vessels and disciplined interfaces for these powers; mastery is learned through use, not merely inherited.

### Slice region (working name: The Cinderwild)

A once-inhabited borderland built around a ruined sanctuary and an ancient flame conduit. The region contains:

1. **The Wayfarer's Ember** — a quiet arrival space where the player completes the identity ritual and learns movement and torch handling.
2. **The Ashen Verge** — an open traversal path with visual landmarks, abandoned structures, low-risk creatures, and the first environmental interaction.
3. **The Scorched Crossing** — the first real combat space; enemies teach spacing, attack cues, and use of the selected dominion.
4. **The Veilwood** — a visually distinct, haze-covered detour with a secret, a discoverable lore object, and a dominion interaction that rewards curiosity.
5. **The Fallen Sanctuary** — the narrative destination where the player encounters the black-flame corruption and evidence of flame consumption.
6. **The Hollow Crucible** — a contained climax arena where a member of the secret order reveals a partial transformation.

These are beats within one compact region, not six separate large levels. Their final boundaries depend on the proven camera, scene size, and content budget.

### Story arc for the slice

**Opening:** The player arrives in the Cinderwild. Three questions are presented through an atmospheric ritual rather than a conventional class screen. The player's choices determine the three torches they are offered. The chosen torch responds to the player in a distinctive visual and audio moment.

**Discovery:** The region contains ordinary traces of fire use: scorched marks, altered vegetation, dormant mechanisms, unusual creature behavior, and ruins that preserve competing interpretations of the dominions.

**Escalation:** Enemy rogues wield torches in disciplined but recognizable ways. One encounter shows an unnatural black flame that persists after normal attacks and damages the environment in an unusual fashion.

**Counterpoint:** The player encounters a surviving guardian or echo associated with white Spiritfire. This demonstrates cleansing and restoration and establishes that not every flame interaction is about damage. It also gives the story a visual counterpoint to corruption.

**Reveal:** At the Fallen Sanctuary, an elite rogue consumes or absorbs a flame rather than merely stealing the torch. Their body transforms; the consumed dominion appears in distorted, bodily form. The attack grammar becomes unfamiliar, despite being partly recognizable from the player's own flame system.

**Ending:** The player defeats or escapes the transformed enemy and recovers evidence that the technique is deliberate, organized, and being used by a hidden order. The slice ends with a concrete next mystery, not a generic “to be continued” screen.

### Narrative guardrails

- Keep dialogue sparse, specific, and supported by environment, animation, and sound.
- Do not explain the secret order completely in the slice; establish a powerful question and a credible threat.
- Create original insignia, faction names, silhouettes, rituals, and lore. The secretive elite-order inspiration must not reproduce recognizable Naruto/Akatsuki designs, names, symbols, costume layouts, or proprietary techniques.
- The morality of consuming flames should remain a genuine world question. Spiritfire can heal and cleanse, but it should not automatically make its wielder morally perfect.

---

## 6. The ten flame dominions (full-game concept)

All names below are working names. Each dominion must be evaluated for distinct verbs, counters, animation language, audio identity, traversal affordances, and interactions before it becomes a finished playable system.

| Flame / working name | Core identity | Main combat verbs | World / system role |
|---|---|---|---|
| **Orange — Hearthfire** | Adaptable, foundational flame | Sweep, ignite, spread embers, detonate combustible setups | Starts chain reactions; practical interactions; reliable baseline |
| **Blue — Jetfire** | Pressure, momentum, precision | Focused jet, dash/propel, pierce, launch, aerial follow-up | Mobility, propulsion, pressure-sensitive mechanisms |
| **Red — Blazefire** | Escalation, overwhelming force | Build heat, heavy strike, eruption, overrun guard | High risk/reward; aggressive encounters; heat management |
| **Clear — Frostfire** | Heat removal and arrest | Steal warmth, freeze, suspend, crystallize | Freeze flows, preserve/disable mechanisms, shape surfaces |
| **Black — Abyssfire** | Persistent consuming corruption | Cling, devour, spread through afflicted targets, deny ordinary extinguishing | Central forbidden threat; special counter interactions |
| **White — Spiritfire** | Cleansing, restoration, spiritual authority | Heal, purify, interrupt, dispel Abyssfire, pacify under conditions | Healing and nonlethal resolution; neutralize corrupted states |
| **Purple — Haze Fire** | Obscurity, zones, manipulation | Release burning smoke, obscure, linger, redirect cloud | Area denial, ambush, cover, environmental propagation |
| **Pink — Allurefire** | Fascination and emotional influence | Mark, distract, draw focus, disrupt immediate intent | Tactical control; must respect player agency and readable resistances |
| **Green — Emeraldfire** | Superheated constructs and ricochets | Cast emerald shards, ricochet, lodge, form temporary structures | Geometry-based combos, traversal anchors, multi-target setups |
| **Yellow — Stormfire** | Electrical discharge and chain reactions | Arc, overload, chain between marked targets, energize surfaces | Conductive puzzles and multi-target combat setups |

### Required design packet for every finished dominion

1. A one-sentence fantasy and a clear combat role.
2. Physical torch silhouette and close-up design.
3. Flame shape language, palette, material response, and sound identity.
4. Basic attack chain, heavy/charged attack, signature ability, movement/defense interaction, and cooldown/resource rules.
5. At least one world interaction outside combat.
6. Strengths, weaknesses, counters, enemy readability, and accessibility/readability variants.
7. Combo matrix entries with other dominions and defined limits to avoid runaway effects.
8. Character animation, VFX, impact frames, hit reaction, sound, UI icon, and in-game capture reference.
9. Source image, prompt/workflow, model/checkpoint/version, seed when applicable, edits, license/terms review, and acceptance status.

### Jam-slice dominion selection

Provisional playable set: Hearthfire, Jetfire, and Haze Fire. The trio covers reliable area ignition, movement/precision, and persistent battlefield control. The slice also showcases Spiritfire as a meaningful restorative/counterforce and Abyssfire as a forbidden threat. The other dominions are fully described in this document as future-game pillars, but are not to be represented as fully implemented in the jam build.

---

## 7. The identity ritual and starting torches

### Player-facing experience

After character appearance is set, the player answers three questions framed around self-perception, response to adversity, and desired legacy. They are not presented as a personality test with right answers. The scene should feel like an ancient rite that listens to the player, with each answer reflected in the environment's light, sound, or markings.

### Example question dimensions

- **Self-perception:** “When people misunderstand you, what do they fail to see?”
- **Adversity:** “When everything begins to fall apart, what part of yourself do you refuse to abandon?”
- **Legacy:** “If you could be remembered for only one thing, what would you want it to be?”

These are placeholder wording pending a dedicated writing pass. Answer options should be emotionally nuanced and avoid simplistic good/evil sorting.

### Selection logic

- Every answer contributes weighted affinity values to flame identities.
- The game combines the three answers rather than mapping a single answer directly to a class.
- The system generates three available starting torches: a strongest-affinity option, a complementary option, and a controlled surprise option. Final algorithm and weights are a tuning decision, not a lore claim.
- In the jam slice, only the three production-ready starting dominions may appear as selectable options; the full release can expand the affinity model to all ten after each dominion is implemented and tested.
- Each option explains its playstyle in plain language without assigning a fixed moral label.
- Player can inspect all three before choosing. Choice is reversible before the ritual is completed; no reroll farming or misleading hidden penalty.
- The chosen torch must be viable to finish the slice. No answer combination may produce a deliberately weak or “wrong” build.

### Data-driven implementation contract

Question text, answer options, affinity weights, torch eligibility, descriptions, and localization keys belong in validated data files, not scattered hard-coded conditionals. A scoring test suite must cover ties, unusual answer combinations, determinism, all three choices appearing, and the guarantee that every valid player receives three distinct available options.

---

## 8. Core gameplay loop

1. **Read the place:** notice a landmark, enemy tell, altered environment, sound cue, or secret path.
2. **Explore:** move, dodge, jump/step if required by the chosen camera, inspect, climb/route around obstacles, and interact with world objects.
3. **Engage:** start with a physical torch strike or dominion cast; manage spacing, enemy telegraphs, and hazard geometry.
4. **Compose:** apply or exploit a status/field, then link it to another action or environmental condition.
5. **Resolve:** defeat, cleanse, evade, or pacify an encounter where the design supports it.
6. **Discover:** collect a torch relic, lore fragment, upgrade, shortcut, or evidence of the flame-eating order.
7. **Return changed:** take a new ability or understanding into the next encounter, then reach the sanctuary climax.

### Player verbs

Move; face/aim; quick-strike; heavy-strike; guard/parry or dodge (choose one core defensive model after combat prototype); cast signature ability; interact; inspect; collect; switch between owned torches only if the slice design can support it without UI complexity; pause; restart.

### Session pacing target

- 0–2 min: identity ritual and weapon selection.
- 2–5 min: safe space and first meaningful ability.
- 5–9 min: first combat and one environmental combo.
- 9–13 min: exploration detour, creature encounter, and lore discovery.
- 13–17 min: rogue ambush and a Spiritfire/Abyssfire story beat.
- 17–20 min: flame-eater transformation, escape/defeat, ending and replay affordance.

Pacing is adjustable after playtests; forced time gates must not prevent competent players from continuing.

---

## 9. Combat design

### Physical torch combat

A torch is a close-range weapon with weight, inertia, a readable arc, and contact feedback. The player should feel that the torch has mass and a hot, living head—not like a generic wand attached to an avatar.

Proposed moveset for the slice:

- **Quick chain:** a fast multi-hit sequence with a clear final strike.
- **Committed strike:** slower, higher impact; creates a larger opening but is punishable if mistimed.
- **Defensive action:** choose either a dodge with clear invulnerability rules or a short guard/parry window. Do not implement multiple defensive systems before one feels great.
- **Dominion cast:** a signature power connected to the currently held torch.
- **Reactive follow-up:** a situational attack/interaction unlocked by the right status or environmental setup.

### Slice abilities (candidate set)

**Hearthfire**
- Quick chain: broad, ember-shedding strikes.
- Charged strike: a heavy hit that ignites volatile material or consumes an existing burn mark.
- Signature: short-range fan/burst of flame that rewards close positioning.

**Jetfire**
- Quick chain: compact, precise torch cuts.
- Charged strike: focused jet that pierces a line or launches a vulnerable target.
- Signature: directional burst used for combat repositioning and selected traversal gaps. Avoid uncontrolled flight that undermines level design.

**Haze Fire**
- Quick chain: smoke-edged strikes with slightly different reach/tempo, not merely a purple recolor.
- Charged strike: releases a short-lived haze mark in a chosen area.
- Signature: a persistent smoke cloud that blocks lines of sight, applies a readable burn/disorientation state, and can be ignited or charged by other world effects.

Ability numbers, input bindings, hitboxes, cooldowns, damage values, and frame windows must be tuned in playtests rather than fixed in the GDD.

### Combo grammar

Use a limited, composable set of interaction properties, for example: **Ignited, Pressurized, Haze-marked, Chilled, Spirit-cleansed, Abyss-corrupted, Charged, Crystallized**. The slice implements only the properties needed for its actual abilities.

Candidate demonstrations:

1. **Haze → Hearthfire:** place a smoke field, then ignite its edge for a broad flame-front with a visible direction and safe counterplay.
2. **Hearthfire → Jetfire:** ignite volatile material, then use Jetfire to propel the burst or drive the target through it.
3. **Haze → enemy telegraph:** obscure the player's position to interrupt targeting or create a flank, with clear limits against elites.
4. **Spiritfire vs Abyssfire:** cleansing removes a specific persistent corruption state and visually changes the target/environment.

These interactions need stable rules. Avoid uncontrolled combinations that chain forever or make bosses trivial. Each combo should have a readable setup, an understandable payoff, a counter or limitation, and a strong visual/audio beat.

### Enemy behavior and fairness

Enemies telegraph intent with animation, posture, sound, and VFX—not color alone. Every damaging action needs readable start-up, active, and recovery states. Hit reactions must preserve readability; excessive hit-flash and particles may not cover attack cues. Bosses should resist some crowd-control effects while still reacting meaningfully to player tactics.

---

## 10. Enemy and creature roster for the slice

| Role | Purpose | Readable behavior | Art/animation requirement |
|---|---|---|---|
| Cinder Grazer (working name) | Non-hostile/territorial creature and world texture | Grazes, reacts to flame proximity, flees or charges when threatened | Distinct silhouette; idle, turn, locomotion, startle, and reaction |
| Ash Rogue | Basic enemy | Approaches, commits to a telegraphed melee attack, recovers | Walk/approach, attack anticipation, attack, miss/recovery, hit, defeat |
| Veil Stalker | Flanker/ambush enemy | Uses cover or Haze-like obscurity, repositions, punishes stationary play | Crouched silhouette, approach/vanish/reappear or equivalent clear, fair motion |
| Torch Adept | Ranged pressure enemy | Telegraphs a projectile/line attack and tries to keep distance | Cast tell, release, recoil/recovery, hit and defeat |
| Flame-Eater Envoy | Unique elite/boss and story reveal | Consumes a flame, changes shape/attack grammar, mixes a recognizable dominion with a monster behavior | Strong pre/post-transformation designs, a transformation sequence, multiple phase cues, attacks, damage reactions, defeat/escape ending |

Final enemy count may be cut if the art/animation or behavior quality gates fail. One great enemy with distinctive animation is better than six visually interchangeable enemies.

### Flame-eater transformation design

The forbidden technique consumes flame essence and forces it into the eater's body. The transformation must visibly change silhouette, movement, sound, attack patterns, and the surrounding environment. It should not be a simple shader tint or an ordinary enemy with larger health.

For the slice, show one transformation based on a dominion the player has encountered. The creature can have recognizable traces of that fire, but the bodily expression is distorted and unsettling. Leave hints that incompatible flames produce different or unstable monster forms in the full game.

---

## 11. World interaction and exploration

Every featured dominion should have at least one purpose beyond dealing damage, but the slice needs only a few carefully authored interactions.

- Combustible growth or ancient fuel responds to Hearthfire.
- A short gap, wind-driven mechanism, or directional conduit responds to Jetfire.
- A concealed passage, sightline puzzle, or environmental marker responds to Haze Fire.
- A corrupted remnant or wounded guardian gives Spiritfire narrative purpose.
- Abyssfire leaves persistent marks that ordinary fire cannot remove.

World objects should signal affordances through art language and animation, not UI labels alone. Do not make every obstacle require a specific power if the player only possesses one torch; alternate routes or a universally available interaction must exist unless the challenge explicitly requires a later discovery.

---

## 12. Art direction bible (pre-production lock)

### Art direction statement

**Mythic, painterly dark fantasy with high-contrast anime combat readability, bespoke torch silhouettes, atmospheric depth, and flame colors treated as living material—not flat color filters.** Environments are ancient, weathered, and restrained; dominant flames are brilliant, volumetric, and visually specific. The protagonist and enemies have clear silhouettes and designed costumes; no generic hooded figures as a shortcut for every faction.

### Palette and value hierarchy

- Environment base: charcoal stone, muted earth, blue-grey haze, ancient bronze, weathered ivory, desaturated foliage.
- Warm navigation accents: distant orange embers and hearth lights.
- Dominions: each flame receives a dedicated hue range, brightness range, edge behavior, particle language, and sound palette.
- Enemy tells: contrast against the environment and remain legible for color-vision differences through shape, motion, and iconography in addition to hue.
- UI: restrained dark surfaces, carefully tuned luminous accents, legible type, no busy borders around every element.

### Shape and material language

- Torches: individually designed heads, shafts, materials, wear, grip, and ornament that express the dominion.
- Hearthfire: broad tapering tongues, sparks and ember trails.
- Jetfire: narrow, forceful streams with pressure ripples and directional streaking.
- Haze Fire: layered translucent smoke masses with bright hot cores and drifting edge wisps.
- Spiritfire: soft luminous filaments, cleansing rings, and fine drifting motes.
- Abyssfire: negative-light impression, swallowed highlights, persistent black cores and controlled peripheral distortion.
- Ruins: large, readable forms and silhouette landmarks; avoid noise-heavy surfaces that hide combat cues.

### Animation language

- Anticipation before high damage; strong follow-through on heavy strikes.
- Flame trails must follow motion and dissipate with intentional timing.
- Character silhouette and weapon silhouette remain readable at actual gameplay scale.
- Animation needs deliberate foot/ground anchors, consistent proportions, stable costume details, and coherent transitions.
- Enemy telegraphs remain visible even when overlapping VFX.

### Prohibited shortcuts

- Procedural geometric stand-ins for visible characters, monsters, trees, buildings, weapons, or key props.
- Unreviewed random generations placed directly into the build.
- Mixing photorealistic, pixel-art, flat vector, and painterly assets without an intentional art-direction reason.
- Using glow, bloom, screen shake, or particle count to hide weak animation or poor composition.
- Reusing the same generated enemy/prop image with color shifts as a substitute for distinct designs.
- Describing an AI output as “AAA” or “masterpiece” without in-game evidence and human review.

---

## 13. AI asset and animation production pipeline

This is a core feature of the project. Art is produced through a controlled AI-assisted workflow, not through one prompt per asset followed by direct import.

### Stage 0 — Capability and license audit

- Run the studio's current diagnostics and inspect the installed ComfyUI configuration, checkpoints, relevant nodes, VRAM, Godot version, export templates, and Blender/RIFE availability.
- Create a model/workflow register: actual model/version, source URL, license/usage terms, local path (not published secrets), VRAM behavior, output dimensions, measured latency, prompt/conditioning inputs, and known failure modes.
- Do not assume all generated content is commercially safe because the generator is local or the studio code is MIT-licensed. Review applicable model/checkpoint, font, audio, and source-material terms.
- Queue GPU generation sequentially when memory headroom is tight. Record actual behavior on the current machine; prior measurements are not guarantees.

### Stage 1 — Art benchmark before mass production

Produce a compact, cross-discipline proof set:

1. Hero character concept and three-quarter turn/feature sheet.
2. One enemy concept with readable silhouette.
3. One torch hero prop, plus one alternate torch design.
4. One full environment key art frame and an in-game-scale composition test.
5. One UI mockup with real typography, icons, hierarchy, and background treatment.
6. Three flame effect tests (Hearthfire, Jetfire, Haze Fire) on both light and dark backgrounds.
7. One short animation tested at gameplay scale.

Evaluate the set together. Do not approve one beautiful standalone portrait if it clashes with the environment and game camera.

### Stage 2 — Style bible and reference pack

For every major visual category, capture approved references and explicit constraints for composition, camera, perspective, silhouette, palette, costume/prop details, material response, lighting, scale, and negative traits. Store a human-readable design sheet and the source/reference identifiers. Do not use copyrighted character images as a direct blueprint.

### Stage 3 — Character identity lock

- Generate candidate hero designs, review them, select one, then derive front/side/back and expression/detail references where feasible.
- Maintain an approved identity sheet for proportions, hair, costume layers, torch grip, distinctive materials, and color accents.
- Use image/reference conditioning available in the verified local workflow. A fixed seed alone is not identity preservation.
- Test multiple frames together as a contact sheet; reject costume drift, changing hands/weapon, proportion changes, ambiguous silhouettes, or incompatible lighting.
- For the protagonist, choose between a controlled 2D cut-out/rig workflow and generated pose/frame sequences only after the animation benchmark. Use whichever gives better in-engine identity and motion quality. Do not assume interpolation can fix inconsistent anatomy or missing poses.

### Stage 4 — Environment generation and composition

- Generate environment key art in the locked camera and palette.
- Break compositions into playable foreground, traversal/collision surfaces, set dressing, background planes, landmarks, and optional parallax layers where the camera benefits from it.
- Use image editing and compositing to clean seams, remove unwanted text/artifacts, align perspective, and match lighting.
- Generate multiple compatible details from the same approved environment reference set. Avoid assembling the level from unrelated images.
- Create explicit collision/traversal maps separately from the rendered artwork; never let collision geometry replace visible art.
- Test seams, occlusion, player readability, and scale in engine with a character present.

### Stage 5 — Props, torches, creatures, and enemies

- Generate props against approved scale references and with consistent light direction.
- Hero torches require a distinct silhouette, usable hand/grip geometry, side/three-quarter views as required, and a readable flame socket.
- Enemy and creature packs are generated by role, not just by color. Each required enemy has an identity sheet, proportion guide, attack pose, hit pose, and locomotion sequence.
- Use background removal, trimming, color correction, compositing, and atlas tools only as conservative cleanup steps. Inspect halos, lost edges, cut-off features, and transparency artifacts.

### Stage 6 — Animation

- Define animation clips before generating frames: purpose, root/anchor, frame count or duration, expected silhouette, contact pose, timing curve, and state transitions.
- Generate key poses or a complete candidate sequence using the best measured locally available method. Maintain consistent camera, character references, scale, lighting and transparent/solid-background plan.
- For 2D cut-out rigs, use AI-generated source art as the base and have an intentional rigging/deformation pass; avoid rubbery joint motion and visibly disconnected limbs.
- If using image-to-video or frame interpolation, treat output as candidate source material. Extract frames, inspect flicker and identity drift, trim/clean alpha, and rebuild loops only after playback review.
- Use RIFE only where it measurably improves motion; it is not a semantic animation generator and must not be relied on to repair broken motion.
- Review each animation at real game scale and at intended playback speed, in isolation and during actual combat. GIF existence and automated metrics do not certify quality.

### Stage 7 — Fire VFX and shaders

Use a hybrid pipeline: AI-generated flame/smoke textures, flipbook candidates, masks, and concept frames for authored look; shaders, particles, animation curves, and gameplay code for timing, direction, interaction, visibility, and performance. This is not “procedural art” replacing the art—it's an implementation layer that makes the designed visual material react correctly in play.

Each effect needs:
- Approved still/frame references and silhouette.
- Start-up, active, impact, and dissipation timing.
- Color/shape distinction from other flames.
- Hit feedback plus performance-safe overdraw.
- Clear enemy telegraph and hit-confirm variants.
- Reduced-intensity/accessibility options for screen shake and excessive flashes.

### Stage 8 — UI and iconography

- Generate/reference UI concepts only after the art bible is locked.
- Build a custom coherent UI skin with reviewed textures, iconography and typography; use appropriately licensed fonts.
- Icons must remain recognizable at their actual display size and use shape/symbol distinction as well as color.
- All text is proofread; generated UI text is not imported without manual verification.

### Stage 9 — Audio and music

- Create an audio identity sheet for each playable dominion, each enemy role, the flame-eater transformation, and environmental zones.
- Prefer original AI-assisted sound/music generated with tools whose terms are reviewed. Record prompt, tool/version, source files, edits, loops and loudness checks.
- Sound communicates weight: cloth and grip movement, torch swing, ignition, impact material, ability release, hit reactions, ambient creatures, distance, and boss transformation.
- Mix for simultaneous effects and browser playback; do not let every ability peak at full volume.

### Stage 10 — Integration, provenance, and approval

Each asset moves through explicit states: **candidate → technically checked → art-directed/approved → integrated → in-engine checked → final approved**. Preserve original source files and document transformations. Every asset used in the build must have provenance and a recorded rights-review state.

### Quality gate for every visible asset

Score 0–4 against: (1) design fit, (2) identity/style consistency, (3) technical integrity, (4) in-game readability, and (5) animation/material quality where applicable. Critical hero assets, player character, boss, central torch, signature effects and main key art require a human rating of at least 3 in every applicable category. No critical defect can be averaged away by a high overall score.

---

## 14. Technical architecture and content rules

### Provisional engine

Godot 4, using a browser-compatible renderer and only features supported by the chosen web export path. Confirm the installed Godot version, web export templates, renderer constraints, and browser behavior before committing to engine-specific visual features.

### Architecture principles

- Separate combat state, character state, dominion definitions, status effects, enemy behavior, world interactions, UI, and content data.
- Prefer small well-defined systems over a monolithic game controller.
- No hidden global mutable state. Use explicit references/services where needed and scoped scene ownership.
- Store question logic, ability parameters, enemy definitions, interaction rules, asset manifest, and audio mappings in validated data resources where practical.
- Avoid hard-coded content scattered through scripts; centralize tunable values and IDs in resource/configuration data.
- Maintain a stable input abstraction for mouse/keyboard and possible touch controls.
- Manage VFX/animation counts and asset sizes for browser memory and performance.
- Keep network services and paid endpoints optional; the game must play offline after the web build loads, except for the itch host itself.

### Performance targets (initial; must be measured)

- Target smooth 60 FPS on a reasonably capable modern desktop browser at the selected resolution; define a reduced-effects path if needed.
- Avoid runtime loading of large, unnecessary source/concept images.
- Prefer optimized engine-ready atlases/textures, appropriate compression, audio formats, and bounded effects lifetime.
- Record initial and final export size, load time, memory/performance observations, and test-browser details. A target without a measurement is not a verified result.

### Save/restart

For the jam slice, store only what improves repeatability: selected answers/torch and a limited progress flag or best run if reliable persistence is available. The game must always provide a clear new-run/restart path; no account or cloud backend is required.

---

## 15. Accessibility, UX, and readability

- Teach movement, attack, special ability, interact, and pause through brief contextual prompts.
- Do not require the player to infer controls from an image alone.
- Make enemy telegraphs readable through shape and timing, not color alone.
- Provide remappable or clearly documented controls if feasible.
- Avoid rapid full-screen flashes; make screen shake and high-intensity VFX reducible.
- Maintain readable text contrast and configurable text scale if achievable in the jam schedule.
- Let the player review all three starting torch descriptions before choosing.
- Explain unusual status effects through first-use microcopy rather than a large mandatory manual.
- Ensure a player cannot become permanently trapped or lose the only required progress path because they chose one of the offered starting torches.

---

## 16. Audio and presentation

### Audio pillars

- **Torch handling:** grip, cloth, shaft movement, heated material.
- **Combat:** distinct physical impacts, clean whoosh/transients, hit confirmation, recovery, enemy telegraphs.
- **Dominion identities:** Jetfire is pressured and directional; Hearthfire is textured with crackle and ember snap; Haze Fire is layered, low-mid, and spatially diffuse; Spiritfire is clear and resolving; Abyssfire is unsettling and subtractive rather than merely louder.
- **World:** wind through ruined arches, ash movement, distant creatures, resonant old mechanisms, quiet pockets before major encounters.
- **Transformation:** a unique event with a clear rise, consumption moment, bodily change, and new combat state.

Music should support place and rhythm without drowning out feedback. Use a restrained exploration theme, a combat layer or cue, and a distinctive transformation cue rather than a sprawling soundtrack.

---

## 17. Risks and mitigations

| Risk | Why it matters | Mitigation / trigger |
|---|---|---|
| Character identity drifts between AI-generated frames | Breaks immersion immediately | Run animation proof before mass production; lock identity references; choose a cut-out/rig workflow if frame consistency fails |
| The world looks like unrelated AI images | Destroys art direction | Approve a cross-discipline proof set; share reference pack; fix camera/light/palette; reject mismatches |
| Too many dominions dilute polish | More colors create more art, combat and QA states | Limit the slice to three fully playable dominions; preserve the other seven in the GDD/roadmap |
| Browser export/render limitations | Beautiful editor scenes can fail in browser | Audit renderer and export pipeline on Day 1–2; build and run a minimal browser target early |
| Generations consume the schedule | Large candidate pools do not equal finished assets | Establish a minimum approved set, review immediately, stop generating once coverage is met |
| VFX hide gameplay or tank performance | Spectacle can reduce readability and frame rate | Use per-effect budgets, effect reduction, real-browser profiling, and enemy cue tests |
| AI model or asset rights unclear | Submission and later distribution risk | Maintain per-source provenance and explicit human rights review; replace uncertain sources |
| Scope expands toward a full open world | Release becomes incomplete | Treat the slice route and ending as non-negotiable; cut extra areas, variants, and optional systems first |
| Final build differs from tested build | Invalidates evidence | Freeze, rebuild, checksum, cold launch the exact release package, keep final release reserve |

---

## 18. Production plan and dates

The jam page currently lists the submission cutoff as October 31, 2026 at 03:00 UTC (October 30 at 11:00 p.m. EDT). The schedule below targets an earlier submission and retains emergency time.

### Oct 17 — Contract and baseline

- Freeze this GDD's core fantasy, platform rules and scope boundaries.
- Audit the game-studio repo, local tools, checkpoints, export templates, licenses, and current test baseline.
- Select candidate engine/camera through a risk checklist.
- Identify existing assets/tool results, if any, and decide whether the submission clearly meets the jam's “majority new content” rule.

### Oct 18 — Visual proof and technical spike

- Create the art bible and a cross-discipline visual benchmark.
- Produce the first character, torch, flame, environment, UI and animation test assets.
- Test an actual browser export early, not at the end.
- Approve/reject the initial animation pipeline.

### Oct 19–20 — Combat proof

- Implement movement, aiming/facing, quick attack, selected defensive action, one dominion ability, hit response and one enemy.
- Integrate the approved hero/torch assets.
- Playtest the core interaction before expanding.

### Oct 21 — Vertical-slice gate

- Reach one complete playable combat loop inside the target camera and world style.
- Include a start state, objective, encounter, feedback, win/loss/recovery path, and restart.
- Gate: if visual consistency or combat feel fails, repair those foundations before producing more content.

### Oct 22–24 — Content production

- Complete the three playable dominions, enemy roles, main route, landmark art, key props, signature VFX, and audio identity.
- Add the opening ritual and initial discovery beats.
- Integrate and test asset batches as they pass review; never leave a large unintegrated asset queue.

### Oct 25–26 — Narrative and encounter completion

- Complete the Fallen Sanctuary sequence and flame-eater reveal.
- Add Spiritfire cleansing/corruption counterplay, secrets, reward, UI/tutorial, title and ending.
- Run structured combat and navigation playtests.

### Oct 27 — Content freeze

- Stop new features and nonessential assets.
- Fix critical art consistency, combat readability, input, recovery and browser issues.
- Create the release candidate and evidence capture checklist.

### Oct 28 — Verification

- Run scenario coverage, keyboard/mouse checks, browser cold launch, restart paths, performance review, asset provenance checks, and visual review at native gameplay scale.
- Record actual frame-rate observations, package size, defects, and supported browsers.

### Oct 29 — Release candidate and submission page

- Freeze the build candidate, assemble credits/tool workflow summary, inspect screenshots and trailer/GIF if time permits, and make the itch page clear about controls and playtime.
- Confirm the game is free and browser playable.

### Oct 30 — Reserve and submit

- Fix only release blockers, rebuild, verify the exact uploaded build, submit before the final hours, and retain the upload/build hash and test evidence.

### Release reserve rule

At least 20% of the sprint should remain for integration failures, quality fixes, browser validation, packaging and submission. Optional content is cut before the reserve is spent.

---

## 19. Quality gates and completion criteria

### Gate 1 — Concept and compliance

Pass only when the game brief, jam rules, originality/right-to-distribute review process, release target, non-goals and evidence plan are recorded.

### Gate 2 — Art/animation proof

Pass only when hero, torch, environment, enemy, UI, signature VFX and one meaningful animation appear coherent together in the actual target camera. An isolated concept image is not enough.

### Gate 3 — Combat proof

Pass only when a player can move, deliberately target or face the enemy, land torch attacks, read incoming attacks, use a dominion ability, observe a meaningful interaction, and recover/restart after a result.

### Gate 4 — Playable vertical slice

Pass only when the selected starting torch is playable from opening through the core route and ending without dead ends or missing content. All three starting options need complete basic combat viability.

### Gate 5 — Content freeze

All must-have assets are integrated and reviewed; optional additions stop unless they repair a release blocker.

### Gate 6 — Browser release candidate

Launch the exact build in a real target browser. Verify loading, input, sound, effects, collisions, all core scenarios, pause/restart, no permanent softlocks, and acceptable performance. Keep screenshots/video evidence.

### Gate 7 — Submission and audit

Verify the exact uploaded package, game page instructions, rights/credits statement, AI workflow credits if desired, provenance manifest, export checksum, known limitations, and unresolved defects.

### Must-pass playtest questions

- Can a first-time player understand the movement and combat within the first minute?
- Can a player tell when an enemy is about to attack and why they took damage?
- Do the three starting torches feel mechanically different—not just visually different?
- Does at least one combo produce a memorable “I figured that out” moment?
- Is the environment worth exploring when no enemy is present?
- Does the flame-eater transformation feel like a story event rather than a generic boss phase?
- Are the player character, torch, enemy, background and VFX visually consistent at actual play size?
- Can a player finish the slice and restart without guidance from the developer?

---

## 20. Evidence, asset inventory, and release audit

Keep the following within the project workspace/repository, excluding machine secrets, model weights, caches and oversized redundant exports:

- GDD, art bible, narrative beat sheet, camera proof and design decision log.
- Tool/model registry and license/rights-review states.
- Prompt/workflow records, seeds where applicable, source references, candidate/rejected contact sheets, edit history and checksums.
- Approved asset manifest with dimensions, intended use, file format, atlas membership, license/provenance state and in-engine approval.
- Animation clip manifest with timing, anchors, source frames, processing steps, diagnostic output and human playback decision.
- Combat scenario definitions and test results; actual browser launch evidence.
- Build/export logs, final package size and SHA-256, supported browser notes, known defects and release checklist.
- AI tool and workflow acknowledgement appropriate for the jam's rules and the applicable service/model terms.

Never commit secrets, provider tokens, `.env`, virtual environments, local databases, engine caches, or pretrained model weights. Keep the public repo focused on reusable source, documentation, approved game assets that may legally be redistributed, and reproducible instructions.

---

## 21. Open design decisions

These are intentionally unresolved and must be decided by small prototypes or collaborative review—not silently assumed:

1. **Final title and setting vocabulary.** The region/faction names in this document are placeholders.
2. **Camera winner.** Compare three-quarter 2.5D with side-on cinematic presentation using one playable benchmark.
3. **Player art/animation method.** Choose a 2D cut-out rig or generated frame workflow based on measured identity and motion quality.
4. **Defensive mechanic.** Dodge or guard/parry; select the one that produces better combat feel and clearer feedback under scope constraints.
5. **Starting-question wording and affinity weights.** Review for nuance, predictability, and viable outcomes.
6. **Exact dominion ability values and counters.** Tune through playtests rather than GDD guesswork.
7. **Final route length and enemy counts.** Constrain them by measured content production and performance.
8. **Music/audio generation route.** Select only after current tool availability and redistribution terms are checked.
9. **Final asset/model licenses.** Human review required before claiming legal clearance.
10. **Commercial distribution status.** The jam slice's license and content strategy must be reviewed separately from the studio repo's software license.

---

## 22. Initial decision recommendations

For the first production pass, use these defaults unless evidence argues otherwise:

- Three-quarter 2.5D browser action-adventure as the camera candidate, with a side-on benchmark kept small and time-boxed.
- Mythic dark fantasy with painterly environment art and anime-scale action readability.
- One compact, contiguous region with a complete opening, exploration route, boss reveal, ending, and restart.
- Three fully playable jam-slice dominions: Orange/Hearthfire, Blue/Jetfire, Purple/Haze Fire.
- White/Spiritfire as the restorative counterpoint; Black/Abyssfire as the forbidden threat.
- One high-quality flame-eater transformation rather than many lower-quality bosses.
- AI-generated/refined art, animation, audio and UI as the asset source; small programmatic runtime effects used only to animate and respond to authored art.
- Fully documented provenance and actual browser playtest before release claims.
- No mass generation until art direction and the end-to-end asset/animation proof are approved.

## 23. References

- AI Browser Game Jam 5 official overview, rules, theme, voting categories and current submission dates: https://itch.io/jam/ai-jam-5
- 11vatedTech AI Game Studio source repository: https://github.com/11vatedTech/11vatedTech_AI-GameStudio
- Studio's 14-day production profile: `docs/workflows/game-jam-14d.md`
- Studio's canonical agent instructions: `AGENTS.md`

---

**Review status:** GDD v0.1 establishes a recommended design baseline. It is not a claim that the game is implemented, visually approved, tested, commercially cleared, or release-ready. The next gate is to approve the creative direction and produce an actual visual/animation proof set before committing the production pipeline.
