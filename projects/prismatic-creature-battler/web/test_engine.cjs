const assert = require("node:assert/strict");
const eng = require("./engine.js");

function runTests() {
  // 1. Roster completeness: 8 distinct creatures, Origins, Instincts, Signatures
  assert.equal(eng.ROSTER.length, 8, "Roster must contain exactly 8 creatures");
  const origins = new Set(eng.ROSTER.map((c) => c.origin));
  const instincts = new Set(eng.ROSTER.map((c) => c.instinct));
  assert.equal(origins.size, 8, "All 8 creatures must have distinct Origins");
  assert.equal(instincts.size, 8, "All 8 creatures must have distinct Instincts");

  // 2. Signature Resonance Trio: Tempest Wyrm + Prismhart + Riftstalker
  const s1 = eng.runFullSimulation({
    playerSlots: ["prismhart", "pyrewarden", "abyssal-ryu", "tempest-wyrm", "riftstalker", "solarius"],
    playerCaptain: 3,
    playerDirective: "prism-overcharge",
    enemySlots: eng.OPPONENT_GAUNTLET[0].slots,
    enemyCaptain: 0,
    enemyDirective: "vanguard-bastion",
    enemyStatMultiplier: 1.05
  });
  assert.equal(s1.winner, "player", "Voltbrand Resonance Chain must defeat higher-stat Round 1 brute lineup");
  assert.ok(s1.totalResonanceChains >= 5, "Battle must trigger multiple Refractive Resonance chains");
  assert.ok(s1.playerConvergences >= 1, "Prism Gauge must reach 100% and unleash Convergence");

  // Verify Prismhart & Riftstalker specifically triggered Resonance
  const prismhartUnit = s1.playerUnits.find((u) => u.id === "prismhart");
  const riftstalkerUnit = s1.playerUnits.find((u) => u.id === "riftstalker");
  assert.ok(prismhartUnit.stats.resonanceTriggers >= 1, "Prismhart must trigger Refractive Ward from Voltbrand");
  assert.ok(riftstalkerUnit.stats.resonanceTriggers >= 1, "Riftstalker must trigger Phase Rend on marked enemy");

  // 3. Tactical Counterplay & Positioning Proof (Round 3 Apex)
  const g3 = eng.OPPONENT_GAUNTLET[2];
  const unadapted = eng.runFullSimulation({
    playerSlots: eng.ARCHETYPES[0].slots,
    playerCaptain: 3,
    playerDirective: "prism-overcharge",
    enemySlots: g3.slots,
    enemyCaptain: g3.captainSlot,
    enemyDirective: g3.directive,
    enemyStatMultiplier: g3.statMultiplier
  });
  const adapted = eng.runFullSimulation({
    playerSlots: eng.ARCHETYPES[0].slots,
    playerCaptain: 4, // Promote Riftstalker to Captain
    playerDirective: "phase-ambush", // Switch to Void Flank Protocol
    enemySlots: g3.slots,
    enemyCaptain: g3.captainSlot,
    enemyDirective: g3.directive,
    enemyStatMultiplier: g3.statMultiplier
  });
  assert.equal(unadapted.winner, "enemy", "Unadapted default setup loses to Round 3 Grand Archon");
  assert.equal(adapted.winner, "player", "Adapting Captain + Tactical Directive flips Round 3 to a decisive victory");

  // 4. Non-Pay-to-Win Cosmetic Foil Invariance Proof
  const foilRunA = eng.runFullSimulation({
    playerSlots: eng.ARCHETYPES[0].slots,
    foilMap: {
      "tempest-wyrm": "prismatic-spectrum",
      "prismhart": "relic-foil",
      "riftstalker": "phantom-foil"
    }
  });
  const foilRunB = eng.runFullSimulation({
    playerSlots: eng.ARCHETYPES[0].slots,
    foilMap: {
      "tempest-wyrm": "standard-edition",
      "prismhart": "standard-edition",
      "riftstalker": "standard-edition"
    }
  });
  assert.equal(foilRunA.tick, foilRunB.tick, "Foil edition must not change battle tick count");
  assert.equal(foilRunA.totalResonanceChains, foilRunB.totalResonanceChains, "Foil edition must not change Resonance triggers");
  assert.deepEqual(
    foilRunA.playerUnits.map((u) => u.hp),
    foilRunB.playerUnits.map((u) => u.hp),
    "Foil edition must have zero effect on unit HP outcomes"
  );

  console.log("ALL 4 ENGINE CONTRACT SUITES PASSED (Roster, Resonance Trio, Counterplay Adaptation, Cosmetic Fairness).");
}

runTests();
