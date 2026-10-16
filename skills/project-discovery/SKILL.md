---
name: project-discovery
description: Turn an ambiguous idea into explicit requirements, constraints and a testable brief.
---
# Project Discovery and Constraints

Summary: Turn an ambiguous idea into explicit requirements, constraints and a testable brief.
Tags: discovery,brief,requirements,scope

## Mission
Turn an ambiguous idea into explicit requirements, constraints and a testable brief. This is an operational production procedure, not a claim that a tool is installed or the task has already passed. Apply it at the depth appropriate to the project’s jam profile.

## Required inputs
- Project brief, target genre/style/platform, time budget, and explicit acceptance criteria.
- Relevant approved project contracts and the current repository/source state.
- Actual tool/model availability, constraints, and previous evidence.

## Procedure
1. Extract the player experience, target platform, genre, jam rules, deadline, team capacity, AI-generation requirements, licenses, available tools and existing assets.
2. Separate confirmed facts from assumptions.
3. Inspect actual repository and environment before proposing installs.
4. Convert must-haves into acceptance criteria and non-goals.

## Acceptance criteria
- A brief, constraints matrix, assumption list, risk register, and first playable milestone exist.

## Failure modes and cautions
- Treating a plan as proof; asking for information already in the repo; silently assuming a target platform.
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
