# Animation Production Execution Runbook

This is an execution guide for character animation, not a guide to add superficial motion to still pictures.

## A. Start with the gameplay action

For every action, create an `animation-sequence-v2` manifest and declare:

- What the player is trying to do and what the opponent should read.
- Starting and ending state, move commitment, cancel window and recovery.
- Root travel, foot contact, center of mass, anticipation, contact/release, follow-through and recovery.
- Exact gameplay events: attack activation, hit frame, hit stop, damage resolve, sound/VFX, combo window and cancelability.
- Identity invariants: hair, face, outfit, silhouette, left/right, torch ownership, hand grip, material, camera and aspect.

## B. Run method discovery

1. Probe Blender version and usable background execution.
2. Query the installed Blender MCP tool list if connected; verify it can inspect scene, actions, bones, materials and render views.
3. Check local ComfyUI through its live model/node inventory and look for reference-edit/pose/control workflow capabilities that are actually installed.
4. Check existing 3D rigs/motion assets and their license register. Do not download or assume a motion source is distributable.
5. Select one method for a small proof. Use Blender for 3D body motion if a compatible rig/mesh and action requirements exist; use keyframe-conditioned 2D if the visual style requires hand-rendered 2D; use cutout only where the deformation remains convincing.

## C. Blender rigged-action path

1. Create/import a clean source `.blend` in a disposable project folder; never edit the only source copy.
2. Inventory objects, armatures, bone names, Actions, FPS, frame range, cameras and materials using `tools/blender/inspect_animation_scene.py`.
3. Map the intended action into named key poses and bone transforms. Use `examples/blender/torch_sweep_pose_spec.example.json` as a small example; replace all rig/bone names with those from the actual scene.
4. Validate the pose spec before launch. Confirm the armature contains every referenced pose bone and that frames/events are consistent.
5. Run `author_action_from_pose_spec.py` against a copy of the source file, writing a new `.blend` output. The script keys Euler rotations and optional bone locations; it does not auto-invent convincing choreography. Pose values must be planned for the rig and reviewed.
6. Render named Action frames with `render_action_review.py` into a separate evidence folder. Compare the timing chart with motion at intended and slow speeds.
7. Inspect contact poses, weight, feet, shoulders, hips, weapon/hand ownership, silhouette, anticipation, follow-through and recovery. Repair the actual pose/curve or change approach.
8. Export the action into the target engine and inspect transitions/hit events under the game camera. A rendered sequence alone is not runtime verification.

## D. AI-conditioned 2D action path

1. Create a canonical character identity sheet and single-grip weapon reference.
2. Specify the locked camera, full-body framing, scale, palette, hair, outfit, footwear, hand/weapon grip and flame design; list allowed motion variables separately.
3. Generate only the key poses with reference conditioning/editing. Keep the original reference immutable. Avoid simultaneous changes to prompt, model, denoise, camera, and composition.
4. Assemble a labeled contact sheet and run identity/prop review. Reject drift; do not disguise it with interpolation.
5. Correct broken anatomy/gear using reference edit, layer reconstruction or a different model/graph. If this repeatedly fails, switch to a rigged route instead of accepting a disconnected montage.
6. Generate in-betweens only after key poses tell a coherent action. Interpolate or RIFE only after comparing edge/alpha and shape at playback rate.
7. Review on light, dark, and game backgrounds; inspect transparent fringes, bounding box, common pivot, foot contact and clip seam.
8. Integrate the frames and trigger gameplay events at the correct frame. Record actual engine output.

## E. Cutout / 2D rig route

Segment head/torso/upper arm/forearm/hand/weapon, pelvis/thigh/shin/foot and separate cape/cloth only when it serves the style. Reconstruct pixels hidden behind overlaps before rigging. Establish pivots at shoulder, elbow, wrist, hip, knee, ankle and prop grip. Stress test extreme poses and layered occlusion. Reject visible gaps, stretched art, robotic hinge rotation or paper-doll silhouette.

## F. Motion capture / retarget route

Use a legal motion source (e.g. self-captured pose/video or a separately licensed source), extract skeleton tracking through an installed local route, map skeleton proportions, retarget to the target armature, clean feet/root, set hand/weapon constraints, and restage the timing and contact. Capture permission/license information in provenance. Motion capture is not a final action until cleaned and integrated.

## G. Acceptance checklist

A clip is not done until:

- Same identity/equipment/prop grip persists through all key and in-between frames.
- Poses communicate intention and distinct phases; weapon path/contact is legible.
- Root, foot placement, center-of-mass and pivot behavior are controlled.
- Frames have compatible size/origin/alpha, no broken edge artifacts, and no duplicate holds unless intentional.
- Clip can enter and exit from defined states without snapping.
- Damage/hitbox/audio/VFX/combo events are synchronized with action timing.
- Intended-speed playback and a slow review were examined.
- Actual target-engine playback evidence is linked before `runtime-verified` status.

## H. Failed asset recovery

Do not stop at “identity drift” or “shoulder reconstruction needed.” Test one of: reference-conditioned edits, masked redraw/inpainting with immutable identity anchors, a different available model/workflow, layer reconstruction, cutout with rebuilt occluded plates, suitable 3D character/rig, compatible motion retarget, or a hybrid. The agent chooses and executes the next safe alternative; ask the operator only for a material creative choice, permission, or specifically required approval.
