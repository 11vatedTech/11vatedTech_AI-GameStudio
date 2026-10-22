---
name: combat-vfx-audio
description: Create signature effects and sound that communicate hit, force, flame behavior and tactical state.
---

# Combat VFX and Audio Production

Summary: Create signature effects and sound that communicate hit, force, flame behavior and tactical state.
Tags: vfx,audio,combat,shaders,particles

## Principle
VFX and sound support movement and gameplay truth; they do not substitute for animation, damage timing, hitboxes or a readable target. Every signature ability needs authored staging over time, not just a colored flash.

## Effect brief
For each move, define source, trajectory, timing, shape silhouette, density, color/material, interaction with world, impact, decay, target reaction, screen feedback, sound cue, audio envelope, accessibility behavior and performance budget.

## Production paths
- 2D: generate/refine effect texture sequences with stable frame style and alpha; build trails/impacts from layered images or mesh/particle systems as appropriate; remove edge halos and inspect over bright/dark scenes.
- 3D: use Blender curves/meshes, materials, geometry nodes where appropriate, sprite cards, volumetrics only when affordable, and render multi-angle/game-camera tests.
- Runtime: integrate with the actual ability/event frames, target status, camera and audio mixer; make effects respond to velocity/impact rather than simply play on button press.
- Audio: produce or record original/source-permitted impacts, ignition, jet whoosh, crystal clink/shatter, electric arc, smoke/void, cleansing and monster-transformation cues. Preserve source stems and mix version. A generic sound reused for every dominion weakens identity.

## Domain differentiation
- Jetfire: tight directional plume, pressure/acceleration and high-speed rush sound.
- Blazefire: building heat, heavy ignition, thick contact burst and collapsing embers.
- Frostfire: thermal vacuum/hiss, crystalline freeze, brittle crack and suspended particle decay.
- Abyssfire: suppressed high-frequency ambience, light absorption, clinging corrupted tendrils; preserve readability.
- Spiritfire: harmonic clear tone, cleansing wave, residual healing particles and explicit neutralization cue.
- Haze Fire: volumetric smoke that flows and obstructs only as designed; layer sound to suggest spatial enclosure.
- Allurefire: tonal/melodic motif and clear target mark; provide accessibility alternatives for charm/disorientation.
- Emeraldfire: faceted projectile emission, distinct ricochet impacts and readable bounce order.
- Stormfire: charge, sharp discharge, ordered branching arcs and conductive feedback.
- Hearthfire: warm crackle, clear ignition and controlled spread.

## QA
Synchronize effects/sound to keyframes and gameplay events; inspect at target scale, low graphics settings, reduced flash/contrast settings and browser frame rate. Prevent effects from hiding enemy state/telegraphs. Compare identical scene with and without effects to ensure the body action still reads.

## Acceptance criteria
- Every effect/audio cue is triggered by a defined gameplay or authored animation event.
- The character's body action and target state remain readable without the effect layer.
- Alpha, timing, mix level, accessibility behavior and target-engine playback are inspected and recorded.
