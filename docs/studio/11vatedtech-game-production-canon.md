# 11vatedTech Game Production Canon

**Status:** authoritative operating standard, version 1.0.  
**Scope:** any game, engine or art style; profile-specific tailoring is mandatory.  
**Principle:** the agent directs a repeatable studio process. The process supports judgment; it does not replace it.

## 1. Production constitution

1. **Start with the game, not the tool.** Every generation, system, effect, and scene must serve the player experience or a release requirement.
2. **Art direction precedes asset volume.** Establish the visual thesis, reference hierarchy, scale, camera, palette, materials, silhouette language, and implementation constraints before batch creation.
3. **Playable early, coherent throughout.** Build a vertical slice before multiplying content, then keep the build runnable as content expands.
4. **Every asset has a role and lineage.** A generated concept is not automatically a final asset. Preserve sources, processing steps, model/workflow identity, hashes, and review decisions.
5. **Motion is evaluated in time.** Still-frame quality does not prove animation quality. Inspect cycles, transitions, alpha, anchors and gameplay synchronization at target speed and scale.
6. **Evidence has provenance.** Separate unit test results, simulated integration, real tool execution, agent assessment, human review, and legal review.
7. **Failures are data.** Keep failed experiments and reasons. Never quietly weaken tests or relabel an unsuccessful workflow as success.
8. **Scope protects quality.** Reduce features when the critical path, integration, polish or release buffer is threatened.
9. **Local-first by default.** Use compatible free local software and models where practical. No paid API or remote model is mandatory for the core workflow.
10. **Commercial honesty.** Code, model weights, generated content, fonts, audio, and third-party assets have separate rights and obligations.

## 2. Lifecycle and gates

The lifecycle is **Discover → Research → Define → Design → Scope → Prototype → Visual Identity → Vertical Slice → Produce → Integrate → Playtest → Refine → Verify → Package → Release → Learn**. Iteration backwards is allowed and logged; skipped requirements are not.

| Stage | Inputs | Required outputs | Exit gate | Evidence |
|---|---|---|---|---|
| Discover | Brief, jam rules, target player/platform, available time/tools | Constraints, assumptions, non-goals, open questions | Rules and deadline are explicit | Brief + constraint list |
| Research | Genre references, official docs, model/tool options, rights | Decision log with sources, applicability, rejected options | Every consequential adoption has a reason | Source register + decision entries |
| Define | Audience, fantasy, constraints | Creative thesis, design pillars, differentiator | A one-sentence distinction from a generic genre implementation | Brief review |
| Design | Thesis and genre | Player verbs, loop, states, controls, progression, failure/success | Win/lose/restart or equivalent states are defined | GDD + state diagram |
| Scope | Time profile, dependencies, tool latency, QA needs | MVP, dependency graph, cuts, reserve | Mandatory tasks fit working capacity excluding release reserve | Jam plan |
| Prototype | Smallest game loop | Player input + world response + meaningful objective | One loop is playable, not mocked | Engine run/harness |
| Visual identity | References, game scale/camera | Art bible, style board, first approved hero/environment/prop | Assets share coherent shape, palette, materials, light and scale | Contact sheet + review record |
| Vertical slice | Prototype + visual identity | One complete representative experience | Start → play → meaningful outcome → restart is possible | Actual build and playtest |
| Produce | Approved specs, workflows, budgets | Assets, animations, levels, audio, UI | Candidate/ready/approved status tracked per item | Manifest + provenance |
| Integrate | Selected assets/systems | Engine assets and working systems | Engine imports and references resolve; gameplay state is valid | Engine logs + scene inspection |
| Playtest | Actual build | Findings with severity, context, reproduction | Critical usability/gameplay defects triaged | Human or agent session evidence; reviewer type explicit |
| Refine | Findings | Fixes and measured changes | Important defects resolved or accepted explicitly | Before/after + retest |
| Verify | Candidate release | Test matrix, performance checks, rights/status register | Technical blockers resolved; human gates labeled honestly | Test reports and logs |
| Package | Frozen candidate | Source, playable build, docs, manifests, hashes | Archive opens and hashes verify | Archive test + SHA-256 |
| Release | Audit + approvals | Versioned release | Required human gates passed or release explicitly marked prerelease | Release manifest |
| Learn | Timings, failures, reviews | Postmortem + reusable updates | Findings distinguish observation from generalization | Postmortem |

