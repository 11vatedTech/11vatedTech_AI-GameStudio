---
name: visual-qa
description: Review visual candidates in isolation and final rendering context.
---
# Visual Asset and In-Engine QA

Summary: Review visual candidates in isolation and final rendering context.
Tags: visual-qa,review,contact-sheet,art-direction

## Mission
Review visual candidates in isolation and final rendering context. This is an operational production procedure, not a claim that a tool is installed or the task has already passed. Apply it at the depth appropriate to the project’s jam profile.

## Required inputs
- Project brief, target genre/style/platform, time budget, and explicit acceptance criteria.
- Relevant approved project contracts and the current repository/source state.
- Actual tool/model availability, constraints, and previous evidence.

## Procedure
1. Check technical integrity, compare to references at full and target scale, inspect identity/material/readability; then inspect in running scene.
2. Keep human/agent/automated statuses separate.

## Acceptance criteria
- Major assets have in-game evidence and explicit review state.

## Failure modes and cautions
- Entropy/CLIP/occupancy treated as quality certification.
- Distinguish a successful command from a valid artifact, an integrated asset, an in-engine verified result, and a human-approved release.

## Required evidence
- Source inputs/references and configuration needed to understand the result.
- Changed paths, exact commands, exit codes, logs and artifact hashes where relevant.
- QA findings, rejected alternatives, unresolved defects and checks not run.

## Handoff contract
Return the changed files and exact output paths; include test/runtime status and a truthful limitations statement. Preserve the original inputs and frozen releases. Ask for human review only when the decision is subjective, legal, rights-related, or otherwise outside automation.

## Reference starting points
- https://docs.comfy.org/

## Studio operating rule
Use repeatable processes, project-scoped context, explicit configuration and evidence. Never claim artistic quality, legal clearance or human playtesting from a technical exit code.
