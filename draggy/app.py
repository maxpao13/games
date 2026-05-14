import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Draggy", page_icon="🏎️", layout="wide")

st.markdown("""
<style>
  .main .block-container { padding-top: 0.5rem; padding-bottom: 0; max-width: 100%; }
  footer { display: none; }
  header { display: none; }
  #MainMenu { display: none; }
</style>
""", unsafe_allow_html=True)

GAME_HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  background: #0d0d0d;
  color: #fff;
  font-family: 'Courier New', monospace;
  display: flex;
  flex-direction: column;
  align-items: center;
  overflow: hidden;
  user-select: none;
  padding: 8px;
}
#game-container { width: 920px; max-width: 100%; }

#header { text-align: center; margin-bottom: 6px; }
#header h1 {
  font-size: 1.8em;
  color: #ff4500;
  text-shadow: 0 0 20px #ff4500, 0 0 40px #ff2200;
  letter-spacing: 6px;
}

#controls-hint {
  text-align: center;
  color: #666;
  font-size: 0.72em;
  margin-bottom: 8px;
  letter-spacing: 1px;
}
kbd {
  background: #2a2a2a;
  border: 1px solid #555;
  border-radius: 3px;
  padding: 1px 6px;
  color: #ddd;
  font-family: 'Courier New', monospace;
  font-size: 0.95em;
}

/* Dashboard row */
#dashboard {
  display: flex;
  gap: 8px;
  justify-content: center;
  align-items: stretch;
  margin-bottom: 8px;
}

.panel {
  background: #141414;
  border: 1px solid #2a2a2a;
  border-radius: 8px;
  padding: 10px;
}

/* RPM Gauge */
#gauge-panel {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 230px;
}
#gauge-label { color: #555; font-size: 0.65em; letter-spacing: 3px; margin-bottom: 2px; }

/* Speed panel */
#speed-panel {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  min-width: 130px;
}
#speed-num {
  font-size: 3.2em;
  font-weight: bold;
  color: #00ff88;
  text-shadow: 0 0 12px #00ff88;
  line-height: 1;
  min-width: 80px;
  text-align: center;
}
#speed-unit { color: #444; font-size: 0.7em; letter-spacing: 2px; }
.divider { height: 1px; background: #222; width: 100%; margin: 2px 0; }
#gear-label-txt { color: #444; font-size: 0.65em; letter-spacing: 3px; }
#gear-num {
  font-size: 2.8em;
  font-weight: bold;
  color: #fff;
  background: #1f1f1f;
  border: 2px solid #333;
  border-radius: 6px;
  width: 58px;
  height: 58px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Shift panel */
#shift-panel {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  min-width: 130px;
}
#shift-label { color: #444; font-size: 0.65em; letter-spacing: 2px; text-align: center; }
#shift-light {
  width: 78px;
  height: 78px;
  border-radius: 50%;
  background: #1a1a1a;
  border: 3px solid #2a2a2a;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.62em;
  font-weight: bold;
  text-align: center;
  line-height: 1.3;
  transition: background 0.08s, box-shadow 0.08s, border-color 0.08s;
}
#shift-light.sl-green {
  background: radial-gradient(circle at 38% 38%, #88ff88, #00bb00);
  border-color: #00ff00;
  box-shadow: 0 0 18px #00ff00, 0 0 36px #009900;
  color: #002200;
}
#shift-light.sl-yellow {
  background: radial-gradient(circle at 38% 38%, #ffff88, #ccaa00);
  border-color: #ffdd00;
  box-shadow: 0 0 18px #ffdd00, 0 0 36px #aa8800;
  color: #221100;
}
#shift-light.sl-red {
  background: radial-gradient(circle at 38% 38%, #ff8888, #cc0000);
  border-color: #ff0000;
  box-shadow: 0 0 18px #ff0000, 0 0 36px #880000;
  color: #fff;
  animation: blink 0.18s ease-in-out infinite alternate;
}
@keyframes blink {
  from { box-shadow: 0 0 18px #ff0000; }
  to   { box-shadow: 0 0 40px #ff0000, 0 0 60px #cc0000; }
}
#shift-quality {
  font-size: 0.9em;
  font-weight: bold;
  height: 20px;
  text-align: center;
  min-width: 100px;
}

/* Throttle bar */
#throttle-panel {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  min-width: 70px;
  justify-content: center;
}
#throttle-label { color: #444; font-size: 0.65em; letter-spacing: 2px; }
#throttle-bg {
  width: 28px;
  height: 110px;
  background: #111;
  border: 1px solid #2a2a2a;
  border-radius: 4px;
  display: flex;
  flex-direction: column-reverse;
  overflow: hidden;
}
#throttle-fill {
  width: 100%;
  height: 0%;
  background: linear-gradient(to top, #ff4500, #ff8800);
  transition: height 0.04s;
  border-radius: 3px;
}
#throttle-key { color: #444; font-size: 0.65em; }

