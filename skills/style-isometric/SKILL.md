---
name: style-isometric
description: Maintain projection, scale, occlusion and collision clarity.
---
# Isometric and 2.5D Art

Summary: Maintain projection, scale, occlusion and collision clarity.
Tags: art-style,isometric,2.5d,camera

## Mission
Maintain projection, scale, occlusion and collision clarity. This is an operational production procedure, not a claim that a tool is installed or the task has already passed. Apply it at the depth appropriate to the project’s jam profile.

## Required inputs
- Project brief, target genre/style/platform, time budget, and explicit acceptance criteria.
- Relevant approved project contracts and the current repository/source state.
- Actual tool/model availability, constraints, and previous evidence.

## Procedure
1. Specify projection angle, tile dimensions, object height and sorting rules.
2. Calibrate grid.
3. Separate visual bounds from collision footprints.
4. Test navigation, selection and tall-object occlusion.

## Acceptance criteria
- Assets align to projection and depth sorting is stable.

## Failure modes and cautions
- Mixing perspective views or arbitrary rotations that break projection.
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
