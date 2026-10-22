import { PAGE } from './geometry.js';
import { poseAt } from './animation.js';

const C = Object.freeze({ paper: '#F1E7CF', light: '#FAF6E9', ink: '#182A35', sage: '#688A87', rust: '#D96C4D', gold: '#E7B957', graphite: '#58635D' });
const seedRandom = (seed) => { let value = seed >>> 0 || 1; return () => { value ^= value << 13; value ^= value >>> 17; value ^= value << 5; return (value >>> 0) / 4294967296; }; };

export function createRenderer(canvas) {
  const ctx = canvas.getContext('2d', { alpha: false });
  if (!ctx) throw new Error('Canvas2D is unavailable');
  let particles = [];
  let generatedSeed = -1;
  let resizeObserver;
  const renderSamples = [];

  const path = (points, context = ctx) => {
    if (!points?.length) return;
    context.beginPath(); context.moveTo(points[0].x, points[0].y);
    for (let i = 1; i < points.length; i += 1) context.lineTo(points[i].x, points[i].y);
  };
  const line = (points, color, width, alpha = 1, dash = []) => {
    if (!points?.length) return;
    ctx.save(); ctx.globalAlpha = alpha; ctx.strokeStyle = color; ctx.lineWidth = width; ctx.lineCap = 'round'; ctx.lineJoin = 'round'; ctx.setLineDash(dash); path(points); ctx.stroke(); ctx.restore();
  };
  const drawPaper = (seed, time, reducedMotion) => {
    ctx.fillStyle = C.paper; ctx.fillRect(0, 0, PAGE.width, PAGE.height);
    const rand = seedRandom(seed ^ 0x51a7);
    for (let i = 0; i < 340; i += 1) {
      const x = rand() * PAGE.width; const y = rand() * PAGE.height;
      ctx.fillStyle = i % 3 ? 'rgba(24,42,53,.045)' : 'rgba(255,255,255,.2)';
      ctx.fillRect(x, y, .65 + rand() * 1.1, .55 + rand() * .9);
    }
    ctx.save();
    const washTime = reducedMotion ? 0 : time;
    const wash = (x, y, rx, ry, color, speed) => {
      const scale = 1 + Math.sin(washTime * speed) * .035;
      const gradient = ctx.createRadialGradient(x, y, 5, x, y, rx * scale);
      gradient.addColorStop(0, color); gradient.addColorStop(.58, color.replace(/[\d.]+\)$/, '0.06)')); gradient.addColorStop(1, 'rgba(104,138,135,0)');
      ctx.fillStyle = gradient; ctx.beginPath(); ctx.ellipse(x, y, rx * scale, ry * scale, 0, 0, Math.PI * 2); ctx.fill();
    };
    wash(500, 320, 262, 165, 'rgba(104,138,135,.20)', .31);
    wash(916, 442, 213, 137, 'rgba(231,185,87,.13)', .22);
    wash(225, 548, 153, 68, 'rgba(217,108,77,.07)', .19);
    ctx.restore();

    // Page edge and sparse registration/marginal marks keep the composition authored, not faux-antique.
    ctx.strokeStyle = 'rgba(24,42,53,.20)'; ctx.lineWidth = 1;
    ctx.strokeRect(24, 24, PAGE.width - 48, PAGE.height - 48);
    ctx.strokeStyle = 'rgba(24,42,53,.12)'; ctx.beginPath(); ctx.moveTo(56, 68); ctx.lineTo(1224, 68); ctx.moveTo(56, 650); ctx.lineTo(1224, 650); ctx.stroke();
    ctx.fillStyle = 'rgba(24,42,53,.52)'; ctx.font = '12px Georgia, serif'; ctx.fillText('A LINE IS A KIND OF WEATHER', 62, 52);
    ctx.font = '11px Courier New, monospace'; ctx.fillText('FOLIO 01 · THE DRAWN RIDGE', 1035, 52);

    // Printed ridges are the only non-player authored walkable surfaces.
    ctx.save(); ctx.lineWidth = 3; ctx.strokeStyle = C.ink; ctx.fillStyle = 'rgba(104,138,135,.23)'; ctx.lineJoin = 'round';
    ctx.beginPath(); ctx.moveTo(100, 584); ctx.lineTo(100, 559); ctx.bezierCurveTo(151, 547, 235, 546, 372, 559); ctx.lineTo(372, 584); ctx.closePath(); ctx.fill(); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(911, 250); ctx.lineTo(911, 222); ctx.bezierCurveTo(968, 214, 1033, 216, 1116, 224); ctx.lineTo(1116, 250); ctx.closePath(); ctx.fill(); ctx.stroke();
    ctx.strokeStyle = 'rgba(24,42,53,.23)'; ctx.lineWidth = 1; ctx.setLineDash([3, 7]);
    ctx.beginPath(); ctx.moveTo(114, 579); ctx.lineTo(358, 579); ctx.moveTo(928, 239); ctx.lineTo(1098, 239); ctx.stroke(); ctx.restore();

    // A sparse botanical marginal drawing stays outside collision space.
    ctx.save(); ctx.globalAlpha = .34; ctx.strokeStyle = C.sage; ctx.lineWidth = 1.35; ctx.beginPath(); ctx.moveTo(1170, 405); ctx.bezierCurveTo(1198, 382, 1181, 350, 1205, 328); ctx.stroke();
    for (const [x, y, rotation] of [[1183, 389, -.5], [1190, 365, .6], [1191, 342, -.55]]) { ctx.save(); ctx.translate(x, y); ctx.rotate(rotation); ctx.beginPath(); ctx.ellipse(0, 0, 6, 14, 0, 0, Math.PI * 2); ctx.stroke(); ctx.restore(); }
    ctx.restore();
  };
  const drawGoal = (goal, solved, time, reducedMotion) => {
    if (reducedMotion) time = 0;
    ctx.save(); ctx.translate(goal.x, goal.y); ctx.rotate(Math.PI / 4);
    ctx.strokeStyle = solved ? C.rust : C.ink; ctx.lineWidth = 2.4; ctx.strokeRect(-20, -20, 40, 40);
    ctx.rotate(-Math.PI / 4); ctx.beginPath(); ctx.arc(0, 0, 12, 0, Math.PI * 2); ctx.stroke();
    ctx.fillStyle = solved ? C.rust : C.gold; ctx.beginPath(); ctx.arc(0, 0, 4 + (solved ? 0 : Math.sin(time * 2) * 1.2), 0, Math.PI * 2); ctx.fill();
    ctx.fillStyle = C.ink; ctx.font = '12px Georgia, serif'; ctx.textAlign = 'center'; ctx.fillText(solved ? 'page complete' : 'folio seal', 0, -29);
    ctx.restore();
  };
  const drawBead = (bead, time, reducedMotion) => {
    if (reducedMotion) time = 0;
    ctx.save(); ctx.shadowColor = 'rgba(231,185,87,.38)'; ctx.shadowBlur = 14;
    ctx.fillStyle = C.gold; ctx.strokeStyle = C.light; ctx.lineWidth = 3;
    ctx.beginPath(); ctx.arc(bead.x, bead.y, 10, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
    ctx.shadowBlur = 0; ctx.fillStyle = 'rgba(250,246,233,.85)'; ctx.beginPath(); ctx.arc(bead.x - 3, bead.y - 3, 2.2, 0, Math.PI * 2); ctx.fill();
    ctx.strokeStyle = 'rgba(231,185,87,.48)'; ctx.lineWidth = 1.2; ctx.beginPath(); ctx.arc(bead.x, bead.y, 16 + Math.sin(time * 2) * 1.5, 0, Math.PI * 2); ctx.stroke();
    ctx.restore();
  };
  const drawCreature = (actor, reducedMotion, time, scale = 1) => {
    const pose = poseAt(actor.pose, time, reducedMotion);
    ctx.save(); ctx.translate(actor.x, actor.y + pose.bob); ctx.rotate(actor.angle + pose.tilt); ctx.scale(actor.facing * pose.stretch, pose.squash);
    // Fixed body and eye anchors preserve identity; pose deformation affects the same authored silhouette.
    ctx.lineCap = 'round'; ctx.lineJoin = 'round';
    ctx.strokeStyle = C.ink; ctx.lineWidth = 9; ctx.beginPath(); ctx.moveTo(-15, 14); ctx.quadraticCurveTo(-29 + pose.tail * 12, 29 + pose.tail * 4, -45 + pose.tail * 23, 21 - pose.tail * 8); ctx.stroke();
    ctx.strokeStyle = C.rust; ctx.lineWidth = 3.5; ctx.beginPath(); ctx.moveTo(-15, 14); ctx.quadraticCurveTo(-29 + pose.tail * 12, 29 + pose.tail * 4, -45 + pose.tail * 23, 21 - pose.tail * 8); ctx.stroke();
    ctx.fillStyle = C.ink; ctx.beginPath(); ctx.moveTo(-28, 6); ctx.bezierCurveTo(-38, -9, -23, -31, -4, -34); ctx.bezierCurveTo(15, -40, 35, -27, 35, -9); ctx.bezierCurveTo(41, 11, 24, 31, 4, 29); ctx.bezierCurveTo(-11, 31, -25, 21, -28, 6); ctx.closePath(); ctx.fill();
    ctx.fillStyle = C.rust; ctx.beginPath(); ctx.ellipse(21, 19, 5.5, 4, -.25, 0, Math.PI * 2); ctx.fill();
    if (pose.anticipation) { ctx.strokeStyle = 'rgba(217,108,77,.65)'; ctx.lineWidth = 1.4; ctx.beginPath(); ctx.arc(3, -3, 47, -.75, -.25); ctx.stroke(); }
    if (pose.blink < .5) {
      ctx.strokeStyle = C.light; ctx.lineWidth = 3.5;
      ctx.beginPath(); ctx.moveTo(4, -8); ctx.lineTo(10, -8); ctx.moveTo(20, -9); ctx.lineTo(26, -9); ctx.stroke();
    } else {
      ctx.fillStyle = C.light; ctx.beginPath(); ctx.ellipse(8, -8, 4.4, 7, -.12, 0, Math.PI * 2); ctx.ellipse(23, -9, 4.1, 6.7, -.1, 0, Math.PI * 2); ctx.fill();
      ctx.fillStyle = C.ink; ctx.beginPath(); ctx.arc(9, -7.3, 1.45, 0, Math.PI * 2); ctx.arc(24, -8.3, 1.4, 0, Math.PI * 2); ctx.fill();
    }
    ctx.restore();
  };
  const updateParticles = (events, sim, dt) => {
    if (sim.seed !== generatedSeed) { particles = []; generatedSeed = sim.seed; }
    for (const event of events) {
      if (event.type === 'stroke_committed' || event.type === 'page_solved') {
        const origin = event.type === 'page_solved' ? sim.goal : sim.bead;
        const random = seedRandom(sim.seed ^ event.tick ^ 0x91a3);
        const burst = event.type === 'page_solved' ? 20 : 12;
        for (let i = 0; i < burst && particles.length < 24; i += 1) {
          const angle = random() * Math.PI * 2; const speed = 16 + random() * 42;
          particles.push({ x: origin.x, y: origin.y, vx: Math.cos(angle) * speed, vy: Math.sin(angle) * speed, age: 0, life: .5 + random() * .6, radius: 1 + random() * 2.2, color: i % 3 ? C.rust : C.gold });
        }
      }
    }
    for (const particle of particles) { particle.age += dt; particle.x += particle.vx * dt; particle.y += particle.vy * dt; particle.vx *= .985; particle.vy *= .985; }
    particles = particles.filter((particle) => particle.age < particle.life).slice(0, 24);
    sim.diagnostics.maxParticles = Math.max(sim.diagnostics.maxParticles, particles.length);
  };
  const drawParticles = () => {
    for (const particle of particles) { ctx.globalAlpha = 1 - particle.age / particle.life; ctx.fillStyle = particle.color; ctx.beginPath(); ctx.arc(particle.x, particle.y, particle.radius, 0, Math.PI * 2); ctx.fill(); }
    ctx.globalAlpha = 1;
  };
  const drawGuides = (sim) => {
    ctx.save(); ctx.strokeStyle = 'rgba(24,42,53,.38)'; ctx.lineWidth = 1.5; ctx.setLineDash([5, 7]);
    if (!sim.rail.length && !sim.draft.length) { ctx.beginPath(); ctx.moveTo(sim.actor.x + 48, sim.actor.y - 18); ctx.quadraticCurveTo(455, 404, sim.bead.x - 15, sim.bead.y - 18); ctx.stroke(); }
    ctx.setLineDash([]);
    if (sim.rail.length) {
      const a = sim.rail[0]; const b = sim.rail.at(-1);
      for (const point of [a, b]) { ctx.fillStyle = C.light; ctx.strokeStyle = C.rust; ctx.lineWidth = 3; ctx.beginPath(); ctx.arc(point.x, point.y, 7, 0, Math.PI * 2); ctx.fill(); ctx.stroke(); }
      ctx.fillStyle = C.ink; ctx.font = '12px Courier New, monospace'; ctx.fillText('YOUR RAIL', a.x + 11, a.y - 12);
    }
    ctx.restore();
  };
  const drawTitle = (sim) => {
    if (sim.state !== 'TITLE') return;
    ctx.save(); ctx.fillStyle = 'rgba(241,231,207,.77)'; ctx.fillRect(0, 0, PAGE.width, PAGE.height);
    ctx.fillStyle = C.ink; ctx.textAlign = 'center'; ctx.font = 'italic 30px Georgia, serif'; ctx.fillText('A line is a kind of weather.', PAGE.width / 2, 307);
    ctx.font = '16px Georgia, serif'; ctx.fillStyle = '#4a5c57'; ctx.fillText('Draw one continuous rail. The gold bead follows; the ink-being rides.', PAGE.width / 2, 344);
    ctx.font = '13px Courier New, monospace'; ctx.fillStyle = C.rust; ctx.fillText('CHOOSE “USE GUIDED LINE” FOR KEYBOARD PLAY', PAGE.width / 2, 385);
    ctx.restore();
  };
  function render(sim, events = [], dt = 0) {
    const startedAt = performance.now();
    updateParticles(events, sim, dt);
    ctx.save(); ctx.setTransform(canvas.width / PAGE.width, 0, 0, canvas.height / PAGE.height, 0, 0);
    drawPaper(sim.seed, sim.time, sim.reducedMotion);
    drawGuides(sim);
    if (sim.rail.length) {
      line(sim.rail, 'rgba(217,108,77,.14)', 22);
      line(sim.rail, C.rust, 9);
      line(sim.rail, C.ink, 2.1, .68);
    }
    if (sim.draft.length) {
      line(sim.draft, 'rgba(217,108,77,.17)', 19);
      line(sim.draft, C.rust, 7);
      line(sim.draft, C.light, 1.5, .62);
    }
    drawGoal(sim.goal, sim.state === 'SOLVED', sim.time, sim.reducedMotion);
    if (sim.bead.attached || sim.state !== 'TITLE') drawBead(sim.bead, sim.time, sim.reducedMotion);
    if (!sim.reducedMotion) drawParticles();
    drawCreature(sim.actor, sim.reducedMotion, sim.time);
    drawTitle(sim);
    if (sim.state === 'TITLE') {
      ctx.fillStyle = C.ink; ctx.font = '11px Courier New, monospace'; ctx.textAlign = 'center'; ctx.fillText('PRESS START BELOW OR DRAW TO BEGIN', PAGE.width / 2, 646);
    }
    ctx.restore();
    renderSamples.push(performance.now() - startedAt);
    if (renderSamples.length > 240) renderSamples.shift();
  }
  const getDiagnostics = () => {
    const ordered = [...renderSamples].sort((a, b) => a - b);
    const percentile = (p) => ordered.length ? ordered[Math.min(ordered.length - 1, Math.ceil(ordered.length * p) - 1)] : 0;
    return { sampledFrames: ordered.length, renderCpuMsMedian: percentile(.5), renderCpuMsP95: percentile(.95), maxParticles: particles.length, backingWidth: canvas.width, backingHeight: canvas.height };
  };
  const resize = (host) => {
    const rect = host.getBoundingClientRect();
    const dpr = Math.min(2, window.devicePixelRatio || 1);
    const width = Math.max(1, Math.round(rect.width * dpr));
    const height = Math.max(1, Math.round(rect.height * dpr));
    if (canvas.width !== width || canvas.height !== height) { canvas.width = width; canvas.height = height; }
  };
  const observe = (host) => { resize(host); resizeObserver = new ResizeObserver(() => resize(host)); resizeObserver.observe(host); };
  const dispose = () => resizeObserver?.disconnect();
  return { render, resize, observe, dispose, getDiagnostics };
}
