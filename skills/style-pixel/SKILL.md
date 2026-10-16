---
name: style-pixel
description: Create pixel art with deliberate grid, palette, clusters and animation.
---
# Pixel-Art Production

Summary: Create pixel art with deliberate grid, palette, clusters and animation.
Tags: art-style,pixel-art,sprites,animation

## Mission
Create pixel art with deliberate grid, palette, clusters and animation. This is an operational production procedure, not a claim that a tool is installed or the task has already passed. Apply it at the depth appropriate to the project’s jam profile.

## Required inputs
- Project brief, target genre/style/platform, time budget, and explicit acceptance criteria.
- Relevant approved project contracts and the current repository/source state.
- Actual tool/model availability, constraints, and previous evidence.

## Procedure
1. Choose logical resolution, pixel scale, palette, outline and cluster grammar.
2. Test view control before batch generation.
3. Inspect native pixels and final scale; use nearest-neighbor unless the style specifies otherwise.

## Acceptance criteria
- Native art is readable, palette is coherent and animation avoids jitter.

## Failure modes and cautions
- Pixelating illustration and calling it authored pixel art; half-pixel movement.
- Distinguish a successful command from a valid artifact, an integrated asset, an in-engine verified result, and a human-approved release.

## Required evidence
- Source inputs/references and configuration needed to understand the result.
- Changed paths, exact commands, exit codes, logs and artifact hashes where relevant.
- QA findings, rejected alternatives, unresolved defects and checks not run.

## Handoff contract
Return the changed files and exact output paths; include test/runtime status and a truthful limitations statement. Preserve the original inputs and frozen releases. Ask for human review only when the decision is subjective, legal, rights-related, or otherwise outside automation.

## Reference starting points
- https://docs.godotengine.org/en/stable/tutorials/2d/2d_sprite_animation.html

## Studio operating rule
Use repeatable processes, project-scoped context, explicit configuration and evidence. Never claim artistic quality, legal clearance or human playtesting from a technical exit code.
