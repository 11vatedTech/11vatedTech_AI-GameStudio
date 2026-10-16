---
name: jam-finalization
description: Ship the actual build under deadline.
---
# Jam Freeze and Finalization

Summary: Ship the actual build under deadline.
Tags: game-jam,release,polish,scope

## Mission
Ship the actual build under deadline. This is an operational production procedure, not a claim that a tool is installed or the task has already passed. Apply it at the depth appropriate to the project’s jam profile.

## Required inputs
- Project brief, target genre/style/platform, time budget, and explicit acceptance criteria.
- Relevant approved project contracts and the current repository/source state.
- Actual tool/model availability, constraints, and previous evidence.

## Procedure
1. Freeze optional features; play exact export, fix crashes/softlocks/input/artifacts/attribution; verify restart and ending; capture evidence and hashes.

## Acceptance criteria
- Player can start, finish/reach ending, restart, and launch packaged deliverable.

## Failure modes and cautions
- Feature creep, stale export, missing attribution.
- Distinguish a successful command from a valid artifact, an integrated asset, an in-engine verified result, and a human-approved release.

## Required evidence
- Source inputs/references and configuration needed to understand the result.
- Changed paths, exact commands, exit codes, logs and artifact hashes where relevant.
- QA findings, rejected alternatives, unresolved defects and checks not run.

## Handoff contract
Return the changed files and exact output paths; include test/runtime status and a truthful limitations statement. Preserve the original inputs and frozen releases. Ask for human review only when the decision is subjective, legal, rights-related, or otherwise outside automation.

## Reference starting points
- https://docs.godotengine.org/en/stable/tutorials/editor/command_line_tutorial.html

## Studio operating rule
Use repeatable processes, project-scoped context, explicit configuration and evidence. Never claim artistic quality, legal clearance or human playtesting from a technical exit code.
