# Asset Production Standard

**Status:** canonical production procedure. **Scope:** all generated, edited, authored, and imported game assets. **Evidence boundary:** this standard describes the required workflow; a particular asset is complete only when its own record and validation demonstrate completion.

## 1. The unit of production is an integrated asset

An attractive source image is a candidate, not a finished game asset. Asset production ends only after the selected result has been refined, technically validated, integrated into the target project, inspected at actual in-game scale, and approved at the appropriate review level.

The canonical lifecycle is:

**Specify → Reference → Generate/Author → Compare → Select → Refine → Validate → Integrate → Inspect in Context → Approve or Reject.**

Do not skip candidate selection for important assets. Do not overwrite raw sources with derivatives. A successful process exit code proves only the operation that produced it.

## 2. Asset brief

Every important asset receives a structured specification with:

- Stable ID, asset type, intended player-facing purpose, and owning project.
- Art-bible revision and approved visual references.
- Style, silhouette, palette, materials, lighting, camera/projection, and detail-density constraints.
- Target dimensions, aspect ratio, effective in-game size, transparency policy, and padding.
- Pivot/anchor/ground contact requirements and collision relationship where applicable.
- Required states, poses, frame timing, variants, or tiling behavior.
- Target engine and import settings.
- Licensing/provenance expectations and validation checks.
- Candidate-review state and explicit reasons for rejection or revision.

The spec should constrain what matters, not prescribe arbitrary detail. A tiny gameplay icon and a hero concept illustration need different criteria.

## 3. Select a method by asset class

Choose a workflow from observed task fitness, not brand familiarity:

| Asset class | Primary concerns | Candidate methods |
|---|---|---|
| Character concept | identity, costume, silhouette, pose communication | text-to-image, reference editing, multi-reference conditioning |
| In-game sprite | silhouette at gameplay scale, clean alpha, pivot, palette | style-specific generation, segmentation/matting, manual refinement |
| Character animation | identity invariants, pose/action readability, timing, anchors | authored keyframes, reference-guided editing, cutout/rig, Blender-rendered frames |
| Environment plate | composition, safe gameplay space, depth, lighting, aspect ratio | text-to-image, controlled img2img, inpainting, layered composition |
| Modular environment/tiles | edges, repeated scale/material, tileability, collision alignment | modular generation plus manual seam validation, authored tile workflow |
| VFX | temporal readability, alpha, compositing, impact timing | generated/painted frames, shader/particle system, authored animation |
| UI art | legibility, consistency, scaling, accessibility | authored layout plus generated supporting illustration; avoid baking critical text into images |
| Texture/material | seams, scale, PBR channel correctness if needed | texture generation, tiling tests, material inspection in engine |
| 3D object/reference | geometry feasibility, topology, silhouette, rigging/material constraints | concept generation, Blender modeling/sculpting, procedural assistance where appropriate |

This table is a decision aid, not a claim that every listed method is implemented or suitable for every model. Check the capability register and local tool diagnostics first.

## 4. Generation and candidate control

For each generation run, preserve the model/checkpoint identifier, exact variant and license reference, workflow version/hash, prompt and negative constraints if used, reference image IDs/hashes, seed if supported, dimensions, timing, and error result. Record seed as a reproducibility input, never as a guarantee of character identity.

For critical assets, generate a bounded candidate set. Compare candidates against the same art bible and use case. A blind comparison is useful where practical. Do not increase candidate count when evaluation/integration is already the bottleneck.

The workflow should use one approved visual proof set (typically focal character/object, environment, prop, UI, and representative effect) before batch production. If that set does not cohere in one engine scene, revise the visual direction before generating the long tail.

## 5. Refinement discipline

Choose refinement operations based on a diagnosed defect. Maintain source and derivative separation and record every transformation.

Potential operations include:

- Cropping, trimming, padding, canvas normalization, and alpha-channel repair.
- Background removal or matting, edge decontamination, and halo inspection.
- Color/palette adjustments appropriate to the style.
- Upscaling or high-resolution refinement when it improves the actual target use.
- Inpainting/retouching of localized flaws.
- Scale, pivot, baseline, or anchor normalization.
- Atlas packing and metadata generation.

Background removal based on a solid-color tolerance should be documented as a limited edge-connected color operation. It is not semantic segmentation or professional matting. Validate extracted edges on light, dark, saturated, and actual scene backgrounds. Do not flatten transparency unless the asset class requires it.

Never apply one universal pixelation, sharpening, upscaling, segmentation, or palette transform to every art style.

## 6. Technical validation

Validate at least the checks relevant to the asset class:

- File can be opened; dimensions and color mode meet contract.
- Alpha channel and foreground bounds are plausible; empty or near-empty images are flagged.
- Aspect ratio, occupancy and crop do not cut required features.
- Reference and derivative hashes are recorded.
- Palette/material behavior is checked against the relevant art direction; generic metrics are only warning signals.
- Sprite scale, feet baseline, pivot and anchor are stable across related assets.
- Animation frames preserve canvas and identity invariants; atlas frame references are correct.
- Tiling and seams are tested for tile assets.
- Engine references, import settings and resource paths resolve.
- Target viewport and in-game background do not hide important shapes or details.

Technical validation cannot certify artistic quality. Metrics such as variance, occupancy, palette count, perceptual embeddings, or frame-box drift need calibration and are not interchangeable with a visual review.

## 7. In-engine review and approval

Place important assets in a representative scene before approval. Inspect at the real camera and expected display scale; check silhouette, readability, lighting, contrast, visual hierarchy, style coherence, and effects on gameplay information.

Record separate statuses:

- `candidate`: generated/authored, not yet assessed.
- `technical_pass`: required file/structure checks passed.
- `integrated`: referenced by the project/scene.
- `engine_verified`: inspected in the target engine or a relevant test scene.
- `agent_recommended`: agent recommends the asset, with rationale.
- `human_approved`: an actual human reviewer approved it.
- `rejected` or `needs_revision`: reason recorded.

Do not infer an approval status from a missing defect report.

## 8. Provenance, rights and change impact

Record origins and transformations for first-party, generated, edited, and imported content. Track model/tool terms separately from output copyright questions and third-party source licenses. Never claim universal commercial clearance solely because a model card uses a permissive license.

An art-bible or specification change should identify affected assets and tests. Preserve rejected candidates when their failure teaches a reusable lesson, while avoiding unbounded file accumulation.

## 9. Release acceptance

A critical asset is release-ready only when its spec is satisfied, source/provenance is recorded, technical checks pass, engine references resolve, contextual review has occurred, and required human/legal gates are truthfully represented.

## 10. Research references

- [ComfyUI official documentation](https://docs.comfy.org/): version-sensitive local workflows, nodes, conditioning, and API behavior.
- [FLUX.2 official repository](https://github.com/black-forest-labs/flux2): model capabilities and variant-specific license table; recheck the precise file at adoption.
- [Godot 2D sprite animation](https://docs.godotengine.org/en/stable/tutorials/2d/2d_sprite_animation.html): individual images, spritesheets, `AnimatedSprite2D`, and `AnimationPlayer` integration.
- [Godot AnimationTree](https://docs.godotengine.org/en/stable/tutorials/animation/animation_tree.html): advanced blending/state transitions backed by `AnimationPlayer`.
- [W3C WCAG 2.2 Quick Reference](https://www.w3.org/WAI/WCAG22/quickref/): reference for relevant UI accessibility considerations; it does not certify whole-game accessibility.

These sources inform the standard; each chosen workflow still requires local, version-specific validation.
