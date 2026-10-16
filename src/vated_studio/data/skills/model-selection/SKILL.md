---
name: model-selection
description: Choose models by measured usable output, license, memory and time.
---
# Model Selection and Resource Benchmarking

Summary: Choose models by measured usable output, license, memory and time.
Tags: models,benchmark,vram,licensing

## Mission
Choose models by measured usable output, license, memory and time. This is an operational production procedure, not a claim that a tool is installed or the task has already passed. Apply it at the depth appropriate to the project’s jam profile.

## Required inputs
- Project brief, target genre/style/platform, time budget, and explicit acceptance criteria.
- Relevant approved project contracts and the current repository/source state.
- Actual tool/model availability, constraints, and previous evidence.

## Procedure
1. Record exact weight file/hash/license/dtype/dependencies.
2. Compare controlled prompts/references; measure cold/warm latency, VRAM, usable candidate rate, refinement effort and failure rate.
3. Promote per task type only.

## Acceptance criteria
- Decision contains real artifacts, cost, license and scoped recommendation.

## Failure modes and cautions
- Generalizing from one lucky image; confusing repo and weight license.
- Distinguish a successful command from a valid artifact, an integrated asset, an in-engine verified result, and a human-approved release.

## Required evidence
- Source inputs/references and configuration needed to understand the result.
- Changed paths, exact commands, exit codes, logs and artifact hashes where relevant.
- QA findings, rejected alternatives, unresolved defects and checks not run.

## Handoff contract
Return the changed files and exact output paths; include test/runtime status and a truthful limitations statement. Preserve the original inputs and frozen releases. Ask for human review only when the decision is subjective, legal, rights-related, or otherwise outside automation.

## Reference starting points
- https://github.com/black-forest-labs/flux2

## Studio operating rule
Use repeatable processes, project-scoped context, explicit configuration and evidence. Never claim artistic quality, legal clearance or human playtesting from a technical exit code.
