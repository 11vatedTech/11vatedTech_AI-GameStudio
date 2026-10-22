# Torch: Dominions — Art Bible v0.1

**Status:** Direction proposal; visual approval pending Gate 0. No asset in this document is automatically approved for the game.

## 1. Visual thesis

Build an original mythic dark-fantasy world where restrained, beautifully composed environments make each supernatural fire feel vivid and meaningful. Use painterly environmental grandeur, readable anime-scale character acting, material-rich costume/props, and flame VFX with a strong graphic silhouette. The target is a coherent authored game—not photorealism, generic mobile fantasy, pixel-art by default, or uncurated image-generation collage.

**Working title:** *Torch: Dominions* (unlocked, subject to originality/name review).

**Player-facing promise:** different flames, different combat languages, a world whose mysteries are visible before they are explained.

## 2. Camera benchmark is a gate, not an assumption

Test two variants with the same hero, torch, rogue, and environment motif:

- **A — Elevated three-quarter 2.5D:** show body, torch silhouette, ground plane, cover, traversable routes, enemy tells, and layered environment depth. The camera keeps enough top-down information to make dodges and area effects readable.
- **B — Side-on cinematic:** prioritize pose silhouette, readable wind-ups, impact reactions and parallax. Validate vertical movement and combo spectacle in a horizontally framed encounter.

Score on a 1–5 scale: hero identity consistency; action readability; animation plausibility; VFX legibility; environmental scale; ability to integrate rich AI-generated backgrounds; browser performance; and production time. Keep the camera decision open until both are seen in a working engine scene. A beautiful still is not sufficient evidence.

## 3. Palette system

Environment palette is mostly controlled: cool slate, deep teal, weathered stone, mossy emerald, ash, and warm sunset accents. Dominant flame colors are reserved for gameplay signals, interactive world features, and focal story moments.

| Purpose | Working color | Hex | Usage |
|---|---|---:|---|
| Night / shadow base | Obsidian blue | `#101822` | Deep shadow, UI foundations |
| Stone / neutral | Ash slate | `#56616B` | Ruins, rock, inactive metal |
| Cool environment light | Glacier blue | `#9DC8D8` | Fog, distant atmosphere, frost hints |
| Hearthfire | Ember orange | `#FF8A26` | Burn state, reliable basic flame |
| Jetfire | Ion blue | `#48B9FF` | Directional thrust, precision |
| Blazefire | Furnace red | `#F04438` | Escalation, danger, overheat |
| Frostfire | Pale cyan-white | `#D9FAFF` | Steal warmth, freeze |
| Abyssfire | Near-black with violet rim | `#1A1024` + `#7C32C9` | Corruption; must remain visible against dark ground |
| Spiritfire | Pearl-white / soft silver | `#F4F3E9` | Cleansing, healing; do not bloom out all detail |
| Haze Fire | Amethyst | `#A65CFF` | Cloud, obscurity, zones |
| Allurefire | Rose-magenta | `#FF6FB8` | Mark/influence; never use color alone to indicate control |
| Emeraldfire | Faceted green | `#38D982` | Shards, constructs |
| Stormfire | Electric gold | `#FFD34F` | Electrical arcs and chain reaction |

Color alone must never be the sole indicator of damage, status, affinity, or interaction. Pair color with shape, animation, sound, outline, icon, and/or pattern.

## 4. Shape language by dominion

- Hearthfire: broad, rolling tongues and ember sprays; readable and grounded.
- Jetfire: narrow directional cone with a bright compressed core and trailing filaments.
- Blazefire: expanding crown, explosive radial bursts, heat shimmer.
- Frostfire: negative-space flame, crystalline edges, desaturated center, particles moving inward as heat is stolen.
- Abyssfire: negative silhouette that consumes local light, violet edge, unnerving slow adhesion. Must remain readable in dark environments.
- Spiritfire: stable vertical wisps, drifting motes, graceful cleansing rings, low-noise healing field.
- Haze Fire: volumetric/sprite cloud with rolling edges and readable density bands; do not make opaque full-screen fog.
- Allurefire: curved ribbons/petals and heartbeat-like pulses. Effects telegraph influence range and resistance.
- Emeraldfire: angular faceted shards with strong specular accents and readable trajectory.
- Stormfire: branching high-contrast arcs with short-lived afterimages and clear endpoints.

## 5. Character and costume design

The protagonist should be original and recognizable in silhouette without relying on a franchise-shaped cloak, headband, uniform, logo or face design. Direction: a practical wayfarer with layered travel garments, protective wraps, a single asymmetrical mantle or scarf, worn fasteners, material contrast (matte fabric, weathered leather, engraved metal, mineral/glass detail), and an intentionally designed torch harness. The body must remain readable at small screen scale. Avoid a completely black costume lost against night backgrounds.

Required identity reference sheet before animation:

1. Full-body front, three-quarter, side, and back views under neutral light.
2. Face/hood/hair/eye reference and expression row.
3. Costume materials and color chips.
4. Torso/shoulder/hand/boot construction and torch-hold positions.
5. Exact prop scale and grip contact points.
6. Clear no-change list: head/face, hair silhouette, outer garment, accent trim, body proportion, carried gear, torch handle, dominant palette.

Reference sheets are consistency anchors, not directly shipped sprite sheets. Generated views need manual cross-view inspection before they become production references.

## 6. Torch prop design

