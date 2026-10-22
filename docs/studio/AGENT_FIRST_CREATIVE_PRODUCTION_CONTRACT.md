# Agent-First Creative Production Contract

**Status:** proposed operating standard for the 11vatedTech AI Game Studio.  
**Intent:** the agent owns routine creative production end-to-end. It must explore the real toolchain, produce assets and motion, integrate them, and iterate against evidence—not merely identify deficiencies or hand missing art back to the operator.

## 1. Non-negotiable creative rule

The agent is the default executing artist, animator, technical artist, integrator, QA operator, and production coordinator. It must attempt the available automated methods before asking the operator to do production work.

A failed operation is a diagnosis and a branch in the method-selection tree, not a reason to stop. Record the failure, inspect why it failed, choose a materially different suitable method, and continue within the current resource and time budget.

The operator may set creative direction, prioritize alternatives, approve irreversible or high-consequence choices, and configure explicit human-only gates. Those choices do not make the operator responsible for generating images, repairing layers, animating characters, rigging models, authoring effects, or integrating assets.

## 2. Prohibited false deliverables

These are not acceptable substitutes unless they are explicitly the intended style of the game:

- Geometric primitives, colored rectangles, stick figures, generic icons, gradient blobs, emoji, or bare SVG/CSS/canvas drawings used in place of designed character art, environments, props, creatures, or polished interface.
- Pulsing, scaling, rotating, tinting, shaking, or sliding a static image and calling that character animation.
- A pose sheet, contact sheet, poster, GIF, or set of individually attractive pictures described as a completed animation.
- A mesh that has no suitable rig, deformations, authored motion, material integrity, playable action, or reliable prop grip.
- Interpolation presented as action generation.
- A model-generation failure treated as grounds to stop without trying a distinct valid approach.
- Placeholder or stock content quietly left in a final build when original authored content was requested.

SVG, canvas, shaders, particles, procedural geometry, procedural textures, and code-driven effects are valid techniques for appropriate roles: UI, compositing, dynamic effects, abstract stylization, gameplay geometry, simulation, and system visualization. They must not silently become the default replacement for designed visual content when AI-generated imagery, layer reconstruction, 2D rigging, or 3D production is available and better suited.

## 3. Required creative execution loop

For every important asset or animation:

1. **Specify:** define player-facing purpose, art style, dimensions/scale, camera/view, silhouette, materials, palette, anchor/pivot, variations, engine format, and acceptance criteria.
2. **Discover:** inspect installed programs, local model/services, MCP tools, plugins, checkpoints, workflows, formats, runtime budgets, and relevant specialist skills. Use actual host results, not assumptions.
3. **Choose the method:** compare image generation, reference edit, multi-view generation, layered reconstruction, 2D rigging, 3D modeling/rigging, keyframing, motion retargeting, and frame-generation routes.
4. **Produce a small proof:** generate only enough material to test the highest-risk requirement. Never start a large batch before the proof passes.
5. **Critique:** inspect identity, silhouette, anatomy, materials, lighting, pose readability, temporal continuity, play-scale readability, and integration constraints.
6. **Repair or switch:** correct the actual defect through the best available tool. If the method cannot meet its invariants, switch methods instead of polishing a bad base.
7. **Integrate:** import into the real project and exercise the asset using the target renderer/engine. Ensure collision, timings, pivots, lighting, audio, gameplay state, and camera agree.
8. **Validate and record:** retain inputs, workflow/model versions, prompt/config, logs, outputs, hashes, comparative review, rejected candidates, runtime evidence, and remaining uncertainty.

Ask the operator for a decision between genuinely subjective creative directions when needed. Do not ask them to perform missing production steps that available tools can handle.

## 4. Tool discovery is real, not ceremonial

A capability marked available must point to an executable, MCP tool, service health check, or explicit manual activation step. Keep these evidence states separate:

- **detected:** executable or service endpoint found;
- **connected:** compatible protocol/endpoint responds;
- **workflow-verified:** the intended feature has actually run;
- **artifact-valid:** file, structure, expected channels/tracks, and dependencies pass checks;
- **identity-valid:** character, prop, palette, camera and proportions meet cross-view/frame anchors;
- **integrated:** real project references and gameplay events are wired;
- **runtime-verified:** visible result was observed in the target engine/runtime;
- **agent-approved:** an explicit review rubric passed;
- **operator-approved:** the operator explicitly chose a subjective/high-consequence option;
- **rights-cleared:** the applicable source/model/asset rights register has been reviewed.

