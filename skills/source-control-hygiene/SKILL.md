---
name: source-control-hygiene
description: Keep work recoverable, reviewable and safe to publish.
---
# Source Control and Public Repository Hygiene

Summary: Keep work recoverable, reviewable and safe to publish.
Tags: git,workspace,repo-hygiene,versioning

## Mission
Keep work recoverable, reviewable and safe to publish. This is an operational production procedure, not a claim that a tool is installed or the task has already passed. Apply it at the depth appropriate to the project’s jam profile.

## Required inputs
- Project brief, target genre/style/platform, time budget, and explicit acceptance criteria.
- Relevant approved project contracts and the current repository/source state.
- Actual tool/model availability, constraints, and previous evidence.

## Procedure
1. Inspect repo status; exclude `.env`, venv, caches, SQLite local state, duplicated builds and model weights.
2. Keep immutable releases, generated source provenance and secret scan.

## Acceptance criteria
- Repository clones cleanly without known secrets/machine state.

## Failure modes and cautions
- ZIP mistaken for Git history; model weights published without redistrib review.
- Distinguish a successful command from a valid artifact, an integrated asset, an in-engine verified result, and a human-approved release.

## Required evidence
- Source inputs/references and configuration needed to understand the result.
- Changed paths, exact commands, exit codes, logs and artifact hashes where relevant.
- QA findings, rejected alternatives, unresolved defects and checks not run.

## Handoff contract
Return the changed files and exact output paths; include test/runtime status and a truthful limitations statement. Preserve the original inputs and frozen releases. Ask for human review only when the decision is subjective, legal, rights-related, or otherwise outside automation.

## Reference starting points
- https://docs.github.com/en/actions/reference/security/secure-use

## Studio operating rule
Use repeatable processes, project-scoped context, explicit configuration and evidence. Never claim artistic quality, legal clearance or human playtesting from a technical exit code.
