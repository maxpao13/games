import streamlit as st
import streamlit.components.v1 as components
import random
import time

st.set_page_config(page_title="Traffic Dodger", page_icon="🚗", layout="centered")

# ── Constants ──────────────────────────────────────────────────────────────────
LANES      = 5
ROWS       = 11
PLAYER_ROW = ROWS - 1
BASE_TICK  = 0.45
MIN_TICK   = 0.15
ENEMY_CARS = ["🚕", "🚙", "🏎️", "🚌", "🚛"]

# ── Session state ──────────────────────────────────────────────────────────────
def _init():
    st.session_state.setdefault("state",     "idle")   # idle | running | game_over
    st.session_state.setdefault("lane",      LANES // 2)
    st.session_state.setdefault("enemies",   [])
    st.session_state.setdefault("score",     0)
    st.session_state.setdefault("high",      0)
    st.session_state.setdefault("level",     1)
    st.session_state.setdefault("last_tick", 0.0)
    st.session_state.setdefault("spawn_cnt", 0)
    st.session_state.setdefault("music",     True)

def _reset():
    st.session_state.state     = "running"
    st.session_state.lane      = LANES // 2
    st.session_state.enemies   = []
    st.session_state.score     = 0
    st.session_state.level     = 1
    st.session_state.last_tick = time.time()
    st.session_state.spawn_cnt = 0

_init()

# ── Game logic ─────────────────────────────────────────────────────────────────
def _tick_speed():
    return max(MIN_TICK, BASE_TICK - (st.session_state.level - 1) * 0.04)

def _do_tick():
    s = st.session_state
    s.enemies = [[l, r + 1] for l, r in s.enemies if r + 1 < ROWS]

    s.spawn_cnt += 1
    spawn_every  = max(2, 5 - s.level)
    if s.spawn_cnt >= spawn_every:
        s.enemies.append([random.randint(0, LANES - 1), 0])
        s.spawn_cnt = 0

    for l, r in s.enemies:
        if r == PLAYER_ROW and l == s.lane:
            s.state = "game_over"
            if s.score > s.high:
                s.high = s.score
            return

    s.score    += 1
    s.level     = 1 + s.score // 25
    s.last_tick = time.time()

# ── Rendering ──────────────────────────────────────────────────────────────────
def _render_road():
    s       = st.session_state
    CW, CH  = 68, 48

    grid = [[""] * LANES for _ in range(ROWS)]
    for i, (l, r) in enumerate(s.enemies):
        if 0 <= r < ROWS:
            grid[r][l] = ENEMY_CARS[i % len(ENEMY_CARS)]
    grid[PLAYER_ROW][s.lane] = "🚗"

    rows_html = ""
    for ri in range(ROWS):
        cells = ""
        for li in range(LANES):
            border = "border-right:2px dashed rgba(255,255,255,0.18);" if li < LANES - 1 else ""
            cells += (
                f'<div style="width:{CW}px;height:{CH}px;display:flex;'
                f'align-items:center;justify-content:center;font-size:26px;{border}">'
                f'{grid[ri][li]}</div>'
            )
        rows_html += f'<div style="display:flex;">{cells}</div>'

    return (
        f'<div style="background:linear-gradient(180deg,#1a1a2e 0%,#16213e 100%);'
        f'width:{CW*LANES}px;margin:0 auto;border-radius:14px;'
        f'border:3px solid #0f3460;overflow:hidden;'
        f'box-shadow:0 8px 32px rgba(0,0,0,0.6);">'
        f'{rows_html}</div>'
    )

# ── JavaScript: keyboard + music ───────────────────────────────────────────────
def _inject_js():
    music_on = str(st.session_state.music).lower()
    crashed  = str(st.session_state.state == "game_over").lower()

    components.html(f"""
    <script>
    (function() {{
        const pw = window.parent;

        // ── Keyboard controls ──────────────────────────────────────────────
        // Arrow keys and A/D simulate clicking the Left / Right buttons
        if (!pw._trafficKeyBound) {{
            pw._trafficKeyBound = true;
            pw.document.addEventListener('keydown', function(e) {{
                const LEFT  = ['ArrowLeft',  'a', 'A'];
                const RIGHT = ['ArrowRight', 'd', 'D'];
                if (LEFT.includes(e.key) || RIGHT.includes(e.key)) {{
                    e.preventDefault();
                    const label = LEFT.includes(e.key) ? 'Left' : 'Right';
                    pw.document.querySelectorAll('button').forEach(function(btn) {{
                        if (btn.innerText.includes(label)) btn.click();
                    }});
                }}
            }});
        }}

        // ── Music (Web Audio API chiptune, stored on parent window) ────────
        const musicOn = {music_on};

        // Start music on first enable
        if (musicOn && !pw._trafficAudio) {{
            const AC = window.AudioContext || window.webkitAudioContext;
            pw._trafficAudio = new AC();

            // Note helper: square wave melody, sawtooth bass
            function note(ctx, freq, t, dur, type, vol) {{
                const osc  = ctx.createOscillator();
                const gain = ctx.createGain();
                osc.connect(gain);
                gain.connect(ctx.destination);
                osc.type = type;
                osc.frequency.value = freq;
                gain.gain.setValueAtTime(vol, t);
                gain.gain.exponentialRampToValueAtTime(0.0001, t + dur * 0.88);
                osc.start(t);
                osc.stop(t + dur);
            }}

            // Chiptune racing theme in C major (BPM 155)
            const B = 60 / 155;   // one beat in seconds

            //           freq  beats
            const MEL = [
                [392,0.5],[392,0.5],[440,0.5],[392,0.5],
                [349,0.5],[330,0.5],[294,0.5],[262,0.5],
                [330,0.5],[330,0.5],[349,0.5],[330,0.5],
                [294,0.5],[262,0.5],[247,0.5],[262,0.5],
                [262,0.5],[294,0.5],[330,0.5],[349,0.5],
                [392,0.5],[392,0.5],[440,0.5],[494,0.5],
                [392,0.5],[392,0.5],[440,0.5],[392,0.5],
                [349,0.5],[330,0.5],[294,1.0],[294,1.0]
            ];

            const BASS = [
                [131,1],[165,1],[196,1],[175,1],
                [131,1],[165,1],[196,1],[131,1]
            ];

            function scheduleBar(startT) {{
                const ctx = pw._trafficAudio;
                // Melody
                let t = startT;
                for (const [f, b] of MEL) {{
                    note(ctx, f, t, b * B, 'square', 0.06);
                    t += b * B;
                }}
                const loopDur = t - startT;

                // Bass (repeat pattern to fill same duration)
                let bt = startT;
                while (bt < startT + loopDur - 0.01) {{
                    for (const [f, b] of BASS) {{
                        if (bt >= startT + loopDur) break;
                        note(ctx, f, bt, b * B, 'sawtooth', 0.04);
                        bt += b * B;
                    }}
                }}
                return loopDur;
            }}

            let nextStart = pw._trafficAudio.currentTime + 0.05;
            function loop() {{
                if (!pw._trafficAudio) return;
                const dur = scheduleBar(nextStart);
                nextStart += dur;
                pw._trafficMusicTimer = setTimeout(loop, (dur - 0.15) * 1000);
            }}
            loop();
        }}

        // Resume if browser suspended the context (autoplay policy)
        if (musicOn && pw._trafficAudio && pw._trafficAudio.state === 'suspended') {{
            pw._trafficAudio.resume();
        }}

        // Stop music when toggled off
        if (!musicOn && pw._trafficAudio) {{
            clearTimeout(pw._trafficMusicTimer);
            pw._trafficAudio.close().catch(function(){{}});
            pw._trafficAudio = null;
        }}

        // ── Crash sound ────────────────────────────────────────────────────
        const crashed = {crashed};
        if (crashed && !pw._trafficCrashDone) {{
            pw._trafficCrashDone = true;
            const ctx2 = new (window.AudioContext || window.webkitAudioContext)();
            // Descending sawtooth bursts
            [[220,0.00],[165,0.12],[110,0.24],[80,0.36],[55,0.48]].forEach(function([f,t]) {{
                const o = ctx2.createOscillator();
                const g = ctx2.createGain();
                o.connect(g); g.connect(ctx2.destination);
                o.type = 'sawtooth'; o.frequency.value = f;
                g.gain.setValueAtTime(0.18, ctx2.currentTime + t);
                g.gain.exponentialRampToValueAtTime(0.0001, ctx2.currentTime + t + 0.14);
                o.start(ctx2.currentTime + t);
                o.stop(ctx2.currentTime + t + 0.15);
            }});
        }}
        if (!crashed) pw._trafficCrashDone = false;
    }})();
    </script>
    """, height=0)

# ── Layout ─────────────────────────────────────────────────────────────────────
st.markdown("## 🚗 Traffic Dodger")
st.caption("Arrow keys or **A / D** to steer · dodge the traffic!")

# Stats + music toggle
c1, c2, c3, c4 = st.columns(4)
c1.metric("Score",      st.session_state.score)
c2.metric("Level",      st.session_state.level)
c3.metric("High Score", st.session_state.high)
with c4:
    mute_label = "🔊 Music" if st.session_state.music else "🔇 Music"
    if st.button(mute_label, use_container_width=True):
        st.session_state.music = not st.session_state.music
        st.rerun()

st.markdown("---")
road_slot = st.empty()
st.markdown("---")

# Controls
if st.session_state.state in ("idle", "game_over"):
    btn_label = "▶️ Start Game" if st.session_state.state == "idle" else "🔄 Play Again"
    if st.button(btn_label, use_container_width=True):
        _reset()
        st.rerun()
else:
    b1, _, b2 = st.columns([3, 1, 3])
    go_left  = b1.button("⬅️  Left",  use_container_width=True, key="left")
    go_right = b2.button("Right  ➡️", use_container_width=True, key="right")
    if go_left  and st.session_state.lane > 0:
        st.session_state.lane -= 1
    if go_right and st.session_state.lane < LANES - 1:
        st.session_state.lane += 1

# Fill road after controls (so movement is reflected immediately)
if st.session_state.state == "idle":
    road_slot.info("Press **Start Game** to begin. Steer with ← → or A / D.")
elif st.session_state.state == "game_over":
    road_slot.error(
        f"💥 **GAME OVER!**  Score: **{st.session_state.score}**  ·  Level: **{st.session_state.level}**"
    )
else:
    road_slot.markdown(_render_road(), unsafe_allow_html=True)

# Inject JS (keyboard + music) on every render
_inject_js()

# ── Game loop ──────────────────────────────────────────────────────────────────
if st.session_state.state == "running":
    elapsed = time.time() - st.session_state.last_tick
    wait    = max(0.0, _tick_speed() - elapsed)
    time.sleep(wait)
    _do_tick()
    st.rerun()
