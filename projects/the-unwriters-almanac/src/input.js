import { PAGE } from './geometry.js';

export function toLogicalPoint(clientX, clientY, rect, logical = PAGE) {
  if (!rect || rect.width <= 0 || rect.height <= 0 || !Number.isFinite(clientX) || !Number.isFinite(clientY)) return null;
  const scale = Math.min(rect.width / logical.width, rect.height / logical.height);
  const width = logical.width * scale;
  const height = logical.height * scale;
  const left = rect.left + (rect.width - width) / 2;
  const top = rect.top + (rect.height - height) / 2;
  if (clientX < left || clientY < top || clientX > left + width || clientY > top + height) return null;
  const x = (clientX - left) / scale;
  const y = (clientY - top) / scale;
  if (x < 0 || y < 0 || x > logical.width || y > logical.height) return null;
  return { x, y };
}

export class InputController {
  constructor(canvas, game, onChange = () => {}) {
    this.canvas = canvas;
    this.game = game;
    this.onChange = onChange;
    this.pointerId = null;
    this.keys = new Set();
    this.handlers = [];
    this.listen(canvas, 'pointerdown', (event) => this.pointerDown(event));
    this.listen(canvas, 'pointermove', (event) => this.pointerMove(event));
    this.listen(canvas, 'pointerup', (event) => this.pointerEnd(event, false));
    this.listen(canvas, 'pointercancel', (event) => this.pointerEnd(event, true));
    this.listen(canvas, 'lostpointercapture', (event) => this.pointerEnd(event, true));
    this.listen(window, 'blur', () => this.cancel('window_blur'));
    this.listen(document, 'visibilitychange', () => { if (document.hidden) this.cancel('document_hidden'); });
    this.listen(window, 'keydown', (event) => this.keyDown(event));
    this.listen(window, 'keyup', (event) => this.keyUp(event));
  }
  listen(target, type, handler) { target.addEventListener(type, handler); this.handlers.push([target, type, handler]); }
  point(event) { return toLogicalPoint(event.clientX, event.clientY, this.canvas.getBoundingClientRect()); }
  pointerDown(event) {
    if (event.button !== 0 || this.pointerId !== null || this.game.sim.state !== 'PLAYING') return;
    const point = this.point(event);
    if (!point || !this.game.command('draw-start', { point })) return;
    this.pointerId = event.pointerId;
    this.canvas.setPointerCapture?.(event.pointerId);
    event.preventDefault(); this.onChange();
  }
  pointerMove(event) {
    if (this.pointerId !== event.pointerId || !this.game.sim.draft.length) return;
    const point = this.point(event);
    if (point) this.game.command('draw-point', { point });
    this.onChange();
  }
  pointerEnd(event, cancelled) {
    if (this.pointerId !== event.pointerId) return;
    const point = this.point(event);
    if (!cancelled && point) this.game.command('draw-point', { point });
    this.pointerId = null;
    if (this.canvas.hasPointerCapture?.(event.pointerId)) this.canvas.releasePointerCapture(event.pointerId);
    if (cancelled || !point) this.game.command('draw-cancel', { reason: cancelled ? 'pointer_cancelled' : 'pointer_outside_page' });
    else this.game.command('draw-commit');
    this.onChange();
  }
  cancel(reason) {
    if (this.pointerId === null) return;
    const pointerId = this.pointerId; this.pointerId = null;
    if (this.canvas.hasPointerCapture?.(pointerId)) this.canvas.releasePointerCapture(pointerId);
    this.game.command('draw-cancel', { reason }); this.onChange();
  }
  keyDown(event) {
    const key = event.key.toLowerCase();
    const nativeControl = event.target instanceof Element && event.target.closest('button,input,select,textarea,a,[contenteditable="true"]');
    if (nativeControl && key !== 'escape') return;
    if (event.repeat && ['Escape', 'p', 'P', 'r', 'R', 'e', 'E', ' '].includes(event.key)) return;
    if (['arrowleft', 'arrowright', ' ', 'arrowup', 'w'].includes(key)) event.preventDefault();
    if (key === 'arrowleft' || key === 'a') this.keys.add('left');
    if (key === 'arrowright' || key === 'd') this.keys.add('right');
    if (key === ' ' || key === 'arrowup' || key === 'w') { this.keys.add('jump'); if (!event.repeat) this.game.command('jump'); }
    if (key === 'e') this.game.command('erase');
    if (key === 'r') { this.cancel('restart'); this.game.command('restart'); }
    if (key === 'escape' || key === 'p') {
      if (this.game.sim.state === 'PLAYING') { this.cancel('pause'); this.game.command('pause'); }
      else if (this.game.sim.state === 'PAUSED') this.game.command('resume');
    }
    this.game.command('move', { axis: (this.keys.has('right') ? 1 : 0) - (this.keys.has('left') ? 1 : 0) });
    this.onChange();
  }
  keyUp(event) {
    const nativeControl = event.target instanceof Element && event.target.closest('button,input,select,textarea,a,[contenteditable="true"]');
    if (nativeControl) return;
    const key = event.key.toLowerCase();
    if (key === 'arrowleft' || key === 'a') this.keys.delete('left');
    if (key === 'arrowright' || key === 'd') this.keys.delete('right');
    if (key === ' ' || key === 'arrowup' || key === 'w') this.keys.delete('jump');
    this.game.command('move', { axis: (this.keys.has('right') ? 1 : 0) - (this.keys.has('left') ? 1 : 0) });
  }
  dispose() { this.cancel('dispose'); for (const [target, type, handler] of this.handlers) target.removeEventListener(type, handler); this.handlers = []; }
}
