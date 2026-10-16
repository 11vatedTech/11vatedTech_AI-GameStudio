---
name: environment-design
description: Turn concept art into layered, navigable, gameplay-compatible scenes.
---
# Environment and World Art

Summary: Turn concept art into layered, navigable, gameplay-compatible scenes.
Tags: environment,world-art,level-art,composition

## Mission
Turn concept art into layered, navigable, gameplay-compatible scenes. This is an operational production procedure, not a claim that a tool is installed or the task has already passed. Apply it at the depth appropriate to the project’s jam profile.

## Required inputs
- Project brief, target genre/style/platform, time budget, and explicit acceptance criteria.
- Relevant approved project contracts and the current repository/source state.
- Actual tool/model availability, constraints, and previous evidence.

## Procedure
1. Define route, focal point, near/mid/far layers, gameplay-safe areas, materials and lighting.
2. Choose plate, modular kit, tilemap, 3D or hybrid.
3. Align visible ground/platforms with collision and perspective.

## Acceptance criteria
- Visual environment and physics agree in the actual game.

## Failure modes and cautions
- Flat collision rectangles over a painting implying different elevation.
- Distinguish a successful command from a valid artifact, an integrated asset, an in-engine verified result, and a human-approved release.

## Required evidence
- Source inputs/references and configuration needed to understand the result.
- Changed paths, exact commands, exit codes, logs and artifact hashes where relevant.
- QA findings, rejected alternatives, unresolved defects and checks not run.

## Handoff contract
Return the changed files and exact output paths; include test/runtime status and a truthful limitations statement. Preserve the original inputs and frozen releases. Ask for human review only when the decision is subjective, legal, rights-related, or otherwise outside automation.

## Reference starting points
- https://www.khanacademy.org/computing/pixar/animate

## Studio operating rule
Use repeatable processes, project-scoped context, explicit configuration and evidence. Never claim artistic quality, legal clearance or human playtesting from a technical exit code.
