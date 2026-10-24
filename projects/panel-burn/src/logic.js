/* PANEL BURN: pure game rules. No DOM access, so it runs in the browser and in Node tests.

   Layout: two pages, each COLS x ROWS. Row 0 is the top row of the page on screen.
   Player 1 owns the top page and fires DOWN into the bottom page.
   Player 2 owns the bottom page and fires UP into the top page.
   A torch enters a page from the gutter and hits the first intact panel in its column.
*/
(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  else root.PanelBurn = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  const COLS = 6;
  const ROWS = 4;
  const MAX_PANELS = 5;
  const TORCH_DAMAGE = 2;
  const BURN_DAMAGE = 1;
  const REPAIR = 1;

  const TYPES = {
    core: { label: "Story Core", w: 1, h: 1, hp: 5, core: true },
    small: { label: "Small panel", w: 1, h: 1, hp: 4 },
    wide: { label: "Wide panel", w: 2, h: 1, hp: 5 },
    tall: { label: "Tall panel", w: 1, h: 2, hp: 5 },
    large: { label: "Large panel", w: 2, h: 2, hp: 7 },
  };

  const other = (p) => (p === 1 ? 2 : 1);
  const labelOf = (panel) => TYPES[panel.type].label;

  function createPage() {
    return { panels: [], nextId: 1 };
  }

  function cellsOf(panel) {
    const out = [];
    for (let dy = 0; dy < panel.h; dy++) {
      for (let dx = 0; dx < panel.w; dx++) out.push([panel.x + dx, panel.y + dy]);
    }
    return out;
  }

  function panelAt(page, x, y) {
    return page.panels.find((p) => cellsOf(p).some(([cx, cy]) => cx === x && cy === y)) || null;
  }

  // Row order a torch travels, starting at the gutter edge of the defender's page.
  // Player 2's page touches the gutter at its top (row 0); Player 1's page at its bottom.
  function rowOrder(defender) {
    const rows = Array.from({ length: ROWS }, (_, i) => i);
    return defender === 2 ? rows : rows.reverse();
  }

  function canPlace(page, type, x, y) {
    const t = TYPES[type];
    if (!t) return "Unknown panel type.";
    if (x < 0 || y < 0 || x + t.w > COLS || y + t.h > ROWS) return "That panel does not fit on the page.";
    if (page.panels.length >= MAX_PANELS) return `A page holds at most ${MAX_PANELS} panels.`;
    if (t.core && page.panels.some((p) => p.type === "core")) return "A page has only one Story Core.";
    for (let dy = 0; dy < t.h; dy++) {
      for (let dx = 0; dx < t.w; dx++) {
        if (panelAt(page, x + dx, y + dy)) return "That space is already taken.";
      }
    }
    return null;
  }

  function validatePage(page) {
    const cores = page.panels.filter((p) => p.type === "core").length;
    if (cores !== 1) return "Place exactly one Story Core on your page.";
    return null;
  }

  function createGame() {
    return {
      pages: { 1: createPage(), 2: createPage() },
      ready: { 1: false, 2: false },
      phase: "build", // build | battle | over
      turn: 1,
      winner: null,
      log: ["Player 1: build your page."],
    };
  }

  function note(state, msg) {
    state.log.push(msg);
  }

  function assertCanEdit(state, p) {
    if (state.phase !== "build") throw new Error("Pages are locked once battle begins.");
    if (state.ready[p]) throw new Error(`Player ${p} is already ready.`);
  }

  function place(state, p, type, x, y) {
    assertCanEdit(state, p);
    const page = state.pages[p];
    const err = canPlace(page, type, x, y);
    if (err) throw new Error(err);
    const t = TYPES[type];
    const panel = { id: page.nextId++, type, x, y, w: t.w, h: t.h, hp: t.hp, maxHp: t.hp, burning: false };
    page.panels.push(panel);
    return panel;
  }

  function remove(state, p, panelId) {
    assertCanEdit(state, p);
    const page = state.pages[p];
    if (!page.panels.some((q) => q.id === panelId)) throw new Error("No such panel.");
    page.panels = page.panels.filter((q) => q.id !== panelId);
  }

  function assertBattle(state, p) {
    if (state.phase !== "battle") throw new Error("Battle has not started.");
    if (state.turn !== p) throw new Error(`It is Player ${other(p)}'s turn.`);
  }

  function setReady(state, p) {
    if (state.phase !== "build") throw new Error("Battle has already started.");
    if (state.ready[p]) return;
    const err = validatePage(state.pages[p]);
    if (err) throw new Error(err);
    state.ready[p] = true;
    if (state.ready[1] && state.ready[2]) {
      state.phase = "battle";
      state.turn = 1;
      note(state, "Battle begins. Player 1 fires first.");
    } else {
      note(state, `Player ${p} is ready.`);
    }
  }

  // Deal damage to a panel on `owner`'s page. Destroyed panels leave the page (opening a gap).
  // A destroyed Story Core ends the match in favor of the other player.
  function applyDamage(state, owner, panel, amount) {
    panel.hp -= amount;
    if (panel.hp > 0) return { destroyed: false };
    const page = state.pages[owner];
    page.panels = page.panels.filter((q) => q.id !== panel.id);
    note(state, `${labelOf(panel)} on Player ${owner}'s page is destroyed.`);
    if (panel.type === "core") {
      state.winner = other(owner);
      note(state, `Story Core destroyed. Player ${state.winner} wins.`);
    }
    return { destroyed: true };
  }

  // Burning panels take damage at the start of their owner's turn.
  function tickBurn(state, p) {
    for (const panel of [...state.pages[p].panels]) {
      if (state.winner) break;
      if (!panel.burning) continue;
      note(state, `Fire eats at the ${labelOf(panel)} on Player ${p}'s page.`);
      applyDamage(state, p, panel, BURN_DAMAGE);
    }
  }

  function endTurn(state) {
    if (state.phase !== "battle") return;
    if (!state.winner) {
      state.turn = other(state.turn);
      tickBurn(state, state.turn);
    }
    if (state.winner) state.phase = "over";
  }

  // Attacker launches one torch into column `col` of the opposing page.
  // Returns what happened, so the interface can animate it.
  function fire(state, attacker, col) {
    assertBattle(state, attacker);
    if (!Number.isInteger(col) || col < 0 || col >= COLS) throw new Error("Choose a column on the opposing page.");
    const defender = other(attacker);
    const page = state.pages[defender];
    let result = { outcome: "miss", col, row: null, panelId: null, type: null, destroyed: false };

    for (const row of rowOrder(defender)) {
      const panel = panelAt(page, col, row);
      if (!panel) continue;
      const { destroyed } = applyDamage(state, defender, panel, TORCH_DAMAGE);
      if (!destroyed) {
        panel.burning = true;
        note(state, `Torch hits the ${labelOf(panel)} on Player ${defender}'s page and sets it alight.`);
      }
      result = { outcome: "hit", col, row, panelId: panel.id, type: panel.type, destroyed, hp: panel.hp };
      break;
    }

    if (result.outcome === "miss") {
      note(state, `Player ${attacker}'s torch flies through an empty lane in column ${col + 1}.`);
    }
    endTurn(state);
    return result;
  }

  // The one-action defense: extinguish a burning panel, or repair an injured one.
  function reinforce(state, p, panelId) {
    assertBattle(state, p);
    const panel = state.pages[p].panels.find((q) => q.id === panelId);
    if (!panel) throw new Error("Choose one of your own panels.");
    let action;
    if (panel.burning) {
      panel.burning = false;
      action = "extinguish";
      note(state, `Player ${p} puts out the fire on the ${labelOf(panel)}.`);
    } else if (panel.hp < panel.maxHp) {
      panel.hp = Math.min(panel.maxHp, panel.hp + REPAIR);
      action = "repair";
      note(state, `Player ${p} reinforces the ${labelOf(panel)}.`);
    } else {
      throw new Error("That panel is intact and not burning. Pick another panel or throw a torch instead.");
    }
    endTurn(state);
    return { action, panelId };
  }

  return {
    COLS,
    ROWS,
    MAX_PANELS,
    TORCH_DAMAGE,
    BURN_DAMAGE,
    REPAIR,
    TYPES,
    other,
    labelOf,
    createGame,
    canPlace,
    validatePage,
    place,
    remove,
    setReady,
    fire,
    reinforce,
    panelAt,
    rowOrder,
  };
});
