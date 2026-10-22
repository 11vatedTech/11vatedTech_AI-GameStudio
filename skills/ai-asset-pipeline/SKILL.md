---
name: ai-asset-pipeline
description: Orchestrate generation, reference consistency, reconstruction, processing, selection, integration and provenance for complete art sets.
---

# AI Asset Pipeline: From Concept to Engine-Ready Content

Summary: Orchestrate generation, reference consistency, reconstruction, processing, selection, integration and provenance for complete art sets.
Tags: ai-assets,generation,comfyui,consistency,provenance

## Goal
The agent should be capable of producing its asset set—not merely making a prompt or an attractive concept image. Treat generation as one stage in a repeatable art-production pipeline.

## Pipeline
1. Create per-asset contract: role, style, camera, aspect, target scale, detail/material language, alpha, pivots, variants and destination format.
2. Inspect live generator capabilities: exact checkpoint/encoder/upscaler/edit/conditioning nodes, VRAM estimates, model license register and known failures.
3. Choose graph/model per task. Do not use a text-only route when reference-conditioned edit/pose guidance is available and required.
4. Make 2–4 controlled candidates for the risky asset proof. Change one variable at a time; retain rejected candidates and reasons.
5. Compare candidate at native size and game scale using a contact sheet and fixed style checklist. A beautiful isolated image may still fail crop, silhouette, continuity or alpha requirements.
6. Repair defects with masked edits, inpainting, layered painting, background/alpha extraction, material recreation or 3D reconstruction. If repair cannot preserve the anchor, switch workflow.
7. Prepare engine content: alpha/matting, trim/pad, common canvas/pivot, texture compression, mip/bleed controls, dimensions, collision/mesh as needed and import metadata.
8. Integrate in scene/lighting/camera; inspect the real result; record output hashes, inputs, prompt settings, model/node versions, process steps and review status.

## Character identity anchors
Define immutable design features (head/hair silhouette, face markings, torso silhouette, outfit colors, armor, cloak, footwear, prop model and hand grip) separately from allowed movement (pose, expression, camera if explicitly variable, cloth response, expression). Image seeds do not lock identity. Every sequence must be compared to the same reference anchors.

## Environment asset policy
Preserve an environment concept as a north-star image, not the playable level. Build geometry, traversal, occlusion, landmarks, lighting, material breakup, fog/depth and gameplay routes that reproduce the intent at the actual camera. Avoid a “poster world” that looks beautiful only in one screenshot but has no navigable space.

## Resource handling
Serialize heavy generation. Query memory and job state first. If blocked, persist the exact reason and continue non-GPU tasks. Use sequential low-memory routes only if the acceptance target is not compromised. Do not mass-generate before a cross-discipline proof set (character, world, hero prop, enemy, VFX, UI) fits one scene.

## Acceptance
Technical validity, visual/style consistency, identity continuity, engine import, runtime readability and rights/provenance are separate fields—not a single “done” checkbox.
