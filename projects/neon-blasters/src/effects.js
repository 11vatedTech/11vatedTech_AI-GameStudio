export class EffectSystem {
  constructor(simulation, { reducedEffects = () => false } = {}) { this.simulation=simulation; this.reducedEffects=reducedEffects; this.lastEvents=[]; this.dropped=0; }
  consume(events) {
    const cap=this.reducedEffects()?220:720; this.lastEvents=events;
    for(const event of events){
      if(!['hit','fracture','destroyed','split','volatile_burst','overdrive','overload_warning','chain_advanced','powerup_collected'].includes(event.type))continue;
      const target=this.simulation.sim.targets.find(t=>t.id===event.targetId);
    }
    if(this.simulation.sim.particles.length>cap){this.dropped+=this.simulation.sim.particles.length-cap;this.simulation.sim.particles.length=cap;}
  }
}
