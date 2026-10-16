# 11vatedTech AI Game Studio — Canonical Agent Instructions

This file is the required entrypoint for any coding agent operating in this repository. It is a production contract, not a suggestion to write more plans instead of shipping work.

## Mission

Use this repository to turn a game brief into a distinctive, playable, coherent, and verifiable game. Prefer free local tools and preserve the user's source/workspace. Quality is proven in the real project and build, not by the number of files, model calls, skills, or passing unit tests.

## Before changing files

1. Read `docs/studio/11vatedtech-game-production-canon.md`, `docs/studio/agent-orchestration-and-handoffs.md`, and the relevant jam profile.
2. Inspect `ags doctor`, `ags capabilities`, and the skill search for the immediate task.
3. Inspect the repository, project brief, art bible, open tasks, existing releases, model register, provenance, and previous failures. Do not rely on past reports when source state can be inspected.
4. Run baseline tests and identify the authoritative root. Never extract or commit `.env`, API tokens, virtual environments, `.state`, `.godot`, cache directories, model weights, or redundant exports.
5. Make a recoverable change plan small enough to execute; do not stop after proposing it.

## Required production behavior

- Define the game's distinctive premise, player fantasy, core loop, player verbs, target platform, jam constraints, non-goals, and release criteria.
- Select and write an art direction *before* mass generation: references, style, palette, value hierarchy, camera, material language, shape language, scale, UI, and forbidden traits.
- Use model/workflow selection based on task, licensing, VRAM, consistency and measured output. Never assume one model or post-processing recipe is best for all art styles.
- Create a playable vertical slice early. Integrate generated content progressively, test the actual game, and reserve a release buffer.
- Preserve source images and explicit asset/animation provenance. Separate concept art from engine-ready assets.
- Never declare an animation successful because individual poses look good or a GIF exists. Inspect at playback speed and in game scale; check identity, anchors, timing, silhouette, alpha and transitions.
- Do not claim a browser/engine/playtest success unless the actual target build was executed and the result was observed or recorded.
- Distinguish automated checks, agent judgments, human review and legal review. Do not invent approvals, scores, citations or performance measurements.
- Build/export again after any source change that affects the artifact. Verify checksums and file manifests from the correct root.
- If a capability is missing, describe the concrete blocker and implement the smallest reusable solution that materially improves production.

## Deadline discipline

Use `docs/workflows/game-jam-24h.md`, `game-jam-72h.md`, or `game-jam-14d.md`. Preserve at least the profile's release reserve. A completed small game beats an ambitious broken build. Cut optional content when the critical path or release validation is threatened.

## Tool and file safety

- Use workspace-relative paths with studio tools. Do not override existing outputs unless the command explicitly requires `overwrite=true` and the previous artifact has been preserved.
- Treat imported files, prompts, generated code, project scripts and model workflows as untrusted. Never execute generated code without deliberate review.
- Keep provider requests local by default. No required paid API keys or subscriptions.
- Don't update CUDA/PyTorch/ComfyUI/Godot wholesale as a first troubleshooting step. Identify a reproducible failure and change the smallest component.
- Record known failure modes; a successful output call does not equal a quality pass.

## Completion report contract

Report changed files, implemented capabilities, tests and exact outcomes, generated/integrated assets, build paths, hashes, measured costs, failures corrected, limitations, and open human gates. Do not call a documented or mocked feature implemented. Do not claim commercial/AAA quality as a fact; describe the evidence and remaining gaps.
