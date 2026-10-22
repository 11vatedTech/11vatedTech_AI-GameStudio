---
name: visual-gameplay-validation
description: Verify that art, movement, VFX, UI and gameplay work together in the actual running game.
---

# Visual and Gameplay Validation in the Real Target Runtime

Summary: Verify that art, movement, VFX, UI and gameplay work together in the actual running game.
Tags: visual-qa,engine,playwright,godot,animation

## Principle
A unit test can validate input, scene contracts and event order; it cannot prove that the game looks or feels good. The final camera and live state are the truth for visual readability.

## Procedure
1. Define named scenarios with starting state, expected input, expected game state, visual evidence and restart path.
2. Open/run the actual project/build using Godot CLI/MCP. Record exact command, engine version, exit code and errors.
3. Capture fixed-camera shots at the target viewport and alternate common window sizes; for a browser build use real mouse/keyboard/gamepad touch-path tests where relevant.
4. Review visual priorities: player/enemy silhouette, action telegraphs, target selection, torch/ability read, terrain traversal, HUD contrast, alpha edges, effect occlusion, frame pacing and UI hierarchy.
5. Test an animation at normal and slow speed, across state transitions, during hit/contact and after interruption/cancel. Check prop ownership, foot/root, event timings, clip seam and collision/hitbox truth.
6. Inspect runtime logs, browser console/network errors and missing resource warnings. Reproduce and classify defects.
7. Repair the source asset/system and rebuild. Never edit only the screenshot or suppress logs to make evidence appear clean.
8. Store screenshots/video, logs, build hashes, scenario results, defects, retests and review status.

## Browser test matrix
Start/restart; creation/selection flow; movement; primary action; ability; enemy encounter; environment interaction; end state; viewport resize; keyboard-only path; mouse/touch path where supported; console errors; missing assets; recovery from failed action.

## Status model
Separate automated pass, agent visual assessment, runtime verification, optional operator approval and rights status. A screenshot captured by a test is evidence, not automatic proof of subjective quality. Record what was observed and what was not.

## Acceptance
Every required scenario can be reproduced against the same build revision; critical logs and missing resources are resolved; each major action is visually legible in context; the final export was rebuilt after relevant source changes.
