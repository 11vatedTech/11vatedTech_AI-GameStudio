/* PANEL BURN: browser interface. All rules live in logic.js. */
(function () {
  const PB = window.PanelBurn;
  const { COLS, ROWS, TYPES, other } = PB;
  const $ = (sel) => document.querySelector(sel);

  const els = {
    status: $("#status"),
    msg: $("#msg"),
    book: $("#book"),
    log: $("#log"),
    palette: $("#palette"),
    ready: $("#ready"),
    modes: $("#modes"),
    restart: $("#restart"),
    buildControls: $("#build-controls"),
    battleControls: $("#battle-controls"),
  };

  const state = {
    game: PB.createGame(),
    buildType: "small",
    mode: "torch",
    busy: false,
    msg: "",
    msgIsError: false,
  };

  const sheetOf = (p) => document.querySelector(`#page-${p} .sheet`);
  const builder = () => (state.game.ready[1] ? 2 : 1);

  function showMsg(text, isError) {
    state.msg = text;
    state.msgIsError = !!isError;
    render();
  }

  // Build the static grid cells once; panels are redrawn each render.
  function initCells() {
    for (const p of [1, 2]) {
      const holder = sheetOf(p).querySelector(".cells");
      holder.innerHTML = "";
      for (let y = 0; y < ROWS; y++) {
        for (let x = 0; x < COLS; x++) {
          const cell = document.createElement("div");
          cell.className = "cell";
          cell.dataset.page = p;
          cell.dataset.x = x;
          cell.dataset.y = y;
          holder.appendChild(cell);
        }
      }
    }
  }

  function renderPages() {
    for (const p of [1, 2]) {
      const layer = sheetOf(p).querySelector(".panels");
      layer.innerHTML = "";
      for (const panel of state.game.pages[p].panels) {
        const el = document.createElement("div");
        el.className = `panel type-${panel.type}${panel.burning ? " burning" : ""}`;
        el.dataset.page = p;
        el.dataset.id = panel.id;
        el.dataset.x = panel.x;
        el.dataset.y = panel.y;
        el.style.left = `${(panel.x / COLS) * 100}%`;
        el.style.top = `${(panel.y / ROWS) * 100}%`;
        el.style.width = `${(panel.w / COLS) * 100}%`;
        el.style.height = `${(panel.h / ROWS) * 100}%`;

        const name = document.createElement("span");
        name.className = "name";
        name.textContent = TYPES[panel.type].label;
        const hp = document.createElement("span");
        hp.className = "hp";
        hp.textContent = "♥".repeat(Math.max(0, panel.hp));
        el.append(name, hp);
        layer.appendChild(el);
      }
    }
  }

  function statusText() {
    const g = state.game;
    if (g.phase === "build") {
      const b = builder();
      const count = g.pages[b].panels.length;
      return `Player ${b}: build your page (${count}/${PB.MAX_PANELS} panels). Player ${other(b)}'s page is sealed until battle.`;
    }
    if (g.phase === "over") {
      return `Player ${g.winner} wins! The Story Core is destroyed. Press New match to play again.`;
    }
    const t = g.turn;
    return state.mode === "torch"
      ? `Player ${t}'s turn: click a column on Player ${other(t)}'s page to throw a torch.`
      : `Player ${t}'s turn: click one of your own panels to reinforce it (this uses your one action).`;
  }

  function render() {
    const g = state.game;
    const building = g.phase === "build";

    renderPages();

    for (const p of [1, 2]) {
      const page = $(`#page-${p}`);
      const sealed = building ? p !== builder() : false;
      page.classList.toggle("sealed", sealed);
      const isActive = building ? p === builder() : p === g.turn && g.phase === "battle";
      page.classList.toggle("active", isActive);
    }

    els.buildControls.hidden = !building;
    els.battleControls.hidden = building;

    els.palette.querySelectorAll("button").forEach((b) => {
      b.classList.toggle("on", b.dataset.type === state.buildType);
    });
    els.modes.querySelectorAll("button").forEach((b) => {
      b.classList.toggle("on", b.dataset.mode === state.mode);
    });

    els.status.textContent = statusText();
    els.msg.textContent = state.msg;
    els.msg.style.color = state.msgIsError ? "#7a1d00" : "#14532d";

    els.log.innerHTML = "";
    g.log.slice(-8).reverse().forEach((line) => {
      const li = document.createElement("li");
      li.textContent = line;
      els.log.appendChild(li);
    });
  }

  function clearColumnHighlight() {
    document.querySelectorAll(".cell.col-hot").forEach((c) => c.classList.remove("col-hot"));
  }

  function highlightColumn(page, x) {
    clearColumnHighlight();
    document
      .querySelectorAll(`.cell[data-page="${page}"][data-x="${x}"]`)
      .forEach((c) => c.classList.add("col-hot"));
  }

  // Visual of the torch crossing the gutter. Game state has already changed; this only shows it.
  function animateTorch(attacker, col, result, done) {
    const defender = other(attacker);
    const book = els.book.getBoundingClientRect();
    const sheet = sheetOf(defender).getBoundingClientRect();
    const cellH = sheet.height / ROWS;
    const cellW = sheet.width / COLS;
    const x = sheet.left - book.left + (col + 0.5) * cellW;
    const pageTop = sheet.top - book.top;
    const pageBottom = pageTop + sheet.height;

    // Player 2's page touches the gutter at its top; Player 1's at its bottom.
    const entryY = defender === 2 ? pageTop - 8 : pageBottom + 8;
    const exitY = defender === 2 ? pageBottom + 8 : pageTop - 8;
    const hitY = result.outcome === "hit" ? pageTop + (result.row + 0.5) * cellH : exitY;

    const flame = document.createElement("div");
    flame.className = "flame";
    flame.style.left = `${x}px`;
    flame.style.top = `${entryY}px`;
    els.book.appendChild(flame);

    requestAnimationFrame(() =>
      requestAnimationFrame(() => {
        flame.style.top = `${hitY}px`;
      })
    );

    setTimeout(() => {
      flame.remove();
      els.book.classList.remove("shake");
      void els.book.offsetWidth; // restart the shake animation
      els.book.classList.add("shake");

      const word =
        result.outcome !== "hit" ? "WHOOSH!" : result.destroyed ? "KRAAAK!" : "WHAM!";
      const impact = document.createElement("div");
      impact.className = "impact";
      impact.textContent = word;
      impact.style.left = `${x}px`;
      impact.style.top = `${hitY}px`;
      els.book.appendChild(impact);
      setTimeout(() => impact.remove(), 650);

      setTimeout(done, 450);
    }, 480);
  }

  function describe(result, attacker) {
    if (result.outcome === "miss") return `Player ${attacker}'s torch found an empty lane.`;
    if (result.destroyed) return `Player ${attacker}'s torch destroyed a panel.`;
    return `Player ${attacker}'s torch hit a panel and set it alight.`;
  }

  function fireAt(attacker, col) {
    const result = PB.fire(state.game, attacker, col);
    state.busy = true;
    clearColumnHighlight();
    state.msg = "";
    // Re-render only once the torch has landed, so the board does not reveal the result early.
    animateTorch(attacker, col, result, () => {
      state.busy = false;
      showMsg(describe(result, attacker), false);
    });
  }

  function handleBuildClick(page, panelEl, cellEl) {
    if (page !== builder()) {
      showMsg(`Player ${page}'s page is sealed until it is their turn to build.`, true);
      return;
    }
    if (panelEl) {
      PB.remove(state.game, page, Number(panelEl.dataset.id));
      showMsg("Panel removed.", false);
      return;
    }
    if (cellEl) {
      PB.place(state.game, page, state.buildType, Number(cellEl.dataset.x), Number(cellEl.dataset.y));
      showMsg("", false);
    }
  }

  function handleBattleClick(page, panelEl, cellEl) {
    const t = state.game.turn;
    if (state.mode === "torch") {
      if (page === t) {
        showMsg(`Launch torches at Player ${other(t)}'s page, not your own.`, true);
        return;
      }
      const col = cellEl ? Number(cellEl.dataset.x) : Number(panelEl.dataset.x);
      fireAt(t, col);
      return;
    }
    // reinforce
    if (page !== t || !panelEl) {
      showMsg("Reinforce one of your own panels.", true);
      return;
    }
    const { action } = PB.reinforce(state.game, t, Number(panelEl.dataset.id));
    state.mode = "torch"; // the action is spent; the next player starts with torches
    showMsg(action === "extinguish" ? "Fire put out." : "Panel reinforced.", false);
  }

  function onBookClick(e) {
    if (state.busy) return;
    const panelEl = e.target.closest(".panel");
    const cellEl = e.target.closest(".cell");
    const hit = panelEl || cellEl;
    if (!hit) return;
    const page = Number(hit.dataset.page);
    if (!page) return;

    try {
      if (state.game.phase === "build") handleBuildClick(page, panelEl, cellEl);
      else if (state.game.phase === "battle") handleBattleClick(page, panelEl, cellEl);
      else showMsg("The match is over. Press New match to play again.", true);
    } catch (err) {
      showMsg(err.message, true);
    }
  }

  function onBookHover(e) {
    if (state.busy || state.game.phase !== "battle" || state.mode !== "torch") return;
    const cellEl = e.target.closest(".cell");
    const panelEl = e.target.closest(".panel");
    const hit = cellEl || panelEl;
    if (!hit || Number(hit.dataset.page) !== other(state.game.turn)) {
      clearColumnHighlight();
      return;
    }
    highlightColumn(Number(hit.dataset.page), Number(hit.dataset.x));
  }

  function bind() {
    els.palette.addEventListener("click", (e) => {
      const btn = e.target.closest("button[data-type]");
      if (!btn) return;
      state.buildType = btn.dataset.type;
      showMsg("", false);
    });

    els.ready.addEventListener("click", () => {
      try {
        PB.setReady(state.game, builder());
        showMsg(
          state.game.phase === "battle" ? "Battle begins!" : "Pass the device to the next builder.",
          false
        );
      } catch (err) {
        showMsg(err.message, true);
      }
    });

    els.modes.addEventListener("click", (e) => {
      const btn = e.target.closest("button[data-mode]");
      if (!btn) return;
      state.mode = btn.dataset.mode;
      clearColumnHighlight();
      showMsg("", false);
    });

    els.restart.addEventListener("click", () => {
      state.game = PB.createGame();
      state.mode = "torch";
      state.busy = false;
      state.buildType = "small";
      clearColumnHighlight();
      showMsg("", false);
    });

    els.book.addEventListener("click", onBookClick);
    els.book.addEventListener("mouseover", onBookHover);
    els.book.addEventListener("mouseleave", clearColumnHighlight);
  }

  initCells();
  bind();
  render();
})();
