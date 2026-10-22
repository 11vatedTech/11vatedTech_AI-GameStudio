import { closestPointOnPolyline, distance, polylineLength, pointAtDistance, sanitizeStroke, STROKE_LIMITS } from './geometry.js';

export const FIXED_STEP = 1 / 60;
export const MAX_CATCH_UP_STEPS = 5;
export const WORLD = Object.freeze({ start: { x: 196, y: 520 }, goal: { x: 1106, y: 211 }, bead: { x: 650, y: 355 }, ledge: { left: 116, right: 363, top: 558 } });
export const LIMITS = Object.freeze({ events: 64, strokePoints: STROKE_LIMITS.maxPoints, particles: 24, maxFrameDelta: FIXED_STEP * MAX_CATCH_UP_STEPS });

function seededRandom(seed) {
  let value = seed >>> 0 || 1;
  return () => {
    value ^= value << 13;
    value ^= value >>> 17;
    value ^= value << 5;
    return (value >>> 0) / 4294967296;
  };
}

function freshState(seed) {
  const random = seededRandom(seed);
  return {
    seed: seed >>> 0,
    randomState: random() * 0xffffffff >>> 0,
    state: 'TITLE',
    time: 0,
    tick: 0,
    actor: { x: WORLD.start.x, y: WORLD.start.y, vx: 0, vy: 0, grounded: true, facing: 1, pose: 'idle', railDistance: 0, angle: 0 },
    bead: { x: WORLD.bead.x, y: WORLD.bead.y, startDistance: 0, distance: 0, attached: false },
    goal: { ...WORLD.goal },
    draft: [],
    rail: [],
    railLength: 0,
    moveAxis: 0,
    reducedMotion: false,
    message: 'Draw a line from the ink-being toward the seal.',
    events: [],
    particles: [],
    diagnostics: { droppedTime: 0, steps: 0, maxPoints: 0, maxParticles: 0 },
  };
}

