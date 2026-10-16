---
name: python-engineering
description: Build reliable local tools with explicit errors and safe paths.
---
# Python Production Tooling

Summary: Build reliable local tools with explicit errors and safe paths.
Tags: python,testing,engineering,cli

## Mission
Build reliable local tools with explicit errors and safe paths. This is an operational production procedure, not a claim that a tool is installed or the task has already passed. Apply it at the depth appropriate to the project’s jam profile.

## Required inputs
- Project brief, target genre/style/platform, time budget, and explicit acceptance criteria.
- Relevant approved project contracts and the current repository/source state.
- Actual tool/model availability, constraints, and previous evidence.

## Procedure
1. Use typed boundaries, explicit exceptions, atomic writes, timeouts, bounded requests, deterministic sorting and optional dependency checks.
2. Test success, invalid input, missing dependency and partial failure.

## Acceptance criteria
- Commands are predictable; dangerous writes guarded; failures diagnosable.

## Failure modes and cautions
- Swallowed exceptions, unbounded polling, secret/prompt logging.
- Distinguish a successful command from a valid artifact, an integrated asset, an in-engine verified result, and a human-approved release.

## Required evidence
- Source inputs/references and configuration needed to understand the result.
- Changed paths, exact commands, exit codes, logs and artifact hashes where relevant.
- QA findings, rejected alternatives, unresolved defects and checks not run.

## Handoff contract
Return the changed files and exact output paths; include test/runtime status and a truthful limitations statement. Preserve the original inputs and frozen releases. Ask for human review only when the decision is subjective, legal, rights-related, or otherwise outside automation.

## Reference starting points
- https://docs.python.org/3/

## Studio operating rule
Use repeatable processes, project-scoped context, explicit configuration and evidence. Never claim artistic quality, legal clearance or human playtesting from a technical exit code.
