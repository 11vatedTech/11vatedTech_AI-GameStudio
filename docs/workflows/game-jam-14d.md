# 14-Day Game-Jam / Production Sprint Workflow

## Purpose and boundary
This profile allocates **336 elapsed hours**, not guaranteed productive capacity. Keep approximately **20%** as release reserve for integration failures, engine/export issues, and submission requirements. Use `ags jam plan --profile 14d` with real task estimates to produce a task shortlist; the calendar below is an operating rhythm, not a rigid promise.

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
- **Day 1 — Brief, rules, concise research, player fantasy, success criteria and risks.**
- **Day 2 — GDD, game-state model, level route, art bible, architecture, content schema.**
- **Days 3–4 — Prototype risky systems; test visual model/workflow and one meaningful animation.**
- **Day 5 — Playable vertical slice, first cold playtest, scope/architecture review.**
- **Days 6–8 — Core gameplay and level systems; controlled content production with reference/style approvals.**
- **Days 9–10 — Animation set, enemies/encounters, UI, audio and effects integrated.**
- **Day 11 — Content complete; scenario coverage; identify defects and visual inconsistencies.**
- **Day 12 — Content freeze, structured playtest, balance, accessibility and performance review.**
- **Day 13 — Regression, target exports, cold playtest, provenance/license/package audit.**
- **Day 14 — Release candidate, final blockers, packaging, submission and postmortem.**

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
