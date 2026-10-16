---
name: model-licensing
description: Track rights for weights, code, LoRAs, fonts, sounds and third-party assets.
---
# Model and Asset Licensing Due Diligence

Summary: Track rights for weights, code, LoRAs, fonts, sounds and third-party assets.
Tags: licensing,provenance,commercial,model-weights

## Mission
Track rights for weights, code, LoRAs, fonts, sounds and third-party assets. This is an operational production procedure, not a claim that a tool is installed or the task has already passed. Apply it at the depth appropriate to the project’s jam profile.

## Required inputs
- Project brief, target genre/style/platform, time budget, and explicit acceptance criteria.
- Relevant approved project contracts and the current repository/source state.
- Actual tool/model availability, constraints, and previous evidence.

## Procedure
1. Record exact source/revision/filename/hash/license/date.
2. Separate code and weights; track commercial use and redistribution separately; flag unclear terms; keep legal review open.

## Acceptance criteria
- Every shipped component has source/rights status and unresolved cases block commercial claim.

## Failure modes and cautions
- Assuming model family shares one license; “free” means redistributable.
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
