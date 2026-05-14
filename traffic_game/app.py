import streamlit as st
import random
import time

st.set_page_config(page_title="Traffic Dodger", page_icon="🚗", layout="centered")

# ── Constants ──────────────────────────────────────────────────────────────────
LANES       = 5
ROWS        = 11
PLAYER_ROW  = ROWS - 1
BASE_TICK   = 0.45   # seconds per tick at level 1
MIN_TICK    = 0.15   # fastest possible tick
ENEMY_CARS  = ["🚕", "🚙", "🏎️", "🚌", "🚛"]

# ── Session state ──────────────────────────────────────────────────────────────
def _init():
    st.session_state.setdefault("state",      "idle")   # idle | running | game_over
    st.session_state.setdefault("lane",       LANES // 2)
    st.session_state.setdefault("enemies",    [])        # list of [lane, row]
    st.session_state.setdefault("score",      0)
    st.session_state.setdefault("high",       0)
    st.session_state.setdefault("level",      1)
    st.session_state.setdefault("last_tick",  0.0)
    st.session_state.setdefault("spawn_cnt",  0)

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

    # Move all enemies one row down, drop those that leave the grid
    s.enemies = [[l, r + 1] for l, r in s.enemies if r + 1 < ROWS]

    # Spawn a new enemy at the top
    s.spawn_cnt += 1
    spawn_every = max(2, 5 - s.level)
    if s.spawn_cnt >= spawn_every:
        s.enemies.append([random.randint(0, LANES - 1), 0])
        s.spawn_cnt = 0

    # Collision check
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
    s  = st.session_state
    CW = 68   # cell width  (px)
    CH = 48   # cell height (px)

    # Build grid
    grid = [[""] * LANES for _ in range(ROWS)]
    for i, (l, r) in enumerate(s.enemies):
        if 0 <= r < ROWS:
            grid[r][l] = ENEMY_CARS[i % len(ENEMY_CARS)]
    grid[PLAYER_ROW][s.lane] = "🚗"

    rows_html = ""
    for row_idx in range(ROWS):
        cells = ""
        for lane_idx in range(LANES):
            border = (
                "border-right:2px dashed rgba(255,255,255,0.18);"
                if lane_idx < LANES - 1 else ""
            )
            emoji = grid[row_idx][lane_idx]
            cells += (
                f'<div style="width:{CW}px;height:{CH}px;display:flex;'
                f'align-items:center;justify-content:center;font-size:26px;{border}">'
                f'{emoji}</div>'
            )
        rows_html += f'<div style="display:flex;">{cells}</div>'

    road_w = CW * LANES
    return (
        f'<div style="background:linear-gradient(180deg,#1a1a2e 0%,#16213e 100%);'
        f'width:{road_w}px;margin:0 auto;border-radius:14px;'
        f'border:3px solid #0f3460;overflow:hidden;'
        f'box-shadow:0 8px 32px rgba(0,0,0,0.6);">'
        f'{rows_html}</div>'
    )

# ── Layout ─────────────────────────────────────────────────────────────────────
st.markdown("## 🚗 Traffic Dodger")
st.caption("Dodge the oncoming traffic — survive as long as you can!")

# Stats row
c1, c2, c3 = st.columns(3)
c1.metric("Score",      st.session_state.score)
c2.metric("Level",      st.session_state.level)
c3.metric("High Score", st.session_state.high)

st.markdown("---")

# Road placeholder (filled after button processing)
road_slot = st.empty()

st.markdown("---")

# Controls
if st.session_state.state in ("idle", "game_over"):
    label = "▶️ Start Game" if st.session_state.state == "idle" else "🔄 Play Again"
    if st.button(label, use_container_width=True):
        _reset()
        st.rerun()
else:
    b1, _, b2 = st.columns([3, 1, 3])
    moved_left  = b1.button("⬅️  Left",  use_container_width=True, key="left")
    moved_right = b2.button("Right  ➡️", use_container_width=True, key="right")

    if moved_left  and st.session_state.lane > 0:
        st.session_state.lane -= 1
    if moved_right and st.session_state.lane < LANES - 1:
        st.session_state.lane += 1

# Fill the road slot now (after movement has been applied)
if st.session_state.state == "idle":
    road_slot.info("Press **Start Game** to begin. Use ← Left and Right → to dodge!")
elif st.session_state.state == "game_over":
    road_slot.error(
        f"💥 **GAME OVER!**  You scored **{st.session_state.score}** points "
        f"and reached level **{st.session_state.level}**."
    )
else:
    road_slot.markdown(_render_road(), unsafe_allow_html=True)

# ── Game loop (auto-advance) ───────────────────────────────────────────────────
if st.session_state.state == "running":
    elapsed = time.time() - st.session_state.last_tick
    wait    = max(0.0, _tick_speed() - elapsed)
    time.sleep(wait)
    _do_tick()
    st.rerun()
