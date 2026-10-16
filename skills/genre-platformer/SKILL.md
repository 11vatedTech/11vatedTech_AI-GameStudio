---
name: genre-platformer
description: Design platforming around geometry, stable movement, and fair challenge.
---
# Platformer and Precision Movement

Summary: Design platforming around geometry, stable movement, and fair challenge.
Tags: genre,platformer,physics,level-design

## Mission
Design platforming around geometry, stable movement, and fair challenge. This is an operational production procedure, not a claim that a tool is installed or the task has already passed. Apply it at the depth appropriate to the project’s jam profile.

## Required inputs
- Project brief, target genre/style/platform, time budget, and explicit acceptance criteria.
- Relevant approved project contracts and the current repository/source state.
- Actual tool/model availability, constraints, and previous evidence.

## Procedure
1. Define acceleration, jump, air control, coyote time, buffering, gravity and fall speed.
2. Graybox routes first; confirm jumps are reachable; align visible surfaces and collision.
3. Test checkpoints and recovery.

## Acceptance criteria
- All mandatory jumps are reachable and failure feels attributable to the player, not hidden geometry.

## Failure modes and cautions
- Decorative platforms that do not match collision; physics changes without traversal retest.
- Distinguish a successful command from a valid artifact, an integrated asset, an in-engine verified result, and a human-approved release.

## Required evidence
- Source inputs/references and configuration needed to understand the result.
- Changed paths, exact commands, exit codes, logs and artifact hashes where relevant.
- QA findings, rejected alternatives, unresolved defects and checks not run.

## Handoff contract
Return the changed files and exact output paths; include test/runtime status and a truthful limitations statement. Preserve the original inputs and frozen releases. Ask for human review only when the decision is subjective, legal, rights-related, or otherwise outside automation.

## Reference starting points
- https://docs.godotengine.org/en/stable/

## Studio operating rule
Use repeatable processes, project-scoped context, explicit configuration and evidence. Never claim artistic quality, legal clearance or human playtesting from a technical exit code.
