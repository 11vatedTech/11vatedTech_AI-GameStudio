---
name: systemic-design
description: Design interacting rules with explicit state, invariants, and emergent consequences.
---
# Systemic Game Design

Summary: Design interacting rules with explicit state, invariants, and emergent consequences.
Tags: game-design,systems,simulation,emergence

## Mission
Design interacting rules with explicit state, invariants, and emergent consequences. This is an operational production procedure, not a claim that a tool is installed or the task has already passed. Apply it at the depth appropriate to the project’s jam profile.

## Required inputs
- Project brief, target genre/style/platform, time budget, and explicit acceptance criteria.
- Relevant approved project contracts and the current repository/source state.
- Actual tool/model availability, constraints, and previous evidence.

## Procedure
1. Name entities, variables, state owners, actions, invariants, and terminal states.
2. Map interactions and dominant strategies.
3. Build deterministic fixtures for risky combinations and recovery states.

## Acceptance criteria
- Rules are explicit, interactions testable, and softlocks/degenerate loops have prevention or recovery.

## Failure modes and cautions
- Untestable monoliths; assuming emergent behavior is balanced.
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
