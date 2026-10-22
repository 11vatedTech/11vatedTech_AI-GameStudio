(function () {
  "use strict";

  const E = window.PrismaticEngine;
  const canvas = document.getElementById("sanctuaryCanvas");
  const ctx = canvas.getContext("2d");

  const state = {
    selectedCreatureId: "tempest-wyrm",
    selectedSlot: 3,
    roundIndex: 0,
    playerSlots: E.ARCHETYPES[0].slots.slice(),
    playerCaptain: E.ARCHETYPES[0].captainSlot,
    playerDirective: E.ARCHETYPES[0].directive,
    activeArchetypeId: E.ARCHETYPES[0].id,
    foilMap: {},
    battle: null,
    autoTimer: null,
    activeBeams: [],
    convergenceFlash: 0,
    animTime: 0,
    images: {}
  };

  E.ROSTER.forEach(function (c) {
    state.foilMap[c.id] = c.defaultFoil;
    const img = new Image();
    img.src = c.sprite;
    state.images[c.id] = img;
  });
  const arenaImg = new Image();
  arenaImg.src = "assets/sanctuary-arena.png";
  state.images["arena"] = arenaImg;

  function preloadBattleState() {
    const opp = E.OPPONENT_GAUNTLET[state.roundIndex];
    state.battle = E.createBattleState({
      playerSlots: state.playerSlots,
      playerCaptain: state.playerCaptain,
      playerDirective: state.playerDirective,
      enemySlots: opp.slots,
      enemyCaptain: opp.captainSlot,
      enemyDirective: opp.directive,
      enemyStatMultiplier: opp.statMultiplier,
      foilMap: state.foilMap
    });
    state.activeBeams = [];
    updateHUD();
  }

  function updateCardInspector() {
    const c = E.getCreature(state.selectedCreatureId);
    const foilId = state.foilMap[c.id] || c.defaultFoil;
    const foilObj = E.FOIL_EDITIONS.find(function (f) { return f.id === foilId; }) || E.FOIL_EDITIONS[0];

    const cardEl = document.getElementById("livingCard");
    cardEl.setAttribute("data-foil", foilId);
    cardEl.style.setProperty("--unit-color", c.color);

    document.getElementById("cardName").textContent = c.name;
    document.getElementById("cardOriginInstinct").textContent = c.origin + " · " + c.instinct;
    document.getElementById("cardCreatureImg").src = c.sprite;
    document.getElementById("cardCreatureImg").alt = c.name;
    document.getElementById("cardSignature").textContent = "Signature: " + c.signature;
    document.getElementById("cardDesc").textContent = c.resonanceRole;
    document.getElementById("statHpVal").textContent = c.hp;
    document.getElementById("statAtkVal").textContent = c.atk;
    document.getElementById("statDefVal").textContent = c.def;
    document.getElementById("statSpdVal").textContent = c.spd.toFixed(2);
    document.getElementById("cardSerial").textContent = c.serial;
    document.getElementById("cardFoilTag").textContent = foilObj.name;

    Array.from(document.querySelectorAll("[data-foil-btn]")).forEach(function (btn) {
      btn.classList.toggle("active", btn.getAttribute("data-foil-btn") === foilId);
    });
    Array.from(document.querySelectorAll("[data-roster-id]")).forEach(function (el) {
      el.classList.toggle("active", el.getAttribute("data-roster-id") === c.id);
    });
  }

  function buildLeftControls() {
    const foilWrap = document.getElementById("foilButtons");
    foilWrap.innerHTML = "";
    E.FOIL_EDITIONS.forEach(function (f) {
      const btn = document.createElement("button");
      btn.className = "btn";
      btn.setAttribute("data-foil-btn", f.id);
      btn.textContent = f.name;
      btn.title = f.desc;
      btn.addEventListener("click", function () {
        state.foilMap[state.selectedCreatureId] = f.id;
        updateCardInspector();
        if (!state.autoTimer && state.battle && state.battle.tick === 0) {
          preloadBattleState();
        }
      });
      foilWrap.appendChild(btn);
    });

    const rosterWrap = document.getElementById("rosterStrip");
    rosterWrap.innerHTML = "";
    E.ROSTER.forEach(function (c) {
      const cell = document.createElement("div");
      cell.className = "roster-mini";
      cell.setAttribute("data-roster-id", c.id);
      cell.innerHTML =
        '<img src="' + c.sprite + '" alt="' + c.name + '" />' +
        '<div class="roster-mini-name">' + c.name + '</div>' +
        '<div style="font-size:9px;color:' + c.color + ';">' + c.origin + '</div>';
      cell.addEventListener("click", function () {
        state.selectedCreatureId = c.id;
        updateCardInspector();
      });
      rosterWrap.appendChild(cell);
    });

    // 3D Parallax & Spectral Foil Tilt on the Living Card
    const cardEl = document.getElementById("livingCard");
    cardEl.addEventListener("mousemove", function (ev) {
      const rect = cardEl.getBoundingClientRect();
      const nx = (ev.clientX - rect.left) / rect.width;
      const ny = (ev.clientY - rect.top) / rect.height;
      const rotY = (nx - 0.5) * 20;
      const rotX = (0.5 - ny) * 18;
      cardEl.style.transform = "rotateX(" + rotX.toFixed(2) + "deg) rotateY(" + rotY.toFixed(2) + "deg)";
      cardEl.style.setProperty("--foil-angle", Math.round(110 + nx * 90) + "deg");
      cardEl.style.setProperty("--foil-x", Math.round(nx * 100) + "%");
      cardEl.style.setProperty("--foil-y", Math.round(ny * 100) + "%");
      const nebula = document.getElementById("cardNebula");
      nebula.style.transform = "translate(" + ((0.5 - nx) * 14).toFixed(1) + "px, " + ((0.5 - ny) * 14).toFixed(1) + "px)";
    });
    cardEl.addEventListener("mouseleave", function () {
      cardEl.style.transform = "rotateX(0deg) rotateY(0deg)";
    });
  }

  function buildCenterControls() {
    const archBar = document.getElementById("archetypeBar");
    archBar.innerHTML = "";
    E.ARCHETYPES.forEach(function (arch) {
      const btn = document.createElement("button");
      btn.className = "btn" + (arch.id === state.activeArchetypeId ? " active" : "");
      btn.setAttribute("data-arch-id", arch.id);
      btn.textContent = arch.name;
      btn.title = arch.summary;
      btn.addEventListener("click", function () {
        stopAutoBattle();
        state.activeArchetypeId = arch.id;
        state.playerSlots = arch.slots.slice();
        state.playerCaptain = arch.captainSlot;
        state.playerDirective = arch.directive;
        preloadBattleState();
        syncCenterButtons();
      });
      archBar.appendChild(btn);
    });

    const dirBar = document.getElementById("directiveBar");
    dirBar.innerHTML = "";
    E.DIRECTIVES.forEach(function (dir) {
      const btn = document.createElement("button");
      btn.className = "btn" + (dir.id === state.playerDirective ? " active" : "");
      btn.setAttribute("data-dir-id", dir.id);
      btn.textContent = dir.name;
      btn.title = dir.desc;
      btn.addEventListener("click", function () {
        stopAutoBattle();
        state.playerDirective = dir.id;
        preloadBattleState();
        syncCenterButtons();
      });
      dirBar.appendChild(btn);
    });
  }

  function syncCenterButtons() {
    Array.from(document.querySelectorAll("[data-arch-id]")).forEach(function (b) {
      b.classList.toggle("active", b.getAttribute("data-arch-id") === state.activeArchetypeId);
    });
    Array.from(document.querySelectorAll("[data-dir-id]")).forEach(function (b) {
      b.classList.toggle("active", b.getAttribute("data-dir-id") === state.playerDirective);
    });
    const opp = E.OPPONENT_GAUNTLET[state.roundIndex];
    document.getElementById("opponentTitle").textContent = opp.title;
    document.getElementById("roundBadge").textContent = "Gauntlet Round " + (state.roundIndex + 1) + " / 3";
  }

  function updateHUD() {
    if (!state.battle) return;
    const b = state.battle;
    document.getElementById("gaugeFill").style.width = b.playerGauge + "%";
    document.getElementById("gaugeLabel").textContent = b.playerGauge + "% · Convergences: " + b.playerConvergences;
    document.getElementById("chainCounterBadge").textContent = "Resonance Chains: " + b.totalResonanceChains;

    const phaseText = b.finished ? "FINISHED (" + b.winner.toUpperCase() + ")" : (b.tick === 0 ? "PREPARE" : "BATTLE TICK " + b.tick);
    document.getElementById("phaseBadge").textContent = "Phase: " + phaseText;

    const winEl = document.getElementById("winnerStatus");
    if (b.finished) {
      winEl.textContent = b.winner === "player" ? "★ VICTORY" : "DEFEAT — Adapt Formation";
      winEl.style.color = b.winner === "player" ? "var(--emerald)" : "var(--crimson)";
    } else {
      winEl.textContent = b.tick === 0 ? "Formation Ready" : "Resolving Resonance...";
      winEl.style.color = "var(--crystal)";
    }

    const logEl = document.getElementById("causalLog");
    logEl.innerHTML = "";
    b.log.slice(0, 18).forEach(function (line) {
      const div = document.createElement("div");
      div.className = "log-entry";
      if (line.indexOf("RESONANCE") !== -1) div.classList.add("resonance");
      if (line.indexOf("CONVERGENCE") !== -1) div.classList.add("convergence");
      div.textContent = line;
      logEl.appendChild(div);
    });
  }

  function unitCoords(side, slot) {
    const col = slot % 3;
    const isFront = slot < 3;
    const spread = isFront ? 210 : 245;
    const x = 470 + (col - 1) * spread;
    let y;
    if (side === "player") {
      y = isFront ? 338 : 454;
    } else {
      y = isFront ? 204 : 96;
    }
    return { x: x, y: y };
  }

  function pushEventsToBeams(events) {
    (events || []).forEach(function (ev) {
      const fromSide = ev.side;
      const toSide = ev.type === "RESONANCE" && ev.label.indexOf("HEARTWOOD") !== -1 ? ev.side : (ev.side === "player" ? "enemy" : "player");
      const a = unitCoords(fromSide, ev.sourceSlot || 0);
      const b = unitCoords(toSide, ev.targetSlot || 0);
      state.activeBeams.push({
        a: a,
        b: b,
        color: ev.color || "#38E5FF",
        label: ev.label || "RESONANCE",
        ttl: 0.85
      });
      if (ev.type === "CONVERGENCE") {
        state.convergenceFlash = 1.0;
      }
    });
  }

  function doStepTick() {
    if (!state.battle) preloadBattleState();
    if (state.battle.finished) {
      stopAutoBattle();
      return;
    }
    E.stepBattle(state.battle);
    pushEventsToBeams(state.battle.events);
    updateHUD();
    if (state.battle.finished) stopAutoBattle();
  }

  function startAutoBattle() {
    stopAutoBattle();
    if (!state.battle || state.battle.finished || state.battle.tick > 0) {
      preloadBattleState();
    }
    doStepTick();
    state.autoTimer = setInterval(doStepTick, 380);
  }

  function stopAutoBattle() {
    if (state.autoTimer) {
      clearInterval(state.autoTimer);
      state.autoTimer = null;
    }
  }

  // Click / Double-Click on Canvas Player Pedestals to Assign Creature or Captain
  canvas.addEventListener("click", function (ev) {
    const rect = canvas.getBoundingClientRect();
    const mx = ((ev.clientX - rect.left) / rect.width) * canvas.width;
    const my = ((ev.clientY - rect.top) / rect.height) * canvas.height;

    for (let slot = 0; slot < 6; slot++) {
      const pt = unitCoords("player", slot);
      const dist = Math.hypot(mx - pt.x, my - pt.y);
      if (dist <= 52) {
        state.selectedSlot = slot;
        if (state.playerSlots[slot] === state.selectedCreatureId) {
          state.playerCaptain = slot;
        } else {
          state.playerSlots[slot] = state.selectedCreatureId;
        }
        stopAutoBattle();
        preloadBattleState();
        return;
      }
    }
  });

  function drawHexPedestal(x, y, radius, strokeColor, fillAlpha, isCaptain) {
    ctx.save();
    ctx.beginPath();
    for (let i = 0; i < 6; i++) {
      const ang = (Math.PI / 3) * i - Math.PI / 6;
      const hx = x + Math.cos(ang) * radius;
      const hy = y + Math.sin(ang) * (radius * 0.56);
      if (i === 0) ctx.moveTo(hx, hy);
      else ctx.lineTo(hx, hy);
    }
    ctx.closePath();
    ctx.fillStyle = "rgba(10, 16, 32, " + fillAlpha + ")";
    ctx.fill();
    ctx.lineWidth = isCaptain ? 3.2 : 2.0;
    ctx.strokeStyle = isCaptain ? "#F5C451" : strokeColor;
    ctx.stroke();
    ctx.restore();
  }

  function renderArena(dt) {
    state.animTime += dt;
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // 1. Sanctuary Backdrop
    const arenaImg = state.images["arena"];
    if (arenaImg && arenaImg.complete && arenaImg.naturalWidth > 0) {
      ctx.save();
      ctx.globalAlpha = 0.42;
      ctx.drawImage(arenaImg, 0, 0, canvas.width, canvas.height);
      ctx.restore();
    }

    // 2. Dimensional Sanctuary Grid & Center Resonance Equator
    ctx.save();
    ctx.strokeStyle = "rgba(56, 229, 255, 0.18)";
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(90, 270);
    ctx.lineTo(850, 270);
    ctx.stroke();

    // Draw adjacency circuit lines between Player units
    if (state.battle) {
      const pUnits = state.battle.playerUnits;
      const wyrm = pUnits.find(function (u) { return u.id === "tempest-wyrm" && u.hp > 0; });
      const hart = pUnits.find(function (u) { return u.id === "prismhart" && u.hp > 0; });
      const stalker = pUnits.find(function (u) { return u.id === "riftstalker" && u.hp > 0; });
      if (wyrm && hart) {
        const p1 = unitCoords("player", wyrm.slot);
        const p2 = unitCoords("player", hart.slot);
        ctx.strokeStyle = E.areAdjacent(wyrm.slot, hart.slot) ? "rgba(122, 240, 255, 0.72)" : "rgba(122, 240, 255, 0.28)";
        ctx.setLineDash([6, 4]);
        ctx.lineWidth = 2.2;
        ctx.beginPath();
        ctx.moveTo(p1.x, p1.y + 18);
        ctx.lineTo(p2.x, p2.y + 18);
        ctx.stroke();
      }
      if (hart && stalker) {
        const p2 = unitCoords("player", hart.slot);
        const p3 = unitCoords("player", stalker.slot);
        ctx.strokeStyle = "rgba(194, 92, 255, 0.55)";
        ctx.setLineDash([5, 5]);
        ctx.beginPath();
        ctx.moveTo(p2.x, p2.y + 18);
        ctx.lineTo(p3.x, p3.y + 18);
        ctx.stroke();
      }
    }
    ctx.restore();

    // 3. Draw All 12 Dimensional Creature Projections
    if (state.battle) {
      const allUnits = state.battle.enemyUnits.concat(state.battle.playerUnits);
      allUnits.forEach(function (u) {
        const pos = unitCoords(u.side, u.slot);
        const alive = u.hp > 0;
        drawHexPedestal(pos.x, pos.y + 24, 52, alive ? u.color : "#2b3347", alive ? 0.85 : 0.4, u.isCaptain);

        // Volumetric hologram light cone
        if (alive) {
          const grad = ctx.createLinearGradient(pos.x, pos.y - 42, pos.x, pos.y + 26);
          grad.addColorStop(0, "rgba(56, 229, 255, 0)");
          grad.addColorStop(1, u.side === "player" ? "rgba(56, 229, 255, 0.16)" : "rgba(255, 77, 109, 0.14)");
          ctx.fillStyle = grad;
          ctx.beginPath();
          ctx.moveTo(pos.x - 36, pos.y - 34);
          ctx.lineTo(pos.x + 36, pos.y - 34);
          ctx.lineTo(pos.x + 48, pos.y + 24);
          ctx.lineTo(pos.x - 48, pos.y + 24);
          ctx.closePath();
          ctx.fill();
        }

        // Creature Sprite
        const spr = state.images[u.id];
        if (spr && spr.complete && spr.naturalWidth > 0) {
          ctx.save();
          ctx.globalAlpha = alive ? 1.0 : 0.22;
          const bob = alive ? Math.sin(state.animTime * 3.4 + u.slot) * 4.0 : 0;
          ctx.drawImage(spr, pos.x - 42, pos.y - 52 + bob, 84, 84);
          ctx.restore();
        }

        // Shield facet ring
        if (alive && u.shield > 0) {
          ctx.save();
          ctx.strokeStyle = "#7AF0FF";
          ctx.lineWidth = 2.4;
          ctx.beginPath();
          ctx.arc(pos.x, pos.y - 10, 44, 0, Math.PI * 2);
          ctx.stroke();
          ctx.restore();
        }

        // HP Bar + Dual Shape/Color Status Badges
        const barW = 84, barH = 7;
        const bx = pos.x - barW / 2, by = pos.y + 34;
        ctx.fillStyle = "#060913";
        ctx.fillRect(bx, by, barW, barH);
        const ratio = Math.max(0, Math.min(1, u.hp / u.maxHp));
        ctx.fillStyle = u.side === "player" ? "#2CEAA3" : "#FF4D6D";
        ctx.fillRect(bx, by, barW * ratio, barH);

        // Name & Captain Crown
        ctx.font = "bold 11px Segoe UI, sans-serif";
        ctx.textAlign = "center";
        ctx.fillStyle = "#F2F6FF";
        ctx.fillText((u.isCaptain ? "★ " : "") + u.name, pos.x, pos.y + 52);

        // Status Marks (Voltbrand, Solar Brand, Eclipse Tether)
        const marks = [];
        if (u.marks.voltbrand > 0) marks.push({ txt: "⚡VOLT", col: "#38E5FF" });
        if (u.marks.solarBrand > 0) marks.push({ txt: "☀SOLAR", col: "#FF6B4A" });
        if (u.marks.eclipseTether > 0) marks.push({ txt: "☾TETHER", col: "#D06BFF" });
        marks.forEach(function (m, idx) {
          ctx.fillStyle = "rgba(7, 10, 20, 0.9)";
          ctx.fillRect(pos.x - 32, pos.y - 66 - idx * 14, 64, 13);
          ctx.fillStyle = m.col;
          ctx.font = "bold 10px Segoe UI, sans-serif";
          ctx.fillText(m.txt, pos.x, pos.y - 56 - idx * 14);
        });
      });
    }

    // 4. Active Refractive Resonance Beams
    for (let i = state.activeBeams.length - 1; i >= 0; i--) {
      const bm = state.activeBeams[i];
      bm.ttl -= dt;
      if (bm.ttl <= 0) {
        state.activeBeams.splice(i, 1);
        continue;
      }
      ctx.save();
      ctx.globalAlpha = Math.min(1, bm.ttl * 1.4);
      ctx.strokeStyle = bm.color;
      ctx.lineWidth = 3.5;
      ctx.shadowColor = bm.color;
      ctx.shadowBlur = 12;
      ctx.beginPath();
      ctx.moveTo(bm.a.x, bm.a.y - 10);
      ctx.lineTo(bm.b.x, bm.b.y - 10);
      ctx.stroke();

      const mx = (bm.a.x + bm.b.x) * 0.5;
      const my = (bm.a.y + bm.b.y) * 0.5 - 14;
      ctx.fillStyle = "rgba(7, 10, 20, 0.88)";
      ctx.fillRect(mx - 75, my - 11, 150, 16);
      ctx.fillStyle = bm.color;
      ctx.font = "bold 10.5px Segoe UI, sans-serif";
      ctx.textAlign = "center";
      ctx.fillText(bm.label, mx, my + 1);
      ctx.restore();
    }

    // 5. Convergence Supernova Wave
    if (state.convergenceFlash > 0) {
      state.convergenceFlash = Math.max(0, state.convergenceFlash - dt * 1.5);
      ctx.save();
      ctx.strokeStyle = "rgba(245, 196, 81, " + state.convergenceFlash.toFixed(2) + ")";
      ctx.lineWidth = 6;
      ctx.beginPath();
      ctx.arc(470, 270, (1.0 - state.convergenceFlash) * 420, 0, Math.PI * 2);
      ctx.stroke();
      ctx.restore();
    }
  }

  // Bind UI Buttons
  document.getElementById("btnLaunchBattle").addEventListener("click", startAutoBattle);
  document.getElementById("btnStepTick").addEventListener("click", function () {
    stopAutoBattle();
    doStepTick();
  });
  document.getElementById("btnInstantResolve").addEventListener("click", function () {
    stopAutoBattle();
    if (!state.battle || state.battle.finished) preloadBattleState();
    while (!state.battle.finished && state.battle.tick <= state.battle.maxTicks) {
      E.stepBattle(state.battle);
    }
    pushEventsToBeams(state.battle.events);
    updateHUD();
  });
  document.getElementById("btnResetPrep").addEventListener("click", function () {
    stopAutoBattle();
    preloadBattleState();
  });

  [0, 1, 2].forEach(function (rIdx) {
    document.getElementById("btnRound" + (rIdx + 1)).addEventListener("click", function () {
      stopAutoBattle();
      state.roundIndex = rIdx;
      preloadBattleState();
      syncCenterButtons();
    });
  });

  document.getElementById("btnVerifyFairness").addEventListener("click", function () {
    const runFoil = E.runFullSimulation({
      playerSlots: state.playerSlots,
      playerCaptain: state.playerCaptain,
      playerDirective: state.playerDirective,
      foilMap: { "tempest-wyrm": "prismatic-spectrum", "prismhart": "relic-foil", "riftstalker": "phantom-foil" }
    });
    const runStd = E.runFullSimulation({
      playerSlots: state.playerSlots,
      playerCaptain: state.playerCaptain,
      playerDirective: state.playerDirective,
      foilMap: { "tempest-wyrm": "standard-edition", "prismhart": "standard-edition", "riftstalker": "standard-edition" }
    });
    const identical =
      runFoil.tick === runStd.tick &&
      runFoil.totalResonanceChains === runStd.totalResonanceChains &&
      JSON.stringify(runFoil.playerUnits.map(function (u) { return u.hp; })) ===
        JSON.stringify(runStd.playerUnits.map(function (u) { return u.hp; }));
    document.getElementById("fairnessProofBanner").textContent = identical
      ? "✓ VERIFIED: Prismatic/Phantom/Relic Foil vs Standard produced 100% identical ticks (" + runFoil.tick + "), chains (" + runFoil.totalResonanceChains + "), and unit HP."
      : "Fairness mismatch!";
  });

  // Initialize
  buildLeftControls();
  buildCenterControls();
  updateCardInspector();
  preloadBattleState();
  syncCenterButtons();

  let lastTs = performance.now();
  function loop(now) {
    const dt = Math.min(0.1, (now - lastTs) / 1000);
    lastTs = now;
    renderArena(dt);
    requestAnimationFrame(loop);
  }
  requestAnimationFrame(loop);
})();
