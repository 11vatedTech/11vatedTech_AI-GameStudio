export const PAGE = Object.freeze({ width: 1280, height: 720 });
export const STROKE_LIMITS = Object.freeze({ minPoints: 2, maxPoints: 72, minLength: 640, maxLength: 1480 });
export const DRAW_BOUNDS = Object.freeze({ left: 72, right: 1208, top: 94, bottom: 626 });

export function distance(a, b) {
  return Math.hypot(b.x - a.x, b.y - a.y);
}

export function polylineLength(points) {
  let total = 0;
  for (let i = 1; i < points.length; i += 1) total += distance(points[i - 1], points[i]);
  return total;
}

export function closestPointOnPolyline(point, points) {
  if (!points.length) return null;
  if (points.length === 1) return { ...points[0], distance: distance(point, points[0]), arcDistance: 0, segment: 0, t: 0 };
  let best = null;
  let walked = 0;
  for (let i = 1; i < points.length; i += 1) {
    const a = points[i - 1];
    const b = points[i];
    const dx = b.x - a.x;
    const dy = b.y - a.y;
    const squared = dx * dx + dy * dy;
    const t = squared === 0 ? 0 : Math.max(0, Math.min(1, ((point.x - a.x) * dx + (point.y - a.y) * dy) / squared));
    const x = a.x + dx * t;
    const y = a.y + dy * t;
    const d = Math.hypot(point.x - x, point.y - y);
    const segmentLength = Math.sqrt(squared);
    if (!best || d < best.distance) best = { x, y, distance: d, arcDistance: walked + segmentLength * t, segment: i - 1, t };
    walked += segmentLength;
  }
  return best;
}

// Deterministic distance-based resampling prevents device/reporting-rate changes from
// changing puzzle geometry. The max-point fallback preserves endpoints and shape order.
export function sanitizeStroke(rawPoints, limits = STROKE_LIMITS) {
  if (!Array.isArray(rawPoints)) return [];
  const cleaned = [];
  for (const candidate of rawPoints) {
    if (!candidate || !Number.isFinite(candidate.x) || !Number.isFinite(candidate.y)) continue;
    const point = {
      x: Math.max(DRAW_BOUNDS.left, Math.min(DRAW_BOUNDS.right, candidate.x)),
      y: Math.max(DRAW_BOUNDS.top, Math.min(DRAW_BOUNDS.bottom, candidate.y)),
    };
    if (!cleaned.length || distance(cleaned.at(-1), point) >= 3) cleaned.push(point);
  }
  if (cleaned.length < limits.minPoints) return cleaned;
  const total = polylineLength(cleaned);
  if (cleaned.length <= limits.maxPoints) return cleaned;
  const interval = total / (limits.maxPoints - 1);
  const sampled = [cleaned[0]];
  let carry = 0;
  let previous = cleaned[0];
  for (let i = 1; i < cleaned.length - 1; i += 1) {
    const current = cleaned[i];
    const segment = distance(previous, current);
    carry += segment;
    if (carry >= interval) {
      sampled.push(current);
      carry = 0;
    }
    previous = current;
  }
  sampled.push(cleaned.at(-1));
  if (sampled.length <= limits.maxPoints) return sampled;
  const reduced = [];
  for (let i = 0; i < limits.maxPoints; i += 1) {
    reduced.push(sampled[Math.round(i * (sampled.length - 1) / (limits.maxPoints - 1))]);
  }
  return reduced;
}

export function pointAtDistance(points, targetDistance) {
  if (!points.length) return null;
  let remaining = Math.max(0, targetDistance);
  for (let i = 1; i < points.length; i += 1) {
    const a = points[i - 1];
    const b = points[i];
    const length = distance(a, b);
    if (remaining <= length || i === points.length - 1) {
      const t = length === 0 ? 0 : Math.min(1, remaining / length);
      return { x: a.x + (b.x - a.x) * t, y: a.y + (b.y - a.y) * t, angle: Math.atan2(b.y - a.y, b.x - a.x), segment: i - 1, t };
    }
    remaining -= length;
  }
  return { ...points.at(-1), angle: 0, segment: points.length - 2, t: 1 };
}
