---
name: animation-full-stack
description: Produce meaningful character motion from action intent through rigging, animation, playback review and game-engine integration.
---

# Full-Stack Character Animation Production

Summary: Produce meaningful character motion from action intent through rigging, animation, playback review and game-engine integration.
Tags: animation,rigging,2d,3d,retargeting,engine

## Mission
Create actions that communicate intention, weight, timing and contacts. A still image transformed by a tween is not character animation. Frame assembly is not motion authorship. Interpolation is refinement only after correct movement is present.

## Required inputs
Action intent, target camera/scale, character identity reference, rig or segmentation plan, frame rate, state machine neighbors, action phases, gameplay events, platform budget and source/license provenance.

## Method selection
- 3D rigged Blender path: choose for multi-angle views, reusable moves, realistic body weight, expressive full-body actions, or combo sets. Inspect mesh, armature and weights; define root and weapon socket; author named Actions and transitions; render action frames; export and test target engine.
- Reference-conditioned 2D keyframes: choose for frame-rendered styles. Freeze identity/camera/gear; design semantic poses; repair key poses before in-betweens; inspect all frames and alpha at speed.
- Layered cutout: choose for limited-camera use only if hidden body parts can be reconstructed and deformation remains convincing through extreme poses.
- Motion capture/retarget: choose where source motion, source permission, rig mapping, capture continuity and cleanup costs make it better than manual keyframing. Repair feet, root, hands, weapon contact and timing.
- Hybrid: combine an appropriate body-motion source with designed fire trails, impacts, particles, shaders and animation events.

## Action authoring
Create a pose/timing table with anticipation, initiation, acceleration, key action, contact/release, follow-through, recoil/reaction and recovery. Specify center-of-mass shift, planted foot, root path, shoulder/hip counter-rotation, hand grip, weapon path and collision/hit frames. Set event markers for hitbox activation/deactivation, impact, sound, VFX, cancel windows and combo branches. Action data—not the visual effect—owns gameplay truth.

## Review and repair
Inspect a frame strip, intended-speed playback and slow playback. Check identity/gear continuity, hand/weapon ownership, feet/root, silhouette, cloth/secondary motion, contact timing, deformation and transitions. If the clip fails, repair its cause: retime curves, alter key poses, rebuild pivot/hidden plate, adjust retarget mapping, replace damaged frames or change method. Do not add glow/pulse to hide bad animation.

## Acceptance
- All required semantic action phases appear in time order.
- Bone/pose channels, root/pivot and prop grip are continuous by design.
- Gameplay event timing is synchronized and reproducible.
- The clip plays in its actual engine state machine with valid enter/exit transitions.
- Evidence references source, spec, output action/frame strip, test result and remaining defects.
