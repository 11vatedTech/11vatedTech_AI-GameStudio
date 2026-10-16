---
name: godot-animation
description: Integrate SpriteFrames, AnimationPlayer, and AnimationTree appropriately.
---
# Godot Animation Integration

Summary: Integrate SpriteFrames, AnimationPlayer, and AnimationTree appropriately.
Tags: godot,animation,engine-integration

## Mission
Integrate SpriteFrames, AnimationPlayer, and AnimationTree appropriately. This is an operational production procedure, not a claim that a tool is installed or the task has already passed. Apply it at the depth appropriate to the project’s jam profile.

## Required inputs
- Project brief, target genre/style/platform, time budget, and explicit acceptance criteria.
- Relevant approved project contracts and the current repository/source state.
- Actual tool/model availability, constraints, and previous evidence.

## Procedure
1. Use AnimatedSprite2D for simple frames, AnimationPlayer for property/node tracks, AnimationTree for meaningful transition/blending needs.
2. Define one state owner.
3. Validate clips, loops, transitions and event sync in engine.

## Acceptance criteria
- States transition correctly, resources resolve and visible playback is verified.

## Failure modes and cautions
- Animation systems fight over the same properties; AnimationTree added without need.
- Distinguish a successful command from a valid artifact, an integrated asset, an in-engine verified result, and a human-approved release.

## Required evidence
- Source inputs/references and configuration needed to understand the result.
- Changed paths, exact commands, exit codes, logs and artifact hashes where relevant.
- QA findings, rejected alternatives, unresolved defects and checks not run.

## Handoff contract
Return the changed files and exact output paths; include test/runtime status and a truthful limitations statement. Preserve the original inputs and frozen releases. Ask for human review only when the decision is subjective, legal, rights-related, or otherwise outside automation.

## Reference starting points
- https://docs.godotengine.org/en/stable/tutorials/2d/2d_sprite_animation.html
- https://docs.godotengine.org/en/stable/tutorials/animation/animation_tree.html

## Studio operating rule
Use repeatable processes, project-scoped context, explicit configuration and evidence. Never claim artistic quality, legal clearance or human playtesting from a technical exit code.
