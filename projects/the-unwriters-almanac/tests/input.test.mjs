import test from 'node:test';
import assert from 'node:assert/strict';
import { toLogicalPoint } from '../src/input.js';

test('pointer coordinates map into the same logical point after CSS scaling', () => {
  const logical = { width: 1280, height: 720 };
  const rect = { left: 20, top: 40, width: 640, height: 360 };
  assert.deepEqual(toLogicalPoint(20 + 320, 40 + 180, rect, logical), { x: 640, y: 360 });
  assert.deepEqual(toLogicalPoint(20 + 160, 40 + 90, rect, logical), { x: 320, y: 180 });
});

test('contain-fit mapping accounts for letterboxing and rejects points outside the page', () => {
  const rect = { left: 0, top: 0, width: 500, height: 500 };
  assert.deepEqual(toLogicalPoint(250, 250, rect), { x: 640, y: 360 });
  assert.equal(toLogicalPoint(250, 10, rect), null);
  assert.deepEqual(toLogicalPoint(5, 250, rect), { x: 12.8, y: 360 });
  assert.equal(toLogicalPoint(-1, 250, rect), null);
  assert.equal(toLogicalPoint(0, 0, { left: 0, top: 0, width: 0, height: 4 }), null);
});
