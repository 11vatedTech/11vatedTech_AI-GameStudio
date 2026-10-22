---
name: agent-capability-discovery
description: Discover what the current host can really run and select the strongest safe workflow before producing content.
---

# Agent Capability Discovery and Tool Selection

Summary: Discover what the current host can really run and select the strongest safe workflow before producing content.
Tags: mcp,capabilities,environment,discovery,orchestration

## Mission
Eliminate assumptions. The agent must distinguish installed executable, responsive service, registered MCP server, tools actually offered by the host, accessible models/nodes, and verified task-level execution.

## Procedure
1. Read the Studio capability register and relevant specialist skills. Run the read-only preflight.
2. Inspect tool/version and health: Blender, Godot, ComfyUI, SD WebUI, Krita, FFmpeg, audio tooling, browsers, CUDA/PyTorch where relevant, disk/RAM/VRAM.
3. Query the current agent host's MCP server/tool list. Never infer client configuration path/format; use the installed client's official settings/docs. Don't reveal secrets.
4. For ComfyUI, introspect live models, custom nodes and templates; confirm input/output nodes and workflow API format. Never treat HTTP health alone as proof a required model exists.
5. Compare available methods against the asset registry using visual invariants, licensing, model memory, cold-start time and downstream integration.
6. Run a small disposable smoke task. Save exact tool version, input hash, output hash, duration, logs and status.
7. If a needed tool isn't present, determine whether there is a free local install path and its dependencies/license/security. Install only when user authorization/environment policy permits; otherwise produce an exact opt-in runbook.
8. Keep executable discovery report and task-specific capability map with evidence statuses.

## Secure behavior
Do not expose unauthenticated sockets, install arbitrary custom nodes, run remote scripts without inspecting them, touch unrelated running processes or overwrite agent configuration. Use safe mode and telemetry-off defaults where upstream supports them. Do not write tokens into reports.

## Acceptance
The selected path refers to concrete commands/tool names and live evidence. If blocked, the report names the absent capability and a viable alternative; it does not fabricate connection or claim that a documentation-only integration is implemented.