## 3. Project truth model

Maintain one project manifest referencing the authoritative brief, art bible, task graph, asset manifest, animation manifests, license register, QA report and release manifest. Do not duplicate facts in multiple unlinked documents. Changes that affect downstream assets must be recorded as revisions, and the affected assets/tests must be identified.

### Work status

- `backlog`: not started.
- `ready`: inputs and dependencies available.
- `in_progress`: actively executed.
- `blocked`: a real dependency or decision prevents progress.
- `done`: acceptance criteria have evidence.
- `deferred` / `cut`: intentionally removed from current scope with rationale.

### Capability evidence levels

- `documented`: researched or specified, not implemented.
- `implemented`: code exists; end-to-end behavior may be unverified.
- `tested-with-mocks`: protocol/logic tested against simulated responses.
- `tested`: automated tests cover the implementation.
- `demonstrated`: real relevant workflow/output observed.
- `human-approved`: authorized human review recorded.
- `blocked`: unable to proceed for a specific reason.

These are not an overall game-quality score. A project can have tested infrastructure and still be visually or commercially unready.

## 4. Creative-director operating loop

At each significant milestone the agent answers:

1. What player experience are we trying to create here?
2. What currently prevents that experience?
3. Is the bottleneck design, source content, generation, cleanup, integration, motion, feedback, performance, or scope?
4. What is the smallest change that can prove improvement?
5. What observable evidence can disprove the proposed fix?
6. Which outputs, tests, and approvals are affected?

Prefer controlled experiments on one variable rather than simultaneous prompt/model/refinement changes that make results uninterpretable. Preserve a baseline and choose methods using usable final outputs, not concept image beauty alone.

## 5. Visual production contract

Every game's art bible defines:
- Intended style and audience response; examples and explicit non-examples.
- Camera/projection, perspective, viewing scale, target viewport and object scale.
- Color palette and value grouping; focal hierarchy; key/fill/rim light intent where relevant.
- Shape language, material language, surface detail, edge treatment and texture treatment.
- Character/creature identity anchors, environment depth/layers, prop scale, UI visual grammar, and effect hierarchy.
- Asset-level dimensions, anchors/pivots, transparency/alpha policy, animation needs, engine import settings and review criteria.

For an individual asset, use **specify → reference → generate → compare → select → refine → validate technically → integrate → inspect in context → approve/reject**. Do not bypass selection and in-game inspection for important art.

## 6. Animation contract

Animation begins with gameplay intention and key poses, not a list of generated pictures. Define action meaning, anticipation, contact, follow-through, recovery, timing, loops, anchor, ground/foot contact, identity invariants, and transitions. Use the method that preserves those invariants: frame-by-frame, conditioned keyframes, cutout/rigging, Blender or authored engine animation. Use interpolation only when a visual comparison shows that it improves motion without damaging silhouette, alpha, timing or identity.

## 7. Code and integration contract

- Separate domain decisions from provider/engine APIs with explicit adapters.
- Use workspace-scoped paths; user-generated names are slugs, not direct paths.
- Avoid global mutable state and hidden provider calls.
- Bound input size, subprocess timeouts, memory-heavy concurrency and output sizes.
- Never shell-interpolate untrusted prompts or filenames into command strings.
- Keep game rules authoritative in gameplay systems; VFX/audio show results but do not substitute for gameplay state.
- Test regression behavior on the real engine/harness where feasible, not only mocked Python functions.

## 8. Release contract

A release is a frozen candidate with a known source version, export preset, engine/tool version, test evidence, dependencies, model/asset rights status, provenance manifests, and verified archive hashes. After any code/asset edit affecting output, rebuild and retest. Human art-direction sign-off, target-platform cold playtest and rights review stay open until real reviewer decisions exist.

## 9. Postmortem rules

Record actual time and material costs where measured. Label estimates and qualitative observations. Generalize only after more than one sufficiently similar experiment or cite external evidence that explains why a finding should generalize. Promote reusable lessons to skills with a description of the context and known exceptions.
