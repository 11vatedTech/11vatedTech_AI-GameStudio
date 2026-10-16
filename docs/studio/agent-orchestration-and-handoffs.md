# Agent Orchestration and Handoffs

The studio is agent-agnostic. Freebuff, Claude Code, Gemini CLI, or another coding agent is the reasoning/operator layer; the repository supplies domain playbooks and deterministic local tools. Avoid coupling core behavior to one model or private host API.

## Operating pattern

1. **Discover capability:** read `docs/capability-register.json`, `ags doctor`, and related skill files.
2. **Declare intent:** formulate task, expected outputs, constraints, acceptance criteria, budget and risk.
3. **Prepare context:** project brief, art bible, current code, provenance and known failures.
4. **Execute:** use an implemented CLI/API/MCP command or work directly in project files. No capability should be claimed merely because it was requested.
5. **Inspect:** validate structured output, technical artifact and actual in-engine effect.
6. **Record:** command result, source/outputs, hashes, duration, errors and review status.
7. **Hand off:** write a structured note for the next role/agent.
8. **Integrate and retest:** resolve conflicts, run impacted regression paths and refresh builds.

## Handoff template

- Producer role / receiving role
- Project and revision
- Objective and why it matters to the player
- Inputs read (paths + hashes/revisions if practical)
- Outputs produced (paths + hashes)
- Decisions made and rationale
- Acceptance criteria and observed results
- Assumptions and unresolved questions
- Known failure modes / risk
- Commands and test evidence
- Status: draft, ready, accepted, rejected, or blocked

## Parallel work

Parallelize independent prompt research, asset candidates, documentation sources, or test design. Do not concurrently mutate the same scene, manifest, source file, model config, or release directory. A designated integrator owns merged project state. GPU tasks should be serialized where memory headroom is low. If a generated asset changes its spec, notify downstream animation/level/UI consumers before they integrate it.

## Conflict resolution

1. Hard jam/platform/licensing constraint wins.
2. Player comprehension and game correctness win over decorative preference.
3. Canonical art bible wins over isolated asset prompt decisions.
4. Reproducible test/evidence wins over memory or confidence.
5. When evidence is ambiguous, run a controlled comparison or retain the reversible option.

## Model/skill selection

Search the skills library using task terminology; load the top specialized skills plus cross-cutting production canon. Avoid loading every skill for every task. Skill instructions are playbooks, not proof of their own claims. When a skill conflicts with current API/model docs or measured machine behavior, update the method and cite why.
