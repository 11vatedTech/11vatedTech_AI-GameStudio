---
name: save-load
description: Persist game state safely across versions.
---
# Save/Load and Persistent Data

Summary: Persist game state safely across versions.
Tags: save-load,persistence,serialization

## Mission
Persist game state safely across versions. This is an operational production procedure, not a claim that a tool is installed or the task has already passed. Apply it at the depth appropriate to the project’s jam profile.

## Required inputs
- Project brief, target genre/style/platform, time budget, and explicit acceptance criteria.
- Relevant approved project contracts and the current repository/source state.
- Actual tool/model availability, constraints, and previous evidence.

## Procedure
1. Define versioned schema, validate/migrate safely, atomic replace, test missing/truncated/bad/out-of-range saves and ensure reset clears only expected state.

## Acceptance criteria
- Valid saves roundtrip and invalid state fails safely.

## Failure modes and cautions
- Serializing whole engine objects; arbitrary untrusted deserialization.
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
