import { CONFIG } from './config.js';

const clamp = (value, min, max) => Math.max(min, Math.min(max, value));
const hashSeed = value => {
  let hash = 2166136261;
  for (const char of String(value)) hash = Math.imul(hash ^ char.charCodeAt(0), 16777619);
  return hash >>> 0 || 1;
};

export function createSimulation(seed = 1, config = CONFIG) {
  let rngState = hashSeed(seed);
  let nextTargetId = 0;
  const particlePool = [];
  const beamPool = [];
  const random = () => {
    rngState = (Math.imul(rngState, 1664525) + 1013904223) >>> 0;
    return rngState / 4294967296;
  };
  const sim = {
    state: 'TITLE', seed, time: 0, score: 0, bestScore: 0, bestCombo: 0,
    combo: 0, comboTimer: 0, accuracy: { matching: 0, total: 0 },
    destroys: 0, chains: 0, charge: 0, spectrum: 0, targets: [],
    particles: [], beams: [], combatFx: [], events: [], sequence: 0,
    spawnTimer: 0, overloadTimer: 0, overload: false, wave: 0,
    powerup: null, upgradeOffer: null, upgrades: [], nextUpgradeAt: 12,
    fireHeld: false, fireTimer: 0, aim: { x: config.width / 2, y: config.height / 2 },
    stats: { droppedSteps: 0, cappedParticles: 0, cappedTargets: 0, cappedEvents: 0 },
    settings: { reducedFlash: false, reducedEffects: false, highContrast: false, muted: false }
  };

  function emit(type, payload = {}) {
    if (['fracture', 'split', 'volatile_burst', 'overdrive', 'overload_warning', 'overdrive_target'].includes(type)
      && sim.combatFx.length < 160) {
      const duration = type === 'overdrive' ? .46 : type === 'fracture' ? .14 : .32;
      sim.combatFx.push({ type, life: duration, maxLife: duration,
        x: payload.x ?? payload.tx ?? 0, y: payload.y ?? payload.ty ?? 0,
        tx: payload.tx ?? 0, ty: payload.ty ?? 0, angle: payload.angle ?? 0,
        radius: payload.family === 'crystal' ? 22 : 15, color: payload.color ?? '#ff704b' });
    }
    if (sim.events.length >= config.maxEventsPerStep * 2) {
      sim.stats.cappedEvents++;
      return;
    }
    sim.events.push({ type, tick: Math.round(sim.time / config.fixedStep), sequence: sim.sequence++, ...payload });
  }

  const spectrum = index => config.colors[index % config.colors.length];

  function spawn(family, x, y, spectrumIndex = Math.floor(random() * 3)) {
    if (sim.targets.length >= config.targetCap) { sim.stats.cappedTargets++; return null; }
    const profiles = {
      block: { hp: 2 + Math.floor(sim.time / 25) % 3, radius: 24, score: 100 },
      crystal: { hp: 3, radius: 28, score: 260 },
      power: { hp: 1, radius: 20, score: 80 },
      volatile: { hp: 2, radius: 23, score: 170 }
    };
    if (!profiles[family]) throw new Error(`Unknown target family: ${family}`);
    const profile = profiles[family];
    const target = { id: ++nextTargetId, family, x, y,
      vx: (random() - .5) * 48, vy: 25 + random() * 45 + sim.time * .035,
      hp: profile.hp, maxHp: profile.hp, radius: profile.radius, score: profile.score,
      spectrum: spectrumIndex, phase: random() * Math.PI * 2,
      fuse: family === 'volatile' ? 2.7 : 0, armed: false, cracks: 0, born: sim.time };
    sim.targets.push(target);
    emit('target_spawned', { targetId: target.id, family, x, y, spectrum: spectrum(spectrumIndex).id });
    return target;
  }

  function begin() {
    if (sim.state !== 'TITLE' && sim.state !== 'RUN_OVER') return;
    const bestScore = sim.bestScore;
    rngState = hashSeed(seed);
    nextTargetId = 0;
    Object.assign(sim, {
      state: 'RUNNING', seed, time: 0, score: 0, bestScore, bestCombo: 0,
      combo: 0, comboTimer: 0, accuracy: { matching: 0, total: 0 }, destroys: 0,
      chains: 0, charge: 0, spectrum: 0, targets: [], particles: [], beams: [],
      combatFx: [], events: [], sequence: 0, spawnTimer: 0, overloadTimer: 0,
      overload: false, wave: 0, powerup: null, upgradeOffer: null, upgrades: [],
      nextUpgradeAt: 12, fireHeld: false, fireTimer: 0,
      aim: { x: config.width / 2, y: config.height / 2 },
      stats: { droppedSteps: 0, cappedParticles: 0, cappedTargets: 0, cappedEvents: 0 }
    });
    particlePool.length = 0;
    beamPool.length = 0;
    emit('run_started', { seed });
    for (const [index, family] of ['block', 'crystal', 'volatile', 'power'].entries()) {
      spawn(family, 250 + index * 250, 205 + (index % 2) * 34, index % 3);
    }
  }

  function addParticle(x, y, color, angle, family, scale = 1, count = 12) {
    const limit = sim.settings.reducedEffects ? Math.floor(config.particleCap * .35) : config.particleCap;
    for (let index = 0; index < count; index++) {
      if (sim.particles.length >= limit) { sim.stats.cappedParticles++; break; }
      const direction = angle + (random() - .5) * Math.PI * 1.7;
      const speed = (45 + random() * 285) * scale;
      const life = .25 + random() * .68;
      const particle = particlePool.pop() || {};
      Object.assign(particle, { x, y, vx: Math.cos(direction) * speed,
        vy: Math.sin(direction) * speed, life, maxLife: life,
        size: 1.5 + random() * 5.5, color, family,
        spin: (random() - .5) * 9, rotation: random() * 6.28,
        square: family === 'block' || random() < .45 });
      sim.particles.push(particle);
    }
  }

  function collectPowerup() {
    const kind = config.powerups[Math.floor(random() * config.powerups.length)];
    if (kind === 'supernova') {
      emit('powerup_collected', { kind, duration: 0 });
      overdrive(true);
      return;
    }
    if (sim.powerup?.kind === kind) sim.powerup.remaining = config.powerupDuration;
    else sim.powerup = { kind, remaining: config.powerupDuration };
    emit('powerup_collected', { kind, duration: config.powerupDuration });
  }

  function destroy(target, angle, depth, chainTargets) {
    const index = sim.targets.indexOf(target);
    if (index < 0) return;
    sim.targets.splice(index, 1);
    sim.score += target.score * Math.max(1, sim.combo + 1);
    sim.destroys++;
    sim.combo = Math.min(config.comboMax, sim.combo + 1);
    sim.comboTimer = config.comboWindow;
    sim.bestCombo = Math.max(sim.bestCombo, sim.combo);
    const chargeGain = 8 + Math.min(sim.combo, 20) * .75;
    sim.charge = clamp(sim.charge + chargeGain * (sim.upgrades.includes('prism-charge') ? 1.3 : 1), 0, config.overdriveThreshold);
    sim.chains++;
    const color = target.family === 'volatile' ? '#ff704b'
      : target.family === 'power' ? '#58f0b1' : spectrum(target.spectrum).color;
    emit('destroyed', { targetId: target.id, family: target.family,
      x: target.x, y: target.y, color, combo: sim.combo, depth });
    addParticle(target.x, target.y, color, angle, target.family,
      target.family === 'crystal' ? 1.35 : 1, target.family === 'crystal' ? 30 : 18);
    if (target.family === 'power') collectPowerup();

    if (target.family === 'crystal' && depth < config.maxChainDepth) {
      const candidates = sim.targets
        .filter(candidate => !chainTargets.has(candidate.id))
        .map(candidate => ({ target: candidate, distance: Math.hypot(candidate.x - target.x, candidate.y - target.y) }))
        .filter(candidate => candidate.distance < 205)
        .sort((a, b) => a.distance - b.distance)
        .slice(0, config.maxSplitBranches);
      for (const { target: branch } of candidates) {
        if (chainTargets.has(branch.id) || !sim.targets.includes(branch)) continue;
        chainTargets.add(branch.id);
        emit('split', { from: target.id, to: branch.id, x: target.x, y: target.y,
          tx: branch.x, ty: branch.y, depth: depth + 1 });
        hit(branch, Math.atan2(branch.y - target.y, branch.x - target.x), true, depth + 1, chainTargets);
      }
    }

    if (target.family === 'volatile' && depth < config.maxChainDepth) {
      const neighbors = sim.targets
        .filter(candidate => !chainTargets.has(candidate.id)
          && Math.hypot(candidate.x - target.x, candidate.y - target.y) < 112)
        .sort((a, b) => a.id - b.id).slice(0, 8);
      for (const neighbor of neighbors) {
        if (chainTargets.has(neighbor.id) || !sim.targets.includes(neighbor)) continue;
        chainTargets.add(neighbor.id);
        neighbor.hp -= neighbor.family === 'volatile' ? 2 : 1;
        emit('volatile_burst', { targetId: target.id, neighborId: neighbor.id,
          depth: depth + 1, x: target.x, y: target.y });
        if (neighbor.hp <= 0) {
          destroy(neighbor, Math.atan2(neighbor.y - target.y, neighbor.x - target.x), depth + 1, chainTargets);
        } else if (neighbor.family === 'volatile') {
          if (!neighbor.armed) {
            neighbor.armed = true;
            neighbor.fuse = .35;
            emit('volatile_warning', { targetId: neighbor.id, x: neighbor.x, y: neighbor.y });
          }
          if (neighbor.fuse <= .35) {
            neighbor.fuse = 0;
            emit('volatile_detonated', { targetId: neighbor.id, x: neighbor.x, y: neighbor.y });
            destroy(neighbor, Math.atan2(neighbor.y - target.y, neighbor.x - target.x), depth + 1, chainTargets);
          }
        }
      }
    }
  }

  function hit(target, angle, secondary = false, depth = 0, chainTargets = new Set()) {
    if (!sim.targets.includes(target) || chainTargets.has(target.id)) return false;
    chainTargets.add(target.id);
    if (target.family === 'power') { destroy(target, angle, depth, chainTargets); return true; }
    const matching = target.family === 'crystal' && target.spectrum === sim.spectrum;
    const damage = (matching ? 1.5 : 1) * (sim.powerup?.kind === 'explosive' ? 1.4 : 1)
      * (sim.upgrades.includes('reinforced-beam') ? 1.3 : 1);
    target.hp -= damage;
    target.cracks++;
    sim.accuracy.total++;
    if (matching) sim.accuracy.matching++;
    emit('hit', { targetId: target.id, x: target.x, y: target.y, damage, matching, secondary, health: Math.max(0, target.hp) });
    emit('fracture', { targetId: target.id, family: target.family, x: target.x, y: target.y,
      angle, cracks: target.cracks, color: spectrum(target.spectrum).color });
    addParticle(target.x, target.y, matching ? '#ffffff' : spectrum(sim.spectrum).color,
      angle, target.family, .48, 5);
    if (target.hp <= 0) destroy(target, angle, depth, chainTargets);
    return true;
  }

  function fire() {
    if (sim.state !== 'RUNNING') return;
    const origin = { x: config.width / 2, y: config.height - 32 };
    const dx = sim.aim.x - origin.x;
    const dy = sim.aim.y - origin.y;
    const length = Math.hypot(dx, dy) || 1;
    const baseAngle = Math.atan2(dy, dx);
    const spreads = sim.powerup?.kind === 'multishot' ? [-.13, 0, .13] : [0];
    const rays = [];
    for (const spread of spreads) {
      const angle = baseAngle + spread;
      const rayX = Math.cos(angle), rayY = Math.sin(angle);
      const intersections = [];
      for (const target of sim.targets) {
        const ox = origin.x - target.x, oy = origin.y - target.y;
        const b = ox * rayX + oy * rayY;
        const c = ox * ox + oy * oy - target.radius * target.radius;
        const discriminant = b * b - c;
        if (discriminant < 0) continue;
        const distance = -b - Math.sqrt(discriminant);
        if (distance >= 0 && distance <= length) intersections.push({ target, distance });
      }
      intersections.sort((a, b) => a.distance - b.distance);
      const contact = intersections.length
        ? { x: origin.x + rayX * intersections[0].distance, y: origin.y + rayY * intersections[0].distance }
        : { x: origin.x + rayX * length, y: origin.y + rayY * length };
      const beam = beamPool.pop() || {};
      Object.assign(beam, { x: origin.x, y: origin.y, tx: contact.x, ty: contact.y,
        color: spectrum(sim.spectrum).color, life: config.beamLifetime, maxLife: config.beamLifetime });
      if (sim.beams.length < 64) sim.beams.push(beam);
      else sim.stats.cappedEvents++;
      const nearest = intersections[0]?.target ?? null;
      emit('shot_fired', { x: origin.x, y: origin.y, tx: contact.x, ty: contact.y,
        spectrum: spectrum(sim.spectrum).id, hitTargetId: nearest?.id ?? null, spread });
      rays.push({ nearest, intersections, angle });
    }

    const hitTargets = new Set();
    for (const ray of rays) {
      if (!ray.nearest || hitTargets.has(ray.nearest.id) || !sim.targets.includes(ray.nearest)) continue;
      const chainTargets = new Set();
      hit(ray.nearest, ray.angle, false, 0, chainTargets);
      for (const id of chainTargets) hitTargets.add(id);
      if (sim.powerup?.kind === 'piercing') {
        for (const intersection of ray.intersections.slice(1, 4)) {
          if (hitTargets.has(intersection.target.id) || !sim.targets.includes(intersection.target)) continue;
          const piercingChain = new Set();
          hit(intersection.target, ray.angle, true, 0, piercingChain);
          for (const id of piercingChain) hitTargets.add(id);
        }
      }
    }
    if (!hitTargets.size) {
      if (sim.combo > 0) emit('chain_miss', { combo: sim.combo });
      sim.combo = 0;
      sim.comboTimer = 0;
    }
  }

  function overdrive(supernova = false) {
    if (!supernova && sim.charge < config.overdriveThreshold) return false;
    if (!supernova) sim.charge = 0;
    const targets = [...sim.targets]
      .sort((a, b) => Math.hypot(a.x - sim.aim.x, a.y - sim.aim.y) - Math.hypot(b.x - sim.aim.x, b.y - sim.aim.y))
      .slice(0, config.overdriveDamage);
    emit('overdrive', { x: sim.aim.x, y: sim.aim.y, count: targets.length, supernova });
    for (const target of targets) {
      emit('overdrive_target', { x: target.x, y: target.y });
      destroy(target, Math.atan2(target.y - sim.aim.y, target.x - sim.aim.x), 0, new Set([target.id]));
    }
    return true;
  }

  function chooseUpgrade(id) {
    if (sim.state !== 'UPGRADE' || !sim.upgradeOffer?.includes(id)) return false;
    sim.upgrades.push(id);
    sim.state = 'RUNNING';
    sim.upgradeOffer = null;
    emit('upgrade_selected', { id });
    return true;
  }

  function update(dt) {
    if (sim.state !== 'RUNNING') return;
    const gameDt = Math.min(dt, config.fixedStep * config.maxCatchupSteps)
      * (sim.powerup?.kind === 'time-dilation' ? .5 : 1);
    sim.time += gameDt;
    sim.wave = Math.floor(sim.time / 22);
    sim.comboTimer = Math.max(0, sim.comboTimer - gameDt);
    if (!sim.comboTimer && sim.combo) { sim.combo = 0; emit('chain_expired'); }
    sim.fireTimer = Math.max(0, sim.fireTimer - gameDt);
    if (sim.fireHeld && sim.fireTimer <= 0) {
      fire();
      sim.fireTimer = Math.max(.045, config.fireInterval * (sim.upgrades.includes('rapid-fire') ? .68 : 1));
    }
    if (sim.powerup) {
      sim.powerup.remaining -= gameDt;
      if (sim.powerup.remaining <= 0) { emit('powerup_expired', { kind: sim.powerup.kind }); sim.powerup = null; }
    }
    const interval = clamp(config.spawnBaseInterval - Math.floor(sim.time / 18) * .075,
      config.spawnMinInterval, config.spawnBaseInterval);
    sim.spawnTimer += gameDt;
    if (sim.spawnTimer >= interval) {
      sim.spawnTimer -= interval;
      const family = sim.time < 7 ? 'block' : ['block', 'block', 'crystal', 'volatile', 'power'][Math.floor(random() * 5)];
      spawn(family, 100 + random() * (config.width - 200), -25, Math.floor(random() * 3));
    }
    for (const target of [...sim.targets]) {
      target.phase += gameDt;
      target.x += target.vx * gameDt + Math.sin(target.phase) * 10 * gameDt;
      target.y += target.vy * gameDt;
      if (target.x < target.radius || target.x > config.width - target.radius) target.vx *= -1;
      if (target.family === 'volatile') {
        target.fuse -= gameDt;
        if (target.fuse <= 0 && !target.armed) {
          target.armed = true; target.fuse = .72;
          emit('volatile_warning', { targetId: target.id, x: target.x, y: target.y });
        } else if (target.armed && target.fuse <= 0) {
          emit('volatile_detonated', { targetId: target.id, x: target.x, y: target.y });
          destroy(target, Math.PI / 2, 0, new Set([target.id]));
        }
      }
      if (target.y > config.height - 86) { target.y = config.height - 86; target.vy = 0; }
    }
    const occupied = sim.targets.filter(target => target.y > config.height * .55).length;
    if (occupied >= config.overloadLimit) {
      sim.overloadTimer += gameDt * (sim.upgrades.includes('cool-headed') ? .75 : 1);
      if (!sim.overload) { sim.overload = true; emit('overload_warning', { count: occupied }); }
    } else {
      sim.overloadTimer = Math.max(0, sim.overloadTimer - gameDt * .65);
      if (sim.overloadTimer === 0) sim.overload = false;
    }
    if (sim.overloadTimer >= config.overloadGrace && occupied >= config.overloadLimit) {
      sim.state = 'RUN_OVER'; sim.fireHeld = false;
      sim.bestScore = Math.max(sim.bestScore, sim.score);
      emit('run_over', { score: sim.score, bestScore: sim.bestScore, time: sim.time,
        bestCombo: sim.bestCombo, destroys: sim.destroys, chains: sim.chains,
        accuracy: sim.accuracy.total ? sim.accuracy.matching / sim.accuracy.total : 0 });
    } else if (sim.destroys >= sim.nextUpgradeAt) {
      sim.state = 'UPGRADE';
      sim.upgradeOffer = [...config.upgrades];
      for (let index = sim.upgradeOffer.length - 1; index > 0; index--) {
        const other = Math.floor(random() * (index + 1));
        [sim.upgradeOffer[index], sim.upgradeOffer[other]] = [sim.upgradeOffer[other], sim.upgradeOffer[index]];
      }
      sim.upgradeOffer = sim.upgradeOffer.slice(0, 3);
      sim.nextUpgradeAt += 12;
      emit('upgrade_offered', { options: sim.upgradeOffer });
    }
    if (sim.combatFx.length > 160) sim.combatFx.length = 160;
    for (let index = sim.particles.length - 1; index >= 0; index--) {
      const particle = sim.particles[index];
      particle.x += particle.vx * gameDt; particle.y += particle.vy * gameDt;
      particle.vx *= Math.pow(.09, gameDt);
      particle.vy = particle.vy * Math.pow(.18, gameDt) + 30 * gameDt;
      particle.rotation += particle.spin * gameDt;
      particle.life -= gameDt;
      if (particle.life <= 0) {
        sim.particles.splice(index, 1);
        if (particlePool.length < config.particleCap) particlePool.push(particle);
      }
    }
    for (let index = sim.beams.length - 1; index >= 0; index--) {
      const beam = sim.beams[index];
      beam.life -= gameDt;
      if (beam.life <= 0) {
        sim.beams.splice(index, 1);
        if (beamPool.length < 64) beamPool.push(beam);
      }
    }
    for (let index = sim.combatFx.length - 1; index >= 0; index--) {
      sim.combatFx[index].life -= gameDt;
      if (sim.combatFx[index].life <= 0) sim.combatFx.splice(index, 1);
    }
  }

  function command(action, payload = {}) {
    switch (action) {
      case 'start': begin(); break;
      case 'aim': sim.aim = { x: clamp(payload.x, 0, config.width), y: clamp(payload.y, 0, config.height) }; break;
      case 'fire-down':
        if (sim.state === 'RUNNING') { sim.fireHeld = true; fire(); sim.fireTimer = Math.max(.045, config.fireInterval * (sim.upgrades.includes('rapid-fire') ? .68 : 1)); }
        break;
      case 'fire-up': sim.fireHeld = false; break;
      case 'spectrum':
        if (sim.state === 'RUNNING' || sim.state === 'UPGRADE' || sim.state === 'PAUSED') {
          sim.spectrum = (sim.spectrum + 1) % config.colors.length;
          emit('spectrum_changed', { index: sim.spectrum });
        }
        break;
      case 'overdrive': overdrive(); break;
      case 'pause':
        if (sim.state === 'RUNNING' || sim.state === 'UPGRADE') { sim.state = 'PAUSED'; sim.fireHeld = false; emit('paused'); }
        else if (sim.state === 'PAUSED') { sim.state = sim.upgradeOffer ? 'UPGRADE' : 'RUNNING'; emit('resumed'); }
        break;
      case 'upgrade': chooseUpgrade(payload.id); break;
      case 'settings': Object.assign(sim.settings, payload); break;
      case 'debug-spawn': if (sim.state === 'RUNNING') spawn(payload.family || 'block', payload.x ?? 640, payload.y ?? 300, payload.spectrum ?? 0); break;
      case 'debug-overload':
        if (sim.state === 'RUNNING') {
          while (sim.targets.filter(target => target.y > config.height * .55).length < config.overloadLimit) spawn('block', 70 + sim.targets.length * 27, config.height * .7, 0);
          sim.overload = true; sim.overloadTimer = config.overloadGrace;
        }
        break;
      default: throw new Error(`Unknown simulation command: ${action}`);
    }
  }

  return { sim, update, command, drainEvents: () => sim.events.splice(0), spawn,
    hit, fire, chooseUpgrade, overdrive, config, random };
}

export function runSeededTrace(seed, trace, config = CONFIG) {
  const game = createSimulation(seed, config);
  game.command('start');
  for (const step of trace) {
    if (step.action) game.command(step.action, step.payload || {});
    if (step.ticks) for (let index = 0; index < step.ticks; index++) {
      if (game.sim.state === 'UPGRADE' && game.sim.upgradeOffer) game.chooseUpgrade(game.sim.upgradeOffer[0]);
      game.update(config.fixedStep);
    }
  }
  const state = game.sim;
  return { state: state.state, score: state.score, combo: state.combo,
    bestCombo: state.bestCombo, time: state.time, destroys: state.destroys,
    chains: state.chains, targets: state.targets.map(({ id, family, hp, x, y }) => ({ id, family, hp, x, y })), charge: state.charge };
}
