import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Draggy", page_icon="🏎️", layout="wide")
st.markdown("""
<style>
  .main .block-container{padding-top:.4rem;padding-bottom:0;max-width:100%}
  footer,header,#MainMenu{display:none}
</style>
""", unsafe_allow_html=True)

GAME_HTML = r"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:#080808;color:#fff;font-family:'Courier New',monospace;
  display:flex;flex-direction:column;align-items:center;overflow:hidden;
  user-select:none;padding:6px}
#wrap{width:920px;max-width:100%}
#hdr{text-align:center;margin-bottom:4px}
#hdr h1{font-size:1.7em;color:#ff4500;text-shadow:0 0 20px #ff4500,0 0 40px #ff2200;letter-spacing:6px}
#hint{text-align:center;color:#555;font-size:.7em;margin-bottom:6px;letter-spacing:1px}
kbd{background:#1e1e1e;border:1px solid #444;border-radius:3px;padding:1px 6px;color:#ccc;font-size:.9em;font-family:'Courier New',monospace}
#cbox{position:relative;border-radius:8px;overflow:hidden;border:1px solid #1a1a1a;margin-bottom:5px}
canvas{display:block}
#overlay{position:absolute;inset:0;background:rgba(0,0,0,.82);display:flex;
  flex-direction:column;align-items:center;justify-content:center;gap:8px;border-radius:8px;z-index:20}
#overlay h2{font-size:1.9em;color:#ff4500;text-shadow:0 0 20px #ff4500;letter-spacing:4px}
#overlay p{color:#888;font-size:.8em;margin:1px 0}
.sbtn{margin-top:12px;padding:11px 28px;background:#ff4500;color:#fff;border:none;border-radius:6px;
  font-size:1.1em;font-family:'Courier New',monospace;cursor:pointer;letter-spacing:3px;transition:all .15s}
