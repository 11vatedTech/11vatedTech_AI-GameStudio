/**
 * The Prismatic Creature Battler — Authoritative Refractive Resonance Engine
 * Works identically in Node.js (automated tests) and Browser (interactive Web/Canvas runtime).
 */
(function (root, factory) {
  if (typeof module === "object" && module.exports) {
    module.exports = factory();
  } else {
    root.PrismaticEngine = factory();
  }
})(typeof self !== "undefined" ? self : this, function () {
  "use strict";

  const FOIL_EDITIONS = [
    {
      id: "prismatic-spectrum",
      name: "Prismatic Spectrum",
      tag: "Iridescent Foil",
      desc: "Rainbow micro-hex diffraction, shifting metallic scale highlights, and luminous crystal wing dispersion.",
      affectsGameplay: false
    },
    {
      id: "phantom-foil",
      name: "Phantom Foil",
      tag: "Dark Holographic",
      desc: "Near-black obsidian chrome, oil-slick violet/cyan rainbows, and deep shadow relief for void & eclipse entities.",
      affectsGameplay: false
    },
    {
      id: "relic-foil",
      name: "Relic Foil",
      tag: "Embossed Metallic",
      desc: "Antique gold and platinum engraving, illuminated sacred runes, and raised filigree borders for ancient guardians.",
      affectsGameplay: false
    },
    {
      id: "standard-edition",
      name: "Standard Sanctuary",
      tag: "Core Collector",
      desc: "Clean obsidian collector frame with subtle Origin rim lighting.",
      affectsGameplay: false
    }
  ];

  const ROSTER = [
    {
      id: "tempest-wyrm",
      name: "Tempest Wyrm",
      origin: "Storm",
      instinct: "Hunter",
      signature: "Voltbrand",
      cost: 3,
      hp: 1220,
      atk: 192,
      def: 36,
      spd: 1.38,
      color: "#38E5FF",
      secondaryColor: "#1A6BFF",
      defaultFoil: "prismatic-spectrum",
      serial: "PCB-001 // UR",
      sprite: "assets/tempest-wyrm.png",
      animGif: "assets/tempest-wyrm_idle.gif",
      resonanceRole: "Applies [VOLTBRAND] electrical mark on strike. Marked targets suffer +30% Resonance damage and trigger adjacent Crystal Guardians.",
      lore: "Born in the upper ionospheric vaults, its wing-membranes store storm-lines that only discharge when refracted through living quartz."
    },
    {
      id: "prismhart",
      name: "Prismhart",
      origin: "Crystal",
      instinct: "Guardian",
      signature: "Refractive Ward",
      cost: 3,
      hp: 1880,
      atk: 118,
      def: 72,
      spd: 0.96,
      color: "#7AF0FF",
      secondaryColor: "#B784FF",
      defaultFoil: "prismatic-spectrum",
      serial: "PCB-002 // UR",
      sprite: "assets/prismhart.png",
      animGif: "assets/prismhart_idle.gif",
      resonanceRole: "When an adjacent ally applies or triggers [VOLTBRAND], grants [REFRACTIVE WARD] (155 Shield) to self & ally and arcs 95 Crystal DMG to a secondary foe.",
      lore: "An ancient automaton stag whose diamond antlers split incoming lightning into protective geometric wards."
    },
    {
      id: "riftstalker",
      name: "Riftstalker",
      origin: "Void",
      instinct: "Assassin",
      signature: "Phase Rend",
      cost: 3,
      hp: 1080,
      atk: 232,
      def: 30,
      spd: 1.46,
      color: "#C25CFF",
      secondaryColor: "#38E5FF",
      defaultFoil: "phantom-foil",
      serial: "PCB-003 // UR",
      sprite: "assets/riftstalker.png",
      animGif: "assets/riftstalker_idle.gif",
      resonanceRole: "Phases past frontline defenders to strike any enemy bearing [VOLTBRAND] or [ECLIPSE TETHER] for 175% critical Phase Rend damage.",
      lore: "It does not cross space—it folds the electrical tension between a marked quarry and its own scythe-blades."
    },
    {
      id: "pyrewarden",
      name: "Pyrewarden",
      origin: "Flame",
      instinct: "Bruiser",
      signature: "Solar Crucible",
      cost: 3,
      hp: 1740,
      atk: 174,
      def: 58,
      spd: 1.06,
      color: "#FF6B4A",
      secondaryColor: "#F5C451",
      defaultFoil: "relic-foil",
      serial: "PCB-004 // SR",
      sprite: "assets/pyrewarden.png",
      animGif: "assets/pyrewarden.png",
      resonanceRole: "Sears target with [SOLAR BRAND] (70 burn DMG). When shielded by [REFRACTIVE WARD] or [ASTROLABE HALO], erupts a 135 DMG magma wave.",
      lore: "Forged in the sunken calderas, its basalt plates glow brighter each time allied light strikes its mane."
    },
    {
      id: "sylvan-aegis",
      name: "Sylvan Aegis",
      origin: "Verdant",
      instinct: "Healer",
      signature: "Heartwood Bloom",
      cost: 2,
      hp: 1520,
      atk: 124,
      def: 50,
      spd: 1.12,
      color: "#2CEAA3",
      secondaryColor: "#F5C451",
      defaultFoil: "relic-foil",
      serial: "PCB-005 // SR",
      sprite: "assets/sylvan-aegis.png",
      animGif: "assets/sylvan-aegis.png",
      resonanceRole: "Heals most injured ally for 195 HP. If target holds [REFRACTIVE WARD] or [SACRED CURRENT], grants +24 ATK Overgrowth.",
      lore: "Amber sap courses through its rune-carved bark, remembers every season, and knits shattered crystal back together."
    },
    {
      id: "abyssal-ryu",
      name: "Abyssal Ryu",
      origin: "Tide",
      instinct: "Controller",
      signature: "Sacred Current",
      cost: 3,
      hp: 1580,
      atk: 156,
      def: 54,
      spd: 1.18,
      color: "#00E5B8",
      secondaryColor: "#38E5FF",
      defaultFoil: "prismatic-spectrum",
      serial: "PCB-006 // UR",
      sprite: "assets/abyssal-ryu.png",
      animGif: "assets/abyssal-ryu.png",
      resonanceRole: "Inflicts [TIDAL LOCK] (-20% SPD) and conducts [VOLTBRAND] to an unmarked enemy, generating +18 Prism Gauge.",
      lore: "Ryu embodies the raw pressure of the ocean trenches, guiding spirit-currents through sacred jade coils."
    },
    {
      id: "solarius",
      name: "Solarius",
      origin: "Astral",
      instinct: "Support",
      signature: "Astrolabe Halo",
      cost: 3,
      hp: 1360,
      atk: 148,
      def: 44,
      spd: 1.28,
      color: "#F5C451",
      secondaryColor: "#7AF0FF",
      defaultFoil: "prismatic-spectrum",
      serial: "PCB-007 // UR",
      sprite: "assets/solarius.png",
      animGif: "assets/solarius_idle.gif",
      resonanceRole: "Amplifies team Prism Gauge gain by +30% and detonates [SOLAR BRAND] on enemies to grant 130 Astral Shield to allies.",
      lore: "Its brass astrolabe rings spin in harmonic lockstep with the sanctuary stars, focusing scattered sparks into solar flare."
    },
    {
      id: "umbral-weaver",
      name: "Umbral Weaver",
      origin: "Eclipse",
      instinct: "Disruptor",
      signature: "Crescent Tether",
      cost: 2,
      hp: 1290,
      atk: 166,
      def: 42,
      spd: 1.32,
      color: "#D06BFF",
      secondaryColor: "#FF4D6D",
      defaultFoil: "phantom-foil",
      serial: "PCB-008 // SR",
      sprite: "assets/umbral-weaver.png",
      animGif: "assets/umbral-weaver.png",
      resonanceRole: "Binds the furthest backline enemy with [ECLIPSE TETHER], echoing 40% of Resonance damage and enabling Riftstalker Phase Rend.",
      lore: "Spinning gravity-threads between moon-shadow and prism light, it turns an opponent's backline into a shared lightning rod."
    }
  ];

  const ARCHETYPES = [
    {
      id: "voltbrand-chain",
      name: "Storm · Crystal · Void — Voltbrand Convergence",
      directive: "prism-overcharge",
      badge: "Signature Resonance Trio",
      summary: "Tempest Wyrm marks targets with Voltbrand -> adjacent Prismhart refracts marks into shields & arcs -> Riftstalker phases past frontline to execute marked foes.",
      slots: ["prismhart", "pyrewarden", "abyssal-ryu", "tempest-wyrm", "riftstalker", "solarius"],
      captainSlot: 3
    },
    {
      id: "solar-crucible",
      name: "Flame · Astral · Eclipse — Solar Crucible",
      directive: "vanguard-bastion",
      badge: "High-Sustain Burn & Detonation",
      summary: "Pyrewarden sears frontline with Solar Brand -> Solarius detonates brands into team-wide Astral Shields -> Umbral Weaver tethers backline.",
      slots: ["pyrewarden", "prismhart", "sylvan-aegis", "solarius", "umbral-weaver", "tempest-wyrm"],
      captainSlot: 0
    },
    {
      id: "abyssal-bloom",
      name: "Tide · Verdant · Crystal — Sacred Sanctuary",
      directive: "phase-ambush",
      badge: "Control & Overgrowth Scaling",
      summary: "Abyssal Ryu spreads Voltbrand & Tidal Lock -> Sylvan Aegis turns wards into ATK Overgrowth -> Riftstalker and Umbral Weaver collapse the backline.",
      slots: ["prismhart", "sylvan-aegis", "abyssal-ryu", "umbral-weaver", "riftstalker", "tempest-wyrm"],
      captainSlot: 2
    }
  ];

  const DIRECTIVES = [
    {
      id: "prism-overcharge",
      name: "Directive I: Refractive Overcharge",
      desc: "Resonance interactions generate +25% Prism Gauge; Convergence deals +20% bonus damage."
    },
    {
      id: "vanguard-bastion",
      name: "Directive II: Crystalline Bastion",
      desc: "Frontline units start combat with 180 Refractive Shield and +12 DEF."
    },
    {
      id: "phase-ambush",
      name: "Directive III: Void Flank Protocol",
      desc: "Backline Hunters, Assassins, and Disruptors gain +18% ATK and prioritize marked targets immediately."
    }
  ];

  const OPPONENT_GAUNTLET = [
    {
      round: 1,
      title: "Round 1 — Ironclad Vanguard (Raw Stat Brute Lineup)",
      desc: "High raw HP/ATK frontline bruisers with weak cross-unit synergy. Prove that Refractive Resonance chains defeat superior raw stats.",
      directive: "vanguard-bastion",
      statMultiplier: 1.05,
      slots: ["pyrewarden", "sylvan-aegis", "pyrewarden", "abyssal-ryu", "sylvan-aegis", "pyrewarden"],
      captainSlot: 0
    },
    {
      round: 2,
      title: "Round 2 — Eclipse Mirror Coven (Backline Disruptors)",
      desc: "Umbral Weavers and Riftstalkers try to snipe your carries. Position Prismhart adjacent to Tempest Wyrm or deploy Solar Crucible sustain to survive and counter.",
      directive: "phase-ambush",
      statMultiplier: 0.96,
      slots: ["pyrewarden", "abyssal-ryu", "sylvan-aegis", "umbral-weaver", "riftstalker", "tempest-wyrm"],
      captainSlot: 4
    },
    {
      round: 3,
      title: "Round 3 — Grand Archon's Prismatic Apex",
      desc: "Full 6-unit Championship Resonance formation. Requires optimal Captain placement, Directive selection, and Prism Gauge Convergence.",
      directive: "prism-overcharge",
      statMultiplier: 0.98,
      slots: ["pyrewarden", "sylvan-aegis", "abyssal-ryu", "tempest-wyrm", "umbral-weaver", "solarius"],
      captainSlot: 3
    }
  ];

  function getCreature(id) {
    return ROSTER.find(function (c) { return c.id === id; }) || ROSTER[0];
  }

  function createUnitInstance(creatureId, slotIndex, side, options) {
    const opts = options || {};
    const proto = getCreature(creatureId);
    const mult = opts.statMultiplier || 1.0;
    const isCaptain = Boolean(opts.isCaptain);
    const directive = opts.directive || "prism-overcharge";
    const isFrontline = slotIndex < 3;

    // Crucial Rule: Foil Edition, Serial Number, and Cosmetic Portrait NEVER alter gameplay stats!
    const baseHp = Math.round(proto.hp * mult * (isCaptain ? 1.12 : 1.0));
    const baseAtk = Math.round(proto.atk * mult * (isCaptain && !isFrontline ? 1.12 : 1.0));
    const baseDef = Math.round(proto.def + (directive === "vanguard-bastion" && isFrontline ? 12 : 0));
    const finalAtk = Math.round(baseAtk * (directive === "phase-ambush" && !isFrontline ? 1.18 : 1.0));
    const startingShield = directive === "vanguard-bastion" && isFrontline ? 180 : 0;

    return {
      uid: side + "-slot-" + slotIndex + "-" + proto.id,
      id: proto.id,
      name: proto.name,
      origin: proto.origin,
      instinct: proto.instinct,
      signature: proto.signature,
      color: proto.color,
      secondaryColor: proto.secondaryColor,
      sprite: proto.sprite,
      foil: opts.foil || proto.defaultFoil,
      serial: proto.serial,
      side: side,
      slot: slotIndex,
      row: isFrontline ? "Frontline" : "Backline",
      col: slotIndex % 3,
      isCaptain: isCaptain,
      maxHp: baseHp,
      hp: baseHp,
      atk: finalAtk,
      def: baseDef,
      spd: proto.spd,
      shield: startingShield,
      energy: 0,
      marks: {
        voltbrand: 0,
        solarBrand: 0,
        tidalLock: 0,
        eclipseTether: 0
      },
      stats: {
        damageDealt: 0,
        shieldGranted: 0,
        resonanceTriggers: 0,
        kills: 0
      }
    };
  }

  function areAdjacent(slotA, slotB) {
    if (slotA === slotB) return false;
    const rowA = Math.floor(slotA / 3), colA = slotA % 3;
    const rowB = Math.floor(slotB / 3), colB = slotB % 3;
    return Math.abs(rowA - rowB) + Math.abs(colA - colB) <= 1;
  }

  function createBattleState(config) {
    const playerSlots = (config && config.playerSlots) || ARCHETYPES[0].slots;
    const enemySlots = (config && config.enemySlots) || OPPONENT_GAUNTLET[0].slots;
    const playerCaptain = config && typeof config.playerCaptain === "number" ? config.playerCaptain : 3;
    const enemyCaptain = config && typeof config.enemyCaptain === "number" ? config.enemyCaptain : 0;
    const playerDirective = (config && config.playerDirective) || "prism-overcharge";
    const enemyDirective = (config && config.enemyDirective) || "vanguard-bastion";
    const enemyMult = (config && config.enemyStatMultiplier) || 1.06;
    const foilMap = (config && config.foilMap) || {};

    const playerUnits = playerSlots.map(function (cid, idx) {
      return createUnitInstance(cid, idx, "player", {
        isCaptain: idx === playerCaptain,
        directive: playerDirective,
        foil: foilMap[cid] || getCreature(cid).defaultFoil
      });
    });

    const enemyUnits = enemySlots.map(function (cid, idx) {
      return createUnitInstance(cid, idx, "enemy", {
        isCaptain: idx === enemyCaptain,
        directive: enemyDirective,
        statMultiplier: enemyMult
      });
    });

    return {
      tick: 0,
      maxTicks: 48,
      finished: false,
      winner: null,
      playerDirective: playerDirective,
      enemyDirective: enemyDirective,
      playerGauge: 0,
      enemyGauge: 0,
      playerConvergences: 0,
      enemyConvergences: 0,
      totalResonanceChains: 0,
      playerUnits: playerUnits,
      enemyUnits: enemyUnits,
      events: [],
      log: [
        "BATTLE START — Cards materialize onto the Prismatic Sanctuary (6v6 Hybrid Arena).",
        "Directive Active: " + playerDirective.toUpperCase() + " | Captain Slot #" + (playerCaptain + 1)
      ]
    };
  }

  function dealDamage(attacker, defender, rawAmount, state, tag) {
    if (defender.hp <= 0) return 0;
    let dmg = Math.max(36, Math.round(rawAmount * 1.45 * (100 / (100 + defender.def))));
    if (defender.marks.voltbrand > 0 && tag !== "VOLTBRAND_INITIAL") {
      dmg = Math.round(dmg * 1.32);
    }
    let remaining = dmg;
    if (defender.shield > 0) {
      const absorbed = Math.min(defender.shield, remaining);
      defender.shield -= absorbed;
      remaining -= absorbed;
    }
    const actual = Math.min(defender.hp, remaining);
    defender.hp = Math.max(0, defender.hp - actual);
    if (attacker) {
      attacker.stats.damageDealt += dmg;
      if (defender.hp === 0) attacker.stats.kills += 1;
    }
    return dmg;
  }

  function addPrismGauge(state, side, baseAmount, reason) {
    const allies = side === "player" ? state.playerUnits : state.enemyUnits;
    const foes = side === "player" ? state.enemyUnits : state.playerUnits;
    const directive = side === "player" ? state.playerDirective : state.enemyDirective;
    const hasSolarius = allies.some(function (u) { return u.hp > 0 && u.id === "solarius"; });

    let gain = baseAmount;
    if (hasSolarius) gain *= 1.30;
    if (directive === "prism-overcharge") gain *= 1.25;
    gain = Math.round(gain);

    if (side === "player") {
      state.playerGauge = Math.min(100, state.playerGauge + gain);
      if (state.playerGauge >= 100) {
        state.playerGauge = 0;
        state.playerConvergences += 1;
        triggerConvergence(state, "player", allies, foes, directive);
      }
    } else {
      state.enemyGauge = Math.min(100, state.enemyGauge + gain);
      if (state.enemyGauge >= 100) {
        state.enemyGauge = 0;
        state.enemyConvergences += 1;
        triggerConvergence(state, "enemy", allies, foes, directive);
      }
    }
  }

  function triggerConvergence(state, side, allies, foes, directive) {
    const bonus = directive === "prism-overcharge" ? 1.25 : 1.0;
    const aoeDmg = Math.round(255 * bonus);
    const aliveAllies = allies.filter(function (u) { return u.hp > 0; });
    const aliveFoes = foes.filter(function (u) { return u.hp > 0; });
    const anchor = aliveAllies[0];

    aliveAllies.forEach(function (u) {
      u.shield += 110;
      u.atk = Math.round(u.atk * 1.12);
    });
    aliveFoes.forEach(function (f) {
      f.marks.voltbrand = Math.max(f.marks.voltbrand, 2);
      dealDamage(anchor, f, aoeDmg, state, "CONVERGENCE");
    });

    const msg = "★ PRISM CONVERGENCE (" + side.toUpperCase() + "): Prismatic Supernova deals " + aoeDmg + " AOE DMG, marks all foes with [VOLTBRAND], and grants +165 Team Shield!";
    state.log.unshift(msg);
    state.events.push({
      tick: state.tick,
      type: "CONVERGENCE",
      side: side,
      sourceSlot: anchor ? anchor.slot : 0,
      targetSlot: aliveFoes[0] ? aliveFoes[0].slot : 0,
      color: "#F5C451",
      label: "PRISM CONVERGENCE SUPERNOVA",
      text: msg
    });
  }

  function selectTarget(actor, foes) {
    const aliveFoes = foes.filter(function (f) { return f.hp > 0; });
    if (!aliveFoes.length) return null;

    // Riftstalker Phase Rend: target marked enemy in backline or frontline first!
    if (actor.id === "riftstalker") {
      const markedBack = aliveFoes.find(function (f) {
        return f.slot >= 3 && (f.marks.voltbrand > 0 || f.marks.eclipseTether > 0);
      });
      if (markedBack) return markedBack;
      const anyMarked = aliveFoes.find(function (f) {
        return f.marks.voltbrand > 0 || f.marks.eclipseTether > 0;
      });
      if (anyMarked) return anyMarked;
    }

    // Umbral Weaver Crescent Tether targets backline first
    if (actor.id === "umbral-weaver") {
      const backline = aliveFoes.filter(function (f) { return f.slot >= 3; });
      if (backline.length) return backline[backline.length - 1];
    }

    // Standard positional targeting: Frontline first (preferring same column), then Backline
    const front = aliveFoes.filter(function (f) { return f.slot < 3; });
    const pool = front.length ? front : aliveFoes;
    const sameCol = pool.find(function (f) { return f.col === actor.col; });
    return sameCol || pool[0];
  }

  function stepBattle(state) {
    if (state.finished) return state;
    state.tick += 1;
    state.events = [];

    const aliveP = state.playerUnits.filter(function (u) { return u.hp > 0; });
    const aliveE = state.enemyUnits.filter(function (u) { return u.hp > 0; });
    if (!aliveP.length || !aliveE.length || state.tick > state.maxTicks) {
      state.finished = true;
      const pHp = aliveP.reduce(function (s, u) { return s + u.hp; }, 0);
      const eHp = aliveE.reduce(function (s, u) { return s + u.hp; }, 0);
      state.winner = pHp >= eHp ? "player" : "enemy";
      state.log.unshift("MATCH COMPLETE — Winner: " + state.winner.toUpperCase() + " (" + aliveP.length + " allies standing, " + state.totalResonanceChains + " Resonance chains triggered).");
      return state;
    }

    const order = aliveP.concat(aliveE).sort(function (a, b) {
      const effA = a.spd * (a.marks.tidalLock > 0 ? 0.8 : 1.0);
      const effB = b.spd * (b.marks.tidalLock > 0 ? 0.8 : 1.0);
      if (Math.abs(effB - effA) > 0.001) return effB - effA;
      return a.side === "player" ? -1 : 1;
    });

    const actor = order[(state.tick - 1) % order.length];
    if (!actor || actor.hp <= 0) return state;

    const allies = actor.side === "player" ? state.playerUnits : state.enemyUnits;
    const foes = actor.side === "player" ? state.enemyUnits : state.playerUnits;
    const target = selectTarget(actor, foes);
    if (!target) return state;

    // Execute creature signature + Refractive Resonance chain
    if (actor.id === "tempest-wyrm") {
      target.marks.voltbrand = 3;
      const dmg = dealDamage(actor, target, actor.atk * 1.12, state, "VOLTBRAND_INITIAL");
      const msg = actor.name + " (" + actor.side + ") strikes " + target.name + " with [Voltbrand] (" + dmg + " DMG) -> Marks with ⚡VOLTBRAND!";
      state.log.unshift(msg);
      state.events.push({
        tick: state.tick,
        type: "SKILL",
        side: actor.side,
        sourceSlot: actor.slot,
        targetSlot: target.slot,
        color: "#38E5FF",
        label: "⚡ VOLTBRAND",
        text: msg
      });
      addPrismGauge(state, actor.side, 18, "Voltbrand");

      // Check Refractive Resonance with Prismhart (adjacent or on team, amplified if adjacent!)
      allies.forEach(function (ally) {
        if (ally.hp > 0 && ally.id === "prismhart") {
          const adjBonus = areAdjacent(actor.slot, ally.slot) ? 1.35 : 1.0;
          const shieldAmt = Math.round(155 * adjBonus);
          ally.shield += shieldAmt;
          actor.shield += Math.round(125 * adjBonus);
          ally.stats.shieldGranted += shieldAmt + Math.round(125 * adjBonus);
          ally.stats.resonanceTriggers += 1;
          state.totalResonanceChains += 1;

          const otherFoes = foes.filter(function (f) { return f.hp > 0 && f.uid !== target.uid; });
          const arcTarget = otherFoes[0] || target;
          const arcDmg = dealDamage(ally, arcTarget, 95 * adjBonus, state, "REFRACTIVE_ARC");
          arcTarget.marks.voltbrand = Math.max(arcTarget.marks.voltbrand, 2);

          const rMsg = "↳ RESONANCE [Refractive Ward]: " + ally.name + (areAdjacent(actor.slot, ally.slot) ? " (Adjacent +35%)" : "") + " refracts Voltbrand into +" + shieldAmt + " Crystal Shield & arcs " + arcDmg + " DMG to " + arcTarget.name + "!";
          state.log.unshift(rMsg);
          state.events.push({
            tick: state.tick,
            type: "RESONANCE",
            side: actor.side,
            sourceSlot: ally.slot,
            targetSlot: arcTarget.slot,
            allySlot: actor.slot,
            color: "#7AF0FF",
            label: "❖ REFRACTIVE WARD CHAIN",
            text: rMsg
          });
          addPrismGauge(state, actor.side, 24, "Refractive Ward Chain");
        }
      });
    } else if (actor.id === "riftstalker") {
      const isMarked = target.marks.voltbrand > 0 || target.marks.eclipseTether > 0;
      const mult = isMarked ? 1.75 : 1.05;
      const dmg = dealDamage(actor, target, actor.atk * mult, state, "PHASE_REND");
      if (isMarked) {
        actor.stats.resonanceTriggers += 1;
        state.totalResonanceChains += 1;
        const msg = "↳ RESONANCE [Phase Rend]: " + actor.name + " phases past frontline to ambush marked " + target.name + " for " + dmg + " CRITICAL VOID DMG!";
        state.log.unshift(msg);
        state.events.push({
          tick: state.tick,
          type: "RESONANCE",
          side: actor.side,
          sourceSlot: actor.slot,
          targetSlot: target.slot,
          color: "#C25CFF",
          label: "✦ PHASE REND ASSASSINATION",
          text: msg
        });
        addPrismGauge(state, actor.side, 26, "Phase Rend Resonance");
      } else {
        const msg = actor.name + " slashes " + target.name + " for " + dmg + " DMG.";
        state.log.unshift(msg);
        state.events.push({
          tick: state.tick,
          type: "ATTACK",
          side: actor.side,
          sourceSlot: actor.slot,
          targetSlot: target.slot,
          color: "#C25CFF",
          label: "VOID SLASH",
          text: msg
        });
        addPrismGauge(state, actor.side, 12, "Void Slash");
      }
    } else if (actor.id === "pyrewarden") {
      target.marks.solarBrand = 3;
      const dmg = dealDamage(actor, target, actor.atk * 1.15, state, "SOLAR_CRUCIBLE");
      const msg = actor.name + " cleaves " + target.name + " with [Solar Crucible] (" + dmg + " DMG) & applies ☀SOLAR BRAND!";
      state.log.unshift(msg);
      state.events.push({
        tick: state.tick,
        type: "SKILL",
        side: actor.side,
        sourceSlot: actor.slot,
        targetSlot: target.slot,
        color: "#FF6B4A",
        label: "☀ SOLAR CRUCIBLE",
        text: msg
      });
      if (actor.shield > 0) {
        actor.stats.resonanceTriggers += 1;
        state.totalResonanceChains += 1;
        foes.filter(function (f) { return f.hp > 0 && f.slot < 3; }).forEach(function (f) {
          dealDamage(actor, f, 115, state, "MOLTEN_WAVE");
        });
        state.log.unshift("↳ RESONANCE [Molten Refraction]: Shielded Pyrewarden erupts a 115 DMG magma wave across enemy Frontline!");
        addPrismGauge(state, actor.side, 22, "Molten Refraction");
      } else {
        addPrismGauge(state, actor.side, 14, "Solar Crucible");
      }
    } else if (actor.id === "solarius") {
      const dmg = dealDamage(actor, target, actor.atk, state, "ASTROLABE");
      const branded = foes.filter(function (f) { return f.hp > 0 && f.marks.solarBrand > 0; });
      if (branded.length > 0) {
        actor.stats.resonanceTriggers += 1;
        state.totalResonanceChains += 1;
        branded.forEach(function (bf) {
          dealDamage(actor, bf, 130, state, "SOLAR_DETONATION");
          bf.marks.solarBrand = 0;
        });
        allies.filter(function (a) { return a.hp > 0; }).forEach(function (a) {
          a.shield += 110;
        });
        const rMsg = "↳ RESONANCE [Astrolabe Halo]: Solarius detonates Solar Brand into 130 Astral DMG & +110 Team Shield!";
        state.log.unshift(rMsg);
        state.events.push({
          tick: state.tick,
          type: "RESONANCE",
          side: actor.side,
          sourceSlot: actor.slot,
          targetSlot: target.slot,
          color: "#F5C451",
          label: "☼ ASTROLABE HALO CHAIN",
          text: rMsg
        });
        addPrismGauge(state, actor.side, 26, "Astrolabe Detonation");
      } else {
        state.log.unshift(actor.name + " projects [Astrolabe Halo] at " + target.name + " (" + dmg + " DMG).");
        state.events.push({
          tick: state.tick,
          type: "SKILL",
          side: actor.side,
          sourceSlot: actor.slot,
          targetSlot: target.slot,
          color: "#F5C451",
          label: "☼ ASTROLABE RAY",
          text: actor.name + " hits " + target.name
        });
        addPrismGauge(state, actor.side, 16, "Astrolabe Ray");
      }
    } else if (actor.id === "abyssal-ryu") {
      target.marks.tidalLock = 2;
      const dmg = dealDamage(actor, target, actor.atk * 1.1, state, "SACRED_CURRENT");
      const markedFoe = foes.find(function (f) { return f.hp > 0 && f.marks.voltbrand > 0; });
      if (markedFoe) {
        actor.stats.resonanceTriggers += 1;
        state.totalResonanceChains += 1;
        foes.filter(function (f) { return f.hp > 0; }).slice(0, 3).forEach(function (f) {
          f.marks.voltbrand = Math.max(f.marks.voltbrand, 2);
          dealDamage(actor, f, 85, state, "CONDUCTIVE_TIDE");
        });
        const rMsg = "↳ RESONANCE [Sacred Current]: Abyssal Ryu conducts ⚡Voltbrand across the enemy formation (+85 Tide DMG)!";
        state.log.unshift(rMsg);
        state.events.push({
          tick: state.tick,
          type: "RESONANCE",
          side: actor.side,
          sourceSlot: actor.slot,
          targetSlot: target.slot,
          color: "#00E5B8",
          label: "≈ CONDUCTIVE TIDE CHAIN",
          text: rMsg
        });
        addPrismGauge(state, actor.side, 24, "Conductive Tide");
      } else {
        state.log.unshift(actor.name + " surges [Sacred Current] into " + target.name + " (" + dmg + " DMG, Tidal Lock).");
        state.events.push({
          tick: state.tick,
          type: "SKILL",
          side: actor.side,
          sourceSlot: actor.slot,
          targetSlot: target.slot,
          color: "#00E5B8",
          label: "≈ SACRED CURRENT",
          text: actor.name + " hits " + target.name
        });
        addPrismGauge(state, actor.side, 15, "Sacred Current");
      }
    } else if (actor.id === "sylvan-aegis") {
      const aliveAllies = allies.filter(function (a) { return a.hp > 0; }).sort(function (a, b) {
        return (a.hp / a.maxHp) - (b.hp / b.maxHp);
      });
      const healTarget = aliveAllies[0] || actor;
      healTarget.hp = Math.min(healTarget.maxHp, healTarget.hp + 195);
      const dmg = dealDamage(actor, target, actor.atk * 0.9, state, "HEARTWOOD");
      if (healTarget.shield > 0) {
        healTarget.atk += 24;
        actor.stats.resonanceTriggers += 1;
        state.totalResonanceChains += 1;
        const rMsg = "↳ RESONANCE [Heartwood Bloom]: Sylvan Aegis heals " + healTarget.name + " (+195 HP) & crystallizes shield into +24 ATK Overgrowth!";
        state.log.unshift(rMsg);
        state.events.push({
          tick: state.tick,
          type: "RESONANCE",
          side: actor.side,
          sourceSlot: actor.slot,
          targetSlot: healTarget.slot,
          color: "#2CEAA3",
          label: "❀ HEARTWOOD OVERGROWTH",
          text: rMsg
        });
        addPrismGauge(state, actor.side, 20, "Heartwood Resonance");
      } else {
        state.log.unshift(actor.name + " restores +195 HP to " + healTarget.name + " & strikes " + target.name + " (" + dmg + " DMG).");
        state.events.push({
          tick: state.tick,
          type: "SKILL",
          side: actor.side,
          sourceSlot: actor.slot,
          targetSlot: target.slot,
          color: "#2CEAA3",
          label: "❀ HEARTWOOD BLOOM",
          text: actor.name + " heals " + healTarget.name
        });
        addPrismGauge(state, actor.side, 14, "Heartwood Bloom");
      }
    } else if (actor.id === "umbral-weaver") {
      target.marks.eclipseTether = 3;
      const dmg = dealDamage(actor, target, actor.atk * 1.12, state, "CRESCENT_TETHER");
      actor.stats.resonanceTriggers += 1;
      state.totalResonanceChains += 1;
      const msg = "↳ RESONANCE [Crescent Tether]: " + actor.name + " binds backline " + target.name + " (" + dmg + " DMG) -> Opens Void Phase Rend lock!";
      state.log.unshift(msg);
      state.events.push({
        tick: state.tick,
        type: "RESONANCE",
        side: actor.side,
        sourceSlot: actor.slot,
        targetSlot: target.slot,
        color: "#D06BFF",
        label: "☾ CRESCENT TETHER",
        text: msg
      });
      addPrismGauge(state, actor.side, 20, "Crescent Tether");
    } else {
      // Prismhart direct strike
      const dmg = dealDamage(actor, target, actor.atk, state, "PRISM_LANCE");
      actor.shield += 110;
      const msg = actor.name + " lances " + target.name + " (" + dmg + " DMG) and fortifies +110 Crystal Shield.";
      state.log.unshift(msg);
      state.events.push({
        tick: state.tick,
        type: "SKILL",
        side: actor.side,
        sourceSlot: actor.slot,
        targetSlot: target.slot,
        color: "#7AF0FF",
        label: "❖ PRISM LANCE",
        text: msg
      });
      addPrismGauge(state, actor.side, 14, "Prism Lance");
    }

    if (state.log.length > 40) state.log.length = 40;

    // Check immediate victory
    const remP = state.playerUnits.filter(function (u) { return u.hp > 0; });
    const remE = state.enemyUnits.filter(function (u) { return u.hp > 0; });
    if (!remP.length || !remE.length) {
      state.finished = true;
      state.winner = remP.length > 0 ? "player" : "enemy";
      state.log.unshift("MATCH COMPLETE — Winner: " + state.winner.toUpperCase() + " (" + remP.length + " allies standing, " + state.totalResonanceChains + " Resonance chains triggered).");
    }
    return state;
  }

  function runFullSimulation(config) {
    const state = createBattleState(config);
    while (!state.finished && state.tick <= state.maxTicks) {
      stepBattle(state);
    }
    return state;
  }

  return {
    FOIL_EDITIONS: FOIL_EDITIONS,
    ROSTER: ROSTER,
    ARCHETYPES: ARCHETYPES,
    DIRECTIVES: DIRECTIVES,
    OPPONENT_GAUNTLET: OPPONENT_GAUNTLET,
    getCreature: getCreature,
    createUnitInstance: createUnitInstance,
    areAdjacent: areAdjacent,
    createBattleState: createBattleState,
    stepBattle: stepBattle,
    runFullSimulation: runFullSimulation
  };
});
