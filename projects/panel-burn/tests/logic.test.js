const test = require("node:test");
const assert = require("node:assert/strict");
const PB = require("../src/logic.js");

// Build a started match. Each list holds [type, x, y] placements for one player.
function started(p1, p2) {
  const g = PB.createGame();
  p1.forEach(([t, x, y]) => PB.place(g, 1, t, x, y));
  p2.forEach(([t, x, y]) => PB.place(g, 2, t, x, y));
  PB.setReady(g, 1);
  PB.setReady(g, 2);
  return g;
}
const at = (g, p, x, y) => PB.panelAt(g.pages[p], x, y);

test("placement rules: bounds, overlap, one core, five-panel limit", () => {
  const g = PB.createGame();
  PB.place(g, 1, "core", 0, 0);
  assert.throws(() => PB.place(g, 1, "small", 0, 0), /taken/);
  assert.throws(() => PB.place(g, 1, "large", 5, 0), /fit/);
  assert.throws(() => PB.place(g, 1, "core", 3, 3), /one Story Core/);
  PB.place(g, 1, "small", 1, 0);
  PB.place(g, 1, "small", 2, 0);
  PB.place(g, 1, "small", 3, 0);
  PB.place(g, 1, "small", 4, 0);
  assert.throws(() => PB.place(g, 1, "small", 5, 0), /at most 5/);
});

test("a page needs exactly one Story Core before readying", () => {
  const g = PB.createGame();
  assert.match(PB.validatePage(g.pages[1]), /Story Core/);
  PB.place(g, 1, "small", 0, 0);
  assert.match(PB.validatePage(g.pages[1]), /Story Core/);
  assert.throws(() => PB.setReady(g, 1), /Story Core/);
});

test("torch from player 1 enters the bottom page from the gutter and stops at the first panel", () => {
  const g = started([["core", 0, 0]], [["small", 2, 0], ["core", 2, 3]]);
  const r = PB.fire(g, 1, 2);
  assert.equal(r.outcome, "hit");
  assert.equal(r.row, 0);
  assert.equal(r.type, "small");
  assert.equal(r.destroyed, false);
  // Torch deals 2, then the barricade burns for 1 at the start of player 2's turn.
  assert.equal(at(g, 2, 2, 0).hp, 1);
  assert.equal(at(g, 2, 2, 0).burning, true);
  assert.equal(at(g, 2, 2, 3).hp, 5, "core is shielded by the barricade");
});

test("a barricade protects the core until it is destroyed, then the lane opens", () => {
  const g = started([["core", 0, 0]], [["small", 2, 0], ["core", 2, 3]]);
  PB.fire(g, 1, 2); // barricade 4 -> 2, then burns to 1 at P2's turn start
  PB.reinforce(g, 2, at(g, 2, 2, 0).id); // P2 puts out the fire
  const shot2 = PB.fire(g, 1, 2); // barricade 1 -> destroyed
  assert.equal(shot2.type, "small");
  assert.equal(shot2.destroyed, true);
  assert.equal(at(g, 2, 2, 0), null);
  PB.fire(g, 2, 5); // P2 spends a turn on an empty column in P1's page
  const shot3 = PB.fire(g, 1, 2); // the torch now reaches the core
  assert.equal(shot3.type, "core");
  assert.equal(shot3.row, 3);
  assert.equal(g.winner, null);
});

test("burning damage ticks on the owner's turn until extinguished or destroyed", () => {
  const g = started([["core", 5, 3]], [["small", 0, 0], ["core", 5, 0]]);
  PB.fire(g, 1, 0); // P2 small: 4 -> 2, then burn tick at P2's turn start -> 1
  assert.equal(at(g, 2, 0, 0).hp, 1);
  assert.equal(at(g, 2, 0, 0).burning, true);
  PB.fire(g, 2, 5); // P2 fires at P1's core (column 5), not at its own page
  assert.equal(at(g, 2, 0, 0).hp, 1, "no tick on P1's turn: P2 panel still at 1");
  PB.fire(g, 1, 1); // P1 misses an empty column in P2's page
  assert.equal(at(g, 2, 0, 0), null, "P2's next turn burns the last HP away");
});

test("destroying the Story Core ends the match", () => {
  const g = started([["core", 5, 3]], [["core", 0, 0]]);
  PB.fire(g, 1, 0); // P2 core 5 -> 3, burning; burn tick at P2 turn start -> 2
  assert.equal(at(g, 2, 0, 0).hp, 2);
  PB.reinforce(g, 2, at(g, 2, 0, 0).id); // P2 extinguishes its core
  PB.fire(g, 1, 0); // 2 -> 0, destroyed
  assert.equal(g.winner, 1);
  assert.equal(g.phase, "over");
  assert.throws(() => PB.fire(g, 2, 0), /has not started|turn/);
});

test("reinforce rejects an intact, unburnt panel", () => {
  const g = started([["core", 0, 0]], [["core", 0, 0]]);
  assert.throws(() => PB.reinforce(g, 1, at(g, 1, 0, 0).id), /intact/);
});

test("turn order is enforced", () => {
  const g = started([["core", 0, 0]], [["core", 0, 0]]);
  assert.throws(() => PB.fire(g, 2, 0), /turn/);
});

test("player 2's torch enters the top page from the bottom edge", () => {
  const g = started([["core", 5, 0], ["small", 0, 3]], [["core", 5, 3]]);
  PB.fire(g, 1, 0); // P1 misses P2's empty column 0
  const r = PB.fire(g, 2, 0);
  assert.equal(r.outcome, "hit");
  assert.equal(r.row, 3, "torch starts at the gutter edge (bottom row of the top page)");
  assert.equal(r.type, "small");
});
