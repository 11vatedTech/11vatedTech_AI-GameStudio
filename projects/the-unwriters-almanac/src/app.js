import { createSimulation, FIXED_STEP, MAX_CATCH_UP_STEPS, WORLD } from './simulation.js';
import { sanitizeStroke } from './geometry.js';
import { InputController } from './input.js';
import { createRenderer } from './renderer.js';

const canvas = document.querySelector('#game');
const host = document.querySelector('#stageWrap');
const overlay = document.querySelector('#overlay');
const overlayKicker = document.querySelector('#overlayKicker');
const overlayTitle = document.querySelector('#overlayTitle');
const overlayBody = document.querySelector('#overlayBody');
const overlayAction = document.querySelector('#overlayAction');
const liveStatus = document.querySelector('#liveStatus');
const stateLabel = document.querySelector('#stateLabel');
const guidedButton = document.querySelector('#guidedButton');
const commitButton = document.querySelector('#commitButton');
const eraseButton = document.querySelector('#eraseButton');
const pauseButton = document.querySelector('#pauseButton');
const restartButton = document.querySelector('#restartButton');
const reducedMotionToggle = document.querySelector('#reducedMotion');

if (!canvas || !host) throw new Error('The puzzle page is missing its playfield.');
const game = createSimulation(0xA17A);
const renderer = createRenderer(canvas);
let previousFrame = 0;
let accumulator = 0;
let lastAnnouncedMessage = '';
let lastState = game.sim.state;
let statusTimer = 0;
let guidedSelected = false;
let drawingCommitted = false;

const announce = (message) => {
  if (!message || message === lastAnnouncedMessage) return;
  lastAnnouncedMessage = message;
  liveStatus.textContent = message;
};
const guidedShapes = [
  { label: 'Gentle current', points: [WORLD.start, { x: 384, y: 478 }, { x: 583, y: 385 }, { x: 789, y: 316 }, { x: 955, y: 253 }, WORLD.goal] },
  { label: 'High arc', points: [WORLD.start, { x: 388, y: 362 }, { x: 580, y: 337 }, { x: 770, y: 330 }, { x: 944, y: 276 }, WORLD.goal] },
  { label: 'Low sweep', points: [WORLD.start, { x: 385, y: 500 }, { x: 563, y: 460 }, { x: 746, y: 396 }, { x: 922, y: 294 }, WORLD.goal] },
];
let selectedShape = 0;

function syncUi() {
  const sim = game.sim;
  const hasStroke = sim.rail.length > 0;
  const hasDraft = sim.draft.length > 0;
  stateLabel.textContent = sim.state === 'TITLE' ? 'A line is waiting to be written' : sim.state === 'PLAYING' ? (hasStroke ? 'The rail is carrying ink and pigment' : sim.message) : sim.state === 'PAUSED' ? 'The page is paused' : 'The page is complete';
  commitButton.disabled = sim.state !== 'PLAYING' || (!hasDraft && !guidedSelected && !drawingCommitted) || hasStroke;
  eraseButton.disabled = sim.state !== 'PLAYING' || (!hasStroke && !hasDraft);
  pauseButton.disabled = sim.state === 'SOLVED';
  pauseButton.innerHTML = sim.state === 'PAUSED' ? 'Resume <kbd>Esc</kbd>' : 'Pause <kbd>Esc</kbd>';
  guidedButton.setAttribute('aria-pressed', String(guidedSelected));
  guidedButton.textContent = guidedSelected ? `Line: ${guidedShapes[selectedShape].label} · choose another` : 'Use guided line';
  if (sim.state === 'PAUSED') {
    overlay.hidden = false; overlayKicker.textContent = 'PAGE PAUSED'; overlayTitle.textContent = 'The ink is resting'; overlayBody.textContent = 'The page and its little inhabitant are waiting.'; overlayAction.textContent = 'Resume page';
  } else if (sim.state === 'SOLVED') {
    overlay.hidden = false; overlayKicker.textContent = 'FOLIO COMPLETE'; overlayTitle.textContent = 'The page found its way.'; overlayBody.textContent = 'One line carried both pigment and the little mark home.'; overlayAction.textContent = 'Begin again';
  } else overlay.hidden = true;
  if (sim.state !== lastState) {
    const announcements = { TITLE: 'Page ready. Start the page or draw a line.', PLAYING: 'The page is in play.', PAUSED: 'Page paused.', SOLVED: 'Page complete. Use Begin again to restart.' };
    announce(announcements[sim.state]); lastState = sim.state;
  }
  if (sim.state === 'TITLE' && !document.querySelector('#startButton')) {
    const startButton = document.createElement('button');
    startButton.className = 'button button-primary start-button';
    startButton.id = 'startButton';
    startButton.type = 'button';
    startButton.textContent = 'Open the page';
    startButton.setAttribute('aria-label', 'Start the puzzle page');
    startButton.addEventListener('click', () => { game.command('start'); startButton.remove(); syncUi(); canvas.focus(); });
    document.querySelector('.controls').prepend(startButton);
  } else if (sim.state !== 'TITLE') document.querySelector('#startButton')?.remove();
}

