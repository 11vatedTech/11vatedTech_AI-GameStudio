# Research and Competitive Technology Review

**Review checked:** 2026-10-16. This is an evidence-backed starting review, not a claim that every model was rerun in this clean-room build. Prior machine experiments are labeled historical evidence. Re-benchmark before changing defaults or weights.

## System conclusions
1. The studio is agent-operated: the reasoning agent directs local commands and creative tools; the core does not require a paid reasoning API.
2. Optimize **usable integrated assets and shipped experience per unit time**, not raw image count or a single model score.
3. Asset tasks differ: concept illustration, pixel sprite, transparent icon, environment plate, keyframe, modular tile, UI control and 3D rig have different constraints.
4. Image identity and animation are distinct. A seed is not identity lock; interpolation does not design a missing action.
5. Generation, refinement, integration, engine validation, human art review, rights review and release are separate statuses.

## Model/workflow findings from the submitted archive

### FLUX.2 Klein
The official Black Forest Labs repo's model table lists Klein 4B and 4B Base as Apache-2.0; 9B variants and FLUX.2 dev use the FLUX Non-Commercial License in that table. It describes text-to-image and single/multi-reference editing. Verify exact downloaded file and current terms at adoption.

Prior local experiment reports Klein 4B distilled FP8 producing detailed character/environment concepts in roughly 8–10 seconds per 1024px candidate and system-observed peak near 11.1/12.2 GB VRAM. This is historical, machine-specific evidence, not a guaranteed benchmark. Keep GPU jobs sequential and remeasure cold/warm time.

### SD 1.5 pixel-art checkpoint
The prior workspace repeatedly observed poor front-view control and sprite-sheet outputs needing manual frame picking. It remains suitable only for task categories where its style and control behavior are proven. It is not a universal pose-control system.

### Z-Image Turbo
Prior single-brief tests reported 512px execution but narrow VRAM headroom and a character readability/pose failure. Sample size is too small to assign a general quality ranking. Keep it experimental until controlled per-category evidence supports promotion; verify exact source and license.

### ComfyUI
The adapter uses the local API workflow/prompt/history/view path. Workflow shapes and nodes are version-sensitive; validate nodes, inputs, model IDs and output paths. Queue acceptance does not mean completed generation.

### Animation methods
Choose among authored frame-by-frame art, reference-conditioned editing, 2D cutout/rigging, Blender rigs rendered to sprites, and interpolation according to the actual character/style. Required proof includes movement and attack at target speed, prop ownership, pivot/alpha correctness, in-engine playback and human visual inspection. The source archive's Klein identity experiment showed promising individual poses but not universal walk-cycle reliability. RIFE was rejected for one sprite test where output became opaque.

## Public professional learning boundary
Pixar in a Box is useful public education on storytelling, animation, light/color, cameras, rigging, effects and environments. Blender and Godot docs provide implementable techniques. This repository does not claim access to private AAA pipelines or reproduce confidential methods. It captures transferable public principles and tests local implementation.

## Source register
See `source-register.json` for official source links, type, use and caveats. Key sources:
- FLUX.2 model matrix: https://github.com/black-forest-labs/flux2
- ComfyUI docs/API: https://docs.comfy.org/ and https://github.com/Comfy-Org/ComfyUI/blob/master/openapi.yaml
- Godot sprite animation: https://docs.godotengine.org/en/stable/tutorials/2d/2d_sprite_animation.html
- Godot animation blending: https://docs.godotengine.org/en/stable/tutorials/animation/animation_tree.html
- Godot CLI: https://docs.godotengine.org/en/stable/tutorials/editor/command_line_tutorial.html
- Blender animation: https://www.blender.org/features/animation/
- RIFE: https://github.com/nihui/rife-ncnn-vulkan
- Pixar in a Box: https://www.khanacademy.org/computing/pixar
- MCP tools: https://modelcontextprotocol.io/docs/concepts/tools
- JSON Schema: https://json-schema.org/draft/2020-12
- GitHub Actions security: https://docs.github.com/en/actions/reference/security/secure-use

## Evidence boundary
- **Implemented in this clean-room repo:** Python service/package, local adapters, asset/animation utilities, planning/state model, schema contracts and specialist knowledge library; current-rebuild evidence is in `tests/` and `VERIFICATION.md`.
- **Inherited historical evidence:** Klein/Z-Image generations, RIFE caveat, Godot Ember/Lumen builds, prior 53-test suite and GPU measurements. These were not rerun by this build-container package run.
- **Not proven by this repository alone:** every model fits every task, universally coherent AI-generated animation, AAA quality, winning jams, or blanket commercial rights.
