export class InputAdapter {
  constructor(canvas, simulation, renderer, onState = () => {}){this.canvas=canvas;this.game=simulation;this.renderer=renderer;this.onState=onState;this.firing=false;this.pointerId=null;this.handlers=[];this.bind();}
  listen(target,type,fn,options){target.addEventListener(type,fn,options);this.handlers.push(()=>target.removeEventListener(type,fn,options));}
  aim(event){const r=this.canvas.getBoundingClientRect(),scale=this.renderer.scale,ox=this.renderer.offsetX,oy=this.renderer.offsetY;this.game.command('aim',{x:(event.clientX-r.left-ox)/scale,y:(event.clientY-r.top-oy)/scale});}
  startFire(event){if(event.button!==0||this.game.sim.state!=='RUNNING')return;event.preventDefault();this.canvas.focus({preventScroll:true});this.pointerId=event.pointerId;try{this.canvas.setPointerCapture(event.pointerId);}catch{}this.aim(event);this.game.command('fire-down');this.firing=true;this.onState();}
  stopFire(event){if(!this.firing)return;if(event&&this.pointerId!==null&&event.pointerId!==this.pointerId)return;this.game.command('fire-up');if(this.pointerId!==null&&this.canvas.hasPointerCapture?.(this.pointerId)){try{this.canvas.releasePointerCapture(this.pointerId);}catch{}}this.pointerId=null;this.firing=false;this.onState();}
  bind(){this.listen(this.canvas,'pointermove',e=>this.aim(e));this.listen(this.canvas,'pointerdown',e=>this.startFire(e));this.listen(this.canvas,'pointerup',e=>this.stopFire(e));this.listen(this.canvas,'pointercancel',e=>this.stopFire(e));this.listen(this.canvas,'lostpointercapture',()=>this.stopFire());
    this.listen(window,'blur',()=>{this.stopFire();if(this.game.sim.state==='RUNNING')this.game.command('pause');});
    this.listen(document,'visibilitychange',()=>{if(document.hidden){this.stopFire();if(this.game.sim.state==='RUNNING')this.game.command('pause');}});
    this.listen(this.canvas,'contextmenu',e=>{e.preventDefault();if(!['TITLE','RUN_OVER'].includes(this.game.sim.state)){this.game.command('spectrum');this.onState();}});
    this.listen(window,'keydown',e=>{if(['Space','ArrowUp','ArrowDown'].includes(e.code))e.preventDefault();if(e.repeat&&['KeyQ','Space','Escape','KeyP'].includes(e.code))return;if(e.code==='KeyQ'){if(!['TITLE','RUN_OVER'].includes(this.game.sim.state)){this.game.command('spectrum');this.onState();}}else if(e.code==='Space'){this.game.command('overdrive');this.onState();}else if(e.code==='Escape'||e.code==='KeyP'){this.game.command('pause');this.onState();}else if(e.code==='Enter'&&['TITLE','RUN_OVER'].includes(this.game.sim.state)){this.game.command('start');this.onState();}});
  }
  destroy(){this.stopFire();for(const off of this.handlers)off();this.handlers.length=0;}
}
