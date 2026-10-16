---
name: background-extraction
description: Create transparent sprites without damaging fine edges and interior details.
---
# Background Extraction and Alpha Cleanup

Summary: Create transparent sprites without damaging fine edges and interior details.
Tags: alpha,segmentation,background-removal,matting

## Mission
Create transparent sprites without damaging fine edges and interior details. This is an operational production procedure, not a claim that a tool is installed or the task has already passed. Apply it at the depth appropriate to the project’s jam profile.

## Required inputs
- Project brief, target genre/style/platform, time budget, and explicit acceptance criteria.
- Relevant approved project contracts and the current repository/source state.
- Actual tool/model availability, constraints, and previous evidence.

## Procedure
1. Use edge-connected color removal only on uniform backgrounds.
2. For fine hair, glow, translucent cloth or color overlap, use segmentation/matting/manual cleanup.
3. Check black/white/in-game backgrounds and alpha.

## Acceptance criteria
- Subject intact, edge clean, unwanted background absent.

## Failure modes and cautions
- Calling thresholding semantic matting; accepting opaque interpolation output.
- Distinguish a successful command from a valid artifact, an integrated asset, an in-engine verified result, and a human-approved release.

## Required evidence
- Source inputs/references and configuration needed to understand the result.
- Changed paths, exact commands, exit codes, logs and artifact hashes where relevant.
- QA findings, rejected alternatives, unresolved defects and checks not run.

## Handoff contract
Return the changed files and exact output paths; include test/runtime status and a truthful limitations statement. Preserve the original inputs and frozen releases. Ask for human review only when the decision is subjective, legal, rights-related, or otherwise outside automation.

## Reference starting points
- https://docs.comfy.org/

## Studio operating rule
Use repeatable processes, project-scoped context, explicit configuration and evidence. Never claim artistic quality, legal clearance or human playtesting from a technical exit code.
