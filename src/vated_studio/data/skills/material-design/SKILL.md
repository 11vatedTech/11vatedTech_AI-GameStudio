---
name: material-design
description: Keep material response consistent and communicate form.
---
# Materials and Surface Language

Summary: Keep material response consistent and communicate form.
Tags: materials,shaders,technical-art,pbr

## Mission
Keep material response consistent and communicate form. This is an operational production procedure, not a claim that a tool is installed or the task has already passed. Apply it at the depth appropriate to the project’s jam profile.

## Required inputs
- Project brief, target genre/style/platform, time budget, and explicit acceptance criteria.
- Relevant approved project contracts and the current repository/source state.
- Actual tool/model availability, constraints, and previous evidence.

## Procedure
1. Specify light/roughness/metalness/texture scale and wear.
2. Render material swatches under real lighting.
3. Validate tiling, UVs, normals, alpha, sorting and import.

## Acceptance criteria
- Materials are distinct, coherent and reproducible under target renderer.

## Failure modes and cautions
- Texture-map existence treated as correctness.
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