/* Christmas tree */
#tree-panel {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  justify-content: center;
  min-width: 80px;
}
#tree-title { color: #444; font-size: 0.6em; letter-spacing: 2px; text-align: center; }
.tree-row { display: flex; gap: 8px; }
.tl {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: #1a1a1a;
  border: 2px solid #2a2a2a;
  transition: all 0.1s;
}
.tl.y { background: radial-gradient(circle at 40% 40%, #ffee88, #bb8800); border-color: #ffcc00; box-shadow: 0 0 8px #ffcc00; }
.tl.g { background: radial-gradient(circle at 40% 40%, #88ff88, #00aa00); border-color: #00ff00; box-shadow: 0 0 10px #00ff00; }
.tl.r { background: radial-gradient(circle at 40% 40%, #ff8888, #aa0000); border-color: #ff0000; box-shadow: 0 0 10px #ff0000; }

/* Track */
#track-wrap {
  position: relative;
  margin-bottom: 8px;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #2a2a2a;
}
#track-canvas { display: block; width: 100%; }

/* Overlay */
#overlay {
  position: absolute;
  inset: 0;
  background: rgba(0,0,0,0.82);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  border-radius: 8px;
  z-index: 20;
}
#overlay h2 { font-size: 1.9em; color: #ff4500; text-shadow: 0 0 20px #ff4500; letter-spacing: 4px; }
#overlay p { color: #888; font-size: 0.82em; margin: 1px 0; }
.start-btn {
  margin-top: 12px;
  padding: 11px 28px;
  background: #ff4500;
  color: #fff;
  border: none;
  border-radius: 6px;
  font-size: 1.1em;
  font-family: 'Courier New', monospace;
  cursor: pointer;
  letter-spacing: 3px;
  transition: all 0.15s;
}
.start-btn:hover { background: #ff6600; box-shadow: 0 0 20px #ff4500; transform: scale(1.03); }
#result-time { font-size: 2.6em; color: #00ff88; font-weight: bold; text-shadow: 0 0 15px #00ff88; }
#result-label { color: #555; font-size: 0.75em; letter-spacing: 3px; }

/* Stats bar */
#stats-bar {
  display: flex;
  justify-content: space-around;
  background: #141414;
  border: 1px solid #2a2a2a;
  border-radius: 8px;
  padding: 7px 15px;
  font-size: 0.75em;
  color: #444;
}
#stats-bar span { color: #aaa; }
</style>
</head>
<body>
<div id="game-container">

  <div id="header"><h1>⚡ DRAGGY ⚡</h1></div>
  <div id="controls-hint">
    Hold <kbd>SPACE</kbd> = gas &nbsp;·&nbsp;
    Press <kbd>F</kbd> or <kbd>SHIFT</kbd> = gear up &nbsp;·&nbsp;
    Shift in the <span style="color:#00ff44">GREEN</span> zone for max power
  </div>

  <div id="dashboard">
    <!-- RPM Gauge -->
    <div class="panel" id="gauge-panel">
      <div id="gauge-label">R P M</div>
      <svg id="rpm-svg" width="220" height="128" viewBox="0 0 220 128">
        <path id="g-bg"     fill="none" stroke="#1e1e1e" stroke-width="20" stroke-linecap="round"/>
        <path id="g-zone-b" fill="none" stroke="#001833" stroke-width="20" stroke-linecap="butt"/>
        <path id="g-zone-g" fill="none" stroke="#003300" stroke-width="20" stroke-linecap="butt"/>
        <path id="g-zone-y" fill="none" stroke="#333300" stroke-width="20" stroke-linecap="butt"/>
        <path id="g-zone-r" fill="none" stroke="#330000" stroke-width="20" stroke-linecap="butt"/>
        <path id="g-fill"   fill="none" stroke="#00aaff" stroke-width="15" stroke-linecap="round"/>
        <circle cx="110" cy="118" r="5" fill="#888"/>
        <line id="g-needle" x1="110" y1="118" x2="110" y2="118" stroke="#fff" stroke-width="2" stroke-linecap="round"/>
        <text id="rpm-val" x="110" y="114" fill="#ccc" font-size="13" font-family="Courier New" text-anchor="middle" font-weight="bold">0</text>
        <text x="8"   y="125" fill="#333" font-size="8" font-family="Courier New">0</text>
        <text x="95"  y="16"  fill="#333" font-size="8" font-family="Courier New">×1000</text>
        <text x="196" y="125" fill="#333" font-size="8" font-family="Courier New">8K</text>
      </svg>
    </div>

    <!-- Speed -->
    <div class="panel" id="speed-panel">
      <div id="speed-num">0</div>
      <div id="speed-unit">MPH</div>
      <div class="divider"></div>
      <div id="gear-label-txt">GEAR</div>
      <div id="gear-num">N</div>
    </div>

    <!-- Shift indicator -->
    <div class="panel" id="shift-panel">
      <div id="shift-label">SHIFT<br>INDICATOR</div>
      <div id="shift-light"></div>
      <div id="shift-quality"></div>
    </div>

    <!-- Throttle -->
    <div class="panel" id="throttle-panel">
      <div id="throttle-label">GAS</div>
      <div id="throttle-bg"><div id="throttle-fill"></div></div>
      <div id="throttle-key">SPACE</div>
    </div>

    <!-- Christmas tree -->
    <div class="panel" id="tree-panel">
      <div id="tree-title">START<br>TREE</div>
      <div class="tree-row"><div class="tl" id="tl0a"></div><div class="tl" id="tl0b"></div></div>
      <div class="tree-row"><div class="tl" id="tl1a"></div><div class="tl" id="tl1b"></div></div>
      <div class="tree-row"><div class="tl" id="tl2a"></div><div class="tl" id="tl2b"></div></div>
      <div class="tree-row"><div class="tl" id="tl3a"></div><div class="tl" id="tl3b"></div></div>
      <div class="tree-row"><div class="tl" id="tl4a"></div><div class="tl" id="tl4b"></div></div>
    </div>
  </div>

  <!-- Track -->
  <div id="track-wrap">
    <canvas id="track-canvas" width="920" height="130"></canvas>
    <div id="overlay">
      <h2>⚡ DRAGGY ⚡</h2>
      <p>Quarter-mile drag race — beat the clock &amp; the CPU</p>
      <p style="margin-top:4px">Hold <kbd>SPACE</kbd> to build revs · Press <kbd>F</kbd> or <kbd>SHIFT</kbd> to change gear</p>
      <p>Hit the green shift light at the right moment for a <span style="color:#00ff44">PERFECT</span> shift!</p>
      <button class="start-btn" id="main-btn" onclick="beginRace()">START ENGINE</button>
    </div>
  </div>

  <!-- Stats -->
  <div id="stats-bar">
    <div>BEST &nbsp;<span id="s-best">--.---s</span></div>
    <div>DISTANCE &nbsp;<span id="s-dist">0 / 402m</span></div>
    <div>SHIFTS &nbsp;<span id="s-shifts">0</span></div>
    <div>PERFECT &nbsp;<span id="s-perfect">0</span></div>
    <div>CPU &nbsp;<span id="s-cpu">0m</span></div>
  </div>
</div>

<script>
// ── Constants ────────────────────────────────────────────────────────────────
const MAX_RPM      = 8000;
const IDLE_RPM     = 950;
const REDLINE      = 7700;
const SHIFT_G_LO   = 6200;   // green zone start
const SHIFT_G_HI   = 7100;   // green zone end / yellow start
const SHIFT_Y_HI   = 7700;   // yellow end / red start (= redline)
const RACE_DIST    = 402;    // metres (quarter mile)

// 6-speed gear ratios (typical performance car)
const GR = [3.36, 2.10, 1.46, 1.09, 0.83, 0.65];
const FD = 3.73;   // final drive
// speed_mph = rpm / (GR[g] * FD) * SF
const SF = 0.00228;

// RPM rise rate at full throttle in 1st gear (lower gears rise faster)
const RPM_RISE  = 4400;   // rpm/s in gear 1 at full torque
const RPM_FALL  = 3200;   // rpm/s when off throttle

// Torque curve — returns 0..1 multiplier
function torque(rpm) {
  const r = rpm / MAX_RPM;
  if (r < 0.12) return 0.3 + r * 4;
  if (r < 0.55) return 0.78 + (r - 0.12) * 0.5;
  if (r < 0.72) return 1.0;
  if (r < 0.92) return 1.0 - (r - 0.72) * 1.8;
  return 0.64 - (r - 0.92) * 4;
}

// Gauge geometry
const GCX = 110, GCY = 118, GRad = 88;
const GA_START = Math.PI, GA_END = 0; // 180° sweep left→right

function rpmAngle(r) { return GA_START + (Math.min(r, MAX_RPM) / MAX_RPM) * Math.PI; }

function arcD(cx, cy, r, a1, a2) {
  const sx = cx + r * Math.cos(a1), sy = cy + r * Math.sin(a1);
  const ex = cx + r * Math.cos(a2), ey = cy + r * Math.sin(a2);
  const lg = (a2 - a1) > Math.PI ? 1 : 0;
  return `M${sx} ${sy} A${r} ${r} 0 ${lg} 1 ${ex} ${ey}`;
}

function initGauge() {
  document.getElementById('g-bg').setAttribute('d', arcD(GCX,GCY,GRad, GA_START, GA_END));
  // Colour zone backgrounds
  document.getElementById('g-zone-b').setAttribute('d', arcD(GCX,GCY,GRad, GA_START, rpmAngle(SHIFT_G_LO)));
  document.getElementById('g-zone-g').setAttribute('d', arcD(GCX,GCY,GRad, rpmAngle(SHIFT_G_LO), rpmAngle(SHIFT_G_HI)));
  document.getElementById('g-zone-y').setAttribute('d', arcD(GCX,GCY,GRad, rpmAngle(SHIFT_G_HI), rpmAngle(SHIFT_Y_HI)));
  document.getElementById('g-zone-r').setAttribute('d', arcD(GCX,GCY,GRad, rpmAngle(SHIFT_Y_HI), GA_END));
}

function updateGauge(rpm) {
  const angle = rpmAngle(rpm);
  const fill  = document.getElementById('g-fill');
  if (rpm > IDLE_RPM + 150) {
    fill.setAttribute('d', arcD(GCX,GCY,GRad, GA_START, angle));
    if      (rpm >= SHIFT_Y_HI) fill.setAttribute('stroke','#ff2200');
    else if (rpm >= SHIFT_G_HI) fill.setAttribute('stroke','#ffcc00');
    else if (rpm >= SHIFT_G_LO) fill.setAttribute('stroke','#00ff44');
    else                        fill.setAttribute('stroke','#00aaff');
  } else {
    fill.setAttribute('d','');
  }
  const needle = document.getElementById('g-needle');
  const nx = GCX + (GRad - 18) * Math.cos(angle);
  const ny = GCY + (GRad - 18) * Math.sin(angle);
  needle.setAttribute('x1', GCX); needle.setAttribute('y1', GCY);
  needle.setAttribute('x2', nx);  needle.setAttribute('y2', ny);
  document.getElementById('rpm-val').textContent = Math.round(rpm / 100) * 100;
}

// ── Game state ───────────────────────────────────────────────────────────────
let gs = 'idle';   // idle | countdown | racing | finished
let rpm    = IDLE_RPM, gear = 1, speed = 0, pos = 0;
let gasDown = false, shiftDown = false;
let throttle = 0, shiftPenalty = 0;
let raceT0 = 0, elapsed = 0;
let shiftCount = 0, perfectCount = 0;
let bestTime = null;
let sqText = '', sqColor = '', sqTimer = 0;

// Opponent
let oPos = 0, oSpeed = 0, oRpm = IDLE_RPM, oGear = 1;
let oppFinished = false, oppTime = null;

let lastTS = null;

// ── Tree lights ──────────────────────────────────────────────────────────────
function setTree(row, cls) {
  document.getElementById('tl'+row+'a').className = 'tl ' + cls;
  document.getElementById('tl'+row+'b').className = 'tl ' + cls;
}
function resetTree() {
  for (let i = 0; i < 5; i++) setTree(i, '');
}

// ── Race start ───────────────────────────────────────────────────────────────
function beginRace() {
  document.getElementById('overlay').style.display = 'none';
  gs = 'countdown';
  rpm = IDLE_RPM; gear = 1; speed = 0; pos = 0;
  throttle = 0; gasDown = false; shiftPenalty = 0;
  shiftCount = 0; perfectCount = 0; elapsed = 0;
  sqTimer = 0; sqText = '';
  oPos = 0; oSpeed = 0; oRpm = IDLE_RPM; oGear = 1;
  oppFinished = false; oppTime = null;
  resetTree();

  // Christmas tree: row 0 = pre-stage (yellow), 1-3 = stage lights (yellow), 4 = GO (green)
  const delays = [0, 700, 1300, 1900, 2500];
  const classes = ['y','y','y','y','g'];
  delays.forEach((d, i) => {
    setTimeout(() => {
      setTree(i, classes[i]);
      if (i === 4) {
        gs = 'racing';
        raceT0 = performance.now();
      }
    }, d);
  });

  lastTS = null;
  requestAnimationFrame(loop);
}

// ── Shift logic ──────────────────────────────────────────────────────────────
function doShift() {
  if (gear >= 6 || gs !== 'racing') return;
  shiftCount++;

  let quality, penalty, color;
  if      (rpm >= SHIFT_G_LO && rpm < SHIFT_G_HI) { quality = '✦ PERFECT!';   penalty = 0.04; color = '#00ff44'; perfectCount++; }
  else if (rpm >= SHIFT_G_HI && rpm < SHIFT_Y_HI) { quality = '✓ GOOD';       penalty = 0.14; color = '#ffcc00'; }
  else if (rpm >= SHIFT_Y_HI)                     { quality = '⚠ OVER-REV!';  penalty = 0.52; color = '#ff2200'; }
  else if (rpm >= 3500)                            { quality = '↓ EARLY';      penalty = 0.38; color = '#ff8800'; }
  else                                             { quality = '↓ TOO EARLY';  penalty = 0.65; color = '#ff4400'; }

  rpm = rpm * (GR[gear] / GR[gear - 1]);   // RPM drop to match wheel speed
  gear++;
  speed = (rpm / (GR[gear-1] * FD)) * SF;

  shiftPenalty = penalty;
  sqText = quality; sqColor = color; sqTimer = 1.6;
}

// ── Opponent AI ──────────────────────────────────────────────────────────────
function tickOpp(dt) {
  if (gs !== 'racing' || oppFinished) return;
  const gRatio = GR[oGear - 1];
  oRpm += (RPM_RISE / gRatio) * torque(oRpm) * dt;
  // Shift between 6700-7000 with small random spread
  if (oRpm >= 6700 + Math.random() * 300 && oGear < 6) {
    oRpm = oRpm * (GR[oGear] / GR[oGear - 1]);
    oGear++;
  }
  oRpm = Math.max(IDLE_RPM, Math.min(oRpm, REDLINE));
  oSpeed = (oRpm / (GR[oGear-1] * FD)) * SF;
  oPos += oSpeed * 0.44704 * dt;
  if (oPos >= RACE_DIST && !oppFinished) {
    oppFinished = true;
    oppTime = (performance.now() - raceT0) / 1000;
    oPos = RACE_DIST;
  }
}

// ── Main loop ────────────────────────────────────────────────────────────────
function loop(ts) {
  if (!lastTS) lastTS = ts;
  const dt = Math.min((ts - lastTS) / 1000, 0.05);
  lastTS = ts;

  if (gs === 'racing') {
    elapsed = (ts - raceT0) / 1000;

    throttle = gasDown ? 1.0 : 0.0;
    const gRatio = GR[gear - 1];

    if (gasDown) {
      rpm += (RPM_RISE / gRatio) * torque(rpm) * (1 - shiftPenalty) * dt;
    } else {
      rpm -= RPM_FALL * dt;
    }
    rpm = Math.max(IDLE_RPM, Math.min(rpm, REDLINE + 300));

    speed = (rpm / (gRatio * FD)) * SF;
    pos  += speed * 0.44704 * dt;
    shiftPenalty = Math.max(0, shiftPenalty - dt * 2.8);

    if (sqTimer > 0) { sqTimer -= dt; if (sqTimer <= 0) sqText = ''; }

    tickOpp(dt);

    if (pos >= RACE_DIST) { pos = RACE_DIST; finishRace(); return; }
    if (!oppFinished && oPos >= RACE_DIST) oPos = RACE_DIST;
  }

  render();
  requestAnimationFrame(loop);
}

function finishRace() {
  gs = 'finished';
  const ft = elapsed;
  if (bestTime === null || ft < bestTime) bestTime = ft;
  const won = !oppFinished || ft <= oppTime;
  const oppStr = oppFinished ? oppTime.toFixed(3) + 's' : 'DNF';

  document.getElementById('overlay').innerHTML = `
    <h2 style="color:${won?'#00ff88':'#ff4500'}">${won?'🏆 YOU WIN!':'💨 CPU WINS!'}</h2>
    <div id="result-time">${ft.toFixed(3)}s</div>
    <div id="result-label">QUARTER MILE ET</div>
    ${bestTime === ft ? '<div style="color:#ffcc00;font-size:0.85em">⭐ NEW BEST TIME!</div>' : ''}
    <div style="color:#555;font-size:0.75em;margin-top:4px">CPU: ${oppStr} &nbsp;|&nbsp; Shifts: ${shiftCount} &nbsp;|&nbsp; Perfect: ${perfectCount}</div>
    <button class="start-btn" onclick="beginRace()">RACE AGAIN</button>
  `;
  document.getElementById('overlay').style.display = 'flex';

  document.getElementById('s-best').textContent = bestTime.toFixed(3) + 's';
}

// ── Render ───────────────────────────────────────────────────────────────────
function render() {
  updateGauge(rpm);
  document.getElementById('speed-num').textContent = Math.round(speed);
  document.getElementById('gear-num').textContent  = gs === 'idle' ? 'N' : gear;
  document.getElementById('throttle-fill').style.height = (throttle * 100) + '%';

  // Shift light
  const sl = document.getElementById('shift-light');
  sl.className = '';
  sl.innerHTML = '';
  if (rpm >= SHIFT_Y_HI)    { sl.className = 'sl-red';    sl.innerHTML = 'OVER<br>REV!'; }
  else if (rpm >= SHIFT_G_HI) { sl.className = 'sl-yellow'; sl.innerHTML = 'SHIFT<br>NOW!'; }
  else if (rpm >= SHIFT_G_LO) { sl.className = 'sl-green';  sl.innerHTML = 'SHIFT<br>NOW!'; }

  // Shift quality
  const sq = document.getElementById('shift-quality');
  if (sqText) { sq.textContent = sqText; sq.style.color = sqColor; sq.style.opacity = Math.min(1, sqTimer * 2); }
  else sq.textContent = '';

  // Stats
  document.getElementById('s-dist').textContent    = Math.round(pos) + ' / 402m';
  document.getElementById('s-shifts').textContent  = shiftCount;
  document.getElementById('s-perfect').textContent = perfectCount;
  document.getElementById('s-cpu').textContent     = Math.round(oPos) + 'm';

  drawTrack();
}

// ── Track canvas ─────────────────────────────────────────────────────────────
const canvas = document.getElementById('track-canvas');
const ctx    = canvas.getContext('2d');

function rrect(ctx, x, y, w, h, r) {
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.lineTo(x + w - r, y); ctx.arcTo(x+w, y,     x+w, y+r,   r);
  ctx.lineTo(x + w, y + h - r); ctx.arcTo(x+w, y+h, x+w-r, y+h, r);
  ctx.lineTo(x + r, y + h); ctx.arcTo(x, y+h, x, y+h-r,   r);
  ctx.lineTo(x, y + r); ctx.arcTo(x, y, x+r, y,           r);
  ctx.closePath();
}

function drawCheckers(x, y, w, h, rows) {
  const rh = h / rows;
  for (let i = 0; i < rows; i++) {
    ctx.fillStyle = (i % 2 === 0) ? '#fff' : '#000';
    ctx.fillRect(x,       y + i*rh, w/2, rh);
    ctx.fillStyle = (i % 2 === 0) ? '#000' : '#fff';
    ctx.fillRect(x + w/2, y + i*rh, w/2, rh);
  }
}

function drawCar(x, y, bodyColor, isPlayer) {
  const cw = 44, ch = 20;
  ctx.save();
  ctx.translate(x, y);

  // Shadow
  ctx.fillStyle = 'rgba(0,0,0,0.4)';
  rrect(ctx, -cw/2 + 2, ch/2 - 2, cw, 6, 3);
  ctx.fill();

  // Body
  const bg = ctx.createLinearGradient(0, -ch/2, 0, ch/2);
  bg.addColorStop(0, lighten(bodyColor, 50));
  bg.addColorStop(1, bodyColor);
  ctx.fillStyle = bg;
  rrect(ctx, -cw/2, -ch/2, cw, ch, 5);
  ctx.fill();

  // Roof
  ctx.fillStyle = '#111';
  rrect(ctx, -cw/4, -ch/2 - 9, cw/2, 10, 3);
  ctx.fill();

  // Windshield
  ctx.fillStyle = 'rgba(136,204,255,0.55)';
  rrect(ctx, -cw/4 + 2, -ch/2 - 7, cw/2 - 4, 7, 2);
  ctx.fill();

  // Wheels
  [[-cw/2 + 8, ch/2 - 1], [cw/2 - 8, ch/2 - 1]].forEach(([wx, wy]) => {
    ctx.fillStyle = '#111'; ctx.beginPath(); ctx.arc(wx, wy, 6, 0, Math.PI*2); ctx.fill();
    ctx.fillStyle = '#555'; ctx.beginPath(); ctx.arc(wx, wy, 3, 0, Math.PI*2); ctx.fill();
  });

  // Headlight
  ctx.fillStyle = '#ffffaa';
  ctx.fillRect(cw/2 - 4, -ch/4, 4, 8);

  // Exhaust flame
  if (isPlayer && gasDown && rpm > 2500) {
    const fl = Math.random() * 18 + 6;
    const fg = ctx.createLinearGradient(-cw/2, 0, -cw/2 - fl, 0);
    fg.addColorStop(0,   '#ff8800');
    fg.addColorStop(0.5, '#ff3300');
    fg.addColorStop(1,   'transparent');
    ctx.fillStyle = fg;
    ctx.beginPath();
    ctx.moveTo(-cw/2, -4);
    ctx.lineTo(-cw/2 - fl, 0);
    ctx.lineTo(-cw/2, 4);
    ctx.fill();
  }

  ctx.restore();
}

function lighten(hex, amt) {
  const r = parseInt(hex.slice(1,3),16), g = parseInt(hex.slice(3,5),16), b = parseInt(hex.slice(5,7),16);
  return `rgb(${Math.min(255,r+amt)},${Math.min(255,g+amt)},${Math.min(255,b+amt)})`;
}

function drawTrack() {
  const W = canvas.width, H = canvas.height;
  ctx.clearRect(0, 0, W, H);

  // Sky/ground
  ctx.fillStyle = '#0d0d0d'; ctx.fillRect(0, 0, W, H);

  const ty1 = Math.round(H * 0.12), ty2 = Math.round(H * 0.88), th = ty2 - ty1;

  // Asphalt
  const ag = ctx.createLinearGradient(0, ty1, 0, ty2);
  ag.addColorStop(0,   '#2a2a2a');
  ag.addColorStop(0.5, '#323232');
  ag.addColorStop(1,   '#2a2a2a');
  ctx.fillStyle = ag;
  ctx.fillRect(0, ty1, W, th);

  // Lane divider dashes
  ctx.setLineDash([18, 14]);
  ctx.strokeStyle = '#3a3a3a'; ctx.lineWidth = 1;
  ctx.beginPath(); ctx.moveTo(0, H/2); ctx.lineTo(W, H/2); ctx.stroke();
  ctx.setLineDash([]);

  // Track borders
  ctx.strokeStyle = '#555'; ctx.lineWidth = 2;
  ctx.beginPath(); ctx.moveTo(0, ty1); ctx.lineTo(W, ty1); ctx.stroke();
  ctx.beginPath(); ctx.moveTo(0, ty2); ctx.lineTo(W, ty2); ctx.stroke();

  // Start line
  ctx.strokeStyle = '#777'; ctx.lineWidth = 3;
  ctx.beginPath(); ctx.moveTo(44, ty1); ctx.lineTo(44, ty2); ctx.stroke();

  // Finish (checkerboard)
  drawCheckers(W - 44, ty1, 20, th, 8);

  // Distance markers
  [100, 200, 300].forEach(m => {
    const mx = 44 + (m / RACE_DIST) * (W - 88);
    ctx.strokeStyle = '#2a2a2a'; ctx.lineWidth = 1; ctx.setLineDash([4,4]);
    ctx.beginPath(); ctx.moveTo(mx, ty1); ctx.lineTo(mx, ty2); ctx.stroke();
    ctx.setLineDash([]);
    ctx.fillStyle = '#333'; ctx.font = '8px Courier New'; ctx.textAlign = 'center';
    ctx.fillText(m + 'm', mx, ty1 - 2);
  });

  // Cars
  const trackLen = W - 88;
  const carX  = 44 + (pos  / RACE_DIST) * trackLen;
  const oppX  = 44 + (oPos / RACE_DIST) * trackLen;

  // Upper lane = player, lower lane = CPU
  const playerY = ty1 + th * 0.27;
  const cpuY    = ty1 + th * 0.73;

  drawCar(carX, playerY, '#ff4500', true);
  drawCar(oppX, cpuY,    '#0066ff', false);

  // Labels
  ctx.textAlign = 'center';
  ctx.fillStyle = '#ff4500'; ctx.font = 'bold 9px Courier New';
  ctx.fillText('YOU', carX, playerY - 23);
  ctx.fillStyle = '#0066ff';
  ctx.fillText('CPU', oppX, cpuY + 30);

  // Timer
  if (gs === 'racing' || gs === 'finished') {
    ctx.fillStyle = '#fff'; ctx.font = 'bold 22px Courier New'; ctx.textAlign = 'center';
    ctx.fillText(elapsed.toFixed(2) + 's', W / 2, 22);
  }
}

// ── Keyboard ─────────────────────────────────────────────────────────────────
document.addEventListener('keydown', e => {
  if (e.code === 'Space') {
    e.preventDefault();
    if (!gasDown && gs === 'racing') gasDown = true;
  }
  if ((e.code === 'KeyF' || e.code === 'ShiftLeft' || e.code === 'ShiftRight') && !shiftDown) {
    e.preventDefault();
    shiftDown = true;
    doShift();
  }
});
document.addEventListener('keyup', e => {
  if (e.code === 'Space')   { e.preventDefault(); gasDown = false; }
  if (e.code === 'KeyF' || e.code === 'ShiftLeft' || e.code === 'ShiftRight') shiftDown = false;
});

// Click inside iframe to grab keyboard focus
document.addEventListener('click', () => document.body.focus());
document.body.setAttribute('tabindex', '0');

// ── Boot ─────────────────────────────────────────────────────────────────────
initGauge();
drawTrack();
// Idle render loop on menu
(function idleLoop() {
  if (gs === 'idle') { drawTrack(); requestAnimationFrame(idleLoop); }
})();
</script>
</body>
</html>
"""

components.html(GAME_HTML, height=620, scrolling=False)
