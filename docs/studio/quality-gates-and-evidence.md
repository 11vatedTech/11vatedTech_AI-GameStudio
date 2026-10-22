# Quality Gates and Evidence

## Gate 0 — Feasibility
**Pass when:** brief/rules/deadline/platform are explicit; required dependencies and model licenses are identified; constraints and blockers are recorded.

## Gate 1 — Design and scope
**Pass when:** distinctive concept, player fantasy, core loop, verbs, controls, success/failure/restart states, non-goals, art direction, and scoped backlog exist; mandatory work fits the time budget with release reserve.

## Gate 2 — Playable vertical slice
**Pass when:** real input changes game state; a player can perform the central mechanic and reach a designed outcome; state is not mocked; a test/harness and a person can reproduce it.

## Gate 3 — Creative and content integration
**Pass when:** the agent has produced and integrated the critical assets/audio/UI (or explicitly tracks candidate status); asset provenance and licensing records exist; engine references resolve; assets are inspected at gameplay scale; animation is inspected as authored movement. Agent production and iteration are the default; human creative approval is a separate gate only when the project explicitly requires it.

## Gate 4 — Release candidate
**Pass when:** relevant unit/integration/engine tests pass; target build launches; core play paths were played; performance is measured against target constraints; accessibility/usability checks completed; high-severity defects resolved or explicitly accepted.

## Gate 5 — Release
**Pass when:** source and binaries are versioned; release archive opens; hashes match; manifests, setup, dependencies and known limitations are included; model/assets rights have been reviewed; any explicitly required human art-direction sign-off and target-audience cold playtest are truly recorded. These are review gates, not a transfer of routine asset creation or testing work to the operator; agents should prepare candidate work, evidence, and automated playtest evidence themselves.

## Evidence types

| Type | Example | What it establishes | What it does not establish |
|---|---|---|---|
| Unit | path guard test | isolated logic follows assertions | external engine/provider behavior |
| Mock integration | Comfy API response fixture | request/response parser and failures | model availability or image quality |
| External integration | real Comfy output saved with hash | endpoint + model produced file at that time | fit to art direction |
| Engine validation | Godot headless import/export | engine process accepted project under that setup | good gameplay or human quality |
| Runtime harness | full sequence assertions | defined deterministic scenario passes | general human usability |
| Actual playtest | session/recording and notes | observed behavior in that build | universal audience response |
| Agent assessment | scored candidate with reasons | agent judgement was recorded | independent human approval |
| Human review | reviewer, decision, evidence | that human decision was given | legal facts outside scope of review |

Never collapse these into one green/red status. A command can succeed while a release is blocked. A game can technically pass while its art is weak. An attractive screenshot can hide broken gameplay.
