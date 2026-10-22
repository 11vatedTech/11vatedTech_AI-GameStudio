const TAU = Math.PI * 2;
const clamp01 = (value) => Math.max(0, Math.min(1, value));
const smooth = (value) => { const x = clamp01(value); return x * x * (3 - 2 * x); };

export function poseAt(state, time, reducedMotion = false) {
  if (reducedMotion) return { squash: 1, stretch: 1, tilt: state === 'traverse' ? 0.12 : 0, bob: 0, blink: 1, tail: 0.08, anticipation: 0.0 };
  const phase = time * TAU;
  if (state === 'anticipate') {
    const windup = Math.sin(phase * 1.9);
    return { squash: 1 - 0.11 * Math.max(0, windup), stretch: 1 + 0.06 * Math.max(0, -windup), tilt: -0.08, bob: 0, blink: 1, tail: 0.32 + windup * 0.18, anticipation: 1 };
  }
  if (state === 'traverse') return { squash: 1 + Math.sin(phase * 2) * 0.06, stretch: 1 - Math.sin(phase * 2) * 0.035, tilt: 0.12 + Math.sin(phase) * 0.05, bob: Math.sin(phase * 2) * 2, blink: 1, tail: Math.sin(phase - 0.8) * 0.22, anticipation: 0 };
  if (state === 'recover') {
    const settle = 1 - smooth((time % 0.48) / 0.48);
    return { squash: 1 - settle * 0.16, stretch: 1 + settle * 0.12, tilt: -0.13 * settle, bob: 1.5 * settle, blink: 1, tail: 0.34 * settle, anticipation: 0 };
  }
  if (state === 'solved') return { squash: 1 + Math.sin(phase) * 0.025, stretch: 1, tilt: -0.08, bob: reducedMotion ? 0 : Math.sin(phase) * 1.5, blink: 1, tail: 0.1, anticipation: 0 };
  const blinkPhase = (time + 0.73) % 3.6;
  const blink = blinkPhase > 3.44 && blinkPhase < 3.53 ? 0.12 : 1;
  return { squash: 1 + Math.sin(phase) * 0.025, stretch: 1 - Math.sin(phase) * 0.018, tilt: Math.sin(phase * 0.5) * 0.035, bob: Math.sin(phase) * 2.2, blink, tail: Math.sin(phase * 0.72 - 0.5) * 0.16, anticipation: 0 };
}

export function lerpPose(previous, current, alpha = 1) {
  const t = clamp01(alpha);
  return Object.fromEntries(Object.keys(current).map((key) => [key, (previous?.[key] ?? current[key]) + (current[key] - (previous?.[key] ?? current[key])) * t]));
}
