---
name: postmortem-learning
description: Capture reusable lessons without overgeneralizing from one experiment.
---
# Evidence-Based Postmortem

Summary: Capture reusable lessons without overgeneralizing from one experiment.
Tags: postmortem,learning,metrics,knowledge-loop

## Mission
Capture reusable lessons without overgeneralizing from one experiment. This is an operational production procedure, not a claim that a tool is installed or the task has already passed. Apply it at the depth appropriate to the project’s jam profile.

## Required inputs
- Project brief, target genre/style/platform, time budget, and explicit acceptance criteria.
- Relevant approved project contracts and the current repository/source state.
- Actual tool/model availability, constraints, and previous evidence.

## Procedure
1. Collect generation/test/playtest time and defects; separate observations from inference; implement the smallest justified process change; preserve previous evidence when claims change.

## Acceptance criteria
- Actions are evidence-backed and revalidation is defined.

## Failure modes and cautions
- Universal claim from one lucky frame.
- Distinguish a successful command from a valid artifact, an integrated asset, an in-engine verified result, and a human-approved release.

## Required evidence
- Source inputs/references and configuration needed to understand the result.
- Changed paths, exact commands, exit codes, logs and artifact hashes where relevant.
- QA findings, rejected alternatives, unresolved defects and checks not run.

## Handoff contract
Return the changed files and exact output paths; include test/runtime status and a truthful limitations statement. Preserve the original inputs and frozen releases. Ask for human review only when the decision is subjective, legal, rights-related, or otherwise outside automation.

## Reference starting points
- https://www.khanacademy.org/computing/pixar/storytelling

## Studio operating rule
Use repeatable processes, project-scoped context, explicit configuration and evidence. Never claim artistic quality, legal clearance or human playtesting from a technical exit code.
