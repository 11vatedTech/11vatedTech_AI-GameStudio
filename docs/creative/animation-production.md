# Animation Production Standard

**Status:** canonical production procedure. **Scope:** generated, authored, cutout, rigged, procedural, and engine-driven animation. **Completion rule:** a sequence is accepted based on coherent motion at intended playback speed and in the target game context, not because files or a GIF exist.

## 1. Design the motion before producing frames

Begin with the action's gameplay purpose and the response it should communicate. Write a short action description, state prerequisites, start/end conditions, transition requirements, target duration, and timing constraints. Decide whether the motion should loop, interrupt, blend, root-move, or hold on a final pose.

For character actions, plan relevant poses such as anticipation, action/contact, follow-through, and recovery. These are useful principles, not a requirement that every tiny action contain every phase. The action should read at the size and speed at which it will be played.

## 2. Freeze the identity invariants

Before generating or authoring keyframes, record the invariants that must survive the motion:

- Character identity and distinctive face/helmet/markings.
- Body proportions, costume, materials, color signatures and equipment.
- Weapon/tool ownership and correct hand attachment.
- Camera view, perspective, orientation and apparent scale.
- Pivot, ground baseline, feet contact and root-motion convention.
- Transparency/background policy and lighting direction.

Movement may deform or occlude parts of the silhouette in justified ways; identity invariants do not mean every pixel must stay identical. Review action-specific features like cape, hair, weapon and held lantern for physically plausible changes rather than freezing them.

## 3. Select the animation method by the motion and source

### Frame-by-frame or authored keyframes
Use when silhouette control, expressive posing or a stylized frame-by-frame look is essential. Design key poses first, then author breakdowns/in-betweens as needed. Validate the sequence instead of assuming independently generated pictures are related frames.

### Reference-guided generation/editing
Use approved character images and controlled pose/action references. Keep identity anchors explicit, use matched camera/scale and preserve a record of references and settings. A seed alone is not identity lock. Review every frame for prop/hand swaps, costume drift, anatomy defects, face changes and inconsistent lighting.

### 2D cutout/skeletal animation
Use when the art can be segmented into stable parts and joint movement is compatible with its style. Inspect overlap, seams, deformation, and disconnected joints. A static painting rotated at joints may look robotic; if the motion depends on volume change, cloth dynamics or strong silhouette changes, use a different technique or redraw critical poses.

### Blender-assisted rigging/rendered sprites
Use where a coherent 3D model/rig is feasible and consistent multi-view animation is valuable. Account for modeling, topology, UV/material, rigging, lighting, render setup, transparency, and iteration time. Test a short action before committing the project to a complete pipeline.

### Engine animation
Use native engine tracks/state systems for timing, transitions, effects, UI, and property animation. In Godot, `AnimatedSprite2D`/`SpriteFrames` supports individual frames or sheets; `AnimationPlayer` can animate properties; `AnimationTree` adds advanced transition/blending on animations controlled by `AnimationPlayer`. Match documentation and behavior to the installed engine version.

### Interpolation
RIFE and comparable frame interpolation methods estimate intermediate frames between supplied images. They do not infer the intended semantic action or repair inconsistent source poses. Run a before/after comparison and reject outputs that damage silhouette, alpha, anatomy, prop consistency, or timing.

## 4. Frame-production contract

An animation manifest should record:

- Stable animation ID and character/asset reference.
- Intended behavior and gameplay state.
- Source reference/keyframe IDs and hashes.
- Production method, model/tool versions and workflow settings.
- Ordered frame paths, frame count, frame rate and duration.
- Canvas dimensions, pivot/anchor, baseline and transparency policy.
- Loop/hold/transition intent.
- Required invariants and diagnostic results.
- Engine mapping and review status.

Keep raw keyframes, cleaned keyframes and interpolated/derived frames distinguishable. Every derivative should retain lineage to its source.

## 5. Frame cleanup and consistency

Before assembling a sequence:

1. Normalize the shared canvas and expected image scale without stretching anatomy.
2. Align pivot/ground anchor according to the chosen root-motion model.
3. inspect feet/contact, hands, held props and weapon attachment.
4. Correct alpha halos, residual backgrounds, and edge damage.
5. Compare silhouette and bounding-box movement; legitimate action should not be mistaken for a defect.
6. Check neighboring frames for accidental duplicates or identity discontinuity.
7. Build a contact sheet and playback preview at the actual frame rate.

Do not blindly normalize bounding boxes in a way that cancels intended motion or makes the character float. Diagnostics must be interpreted in the context of the action.

## 6. Technical diagnostics

Automated signals may include:

- Missing/unreadable/empty frame.
- Frame dimensions and color mode.
- Alpha occupancy and sudden alpha changes.
- Anchor, baseline and bounding-box drift.
- Near-duplicate frames.
- Perceptual/color differences and unusually abrupt transitions.
- Frame rate, duration, loop seam and manifest integrity.
- Missing engine references or animation names.

These signals can flag risks but cannot prove convincing motion. A clean numeric profile can still contain dead, stiff, or nonsensical action. Human or carefully justified agent review at playback speed remains necessary for important animation.

## 7. Gameplay integration

Wire animations to actual game state/events. Define which gameplay conditions start, interrupt, or complete the animation, and whether hitboxes, damage, sound, particles, or movement timing depend on animation events.

Gameplay rules remain authoritative. An attack animation alone must not imply that a hit occurred. Test animation transitions, loop exit, restart, interruption, and event synchronization in the running game.

## 8. Review board and rejection policy

For a critical character, show side-by-side source/reference images, ordered frames, contact sheet, GIF/video playback, engine playback, diagnostic report, and provenance. Explicitly label failed experiments, rejected interpolation, and untested methods.

Reject sequences with unreviewed identity drift, equipment/hand swaps, broken ground contact, severe frame-to-frame visual changes, visible cutout seams, damaging interpolation, or unreadable gameplay timing.

If the sequence fails, diagnose whether the bottleneck is source pose quality, reference control, frame extraction, alignment, rigging, timing, or engine integration. Fix the diagnosed cause; do not automatically request more generations.

## 9. Production-time rules

For short game jams, prioritize only the animations necessary for core readability. A coherent idle, locomotion and one action may be more valuable than many weak clips. Keep a playable fallback using a single strong pose with restrained transform animation only if it fits the design and does not misrepresent motion.

Reserve time for actual engine playback, not just generation. Heavy GPU tasks must be queued according to observed VRAM pressure.

## 10. Research references

- [Godot 2D sprite animation](https://docs.godotengine.org/en/stable/tutorials/2d/2d_sprite_animation.html): frame images, sheets, `AnimatedSprite2D`, and `AnimationPlayer`.
- [Godot AnimationTree](https://docs.godotengine.org/en/stable/tutorials/animation/animation_tree.html): blending and state transitions.
- [Blender animation features](https://www.blender.org/features/animation/): keyframing, IK/FK, nonlinear animation, rigging, and shape keys.
- [RIFE ncnn-vulkan](https://github.com/nihui/rife-ncnn-vulkan): local frame interpolation implementation; check model/runtime compatibility and inspect alpha/silhouette.
- [Pixar in a Box](https://www.khanacademy.org/computing/pixar): public educational material on animation, story, color/light and related disciplines. It is not access to confidential production pipelines.

Confirm current versions and test exact methods in the installed environment. Public principles are not substitutes for a working animation proof.
