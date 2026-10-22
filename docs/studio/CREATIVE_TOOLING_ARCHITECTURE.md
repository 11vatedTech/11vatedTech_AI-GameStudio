# Creative Tooling Architecture: Discover → Produce → Inspect → Integrate

## Target behavior

The studio must act as the workflow coordinator across specialist programs, models, MCP servers and the game engine. The existing Studio CLI/MCP remains the source of truth for project state, provenance, skill discovery and release status. External MCPs expose capabilities of the actual local creative software; they do not replace Studio policy or evidence tracking.

## Capability layers

1. **Intent/specification:** GDD, art bible, animation/action specs, camera and target-scale contracts.
2. **Discovery/preflight:** executables, service endpoints, MCP tool list, model files, node availability, GPU/RAM/disk, tool versions and licenses.
3. **Creation:** ComfyUI local workflows, Blender modeling/rigging/animation/rendering, Krita layered painting/repair, audio editor, shader/VFX tools, and code where code is appropriate.
4. **Inspection/critique:** compare references, multi-angle views, layer/alpha checks, playback/slow-motion, silhouette and identity checks, scene/rig/action inventories, and output hashes.
5. **Repair/alternate path:** change one variable, select another method, rebuild or regenerate the failing component, then re-run the same checks.
6. **Integration:** Godot import settings, animation state machine, socket/pivot/collision, event markers, audio/VFX hooks, camera and gameplay state.
7. **Runtime verification:** Godot execution, deterministic scenario/playtest, browser launch and input checks, screenshots/recordings/logs.
8. **Evidence and handoff:** provenance, task state, failure/retry history, generated candidate vs accepted vs runtime-verified states.

## Data flow

- The GDD/art bible are authoritative for style and content intent.
- Asset and animation specs are machine-readable task contracts.
- Tool-specific jobs reference specs, not duplicated prose.
- Every job has a durable job ID, queue state, budget estimate, attempt history, inputs, selected method, outputs, hashes, error class and next action.
- Outputs never silently overwrite accepted assets; use candidate/version paths then promote after the gate passes.
- Asset manifests store method, upstream tool/version, model/checkpoint/node set, prompt/seed/settings, source reference hashes, transformations, rights status, review status and integration evidence.

## Method selection policy

Use the registry in `docs/registries/asset-method-registry.json`. The agent must select the least risky method likely to meet the creative acceptance bar—not the easiest method to make a passing unit test.

### Characters and creatures
- 2D sprite/frame path: reference-conditioned keyframes or approved multi-view-to-frame workflow; identity/gear anchors; keyframe correction; in-betweens only after semantic keys pass.
- 2D cutout path: layered artwork, hidden-region reconstruction, correct pivots, mesh/weights, pose stress tests, reject paper-doll artifacts.
- 3D path: concept/reference, mesh creation or model reconstruction, cleanup/remesh, topology inspection, UV/material setup, rig/weights, authored motion or compatible retarget, action review, export, target-engine inspection.
- Choose the camera before committing to asset production. Camera lock may reduce requirements but must be an explicit art direction choice, not an accidental limitation.

### Environments and props
- Use generated environment/keyframe concepts as art-direction anchors, then create actual scene assets through 3D reconstruction/modeling, properly licensed asset sources, texture/material authoring and lighting. Do not attempt to turn one scenic poster into a full walkable world without a projection/geometry plan.
- For close-up hero props, use multi-view reference assets, 3D reconstruction followed by topology cleanup, or authored mesh. Validate silhouette under game camera and light.

### VFX
- Use authored textures/sequences, meshes/curves, shaders and particles where they improve the result. Each effect must communicate a gameplay state and respond to its source/target. Flat gradient rings and generic bursts are not substitutes for signature attacks.
- Build fire/color identity through shape, motion, density, trail behavior, impact shape and audio—not color alone.

## Required orchestration behavior

- Before heavy work, preflight; never queue concurrent GPU jobs unless measured memory policy explicitly permits it.
- Persist work to a queue and resume rather than losing submitted jobs.
- On repeated failure, escalate method: prompt change → conditioned edit/repair → alternate graph/model → layered reconstruction → rigged 3D or a hybrid route.
- The agent should continue non-GPU tasks while the GPU is blocked.
- External tools are opt-in dependencies, installed/registered one at a time with explicit version, license, socket/security and smoke-test records.
- The studio must not state a method is available until the active host lists the relevant tool and a real task has succeeded.
