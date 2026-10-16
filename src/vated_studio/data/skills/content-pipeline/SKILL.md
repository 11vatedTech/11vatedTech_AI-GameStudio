---
name: content-pipeline
description: Keep large content sets validated and editable.
---
# Data-Driven Content Pipeline

Summary: Keep large content sets validated and editable.
Tags: content,pipeline,data-validation,tools

## Mission
Keep large content sets validated and editable. This is an operational production procedure, not a claim that a tool is installed or the task has already passed. Apply it at the depth appropriate to the project’s jam profile.

## Required inputs
- Project brief, target genre/style/platform, time budget, and explicit acceptance criteria.
- Relevant approved project contracts and the current repository/source state.
- Actual tool/model availability, constraints, and previous evidence.

## Procedure
1. Define IDs/schema, deterministic import/build, missing-reference reports and round-trip tests.
2. Separate source from derived caches.

## Acceptance criteria
- Changes reproduce and failures identify exact content item.

## Failure modes and cautions
- Editing generated outputs as source; conflicting manifests.
- Distinguish a successful command from a valid artifact, an integrated asset, an in-engine verified result, and a human-approved release.

## Required evidence
- Source inputs/references and configuration needed to understand the result.
- Changed paths, exact commands, exit codes, logs and artifact hashes where relevant.
- QA findings, rejected alternatives, unresolved defects and checks not run.

## Handoff contract
Return the changed files and exact output paths; include test/runtime status and a truthful limitations statement. Preserve the original inputs and frozen releases. Ask for human review only when the decision is subjective, legal, rights-related, or otherwise outside automation.

## Reference starting points
- https://json-schema.org/draft/2020-12/

## Studio operating rule
Use repeatable processes, project-scoped context, explicit configuration and evidence. Never claim artistic quality, legal clearance or human playtesting from a technical exit code.
