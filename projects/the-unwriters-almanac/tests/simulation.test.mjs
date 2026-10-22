import test from 'node:test';
import assert from 'node:assert/strict';
import { createSimulation, FIXED_STEP, LIMITS, WORLD, runSeededTrace } from '../src/simulation.js';
import { closestPointOnPolyline, polylineLength, sanitizeStroke } from '../src/geometry.js';

const validStroke = [WORLD.start, { x: 386, y: 451 }, { x: 580, y: 382 }, { x: 790, y: 314 }, WORLD.goal];

test('same seed and ordered commands reproduce identical simulation state', () => {
  const trace = [{ action: 'start' }, { action: 'draw-commit', payload: { points: validStroke } }, { ticks: 400 }];
  assert.deepEqual(runSeededTrace(91, trace), runSeededTrace(91, trace));
});

test('stroke sanitation clamps drawing, drops invalid points, and bounds point count', () => {
  const noisy = Array.from({ length: 1400 }, (_, i) => ({ x: i, y: 300 + Math.sin(i) * 16 }));
  noisy.push({ x: Number.NaN, y: 4 }, null);
  const result = sanitizeStroke(noisy);
  assert.ok(result.length <= LIMITS.strokePoints);
  assert.deepEqual(result[0], { x: 72, y: 300 });
  assert.ok(result.every((point) => point.x >= 72 && point.x <= 1208 && point.y >= 94 && point.y <= 626));
  assert.ok(polylineLength(result) > 0);
});

test('closest-point query supplies deterministic position and path distance', () => {
  const closest = closestPointOnPolyline({ x: 6, y: 4 }, [{ x: 0, y: 0 }, { x: 10, y: 0 }, { x: 10, y: 10 }]);
  assert.deepEqual(closest, { x: 6, y: 0, distance: 4, arcDistance: 6, segment: 0, t: 0.6 });
});

test('a valid continuous stroke redirects the bead and carries the creature to the seal', () => {
  const game = createSimulation(4);
  game.command('start');
  const result = game.command('draw-commit', { points: validStroke });
  assert.equal(result.accepted, true);
  assert.equal(game.sim.bead.attached, true);
  for (let i = 0; i < 480; i += 1) game.update(FIXED_STEP);
  assert.equal(game.sim.state, 'SOLVED');
  assert.ok(Math.hypot(game.sim.bead.x - WORLD.goal.x, game.sim.bead.y - WORLD.goal.y) < 3);
  assert.ok(Math.hypot(game.sim.actor.x - WORLD.goal.x, game.sim.actor.y - (WORLD.goal.y - 13)) < 3);
  assert.ok(game.drainEvents().some(({ type }) => type === 'page_solved'));
});

test('a line that misses the bead is rejected without poisoning recovery', () => {
  const game = createSimulation(3);
  game.command('start');
  const result = game.command('draw-commit', { points: [WORLD.start, { x: 350, y: 130 }, { x: 680, y: 130 }, WORLD.goal] });
  assert.equal(result.accepted, false);
  assert.equal(game.sim.rail.length, 0);
  assert.match(game.sim.message, /bead/);
  assert.equal(game.command('draw-commit', { points: validStroke }).accepted, true);
});

test('pause freezes game and animation time; resume restores the same line', () => {
  const game = createSimulation(8);
  game.command('start'); game.command('draw-commit', { points: validStroke });
  for (let i = 0; i < 20; i += 1) game.update(FIXED_STEP);
  game.command('pause');
  const before = structuredClone(game.sim);
  for (let i = 0; i < 60; i += 1) game.update(FIXED_STEP);
  assert.equal(game.sim.time, before.time);
  assert.deepEqual(game.sim.actor, before.actor);
  game.command('resume'); game.update(FIXED_STEP);
  assert.ok(game.sim.time > before.time);
});

test('erase, restart, jump, and pointer-draft cancellation are safe and repeatable', () => {
  const game = createSimulation(2);
  game.command('start');
  assert.equal(game.command('draw-start', { point: WORLD.start }), true);
  game.command('draw-point', { point: { x: 250, y: 480 } });
  game.command('draw-cancel', { reason: 'blur' });
  assert.equal(game.sim.draft.length, 0);
  assert.equal(game.sim.rail.length, 0);
  game.command('draw-commit', { points: validStroke });
  game.command('erase');
  assert.equal(game.sim.rail.length, 0);
  assert.deepEqual(game.sim.bead, { ...WORLD.bead, startDistance: 0, distance: 0, attached: false });
  game.command('restart'); game.command('restart');
  assert.equal(game.sim.state, 'TITLE');
  assert.equal(game.sim.actor.x, WORLD.start.x);
  game.command('start'); game.command('jump'); game.update(FIXED_STEP);
  assert.ok(game.sim.actor.y < WORLD.start.y);
});

test('pause cancels uncommitted drawing, completed page ignores edits, and step cap is explicit', () => {
  const game = createSimulation(1);
  game.command('start'); game.command('draw-start', { point: WORLD.start });
  game.command('pause');
  assert.equal(game.sim.state, 'PAUSED');
  assert.equal(game.sim.draft.length, 0);
  game.command('resume'); game.command('draw-commit', { points: validStroke });
  for (let i = 0; i < 480; i += 1) game.update(FIXED_STEP);
  assert.equal(game.sim.state, 'SOLVED');
  assert.equal(game.command('erase'), false);
  assert.equal(game.command('draw-start', { point: WORLD.goal }), false);
  assert.ok(LIMITS.maxFrameDelta <= 5 / 60);
});
