---
name: evidence-claims
description: Distinguish documented, implemented, tested, demonstrated and human-approved.
---
# Evidence Levels and Capability Claims

Summary: Distinguish documented, implemented, tested, demonstrated and human-approved.
Tags: evidence,claims,capabilities,qa

## Mission
Distinguish documented, implemented, tested, demonstrated and human-approved. This is an operational production procedure, not a claim that a tool is installed or the task has already passed. Apply it at the depth appropriate to the project’s jam profile.

## Required inputs
- Project brief, target genre/style/platform, time budget, and explicit acceptance criteria.
- Relevant approved project contracts and the current repository/source state.
- Actual tool/model availability, constraints, and previous evidence.

## Procedure
1. Link status to implementation/tests/artifacts/environment/limitations.
2. Re-run impacted tests after source changes.
3. Mark unavailable checks blocked/not-run; separate human gates.

## Acceptance criteria
- Every capability has evidence level and actual supporting references.

## Failure modes and cautions
- HTTP 200/export exit treated as complete playable game.
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
