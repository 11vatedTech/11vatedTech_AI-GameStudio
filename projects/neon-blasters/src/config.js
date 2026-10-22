export const CONFIG = Object.freeze({
  width: 1280, height: 720, fixedStep: 1 / 60, maxCatchupSteps: 5,
  fireInterval: 0.115, beamLifetime: 0.075, comboWindow: 1.45, comboMax: 99,
  overloadLimit: 15, overloadGrace: 3.2, targetCap: 40, particleCap: 1400,
  maxChainDepth: 4, maxSplitBranches: 3, maxSplitPerEvent: 1,
  spawnBaseInterval: 1.25, spawnMinInterval: 0.34, powerupDuration: 9,
  overdriveThreshold: 100, overdriveDamage: 5, maxEventsPerStep: 240,
  colors: Object.freeze([
    { id: 'cyan', label: 'CYAN', color: '#31d8ff', icon: '◇', pattern: 'DIAMOND' },
    { id: 'magenta', label: 'MAGENTA', color: '#f34fea', icon: '✳', pattern: 'BURST' },
    { id: 'amber', label: 'AMBER', color: '#ffb547', icon: '△', pattern: 'TRIANGLE' }
  ]),
  families: Object.freeze(['block', 'crystal', 'power', 'volatile']),
  powerups: Object.freeze(['multishot', 'piercing', 'explosive', 'time-dilation', 'supernova']),
  upgrades: Object.freeze(['rapid-fire', 'prism-charge', 'reinforced-beam', 'cool-headed'])
});