.sbtn:hover{background:#ff6600;box-shadow:0 0 22px #ff4500;transform:scale(1.03)}
#sbar{display:flex;justify-content:space-around;background:#0f0f0f;border:1px solid #1a1a1a;
  border-radius:6px;padding:6px 12px;font-size:.72em;color:#444}
#sbar span{color:#999}
</style>
</head>
<body>
<div id="wrap">
  <div id="hdr"><h1>⚡ DRAGGY ⚡</h1></div>
  <div id="hint">
    Hold <kbd>SPACE</kbd> = gas &nbsp;·&nbsp;
    Press <kbd>F</kbd> or <kbd>SHIFT</kbd> = gear up &nbsp;·&nbsp;
    Shift in the <span style="color:#00ff44">GREEN</span> zone for max power
  </div>
  <div id="cbox">
    <canvas id="gc" width="920" height="570"></canvas>
    <div id="overlay">
      <h2>⚡ DRAGGY ⚡</h2>
      <p>1 kilometre drag race · reach 500 mph</p>
      <p style="margin-top:4px">Hold <kbd>SPACE</kbd> to build revs · Press <kbd>F</kbd> or <kbd>SHIFT</kbd> to change gear</p>
      <p>Hit the <span style="color:#00ff44">GREEN</span> shift light at the right moment for a PERFECT shift!</p>
      <button class="sbtn" onclick="beginRace()">START ENGINE</button>
    </div>
  </div>
  <div id="sbar">
    <div>BEST &nbsp;<span id="sb-best">--.---s</span></div>
    <div>DISTANCE &nbsp;<span id="sb-dist">0 / 1000m</span></div>
    <div>SPEED &nbsp;<span id="sb-spd">0 mph</span></div>
    <div>SHIFTS &nbsp;<span id="sb-sh">0</span></div>
    <div>PERFECT &nbsp;<span id="sb-pf">0</span></div>
  </div>
</div>
<script>
// ── Canvas / layout constants ──────────────────────────────────────────────
const CW=920, CH=570;
const VH=382;          // POV view height (road+sky)
const DY=VH;           // dashboard starts here
const DH=CH-VH;        // dashboard height = 188
const HZ=150;          // horizon Y
const FOCAL=VH-HZ;     // perspective focal = 232
// world units: 1 WU = 5 m  →  1000 m race = 200 WU
const ROAD_HW=0.72;    // road half-width WU  (~3.6 m)
const PPU=CW*0.45/ROAD_HW; // pixels per WU at z=1  ≈ 575
const NEAR_Z=1.0;      // nearest z (maps to y=VH)
const FAR_Z=200;       // draw distance WU (1000 m)
const RACE_WU=200;     // 1000 m in WU

function pY(wz){return HZ+FOCAL/wz}
function pX(wx,wz){return CW/2+wx*PPU/wz}

// ── Physics constants ──────────────────────────────────────────────────────
const MAX_RPM=8500, IDLE_RPM=950, REDLINE=8200;
const SHIFT_G_LO=6200, SHIFT_G_HI=7100, SHIFT_Y_HI=7900;
// 6-speed ratios
const GR=[3.36,2.10,1.46,1.09,0.83,0.65];
const FD=3.73;
// SF tuned: at REDLINE in 6th → ~534 mph
const SF=0.158;
const RPM_RISE=9000;   // rpm/s at full throttle, gear 1
const RPM_FALL=5200;

function torqueFn(r){
  const t=r/MAX_RPM;
  if(t<0.12)return .3+t*4;
  if(t<0.55)return .78+(t-.12)*.5;
  if(t<0.72)return 1;
  if(t<0.92)return 1-(t-.72)*1.8;
  return .64-(t-.92)*4;
}

// ── State ──────────────────────────────────────────────────────────────────
let gs='idle';
let rpm=IDLE_RPM,gear=1,speed=0,pos=0,camZ=0;
let gasDown=false,shiftDown=false;
let throttle=0,shiftPenalty=0;
let raceT0=0,elapsed=0;
let shiftCount=0,perfectCount=0,bestTime=null;
let sqText='',sqColor='',sqTimer=0;
// opponent
let oPos=0,oSpeed=0,oRpm=IDLE_RPM,oGear=1;
let oppDone=false,oppTime=null;
let lastTS=null;

// ── Pre-baked assets ───────────────────────────────────────────────────────
const stars=Array.from({length:90},()=>[Math.random()*CW, Math.random()*(HZ-10)]);
// crowd silhouette control points
const crowd=(()=>{let a=[];for(let x=0;x<=CW;x+=6)a.push([x,HZ-4-Math.abs(Math.sin(x*.09)*6+Math.sin(x*.05)*5)]);return a})();
// light poles: world Z positions (WU) and side
const POLE_WZS=[8,18,30,45,62,82,105,132,165];
const POLE_H=5.5; // WU  (27.5 m tall)

// ── Christmas tree ─────────────────────────────────────────────────────────
let treeState=[0,0,0,0,0]; // 0=off,1=yellow,2=green

// ── Input ──────────────────────────────────────────────────────────────────
document.addEventListener('keydown',e=>{
  if(e.code==='Space'){e.preventDefault();if(!gasDown&&gs==='racing')gasDown=true;}
  if((e.code==='KeyF'||e.code==='ShiftLeft'||e.code==='ShiftRight')&&!shiftDown){
    e.preventDefault();shiftDown=true;doShift();
  }
});
document.addEventListener('keyup',e=>{
  if(e.code==='Space'){e.preventDefault();gasDown=false;}
  if(e.code==='KeyF'||e.code==='ShiftLeft'||e.code==='ShiftRight')shiftDown=false;
});
document.addEventListener('click',()=>document.body.focus());
document.body.tabIndex=0;

// ── Shift ──────────────────────────────────────────────────────────────────
function doShift(){
  if(gear>=6||gs!=='racing')return;
  shiftCount++;
  let quality,penalty,color;
  if(rpm>=SHIFT_G_LO&&rpm<SHIFT_G_HI){quality='✦ PERFECT!';penalty=0.04;color='#00ff44';perfectCount++;}
  else if(rpm>=SHIFT_G_HI&&rpm<SHIFT_Y_HI){quality='✓ GOOD';penalty=0.14;color='#ffcc00';}
  else if(rpm>=SHIFT_Y_HI){quality='⚠ OVER-REV!';penalty=0.55;color='#ff2200';}
  else if(rpm>=3500){quality='↓ EARLY';penalty=0.40;color='#ff8800';}
  else{quality='↓ TOO EARLY';penalty=0.65;color='#ff4400';}
  rpm*=GR[gear]/GR[gear-1];
  gear++;
  speed=(rpm/(GR[gear-1]*FD))*SF;
  shiftPenalty=penalty;sqText=quality;sqColor=color;sqTimer=1.5;
}

// ── Opponent AI ────────────────────────────────────────────────────────────
function tickOpp(dt){
  if(gs!=='racing'||oppDone)return;
  const gr=GR[oGear-1];
  oRpm+=(RPM_RISE/gr)*torqueFn(oRpm)*dt;
  if(oRpm>=6800+Math.random()*300&&oGear<6){oRpm*=GR[oGear]/GR[oGear-1];oGear++;}
  oRpm=Math.max(IDLE_RPM,Math.min(oRpm,REDLINE));
  oSpeed=(oRpm/(GR[oGear-1]*FD))*SF;
  oPos+=oSpeed*0.44704*dt;
  if(oPos>=1000){oppDone=true;oppTime=(performance.now()-raceT0)/1000;oPos=1000;}
}

// ── Game start ─────────────────────────────────────────────────────────────
function beginRace(){
  document.getElementById('overlay').style.display='none';
  gs='countdown';
  rpm=IDLE_RPM;gear=1;speed=0;pos=0;camZ=0;
  throttle=0;gasDown=false;shiftPenalty=0;
  shiftCount=0;perfectCount=0;elapsed=0;sqTimer=0;sqText='';
  oPos=0;oSpeed=0;oRpm=IDLE_RPM;oGear=1;oppDone=false;oppTime=null;
  treeState=[0,0,0,0,0];
  // Christmas tree sequence
  [0,700,1300,1900,2500].forEach((d,i)=>setTimeout(()=>{
    treeState[i]=i<4?1:2;
    if(i===4){gs='racing';raceT0=performance.now();}
  },d));
  lastTS=null;
  requestAnimationFrame(frame);
}

function finishRace(){
  gs='finished';
  const ft=elapsed;
  if(bestTime===null||ft<bestTime)bestTime=ft;
  const won=!oppDone||ft<=oppTime;
  const oppStr=oppDone?oppTime.toFixed(3)+'s':'DNF';
  const ov=document.getElementById('overlay');
  ov.innerHTML=`
    <h2 style="color:${won?'#00ff88':'#ff4500'}">${won?'🏆 YOU WIN!':'💨 CPU WINS!'}</h2>
    <div style="font-size:2.5em;font-weight:bold;color:#00ff88;text-shadow:0 0 15px #00ff88">${ft.toFixed(3)}s</div>
    <div style="color:#555;font-size:.75em;letter-spacing:3px">1 KILOMETRE ET</div>
    ${bestTime===ft?'<div style="color:#ffcc00;font-size:.85em">⭐ NEW BEST!</div>':''}
    <div style="color:#555;font-size:.75em;margin-top:4px">CPU: ${oppStr} &nbsp;|&nbsp; Shifts: ${shiftCount} &nbsp;|&nbsp; Perfect: ${perfectCount}</div>
    <button class="sbtn" onclick="beginRace()">RACE AGAIN</button>`;
  ov.style.display='flex';
}

// ── Main loop ──────────────────────────────────────────────────────────────
function frame(ts){
  if(!lastTS)lastTS=ts;
  const dt=Math.min((ts-lastTS)/1000,.05);
  lastTS=ts;

  if(gs==='racing'){
    elapsed=(ts-raceT0)/1000;
    throttle=gasDown?1:0;
    const gr=GR[gear-1];
    if(gasDown) rpm+=(RPM_RISE/gr)*torqueFn(rpm)*(1-shiftPenalty)*dt;
    else        rpm-=RPM_FALL*dt;
    rpm=Math.max(IDLE_RPM,Math.min(rpm,REDLINE+400));
    speed=(rpm/(gr*FD))*SF;
    pos+=speed*0.44704*dt;
    camZ=pos/5;
    shiftPenalty=Math.max(0,shiftPenalty-dt*2.8);
    if(sqTimer>0){sqTimer-=dt;if(sqTimer<=0)sqText='';}
    tickOpp(dt);
    if(pos>=1000){pos=1000;camZ=200;finishRace();return;}
    oPos=Math.min(oPos,1000);
  }

  draw();
  requestAnimationFrame(frame);
}

// ── Drawing ────────────────────────────────────────────────────────────────
const canvas=document.getElementById('gc');
const ctx=canvas.getContext('2d');

function draw(){
  ctx.clearRect(0,0,CW,CH);
  drawSky();
  drawRoad();
  drawCenterDashes();
  drawRumbleStrips();
  drawEdgeLines();
  drawPoles();
  drawOppCar();
  drawSpeedFX();
  drawInterior();
  drawDash();
  drawHUD();
  updateStatBar();
}

// ── Sky ────────────────────────────────────────────────────────────────────
function drawSky(){
  const g=ctx.createLinearGradient(0,0,0,HZ);
  g.addColorStop(0,'#03030d');
  g.addColorStop(.7,'#07101a');
  g.addColorStop(1,'#0e1c28');
  ctx.fillStyle=g;ctx.fillRect(0,0,CW,HZ);
  // stars
  ctx.fillStyle='rgba(255,255,255,.55)';
  stars.forEach(([x,y])=>ctx.fillRect(x,y,1,1));
  // crowd silhouette
  ctx.fillStyle='#08080f';
  ctx.beginPath();ctx.moveTo(0,HZ);
  crowd.forEach(([x,y])=>ctx.lineTo(x,y));
  ctx.lineTo(CW,0);ctx.lineTo(0,0);ctx.closePath();ctx.fill();
  // distant track glow above horizon
  const gl=ctx.createLinearGradient(0,HZ-18,0,HZ);
  gl.addColorStop(0,'transparent');
  gl.addColorStop(1,'rgba(255,160,50,.08)');
  ctx.fillStyle=gl;ctx.fillRect(0,HZ-18,CW,18);
}

// ── Road surface with depth stripes ───────────────────────────────────────
function drawRoad(){
  // base trapezoid
  ctx.fillStyle='#1f1f1f';
  ctx.beginPath();
  ctx.moveTo(pX(-ROAD_HW,FAR_Z),pY(FAR_Z));
  ctx.lineTo(pX( ROAD_HW,FAR_Z),pY(FAR_Z));
  ctx.lineTo(pX( ROAD_HW,NEAR_Z),VH);
  ctx.lineTo(pX(-ROAD_HW,NEAR_Z),VH);
  ctx.closePath();ctx.fill();

  // alternating depth strips
  const SP=4.0, HSP=2.0; // stripe period WU
  let k=Math.ceil(camZ/HSP);
  while(true){
    const pz0=k*HSP-camZ, pz1=(k+1)*HSP-camZ;
    if(pz0>=FAR_Z)break;
    if(pz1>0&&k%2===0){
      const a=Math.max(NEAR_Z,pz0), b=Math.min(FAR_Z,pz1);
      const y1=Math.max(HZ,pY(b)), y2=Math.min(VH,pY(a));
      if(y2>y1){
        ctx.fillStyle='#252525';
        ctx.beginPath();
        ctx.moveTo(pX(-ROAD_HW,b),y1);ctx.lineTo(pX(ROAD_HW,b),y1);
        ctx.lineTo(pX(ROAD_HW,a),y2);ctx.lineTo(pX(-ROAD_HW,a),y2);
        ctx.closePath();ctx.fill();
      }
    }
    k++;
  }
}

// ── Center dashes ──────────────────────────────────────────────────────────
function drawCenterDashes(){
  const DP=2.5,DL=1.1;
  let dk=Math.floor(camZ/DP);
  while(true){
    const w0=dk*DP, pz0=w0-camZ, pz1=pz0+DL;
    if(pz0>=FAR_Z)break;
    if(pz1>0){
      const a=Math.max(NEAR_Z,pz0), b=Math.min(FAR_Z,pz1);
      const sy1=Math.max(HZ+1,pY(b)), sy2=Math.min(VH,pY(a));
      if(sy2>sy1){
        ctx.strokeStyle='rgba(210,210,210,.8)';
        ctx.lineWidth=Math.max(1,Math.min(4,3/a));
        ctx.beginPath();ctx.moveTo(CW/2,sy1);ctx.lineTo(CW/2,sy2);ctx.stroke();
      }
    }
    dk++;
  }
}

// ── Rumble strips ──────────────────────────────────────────────────────────
function drawRumbleStrips(){
  const RP=0.6,RH=RP/2;
  const sides=[-ROAD_HW,ROAD_HW];
  const colors=['#cc2200','#dddddd'];
  for(const wx of sides){
    let k=Math.floor(camZ/RH);
    while(true){
      const pz0=k*RH-camZ, pz1=pz0+RH;
      if(pz0>=FAR_Z)break;
      if(pz1>0){
        const a=Math.max(NEAR_Z,pz0), b=Math.min(FAR_Z,pz1);
        const y1=Math.max(HZ,pY(b)), y2=Math.min(VH,pY(a));
        if(y2>y1){
          const col=k%2===0?colors[0]:colors[1];
          const stripW=Math.max(1,Math.min(10,6/a));
          const sx=pX(wx,a);
          ctx.strokeStyle=col;ctx.lineWidth=stripW;
          ctx.beginPath();ctx.moveTo(sx,y1);ctx.lineTo(sx,y2);ctx.stroke();
        }
      }
      k++;
    }
  }
}

// ── Road edge lines ────────────────────────────────────────────────────────
function drawEdgeLines(){
  ctx.strokeStyle='rgba(220,220,220,.7)';ctx.lineWidth=2;
  for(const wx of[-ROAD_HW,ROAD_HW]){
    ctx.beginPath();
    ctx.moveTo(pX(wx,FAR_Z),pY(FAR_Z));
    ctx.lineTo(pX(wx,NEAR_Z),VH);
    ctx.stroke();
  }
}

// ── Light poles ────────────────────────────────────────────────────────────
function drawPoles(){
  POLE_WZS.forEach(wz=>{
    const projZ=wz-camZ;
    if(projZ<=NEAR_Z||projZ>=FAR_Z)return;
    const roadY=pY(projZ);
    const poleScreenH=POLE_H/projZ*FOCAL;
    const topY=roadY-poleScreenH;
    const pw=Math.max(1,2.5/projZ);

    for(const side of[-1,1]){
      const sx=pX(side*(ROAD_HW+0.18),projZ);
      // pole
      ctx.strokeStyle='#2a2a2a';ctx.lineWidth=pw*1.5;
      ctx.beginPath();ctx.moveTo(sx,roadY);ctx.lineTo(sx,topY);ctx.stroke();
      // arm to center
      ctx.lineWidth=pw;
      ctx.beginPath();ctx.moveTo(sx,topY);ctx.lineTo(CW/2,topY+poleScreenH*.12);ctx.stroke();
      // light globe
      const gr=projZ<30?5*pw:2*pw;
      const glow=ctx.createRadialGradient(sx,topY,0,sx,topY,gr*3);
      glow.addColorStop(0,'rgba(255,240,180,.9)');
      glow.addColorStop(.3,'rgba(255,200,80,.4)');
      glow.addColorStop(1,'transparent');
      ctx.fillStyle=glow;
      ctx.beginPath();ctx.arc(sx,topY,gr*3,0,Math.PI*2);ctx.fill();
      ctx.fillStyle='#ffffcc';
      ctx.beginPath();ctx.arc(sx,topY,gr,0,Math.PI*2);ctx.fill();
    }
  });
}

// ── Opponent car (POV) ─────────────────────────────────────────────────────
function drawOppCar(){
  if(gs!=='racing'&&gs!=='finished')return;
  const relM=oPos-pos; // metres ahead (+) or behind (-)
  if(relM<2)return;
  const projZ=relM/5+2;
  if(projZ<NEAR_Z||projZ>FAR_Z)return;

  const roadY=pY(projZ);
  const HW=0.32, CTOP=0.38; // world half-width, top height
  const x0=pX(-HW,projZ),x1=pX(HW,projZ);
  const cw=x1-x0;
  const ch=CTOP/projZ*FOCAL;
  const ty=roadY-ch;

  // body
  ctx.fillStyle='#0044bb';
  ctx.fillRect(x0,ty+ch*.3,cw,ch*.7);
  // roof
  ctx.fillStyle='#002277';
  ctx.fillRect(x0+cw*.15,ty,cw*.7,ch*.5);
  // windshield
  ctx.fillStyle='rgba(120,200,255,.5)';
  ctx.fillRect(x0+cw*.18,ty+ch*.05,cw*.64,ch*.35);
  // brake lights
  ctx.fillStyle='#ff2200';
  ctx.fillRect(x0,ty+ch*.35,cw*.12,ch*.25);
  ctx.fillRect(x1-cw*.12,ty+ch*.35,cw*.12,ch*.25);
  // label
  if(cw>18){
    ctx.fillStyle='#0066ff';ctx.font=`bold ${Math.max(9,cw*.35)}px Courier New`;
    ctx.textAlign='center';
    ctx.fillText('CPU',CW/2,ty-3);
  }
}

// ── Speed FX ───────────────────────────────────────────────────────────────
function drawSpeedFX(){
  if(speed<100)return;
  const t=Math.min(1,(speed-100)/400); // 0 at 100mph, 1 at 500mph

  // radial speed lines from vanishing point
  const n=Math.floor(30*t);
  ctx.save();
  ctx.globalAlpha=.18*t;
  ctx.strokeStyle='#ffffff';
  ctx.lineWidth=1;
  for(let i=0;i<n;i++){
    const ang=(i/n)*Math.PI*2;
    const r0=60+Math.random()*80, r1=r0+40+Math.random()*140;
    ctx.beginPath();
    ctx.moveTo(CW/2+Math.cos(ang)*r0, HZ+Math.sin(ang)*r0*.6);
    ctx.lineTo(CW/2+Math.cos(ang)*r1, HZ+Math.sin(ang)*r1*.6);
    ctx.stroke();
  }
  ctx.restore();

  // blue tunnel vignette at extreme speed
  if(speed>280){
    const v=Math.min(.75,(speed-280)/220);
    const vig=ctx.createRadialGradient(CW/2,VH/2,VH*.18,CW/2,VH/2,VH*.95);
    vig.addColorStop(0,'transparent');
    vig.addColorStop(1,`rgba(0,20,80,${v})`);
    ctx.fillStyle=vig;ctx.fillRect(0,0,CW,VH);
  }

  // chromatic aberration hint at 400+
  if(speed>400){
    const ca=(speed-400)/100*.04;
    ctx.save();ctx.globalAlpha=ca;
    ctx.fillStyle='#ff0000';ctx.fillRect(0,0,8,VH);
    ctx.fillStyle='#0000ff';ctx.fillRect(CW-8,0,8,VH);
    ctx.restore();
  }
}

// ── Car interior ───────────────────────────────────────────────────────────
function drawInterior(){
  // dashboard cowl blending POV into dash
  const cg=ctx.createLinearGradient(0,VH-55,0,VH);
  cg.addColorStop(0,'transparent');
  cg.addColorStop(.5,'rgba(6,6,6,.7)');
  cg.addColorStop(1,'rgba(4,4,4,1)');
  ctx.fillStyle=cg;
  ctx.beginPath();ctx.ellipse(CW/2,VH+8,310,70,0,0,Math.PI*2);ctx.fill();

  // A-pillars
  ctx.strokeStyle='#1a1a1a';ctx.lineWidth=18;
  ctx.beginPath();ctx.moveTo(CW/2-310,VH+8);ctx.lineTo(50,HZ-10);ctx.stroke();
  ctx.beginPath();ctx.moveTo(CW/2+310,VH+8);ctx.lineTo(CW-50,HZ-10);ctx.stroke();
}

// ── Dashboard ──────────────────────────────────────────────────────────────
function drawDash(){
  // panel bg
  ctx.fillStyle='#0a0a0a';ctx.fillRect(0,DY,CW,DH);
  ctx.strokeStyle='#181818';ctx.lineWidth=1;
  ctx.beginPath();ctx.moveTo(0,DY);ctx.lineTo(CW,DY);ctx.stroke();

  // RPM gauge
  drawRpmGauge(175,DY+100,88);

  // Speed + Gear center
  const cx=CW/2;
  ctx.textAlign='center';
  // big speed
  const spd=Math.round(speed);
  const speedColor=speed>400?'#ff4400':speed>250?'#ffcc00':'#00ff88';
  ctx.fillStyle=speedColor;
  ctx.font=`bold 56px Courier New`;
  ctx.shadowColor=speedColor;ctx.shadowBlur=speed>200?20:8;
  ctx.fillText(spd,cx,DY+76);
  ctx.shadowBlur=0;
  ctx.fillStyle='#333';ctx.font='11px Courier New';
  ctx.fillText('MPH',cx,DY+94);

  // gear box
  const gx=cx+95, gy=DY+50;
  ctx.fillStyle='#111';
  roundRect(ctx,gx-24,gy-2,48,52,6);ctx.fill();
  ctx.strokeStyle='#2a2a2a';ctx.lineWidth=1;
  roundRect(ctx,gx-24,gy-2,48,52,6);ctx.stroke();
  ctx.fillStyle='#fff';ctx.font=`bold 34px Courier New`;ctx.textAlign='center';
  ctx.fillText(gs==='idle'?'N':gear,gx,gy+38);
  ctx.fillStyle='#333';ctx.font='9px Courier New';
  ctx.fillText('GEAR',gx,DY+115);

  // Shift light
  drawShiftLight(680,DY+90);

  // Throttle bar
  drawThrottleBar(810,DY+20,20,130);

  // Christmas tree
  drawTree(870,DY+10);

  // Steering wheel
  drawSteeringWheel(cx,DY+162,42);
}

function roundRect(ctx,x,y,w,h,r){
  ctx.beginPath();
  ctx.moveTo(x+r,y);
  ctx.arcTo(x+w,y,x+w,y+h,r);
  ctx.arcTo(x+w,y+h,x,y+h,r);
  ctx.arcTo(x,y+h,x,y,r);
  ctx.arcTo(x,y,x+w,y,r);
  ctx.closePath();
}

function drawRpmGauge(cx,cy,r){
  const SA=Math.PI*.75, EA=Math.PI*2.25, SWEEP=Math.PI*1.5;
  const rpmA=a=>SA+(Math.min(a,MAX_RPM)/MAX_RPM)*SWEEP;

  // zones bg
  [
    [0,SHIFT_G_LO,'#001830'],
    [SHIFT_G_LO,SHIFT_G_HI,'#003300'],
    [SHIFT_G_HI,SHIFT_Y_HI,'#332200'],
    [SHIFT_Y_HI,MAX_RPM,'#2a0000']
  ].forEach(([lo,hi,col])=>{
    ctx.beginPath();ctx.arc(cx,cy,r,rpmA(lo),rpmA(hi));
    ctx.strokeStyle=col;ctx.lineWidth=16;ctx.stroke();
  });

  // active fill
  if(rpm>IDLE_RPM+200){
    const col=rpm>=SHIFT_Y_HI?'#ff2200':rpm>=SHIFT_G_HI?'#ffcc00':rpm>=SHIFT_G_LO?'#00ff44':'#0088ff';
    ctx.beginPath();ctx.arc(cx,cy,r,SA,rpmA(rpm));
    ctx.strokeStyle=col;ctx.lineWidth=11;ctx.stroke();
  }
  // needle
  const na=rpmA(rpm);
  ctx.strokeStyle='#fff';ctx.lineWidth=2;
  ctx.beginPath();ctx.moveTo(cx,cy);
  ctx.lineTo(cx+(r-14)*Math.cos(na),cy+(r-14)*Math.sin(na));ctx.stroke();
  ctx.fillStyle='#666';ctx.beginPath();ctx.arc(cx,cy,5,0,Math.PI*2);ctx.fill();
  // labels
  ctx.fillStyle='#444';ctx.font='8px Courier New';ctx.textAlign='center';
  ctx.fillText('0',cx+r*Math.cos(SA)*1.2,cy+r*Math.sin(SA)*1.2+4);
  ctx.fillText('8K',cx+r*Math.cos(EA)*1.2,cy+r*Math.sin(EA)*1.2+4);
  ctx.fillStyle='#666';ctx.font='9px Courier New';
  ctx.fillText(Math.round(rpm/100)*100,cx,cy+6);
  ctx.fillStyle='#333';ctx.font='8px Courier New';
  ctx.fillText('RPM',cx,cy+18);
}

function drawShiftLight(cx,cy){
  const col=rpm>=SHIFT_Y_HI?['#aa0000','#ff2200','#ff0000']:
            rpm>=SHIFT_G_HI?['#888800','#ffcc00','#ffdd00']:
            rpm>=SHIFT_G_LO?['#006600','#00ff44','#00ff44']:
            ['#1a1a1a','#222','#333'];
  const r=42;
  // outer ring
  ctx.beginPath();ctx.arc(cx,cy,r,0,Math.PI*2);
  ctx.fillStyle=col[0];ctx.fill();
  // inner glow
  const gr=ctx.createRadialGradient(cx-r*.2,cy-r*.2,2,cx,cy,r);
  gr.addColorStop(0,col[2]);gr.addColorStop(1,col[0]);
  ctx.fillStyle=gr;ctx.fill();
  // pulse glow when active
  if(rpm>=SHIFT_G_LO){
    ctx.beginPath();ctx.arc(cx,cy,r+6,0,Math.PI*2);
    ctx.strokeStyle=col[1]+'88';ctx.lineWidth=4;ctx.stroke();
  }
  // label
  ctx.fillStyle=rpm>=SHIFT_G_LO?'#000':'#444';
  ctx.font='bold 9px Courier New';ctx.textAlign='center';
  const lbl=rpm>=SHIFT_Y_HI?'OVER REV':rpm>=SHIFT_G_LO?'SHIFT NOW':'';
  ctx.fillText(lbl,cx,cy+3);
  ctx.fillStyle='#333';ctx.font='9px Courier New';
  ctx.fillText('SHIFT',cx,cy+r+14);
}

function drawThrottleBar(x,y,w,h){
  ctx.fillStyle='#111';
  roundRect(ctx,x,y,w,h,4);ctx.fill();
  ctx.strokeStyle='#1e1e1e';ctx.lineWidth=1;
  roundRect(ctx,x,y,w,h,4);ctx.stroke();
  const fh=h*throttle;
  if(fh>0){
    const fg=ctx.createLinearGradient(0,y+h,0,y+h-fh);
    fg.addColorStop(0,'#cc3300');fg.addColorStop(.5,'#ff5500');fg.addColorStop(1,'#ff9900');
    ctx.fillStyle=fg;
    ctx.fillRect(x+1,y+h-fh,w-2,fh);
  }
  ctx.fillStyle='#333';ctx.font='8px Courier New';ctx.textAlign='center';
  ctx.fillText('GAS',x+w/2,y-4);
}

function drawTree(x,y){
  const colors=[['#aa8800','#ffcc00'],['#888800','#ffee00'],['#888800','#ffee00'],['#888800','#ffee00'],['#006600','#00ff44']];
  const labels=['PRE','S1','S2','S3','GO'];
  ctx.fillStyle='#333';ctx.font='7px Courier New';ctx.textAlign='center';
  ctx.fillText('TREE',x,y-2);
  treeState.forEach((st,i)=>{
    const ly=y+8+i*24;
    const on=st>0;
    const col=on?colors[i][1]:colors[i][0]+'33';
    // pair of lights
    for(const ox of[-10,10]){
      ctx.beginPath();ctx.arc(x+ox,ly,8,0,Math.PI*2);
      ctx.fillStyle=on?col:'#111';ctx.fill();
      if(on){
        ctx.beginPath();ctx.arc(x+ox,ly,8,0,Math.PI*2);
        ctx.strokeStyle=col;ctx.lineWidth=2;ctx.stroke();
      }
    }
  });
}

function drawSteeringWheel(cx,cy,r){
  ctx.strokeStyle='#242424';ctx.lineWidth=7;
  ctx.beginPath();ctx.arc(cx,cy,r,0,Math.PI*2);ctx.stroke();
  ctx.lineWidth=5;
  // spokes
  [-.3,.3,Math.PI].forEach(a=>{
    ctx.beginPath();ctx.moveTo(cx,cy);
    ctx.lineTo(cx+r*Math.cos(a+Math.PI/2),cy+r*Math.sin(a+Math.PI/2));ctx.stroke();
  });
  ctx.fillStyle='#1a1a1a';ctx.beginPath();ctx.arc(cx,cy,8,0,Math.PI*2);ctx.fill();
}

// ── HUD overlays ───────────────────────────────────────────────────────────
function drawHUD(){
  ctx.textAlign='center';
  // timer
  if(gs==='racing'||gs==='finished'){
    ctx.fillStyle='rgba(255,255,255,.9)';ctx.font='bold 20px Courier New';
    ctx.fillText(elapsed.toFixed(2)+'s',CW/2,22);
  }
  // countdown overlay text
  if(gs==='countdown'){
    ctx.fillStyle='rgba(255,200,0,.9)';ctx.font='bold 16px Courier New';
    ctx.fillText('GET READY...',CW/2,VH/2);
  }
  // shift quality
  if(sqText&&sqTimer>0){
    ctx.globalAlpha=Math.min(1,sqTimer*2);
    ctx.fillStyle=sqColor;ctx.font=`bold 22px Courier New`;
    ctx.fillText(sqText,CW/2,HZ+55);
    ctx.globalAlpha=1;
  }
  // "SHIFT!" flash at bottom of POV
  if(rpm>=SHIFT_G_LO&&gs==='racing'){
    const pulse=.5+.5*Math.sin(performance.now()*.015);
    ctx.globalAlpha=.7*pulse;
    const col=rpm>=SHIFT_Y_HI?'#ff2200':rpm>=SHIFT_G_HI?'#ffcc00':'#00ff44';
    ctx.fillStyle=col;ctx.font='bold 14px Courier New';
    ctx.fillText(rpm>=SHIFT_Y_HI?'OVER REV!':'SHIFT NOW!',CW/2,VH-12);
    ctx.globalAlpha=1;
  }
  // progress bar (thin line at top of road)
  if(gs==='racing'||gs==='finished'){
    const t=pos/1000;
    ctx.fillStyle='#333';ctx.fillRect(0,VH-3,CW,3);
    ctx.fillStyle=speed>400?'#ff4400':speed>200?'#ffcc00':'#00ff88';
    ctx.fillRect(0,VH-3,CW*t,3);
    // opponent marker
    const ot=oPos/1000;
    ctx.fillStyle='#0066ff';
    ctx.fillRect(CW*ot-2,VH-5,4,5);
  }
}

function updateStatBar(){
  document.getElementById('sb-dist').textContent=Math.round(pos)+' / 1000m';
  document.getElementById('sb-spd').textContent=Math.round(speed)+' mph';
  document.getElementById('sb-sh').textContent=shiftCount;
  document.getElementById('sb-pf').textContent=perfectCount;
  if(bestTime)document.getElementById('sb-best').textContent=bestTime.toFixed(3)+'s';
}

// ── Boot ───────────────────────────────────────────────────────────────────
(function idle(){
  if(gs==='idle'){draw();requestAnimationFrame(idle);}
})();
</script>
</body></html>"""

components.html(GAME_HTML, height=660, scrolling=False)