Do not infer that an MCP server is installed because the underlying app exists. Do not infer usable models from a ComfyUI health response. Do not infer animation authoring because frame assembly exists. At production-task start, inspect the capability register, run relevant local checks, list available MCP tools, inspect required models/nodes/plugins, then produce a concise capability map.

## 5. Animation means movement, intention and continuity

Animation is not decorative motion applied to a still image. It is pose and shape evolving through time to communicate action, anticipation, force, weight, balance, contact, reaction and recovery.

A character action must define the full event structure appropriate to its move:

- anticipation / loaded pose;
- initiation and acceleration;
- key action, strike, release, or evade;
- contact/impact frame and synchronized gameplay event where relevant;
- follow-through and secondary motion;
- recoil, balance recovery and actionable recovery pose;
- transition or combo branch.

For locomotion, define foot contact, weight transfer, passing pose, push-off, root travel, arm/torso counter-motion, cycle seam and transitions. For attacks, define prop ownership/grip, hand-to-weapon transform, weapon path, contact time, hitbox time, target response, optional hit-stop, sound/VFX event markers, combo windows and cancellation rules.

Acceptance requires: same identity and gear across the sequence; stable root/feet/pivot rules; physically legible movement; useful anticipation and follow-through; no unexplained weapon/hand drift; no missing limbs or costume swaps; no damaging alpha/edge artifacts; consistent timing; readable silhouette at target gameplay scale; valid transitions into/out of neighboring states.

Required review evidence includes a frame strip with frame IDs/timestamps, intended-speed playback, slowed inspection playback, identity/prop/pivot checks, target-engine playback (or clearly marked pre-integration review), rejection notes, and fixed defects.

## 6. Select animation approach by constraint

1. **3D rigged character in Blender:** use when camera freedom, convincing motion, reusable attacks/combos, lighting, and multiple angles justify the setup. Require suitable mesh, armature, skin weights, actions/NLA, IK constraints, prop sockets, root-motion contract, camera/render review, and export validation.
2. **AI-conditioned keyframes:** use when hand-rendered 2D frames serve the art direction. Generate keys from a locked identity reference with fixed camera, gear, silhouette and grip; correct the keys before making in-betweens. Independent images are not a sequence.
3. **Layered 2D rig/cutout:** use only where segmentation, pivots, overlaps, occluded body reconstruction and difficult poses remain convincing. Reject paper-doll deformation when it undermines the style.
4. **Motion capture / pose tracking and retargeting:** where available motion and its rights fit, acquire or capture skeleton motion, retarget, clean contacts and hand/weapon constraints, then restage for the move.
5. **Hybrid:** combine 3D motion for body, AI-assisted imagery/textures/material design, and purpose-built 2D/3D VFX for flames, trails, particles, impacts and transitions.
6. **Interpolation:** refine only after semantic keys already describe valid movement. Compare before/after at speed and on target backgrounds; reject ghosts, silhouette morphs, broken alpha, timing shifts or identity drift.

## 7. Resource-aware execution

Preflight available VRAM, GPU utilization, system RAM, disk headroom, concurrent GPU jobs, model cold/warm latency, expected peak allocation, and whether the operation is cancellable/resumable.

When resources are constrained: do not launch competing heavy jobs; do not kill unrelated processes automatically; persist the exact blocker; continue safe work such as pose spec, rigs/scripts, timing plans, prompt preparation, license research, metadata, scene setup and CPU-safe checks; resume when the resource gate clears; use lighter validated workflows only if they preserve creative invariants. A resource block is a scheduling state, not grounds to downgrade the art target to primitives or a still-image gimmick.

## 8. Recovery contract

For every failed attempt, retain the exact failure and likely cause; classify it as technical, resource, identity, aesthetic, semantic or integration-related; list methods already tried; rank alternatives by acceptance probability, cost and risk; state which safe work can continue; and define a precise resumption condition. Do not rerun the same failed method without a controlled change. Do not call an attempt successful by weakening its acceptance criteria.

## 9. Skill maintenance

When repeated work reveals a better technique, record the experiment and context; compare with baseline; separate one-off observations from general rules; add a reusable procedure or regression test only if it improves repeatability; update capability evidence honestly. The goal is fewer dead ends, stronger creative output, coherent motion, faster iteration and observable success in the actual engine—not a larger skill count.
