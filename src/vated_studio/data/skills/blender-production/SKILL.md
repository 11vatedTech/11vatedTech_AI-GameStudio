---
name: blender-production
description: Use Blender for 3D models, rigging, motion, renders and sprite output where useful.
---
# Blender Asset and Animation Production

Summary: Use Blender for 3D models, rigging, motion, renders and sprite output where useful.
Tags: blender,3d,rigging,rendering

## Mission
Use Blender for 3D models, rigging, motion, renders and sprite output where useful. This is an operational production procedure, not a claim that a tool is installed or the task has already passed. Apply it at the depth appropriate to the project’s jam profile.

## Required inputs
- Project brief, target genre/style/platform, time budget, and explicit acceptance criteria.
- Relevant approved project contracts and the current repository/source state.
- Actual tool/model availability, constraints, and previous evidence.

## Procedure
1. Set units/axes/camera/material/output conventions.
2. Organize rig, actions, NLA and constraints.
3. Verify transforms, pivots, animation names, alpha and texture paths in destination engine.

## Acceptance criteria
- Scene and export are reproducible and target import matches.

## Failure modes and cautions
- Blender process exit mistaken for correct export.
- Distinguish a successful command from a valid artifact, an integrated asset, an in-engine verified result, and a human-approved release.

## Required evidence
- Source inputs/references and configuration needed to understand the result.
- Changed paths, exact commands, exit codes, logs and artifact hashes where relevant.
- QA findings, rejected alternatives, unresolved defects and checks not run.

## Handoff contract
Return the changed files and exact output paths; include test/runtime status and a truthful limitations statement. Preserve the original inputs and frozen releases. Ask for human review only when the decision is subjective, legal, rights-related, or otherwise outside automation.

## Reference starting points
- https://www.blender.org/features/animation/

## Studio operating rule
Use repeatable processes, project-scoped context, explicit configuration and evidence. Never claim artistic quality, legal clearance or human playtesting from a technical exit code.
