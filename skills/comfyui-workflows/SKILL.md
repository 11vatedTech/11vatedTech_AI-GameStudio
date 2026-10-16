---
name: comfyui-workflows
description: Build versioned API workflows and bounded local generation jobs.
---
# ComfyUI Workflow Engineering

Summary: Build versioned API workflows and bounded local generation jobs.
Tags: comfyui,workflow,api,generation

## Mission
Build versioned API workflows and bounded local generation jobs. This is an operational production procedure, not a claim that a tool is installed or the task has already passed. Apply it at the depth appropriate to the project’s jam profile.

## Required inputs
- Project brief, target genre/style/platform, time budget, and explicit acceptance criteria.
- Relevant approved project contracts and the current repository/source state.
- Actual tool/model availability, constraints, and previous evidence.

## Procedure
1. Validate API-format nodes, inputs, links, model IDs, samplers and output nodes.
2. Submit prompt, retain ID, poll history with deadlines, handle errors and validate downloads.
3. Queue GPU jobs sequentially.

## Acceptance criteria
- Bad graphs fail early; outputs have prompt IDs and hashes; timeouts are explicit.

## Failure modes and cautions
- Assuming UI/API graphs match; queue accepted treated as finished.
- Distinguish a successful command from a valid artifact, an integrated asset, an in-engine verified result, and a human-approved release.

## Required evidence
- Source inputs/references and configuration needed to understand the result.
- Changed paths, exact commands, exit codes, logs and artifact hashes where relevant.
- QA findings, rejected alternatives, unresolved defects and checks not run.

## Handoff contract
Return the changed files and exact output paths; include test/runtime status and a truthful limitations statement. Preserve the original inputs and frozen releases. Ask for human review only when the decision is subjective, legal, rights-related, or otherwise outside automation.

## Reference starting points
- https://docs.comfy.org/
- https://github.com/Comfy-Org/ComfyUI/blob/master/openapi.yaml

## Studio operating rule
Use repeatable processes, project-scoped context, explicit configuration and evidence. Never claim artistic quality, legal clearance or human playtesting from a technical exit code.
