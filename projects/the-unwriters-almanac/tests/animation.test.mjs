import test from 'node:test';
import assert from 'node:assert/strict';
import { poseAt } from '../src/animation.js';

for (const state of ['idle', 'anticipate', 'traverse', 'recover', 'solved']) {
  test(`${state} authored pose has finite bounded transforms`, () => {
    for (let i = 0; i < 600; i += 1) {
      const pose = poseAt(state, i / 60);
      assert.ok(Object.values(pose).every(Number.isFinite));
      assert.ok(pose.squash > 0.7 && pose.squash < 1.3);
      assert.ok(pose.stretch > 0.7 && pose.stretch < 1.3);
    }
  });
}

test('reduced motion poses remain temporally stable', () => {
  for (const state of ['idle', 'anticipate', 'traverse', 'recover', 'solved']) {
    assert.deepEqual(poseAt(state, 0, true), poseAt(state, 500, true));
  }
});
