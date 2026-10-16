---
name: genre-racing
description: Tune control feel, track readability and camera around speed.
---
# Racing and Movement-Driven Games

Summary: Tune control feel, track readability and camera around speed.
Tags: genre,racing,vehicle,physics

## Mission
Tune control feel, track readability and camera around speed. This is an operational production procedure, not a claim that a tool is installed or the task has already passed. Apply it at the depth appropriate to the project’s jam profile.

## Required inputs
- Project brief, target genre/style/platform, time budget, and explicit acceptance criteria.
- Relevant approved project contracts and the current repository/source state.
- Actual tool/model availability, constraints, and previous evidence.

## Procedure
1. Define acceleration, braking, steering response, drift, collision recovery and camera lag.
2. Tune a representative track under repeated runs.
3. Test controller sensitivity and high-speed collisions.

## Acceptance criteria
- Steering is predictable; upcoming route and recovery are visible; collisions make sense.

## Failure modes and cautions
- Camera lag hiding hazards; teleport-like collision response.
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
