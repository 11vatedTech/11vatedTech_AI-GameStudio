---
name: character-animation-identity
description: Prevent identity drift across poses and make motion recognizable.
---
# Character Identity Through Animation

Summary: Prevent identity drift across poses and make motion recognizable.
Tags: character,animation,identity,reference

## Mission
Prevent identity drift across poses and make motion recognizable. This is an operational production procedure, not a claim that a tool is installed or the task has already passed. Apply it at the depth appropriate to the project’s jam profile.

## Required inputs
- Project brief, target genre/style/platform, time budget, and explicit acceptance criteria.
- Relevant approved project contracts and the current repository/source state.
- Actual tool/model availability, constraints, and previous evidence.

## Procedure
1. Write identity anchors; choose authored frame/reference edit/cutout/3D rig; maintain camera and anchors; compare adjacent frames for hand/weapon/material drift; inspect at speed and in Godot.

## Acceptance criteria
- Same character remains recognizable with no unreviewed equipment swap.

## Failure modes and cautions
- Same seed treated as lock; individually good frames treated as coherent cycle.
- Distinguish a successful command from a valid artifact, an integrated asset, an in-engine verified result, and a human-approved release.

## Required evidence
- Source inputs/references and configuration needed to understand the result.
- Changed paths, exact commands, exit codes, logs and artifact hashes where relevant.
- QA findings, rejected alternatives, unresolved defects and checks not run.

## Handoff contract
Return the changed files and exact output paths; include test/runtime status and a truthful limitations statement. Preserve the original inputs and frozen releases. Ask for human review only when the decision is subjective, legal, rights-related, or otherwise outside automation.

## Reference starting points
- https://docs.godotengine.org/en/stable/tutorials/2d/2d_sprite_animation.html
- https://www.blender.org/features/animation/

## Studio operating rule
Use repeatable processes, project-scoped context, explicit configuration and evidence. Never claim artistic quality, legal clearance or human playtesting from a technical exit code.