const input = new InputController(canvas, game, syncUi);
renderer.observe(host);
// Allow the browser harness to inspect the authoritative state without replacing player controls.
window.__ALMANAC_TEST__ = { game, renderer, syncUi };

function guidedAction() {
  if (game.sim.state === 'TITLE') game.command('start');
  if (guidedSelected) selectedShape = (selectedShape + 1) % guidedShapes.length;
  else guidedSelected = true;
  game.command('draw-guided', { points: guidedShapes[selectedShape].points });
  syncUi();
}

guidedButton.addEventListener('click', guidedAction);
commitButton.addEventListener('click', () => {
  if (guidedSelected && !game.sim.draft.length) game.command('draw-guided', { points: guidedShapes[selectedShape].points });
  const points = drawingCommitted ? game.sim.draft : undefined;
  const result = game.command('draw-commit', points ? { points } : {});
  guidedSelected = false;
  drawingCommitted = false;
  if (!result?.accepted) announce(game.sim.message);
  else announce('Line committed. Follow the little ink-being toward the seal.');
  syncUi();
});
eraseButton.addEventListener('click', () => { guidedSelected = false; drawingCommitted = false; game.command('erase'); syncUi(); announce(game.sim.message); canvas.focus(); });
pauseButton.addEventListener('click', () => {
  if (game.sim.state === 'PAUSED') game.command('resume'); else game.command('pause');
  syncUi();
});
restartButton.addEventListener('click', () => { guidedSelected = false; drawingCommitted = false; game.command('restart'); syncUi(); announce('Page reset. Start the page and draw a line.'); canvas.focus(); });
overlayAction.addEventListener('click', () => {
  if (game.sim.state === 'PAUSED') game.command('resume');
  else { guidedSelected = false; drawingCommitted = false; game.command('restart'); game.command('start'); }
  syncUi(); canvas.focus();
});
reducedMotionToggle.addEventListener('change', () => { game.command('reduced-motion', { value: reducedMotionToggle.checked }); syncUi(); });

// Pointer drawing is also a direct start action; a first stroke begins the page.
canvas.addEventListener('pointerdown', () => { if (game.sim.state === 'TITLE') { game.command('start'); document.querySelector('#startButton')?.remove(); syncUi(); } }, { capture: true });
window.addEventListener('keydown', (event) => {
  if (event.target instanceof Element && event.target.closest('button,input,select,textarea,a,[contenteditable="true"]')) return;
  if (game.sim.state === 'TITLE' && (event.key === 'Enter' || event.key === ' ')) {
    event.preventDefault(); game.command('start'); document.querySelector('#startButton')?.remove(); syncUi(); canvas.focus();
  }
  if (event.key === 'Escape' && game.sim.state === 'PAUSED') { game.command('resume'); syncUi(); }
});
canvas.addEventListener('pointerup', () => {
  if (game.sim.draft.length && game.sim.state === 'PLAYING') {
    const cleaned = sanitizeStroke(game.sim.draft);
    game.sim.draft = cleaned;
    drawingCommitted = cleaned.length >= 2;
    syncUi();
  }
});
canvas.addEventListener('pointercancel', () => { drawingCommitted = false; syncUi(); });
canvas.addEventListener('lostpointercapture', () => { if (!game.sim.draft.length) drawingCommitted = false; syncUi(); });

function frame(now) {
  if (!previousFrame) previousFrame = now;
  const elapsed = Math.max(0, Math.min((now - previousFrame) / 1000, MAX_CATCH_UP_STEPS * FIXED_STEP));
  previousFrame = now;
  if (game.sim.state === 'PLAYING') {
    accumulator = Math.min(accumulator + elapsed, MAX_CATCH_UP_STEPS * FIXED_STEP);
    let steps = 0;
    while (accumulator >= FIXED_STEP && steps < MAX_CATCH_UP_STEPS) {
      game.update(FIXED_STEP); accumulator -= FIXED_STEP; steps += 1;
    }
    if (steps === MAX_CATCH_UP_STEPS && accumulator >= FIXED_STEP) { game.sim.diagnostics.droppedTime += accumulator; accumulator = 0; }
  } else accumulator = 0;
  const events = game.drainEvents();
  const renderStart = performance.now();
  renderer.render(game.sim, events, elapsed);
  game.sim.diagnostics.lastRenderCpuMs = performance.now() - renderStart;
  game.sim.diagnostics.render = renderer.getDiagnostics();
  syncUi();
  statusTimer += elapsed;
  if (statusTimer > .25 && game.sim.state === 'PLAYING' && game.sim.message !== lastAnnouncedMessage) { announce(game.sim.message); statusTimer = 0; }
  requestAnimationFrame(frame);
}

window.addEventListener('pagehide', () => { input.dispose(); renderer.dispose(); }, { once: true });
requestAnimationFrame(frame);
