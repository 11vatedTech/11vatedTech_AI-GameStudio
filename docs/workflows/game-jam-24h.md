# 24-Hour Game-Jam Operating Workflow

## Purpose and boundary
This profile allocates **24 elapsed hours**, not guaranteed productive capacity. Keep approximately **25%** as release reserve for integration failures, engine/export issues, and submission requirements. Use `ags jam plan --profile 24h` with real task estimates to produce a task shortlist; the calendar below is an operating rhythm, not a rigid promise.

## Non-negotiable rules
- Confirm jam rules, permitted AI/tool use, platform, deadline, attribution, and submission format before implementation.
- Preserve a recoverable source state and working build throughout the sprint.
- Define one distinctive player experience and one smallest compelling loop.
- Produce a small cross-discipline visual proof set before mass asset generation. Review hero, environment, props, interface, and effects together.
- Queue memory-heavy image generation sequentially when VRAM headroom is narrow. Record actual latencies and failures.
- Separate generated candidate, technically valid file, integrated asset, in-engine verified asset, and human-approved asset.
- Use actual player and build evidence. A test harness or export exit code does not prove game feel or art quality.
- If scope slips, cut optional content before consuming the release reserve.

## Suggested schedule
- **00:00–01:00 — Resolve rules, brief, unique hook, platform, time and rights constraints.**
- **01:00–02:00 — Define core loop, cut-lines, art bible, risk list and proof-set needs.**
- **02:00–05:30 — Build a complete playable prototype with one representative challenge and restart.**
- **05:30–08:30 — Generate/refine and approve the smallest coherent set: focal character/object, environment, props and UI.**
- **08:30–13:30 — Integrate gameplay, level, art, animations, effects, sound and menus.**
- **13:30–16:30 — Content freeze; test core loop and repair the most consequential visual/gameplay defects.**
- **16:30–20:00 — Polish feedback, accessibility basics, performance and error recovery.**
- **20:00–24:00 — Build and launch exact export, regression, package, attribution, screenshots/logs/hash, submission.**

## Quality gates
1. **Brief/compliance:** constraints and acceptance tests recorded.
2. **Design/scope:** core loop, states, creative thesis, art bible, risks, and cut lines recorded.
3. **Vertical slice:** the player can perform the core action, receive feedback, and reach a state transition in-engine.
4. **Art proof:** representative character, environment, prop, UI, audio/effect choices fit a coherent style.
5. **Content freeze:** required content is integrated; new features stop unless they resolve a release blocker.
6. **Release candidate:** exact export is launched and core paths, restart, controls, and error recovery are tested.
7. **Submission:** package requirements, attributions, manifests, hashes and human-gate status verified.

## Scope cut order
Cut optional modes first; then secondary enemy variants; extra levels; cosmetics; nonessential narrative branches; expensive optional effects. Do not cut a completable core loop, essential controls, objective feedback, recovery/restart, required attribution, a real launch test, or mandatory submission artifacts.

## Evidence required
Retain the brief, art bible, task plan, asset/model provenance, rejected candidates, test logs with exit codes, actual build and SHA-256, screenshots or recordings from the running game, open defects, and human review decisions.

## Stop rule
Stop generating new assets when the approved minimum set is integrated or when review/integration threatens test and release time. A queue of generated images is not a finished content set.
