# Architecture and Responsibility Boundaries

## Design objective
The studio is a local-first production substrate an external reasoning agent operates. It does not bundle a reasoning model and does not imply an agent has expert judgment merely because it can call tools. Expertise is encoded in skills, contracts, tested utilities and evidence gates.

## Package map
- `cli.py`: operator-facing CLI; predictable JSON output.
- `service.py`: application command registry, dependency composition and run tracking.
- `api/http_server.py`: authenticated loopback HTTP wrapper.
- `mcp_server.py`: JSON-RPC over stdio for the studio command service.
- `readiness.py`: read-only production readiness aggregation (tools, loopback services, RAM/GPU/disk, host MCP Blender override).
- `adapters/`: explicit boundaries for ComfyUI, SD WebUI, Godot, Blender, RIFE and generation workflow builders.
- `assets/`: image inspection/refinement, animation diagnostics/assembly and atlas packing.
- `workflow.py` / `planner.py`: lifecycle state and timeboxed production planning.
- `store.py`: local SQLite run/event/asset/feedback evidence.
- `schemas/`, `skills/`, `docs/`: production contracts and specialist knowledge.
- `templates/`: explicitly marked engine smoke fixture, not finished art.
- `tools/creative_mcp_server.py`: bounded creative-tool MCP server; fixed bundled scripts, workspace-contained paths, `--disable-autoexec` Blender subprocesses.
- `docs/registries/`: asset-method and MCP-tool registries validated against repository schemas.

## Invariants
1. The agent chooses creative strategy; adapters perform narrow, explicit operations.
2. Providers and heavy dependencies are optional; planning works without GPU packages.
3. Workspace writes use resolved paths, explicit overwrite intent and safe archive handling.
4. Outputs preserve provenance and separate tool success from art/release approval.
5. GPU jobs should be serialized when VRAM is constrained.
6. Human approval gates stay open until a person supplies the decision.
7. Reproducibility uses versioned configuration, hashes and retained source inputs.

## Extension contract
A new capability requires a stable interface, input/output contract, dependency and error contract, success/failure tests, capability-register entry and skill/doc references. Keep third-party objects behind adapters. Add schemas backward-compatibly where possible. Write an architecture decision record for dependency direction, persistence, safety, or data-contract changes.

## Not claimed
This code does not supply universal semantic matting, automatic art direction, general video generation, a full game engine, private AAA studio techniques, or market-success prediction. It is extensible toward specialized local tools, with evidence-based capability labels.
