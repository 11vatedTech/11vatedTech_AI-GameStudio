---
name: character-rigging-retargeting
description: Build a usable rig and transfer movement without losing proportions, contacts or torch ownership.
---

# Character Rigging, Weighting and Motion Retargeting

Summary: Build a usable rig and transfer movement without losing proportions, contacts or torch ownership.
Tags: rigging,skinning,retargeting,blender,character

## Inputs
Approved character design/multi-view reference, mesh or source assets, target engine skeleton needs, expected action list, weapon grip transforms, camera, style and license/provenance.

## Pipeline
1. Inspect topology, normals, scale, origin, symmetry and material/texture readability. Reconstruct or retopologize if the mesh cannot deform. Do not assume an image-to-3D mesh is rig-ready.
2. Define skeleton hierarchy: root, pelvis, spine/chest, neck/head, clavicle/upper arms/forearms/hands, legs/feet, plus rig-specific controls. Include a stable hand/weapon socket or grip marker.
3. Bind skin/weights; test shoulders, elbows, hips, knees, wrists and twisting extremities in extreme poses. Repair weights where volume collapses or surfaces detach.
4. Set root-motion convention, units, forward axis, rest pose, rotation order, frame rate and export naming before actions accumulate.
5. Retarget only after source/target bone mapping and proportion differences are explicit. Normalize orientation/scale, adjust root, preserve floor contacts and constrain grip.
6. Create a two-action proof: one locomotion transition and one attack/contact/recovery. Render from game and inspection cameras before producing a full library.
7. Export a new candidate to the destination engine, verify skeleton/weights/materials/animation tracks and test state transitions.

## Prop grip invariants
The torch must remain owned by the intended hand unless the action explicitly throws/drops it. Check palm orientation, grip point, prop offset, forearm twist, shoulder range and contact frames. If an action uses two hands, track both contacts. Event markers and weapon transforms must remain synchronized.

## Failure recovery
- Shoulder gaps/collapse: reweight, adjust rest pose/geometry, use a corrective shape key or rebuild problematic topology.
- Foot sliding: fix root/plant phases, use IK/contact constraints, retarget floor plane and ensure loop seam.
- Prop drift: define a grip socket, constrain hand to prop, adjust retarget map and retest all adjacent poses.
- Face/hair/outfit inconsistency: prefer one rigged 3D identity or regenerate conditioned keys against immutable references; do not rely on seed alone.
- No suitable mesh/rig: switch to layer-reconstructed 2D or another model/asset workflow; don't ship an unrigged bust as playable hero art.

## Acceptance
A rig includes documented bone list, rest pose, units, root/forward convention, weapon socket, action names and export settings. At least two distinct actions pass deformations and prop-contact tests before the rig is treated as production-ready.
