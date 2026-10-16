---
name: playtesting
description: Discover whether real players understand and enjoy the intended experience.
---
# Blind Playtesting and Usability

Summary: Discover whether real players understand and enjoy the intended experience.
Tags: playtesting,usability,feedback,release

## Mission
Discover whether real players understand and enjoy the intended experience. This is an operational production procedure, not a claim that a tool is installed or the task has already passed. Apply it at the depth appropriate to the project’s jam profile.

## Required inputs
- Project brief, target genre/style/platform, time budget, and explicit acceptance criteria.
- Relevant approved project contracts and the current repository/source state.
- Actual tool/model availability, constraints, and previous evidence.

## Procedure
1. Give a build and neutral task without solution/source.
2. Observe hesitations/misreads/input failures.
3. Separate defects from preference; ask neutral post-session questions; replay fixes.

## Acceptance criteria
- Feedback is traceable to observed behavior and player can complete core path.

## Failure modes and cautions
- Harness called a human test; leading questions.
- Distinguish a successful command from a valid artifact, an integrated asset, an in-engine verified result, and a human-approved release.

## Required evidence
- Source inputs/references and configuration needed to understand the result.
- Changed paths, exact commands, exit codes, logs and artifact hashes where relevant.
- QA findings, rejected alternatives, unresolved defects and checks not run.

## Handoff contract
Return the changed files and exact output paths; include test/runtime status and a truthful limitations statement. Preserve the original inputs and frozen releases. Ask for human review only when the decision is subjective, legal, rights-related, or otherwise outside automation.

## Reference starting points
- https://www.w3.org/WAI/WCAG22/quickref/

## Studio operating rule
Use repeatable processes, project-scoped context, explicit configuration and evidence. Never claim artistic quality, legal clearance or human playtesting from a technical exit code.
