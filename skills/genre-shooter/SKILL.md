---
name: genre-shooter
description: Align projectile visuals, collision, travel and encounter pressure.
---
# Shooter and Projectile Systems

Summary: Align projectile visuals, collision, travel and encounter pressure.
Tags: genre,shooter,projectiles,combat

## Mission
Align projectile visuals, collision, travel and encounter pressure. This is an operational production procedure, not a claim that a tool is installed or the task has already passed. Apply it at the depth appropriate to the project’s jam profile.

## Required inputs
- Project brief, target genre/style/platform, time budget, and explicit acceptance criteria.
- Relevant approved project contracts and the current repository/source state.
- Actual tool/model availability, constraints, and previous evidence.

## Procedure
1. Define speed, lifetime, ownership, hit payload, filtering and cleanup.
2. Test fast projectiles, multiple hits, pause/death and scene exit.
3. Balance enemy density and visual clutter.

## Acceptance criteria
- Projectile travel/collision is predictable, ownership is right, damage is applied once.

## Failure modes and cautions
- Visual-only projectiles; oversized invisible hitboxes without intentional telegraph.
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
