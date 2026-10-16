# Game-Jam Operating System

This operating system optimizes for a **complete, distinctive, playable release**, not the largest feature list or asset count. The 24h, 72h and 14d profiles live in `docs/workflows/` and `schemas/jam-profile.schema.json`.

## 1. Intake contract

Capture: event and submission deadline (with timezone), theme, rules, permitted AI/tool constraints, required platform/build, team capacity, engine, hardware, connectivity, chosen genre, expected play session, accessibility constraints, and rights/asset rules. Classify constraints as hard, soft, or assumed. Do not infer a game concept from the model best able to generate images.

## 2. Pick a game shape

Compare 2–3 small concept candidates against: core fantasy, distinctive mechanic, theme fit, first-minute comprehension, feasibility, content burden, art/animation risk, and replay/ending clarity. Select one concept and log why the others lost. Prefer concepts where the player's action is visually legible and can be tested quickly.

## 3. Critical path

Build dependency graph and identify the longest risk chain. Common chain: input/movement → primary interaction/combat → win/lose state → level flow → art integration → runtime export → cold playtest. GPU generation may run independently only when references/specification exist; keep jobs serial on constrained GPUs and review outputs before queueing more.

## 4. Milestone evidence

- **Pitch validated:** a distinctive premise and intended player experience are stated.
- **First playable:** the player can perform the central action and see a game-state consequence.
- **Vertical slice:** one representative loop uses real art/audio/UI and reaches an outcome.
- **Content complete:** no required placeholder remains; optional content is cut or completed.
- **Release candidate:** build can be launched by someone other than the implementing agent with clear instructions.
- **Release frozen:** artifacts hashed; later changes require new version and new test evidence.

## 5. Production scope control

Every task has an estimate, dependency, risk, priority, acceptance criteria and evidence. Re-estimate using measured generation/integration/test durations. Use a reserve for engine/export issues and late fixes. If task estimates exceed working capacity, cut optional systems before reducing testing, rights review or export validation.

## 6. Image and animation cost model

Track candidate count, usable candidate rate, generation latency, peak memory (clearly state whether system-wide or process-specific), refinement minutes, rejected candidate reasons, integration minutes and the number of revisions. For animation, also track coherent cycle acceptance rather than frame count alone. Do not multiply a single fast generation measurement into a guaranteed sprint estimate.

## 7. Quality strategy

A jam-size project still needs a hierarchy: (1) primary player/objective clarity, (2) distinctive hero/critical prop, (3) coherent environment/camera, (4) feedback for core action, (5) UI and sound, (6) polish. The exact priority changes by genre. Do not invest heavily in cosmetics before the game loop is fun/readable.

## 8. Role orchestration

Roles may be handled by one agent or several: creative director resolves style decisions; game designer owns loop/scope; technical artist owns asset/engine contracts; gameplay engineer owns state and correctness; QA owns reproduction/evidence; release lead owns packaging and truth status. Shared files have one write owner at a time. Handoffs include outputs, assumptions, unresolved risks, and acceptance checks.

## 9. Endgame

Declare feature/content freeze at the profile-defined milestone. From then onward only fix defects, readability, integration, accessibility, performance, licensing, or release blockers unless a small change provides strong measurable improvement with enough time to reverify. Never report victory because a build exported successfully; someone must play the build.
