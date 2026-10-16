---
name: image-generation-direction
description: Convert asset specifications into model-appropriate generation requests.
---
# Prompt and Image-Generation Direction

Summary: Convert asset specifications into model-appropriate generation requests.
Tags: image-generation,prompting,models,art-direction

## Mission
Convert asset specifications into model-appropriate generation requests. This is an operational production procedure, not a claim that a tool is installed or the task has already passed. Apply it at the depth appropriate to the project’s jam profile.

## Required inputs
- Project brief, target genre/style/platform, time budget, and explicit acceptance criteria.
- Relevant approved project contracts and the current repository/source state.
- Actual tool/model availability, constraints, and previous evidence.

## Procedure
1. Specify role, composition, camera, subject, silhouette, style, light, material, palette, background and exclusions.
2. Respect model behavior and record seed/settings.
3. Inspect full size and play scale; revise one defect at a time.

## Acceptance criteria
- Workflow is reproducible and candidate selection has a rationale.

## Failure modes and cautions
- Unsupported negative prompts; assuming seed locks identity.
- Distinguish a successful command from a valid artifact, an integrated asset, an in-engine verified result, and a human-approved release.

## Required evidence
- Source inputs/references and configuration needed to understand the result.
- Changed paths, exact commands, exit codes, logs and artifact hashes where relevant.
- QA findings, rejected alternatives, unresolved defects and checks not run.

## Handoff contract
Return the changed files and exact output paths; include test/runtime status and a truthful limitations statement. Preserve the original inputs and frozen releases. Ask for human review only when the decision is subjective, legal, rights-related, or otherwise outside automation.

## Reference starting points
- https://docs.comfy.org/
- https://github.com/black-forest-labs/flux2

## Studio operating rule
Use repeatable processes, project-scoped context, explicit configuration and evidence. Never claim artistic quality, legal clearance or human playtesting from a technical exit code.
