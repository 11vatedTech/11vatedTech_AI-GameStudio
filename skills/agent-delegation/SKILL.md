---
name: agent-delegation
description: Delegate bounded tasks without losing shared state or quality.
---
# Agent Task Decomposition and Handoffs

Summary: Delegate bounded tasks without losing shared state or quality.
Tags: agents,orchestration,handoffs,planning

## Mission
Delegate bounded tasks without losing shared state or quality. This is an operational production procedure, not a claim that a tool is installed or the task has already passed. Apply it at the depth appropriate to the project’s jam profile.

## Required inputs
- Project brief, target genre/style/platform, time budget, and explicit acceptance criteria.
- Relevant approved project contracts and the current repository/source state.
- Actual tool/model availability, constraints, and previous evidence.

## Procedure
1. Give each task explicit inputs, outputs, file ownership, acceptance checks and dependencies.
2. Serialize shared-file edits and run impacted tests after integration.

## Acceptance criteria
- Every handoff has verifiable artifact and status.

## Failure modes and cautions
- Multiple agents editing same file or “done” with no evidence.
- Distinguish a successful command from a valid artifact, an integrated asset, an in-engine verified result, and a human-approved release.

## Required evidence
- Source inputs/references and configuration needed to understand the result.
- Changed paths, exact commands, exit codes, logs and artifact hashes where relevant.
- QA findings, rejected alternatives, unresolved defects and checks not run.

## Handoff contract
Return the changed files and exact output paths; include test/runtime status and a truthful limitations statement. Preserve the original inputs and frozen releases. Ask for human review only when the decision is subjective, legal, rights-related, or otherwise outside automation.

## Reference starting points
- https://modelcontextprotocol.io/docs/concepts/tools

## Studio operating rule
Use repeatable processes, project-scoped context, explicit configuration and evidence. Never claim artistic quality, legal clearance or human playtesting from a technical exit code.
