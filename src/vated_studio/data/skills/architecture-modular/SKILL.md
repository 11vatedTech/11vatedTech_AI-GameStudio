---
name: architecture-modular
description: Set clear ownership boundaries and data contracts.
---
# Modular Game Architecture

Summary: Set clear ownership boundaries and data contracts.
Tags: architecture,modularity,data-driven,engineering

## Mission
Set clear ownership boundaries and data contracts. This is an operational production procedure, not a claim that a tool is installed or the task has already passed. Apply it at the depth appropriate to the project’s jam profile.

## Required inputs
- Project brief, target genre/style/platform, time budget, and explicit acceptance criteria.
- Relevant approved project contracts and the current repository/source state.
- Actual tool/model availability, constraints, and previous evidence.

## Procedure
1. Identify state owners, pure transformations, engine-facing parts and adapters.
2. Use project-scoped config and data-driven content where useful.
3. Validate boundaries, avoid global mutable state and over-abstraction.

## Acceptance criteria
- Dependencies are clear and critical behavior can be tested in isolation.

## Failure modes and cautions
- Monolithic scripts and abstractions with no real benefit.
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
