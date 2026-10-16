---
name: security-local-services
description: Use least privilege and safe boundaries for local APIs/files.
---
# Security for Local Agent Services

Summary: Use least privilege and safe boundaries for local APIs/files.
Tags: security,api,local-first,paths

## Mission
Use least privilege and safe boundaries for local APIs/files. This is an operational production procedure, not a claim that a tool is installed or the task has already passed. Apply it at the depth appropriate to the project’s jam profile.

## Required inputs
- Project brief, target genre/style/platform, time budget, and explicit acceptance criteria.
- Relevant approved project contracts and the current repository/source state.
- Actual tool/model availability, constraints, and previous evidence.

## Procedure
1. Bind loopback; authenticate mutations; bound bodies/timeouts; contain paths; refuse symlink/unsafe archive; avoid secrets in logs; use subprocess argument arrays.

## Acceptance criteria
- Unsafe requests and paths fail; packages exclude credentials and local state.

## Failure modes and cautions
- shell=True, provider filename trust, exposing API publicly.
- Distinguish a successful command from a valid artifact, an integrated asset, an in-engine verified result, and a human-approved release.

## Required evidence
- Source inputs/references and configuration needed to understand the result.
- Changed paths, exact commands, exit codes, logs and artifact hashes where relevant.
- QA findings, rejected alternatives, unresolved defects and checks not run.

## Handoff contract
Return the changed files and exact output paths; include test/runtime status and a truthful limitations statement. Preserve the original inputs and frozen releases. Ask for human review only when the decision is subjective, legal, rights-related, or otherwise outside automation.

## Reference starting points
- https://docs.github.com/en/actions/reference/security/secure-use

## Studio operating rule
Use repeatable processes, project-scoped context, explicit configuration and evidence. Never claim artistic quality, legal clearance or human playtesting from a technical exit code.