export function createSimulation(seed = 1) {
  const initialSeed = seed >>> 0;
  let sim = freshState(initialSeed);
  const emit = (type, payload = {}) => {
    if (sim.events.length < LIMITS.events) sim.events.push({ type, tick: sim.tick, ...payload });
  };
  const resetPuzzle = () => {
    const reducedMotion = sim.reducedMotion;
    sim = freshState(initialSeed);
    sim.reducedMotion = reducedMotion;
    emit('page_reset');
  };
  const beginDraft = (point) => {
    if (sim.state !== 'PLAYING' || sim.rail.length || sim.draft.length) return false;
    if (distance(point, sim.actor) > 150) {
      sim.message = 'Begin your line near the little ink-being.';
      emit('stroke_rejected', { reason: 'start_too_far' });
      return false;
    }
    sim.draft = [{ x: point.x, y: point.y }];
    sim.actor.pose = 'anticipate';
    sim.message = 'Follow the gold bead, then reach the seal.';
    emit('stroke_started');
    return true;
  };
  const appendDraft = (point) => {
    if (sim.state !== 'PLAYING' || !sim.draft.length) return;
    const last = sim.draft.at(-1);
    if (distance(last, point) < 4) return;
    sim.draft.push({ x: point.x, y: point.y });
    if (sim.draft.length > LIMITS.strokePoints * 4) sim.draft = sanitizeStroke(sim.draft, { ...STROKE_LIMITS, maxPoints: LIMITS.strokePoints * 2 });
    emit('stroke_previewed', { pointCount: sim.draft.length });
  };
  const cancelDraft = (reason = 'cancelled') => {
    if (!sim.draft.length) return false;
    sim.draft = [];
    sim.actor.pose = sim.rail.length ? 'traverse' : 'idle';
    sim.message = 'Unfinished line cancelled. The page is unchanged.';
    emit('stroke_cancelled', { reason });
    return true;
  };
  const commitDraft = (raw = null) => {
    if (sim.state !== 'PLAYING' || sim.rail.length) return { accepted: false, reason: 'state' };
    const rail = sanitizeStroke(raw ?? sim.draft);
    sim.draft = [];
    if (rail.length < STROKE_LIMITS.minPoints) {
      sim.message = 'A line needs at least two distinct points.';
      sim.actor.pose = 'recover';
      emit('stroke_rejected', { reason: 'too_short' });
      return { accepted: false, reason: 'too_short' };
    }
    const length = polylineLength(rail);
    const startDistance = distance(rail[0], sim.actor);
    const endDistance = distance(rail.at(-1), sim.goal);
    const beadPoint = closestPointOnPolyline(sim.bead, rail);
    const reasons = [];
    if (startDistance > 150) reasons.push('start');
    if (endDistance > 150) reasons.push('seal');
    if (beadPoint.distance > 104) reasons.push('bead');
    if (length < STROKE_LIMITS.minLength || length > STROKE_LIMITS.maxLength) reasons.push('length');
    if (reasons.length) {
      sim.actor.pose = 'recover';
      sim.message = reasons.includes('bead') ? 'The line must catch the gold bead.' : reasons.includes('seal') ? 'Carry the line all the way to the folio seal.' : reasons.includes('start') ? 'Begin the line beside the ink-being.' : 'That line is too short or too long for this page.';
      emit('stroke_rejected', { reason: reasons[0] });
      return { accepted: false, reason: reasons[0] };
    }
    sim.rail = rail;
    sim.railLength = length;
    sim.bead.attached = true;
    sim.bead.startDistance = beadPoint.arcDistance;
    sim.bead.distance = beadPoint.arcDistance;
    sim.bead.x = beadPoint.x;
    sim.bead.y = beadPoint.y;
    sim.actor.railDistance = 0;
    sim.actor.pose = 'traverse';
    sim.actor.vx = 0;
    sim.actor.vy = 0;
    sim.message = 'The rail is alive. Follow the little mark.';
    sim.diagnostics.maxPoints = Math.max(sim.diagnostics.maxPoints, rail.length);
    emit('stroke_committed', { pointCount: rail.length, length: Math.round(length), beadDistance: Math.round(beadPoint.distance) });
    return { accepted: true, pointCount: rail.length, length, beadDistance: beadPoint.distance };
  };
  const command = (name, payload = {}) => {
    if (name === 'start' && sim.state === 'TITLE') {
      sim.state = 'PLAYING'; sim.message = 'Draw a line from the ink-being toward the seal.'; emit('page_started'); return true;
    }
    if (name === 'restore-title' && sim.state === 'PLAYING' && !sim.rail.length && !sim.draft.length && sim.tick === 0) {
      sim.state = 'TITLE'; sim.message = 'Draw a line from the ink-being toward the seal.'; emit('title_restored'); return true;
    }
    if (name === 'restart') { resetPuzzle(); return true; }
    if (name === 'pause' && sim.state === 'PLAYING') {
      cancelDraft('pause'); sim.state = 'PAUSED'; sim.message = 'The page is paused.'; emit('page_paused'); return true;
    }
    if (name === 'resume' && sim.state === 'PAUSED') { sim.state = 'PLAYING'; sim.message = 'The ink stirs again.'; emit('page_resumed'); return true; }
    if (name === 'reduced-motion') { sim.reducedMotion = Boolean(payload.value); emit('reduced_motion_changed', { value: sim.reducedMotion }); return true; }
    if (name === 'move' && sim.state === 'PLAYING') { sim.moveAxis = Math.max(-1, Math.min(1, Number(payload.axis) || 0)); if (sim.moveAxis) sim.actor.facing = Math.sign(sim.moveAxis); return true; }
    if (name === 'jump' && sim.state === 'PLAYING' && !sim.rail.length && sim.actor.grounded) {
      sim.actor.vy = -430; sim.actor.grounded = false; sim.actor.pose = 'traverse'; emit('creature_jumped'); return true;
    }
    if (name === 'draw-start') return beginDraft(payload.point);
    if (name === 'draw-point') return appendDraft(payload.point);
    if (name === 'draw-cancel') return cancelDraft(payload.reason);
    if (name === 'draw-commit') return commitDraft(payload.points ?? null);
    if (name === 'draw-guided' && sim.state === 'PLAYING' && !sim.rail.length) {
      const points = sanitizeStroke(payload.points ?? []);
      if (points.length < STROKE_LIMITS.minPoints) return false;
      sim.draft = points;
      sim.actor.pose = 'anticipate';
      sim.message = 'Guided line selected. Commit it to change the page.';
      emit('stroke_previewed', { pointCount: points.length, guided: true });
      return true;
    }
    if (name === 'erase' && sim.state === 'PLAYING' && (sim.rail.length || sim.draft.length)) {
      sim.rail = []; sim.railLength = 0; sim.draft = []; sim.bead = { ...WORLD.bead, startDistance: 0, distance: 0, attached: false };
      sim.actor = { ...sim.actor, x: WORLD.start.x, y: WORLD.start.y, vx: 0, vy: 0, grounded: true, pose: 'idle', railDistance: 0, angle: 0 };
      sim.message = 'The line dissolved. Try another path.'; emit('stroke_erased'); return true;
    }
    return false;
  };
  const update = (dt = FIXED_STEP) => {
    if (!Number.isFinite(dt) || dt <= 0 || sim.state !== 'PLAYING') return;
    const step = Math.min(dt, FIXED_STEP);
    sim.tick += 1; sim.time += step; sim.diagnostics.steps += 1;
    if (sim.rail.length) {
      sim.actor.railDistance = Math.min(sim.railLength, sim.actor.railDistance + 194 * step);
      const actorPoint = pointAtDistance(sim.rail, sim.actor.railDistance);
      Object.assign(sim.actor, { x: actorPoint.x, y: actorPoint.y - 13, angle: actorPoint.angle, facing: Math.cos(actorPoint.angle) < 0 ? -1 : 1, pose: 'traverse' });
      sim.bead.distance = Math.min(sim.railLength, sim.bead.distance + 226 * step);
      const beadPoint = pointAtDistance(sim.rail, sim.bead.distance);
      sim.bead.x = beadPoint.x; sim.bead.y = beadPoint.y;
      if (sim.actor.railDistance >= sim.railLength && sim.bead.distance >= sim.railLength) {
        sim.actor.pose = 'solved'; sim.state = 'SOLVED'; sim.message = 'The page has found its way.'; emit('objective_reached'); emit('page_solved');
      }
      return;
    }
    if (sim.moveAxis && sim.actor.grounded) {
      sim.actor.vx = sim.moveAxis * 142;
      sim.actor.x = Math.max(122, Math.min(358, sim.actor.x + sim.actor.vx * step));
    } else if (sim.actor.grounded) sim.actor.vx = 0;
    if (!sim.actor.grounded) {
      sim.actor.vy = Math.min(760, sim.actor.vy + 1120 * step);
      sim.actor.x = Math.max(72, Math.min(1208, sim.actor.x + sim.actor.vx * step));
      sim.actor.y += sim.actor.vy * step;
      if (sim.actor.y >= WORLD.ledge.top - 38 && sim.actor.x <= WORLD.ledge.right && sim.actor.x >= WORLD.ledge.left && sim.actor.vy > 0) {
        sim.actor.y = WORLD.ledge.top - 38; sim.actor.vy = 0; sim.actor.grounded = true; sim.actor.pose = 'recover'; emit('creature_landed');
      }
      if (sim.actor.y > 650) {
        sim.actor.x = WORLD.start.x; sim.actor.y = WORLD.start.y; sim.actor.vx = 0; sim.actor.vy = 0; sim.actor.grounded = true; sim.actor.pose = 'recover'; sim.message = 'A soft landing. Your line is still waiting.'; emit('creature_recovered');
      }
    } else sim.actor.pose = sim.draft.length ? 'anticipate' : 'idle';
  };
  const drainEvents = () => { const events = sim.events; sim.events = []; return events; };
  return { get sim() { return sim; }, command, update, drainEvents };
}

export function runSeededTrace(seed, trace) {
  const game = createSimulation(seed);
  for (const item of trace) {
    if (item.action) game.command(item.action, item.payload);
    if (item.ticks) for (let i = 0; i < item.ticks; i += 1) game.update(FIXED_STEP);
  }
  return structuredClone(game.sim);
}