A torch is a hero weapon. Its silhouette must be recognizable when small and when held. Each has a grip, guard/hand-stop, vessel/head, connection details, and an intentional material story. Avoid a generic stick with a colored glow. The flame may be generated as a separate transparent effect layer so it can be animated, changed by gameplay state, and remain visually legible.

For the three provisional slice torches:

- **Hearthfire:** dark forged haft, warm copper/bronze collars, charred core and asymmetrical ember cage.
- **Jetfire:** narrow, engineered vent channels and a directional nozzle-like head; use original ornamental geometry, not a modern firearm silhouette.
- **Haze Fire:** a perforated cage/lantern head built to suggest smoke release, violet-glass or dark ceramic elements and a clear emitter opening.

One shared family resemblance (handle language, maker marks, metalwork grammar) should connect the torches; each dominion changes the head geometry and flame behavior.

## 7. Environments and composition

The jam region, provisionally **The Cinderwild**, should read as one continuous place composed of distinct beats: Wayfarer's Ember arrival overlook, Ashen Verge, Scorched Crossing, Veilwood detour, Fallen Sanctuary, Hollow Crucible climax.

Composition requirements:

- One dominant distant landmark visible from at least two routes.
- A three-layer depth plan (foreground framing, playable midground, atmospheric background) appropriate to the selected camera.
- Strong route contrast: a clear safe path and at least one optional secret path.
- Controlled focal points: a small number of high-contrast objects per screen, especially during combat.
- Repeated architectural language and material palette so separate generated plates look like one world.
- Landmarks, doors, sanctuary architecture and relics must be original; no logo/text baked into the environment image.

If using painted background plates, define consistent horizon, scale, parallax split, lighting direction and collision geometry. If using 2.5D props, generated concept art can guide modeled/textured assets, but visible in-game props still need coherent real-time integration.

## 8. Enemy and creature silhouette

- Rogue torchbearers: disciplined stance, recognizable weapon/torch shape, readable wind-up, contrasting cloth/armor from protagonist.
- Wild creatures: distinctive locomotion and body silhouette before detailed texture. At least one neutral/curious creature sells world life without requiring combat.
- Flame-Eater: humanoid silhouette becomes anatomically and materially wrong as consumed fire emerges through cracks, mouth/chest/limbs. Transformation must feel like possession of a dominion rather than wearing elemental armor.
- Slice boss: show a readable pre-transform stance, clear transformation beat, then a new locomotion/attack grammar. Avoid only scaling up an ordinary enemy or adding a glowing texture.

## 9. Lighting, VFX and post-processing

- The environment is allowed rich painterly detail; effects must protect action readability.
- Avoid permanent full-screen bloom, saturated fog, opaque particles, giant white flashes, or always-on outlines.
- Bloom should emphasize hot cores, not erase flame shape or character anatomy.
- Every combat effect needs a start, active, linger and end/dissolve state, with a consistent origin point and a timing budget.
- Hit sparks should be brief; important lingering states must have silhouette/animation changes in addition to color.
- Player and enemies use separate VFX value/shape conventions, not necessarily separate colors alone.
- Black fire gets a visible edge against dark areas; white fire retains detail at peak brightness.
- Stress-test effects over bright sky, mid-tone stone, dark woods and overlapping enemy silhouettes.

## 10. UI and iconography

UI should feel like an artifact-navigation system, not a stock RPG HUD. Use dark translucent material, carefully spaced labels, a small controlled set of ornaments, crisp typography, and custom flame icons. The torch/ability row must be readable at browser-native scale. Text must be authored and rendered by the engine/UI layout; never ship AI-generated lettering embedded in images. Include keyboard focus, high-contrast mode and non-color-only status cues.

## 11. Image-generation rules

### Generate in this order
1. Neutral protagonist identity anchor.
2. Chosen camera benchmark scene, with protagonist, torch and one enemy.
3. Hero costume/torch variations and cross-view checks.
4. Environment keyframe/painted plate and prop design language.
5. Dominion flame shape studies individually (one dominion per task).
6. Enemy/creature silhouettes, then approved design views.
7. Key animation poses and per-clip sequence tests.
8. UI icons and audio identity after gameplay grammar is established.

### Prompt requirements
Every production prompt declares subject, camera/view, composition, pose/action, light direction, palette, material, negative constraints, and which details must match reference images. Generate one asset or a controlled comparison per request. Do not ask one generation to solve a whole art direction bible, a sprite sheet, UI typography, and ten unrelated fires simultaneously.

### Universal negative constraints
No letters, logos, watermark, interface text, multiple panels, before/after collage, fused fingers, extra limbs, duplicate props, cropped feet/hands, unclear hand-to-torch contact, inconsistent costume, unrelated weapon, unexpected fire colors, franchise insignia, or photorealistic skin on a stylized body. Adapt the anatomy constraints to the chosen style and platform.

## 12. Visual quality gate

A candidate passes only when:

- It respects the current identity/style references.
- The silhouette and focal point remain readable at target scale.
- Anatomy, hands, equipment contact points and prop geometry are plausible.
- No unwanted text, watermark, logo or unrelated object is present.
- Color/value contrast distinguishes the player, threat, interaction and environment.
- Cropping, transparency, padding and frame dimensions fit the engine contract.
- It has documented provenance and a cleared usage decision.
- It is integrated and inspected in a running scene; source-image beauty alone is not an integration pass.
