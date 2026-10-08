import tkinter as tk
from tkinter import ttk
import math

# ATM PIN DFA — PRESENTATION ANIMATION (interactive)
# Correct PIN: 1234

PIN = "1234"

BG = "#edf2f7"
WHITE = "#ffffff"
TEXT = "#18324a"
MUTED = "#617587"
BLUE = "#2774d6"
GREEN = "#218a50"
GREEN_LIGHT = "#d9f4e1"
RED = "#c72f3d"
RED_LIGHT = "#ffe0e4"
ORANGE = "#d47b08"
ORANGE_LIGHT = "#fff0d1"
YELLOW_LIGHT = "#fff4c2"
FAIL = "#6d7784"
FAIL_FILL = "#f0f2f5"
BLUE_LIGHT = "#cfe3ff"      # normal fill of every q(k,i) state
CUR_GREEN = "#7ee2a0"       # fill of the CURRENT state
DARK_GREEN = "#0f7a3a"      # outline of the CURRENT state

root = tk.Tk()
root.title("ATM PIN DFA — Animation")
root.configure(bg=BG)

# ---- Scale diagram so the whole window fits the screen ----
BASE_W, BASE_H = 1320, 650
sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
S = min(1.0, (sw - 60) / BASE_W, (sh - 350) / BASE_H)
S = max(S, 0.5)

# ---------------- Header ----------------
tk.Label(root, text="ATM PIN VALIDATION — DFA",
         font=("Arial", 20, "bold"), bg=BG, fg=TEXT).pack(pady=(8, 0))
pin_banner = tk.Frame(root, bg=GREEN, padx=10, pady=5)
pin_banner.pack(pady=(2, 6))
tk.Label(pin_banner, text="Correct PIN:", font=("Arial", 16, "bold"),
         bg=GREEN, fg="white").pack(side="left", padx=(6, 10))
for _d in PIN:
    tk.Label(pin_banner, text=_d, font=("Arial", 20, "bold"), width=2,
             bg="white", fg=GREEN).pack(side="left", padx=3)

# ---------------- Controls (at the TOP so they are always visible) ----------------
controls = tk.Frame(root, bg=BG)
controls.pack(pady=4)

tk.Label(controls, text="Attempts (4-digit PINs, comma separated):",
         font=("Arial", 10), bg=BG, fg=TEXT).grid(row=0, column=0, padx=4)

entry = tk.Entry(controls, font=("Arial", 13), width=26, justify="center")
entry.insert(0, "1234")
entry.grid(row=0, column=1, padx=4)

controls2 = tk.Frame(root, bg=BG)
controls2.pack(pady=2)

def mkbtn(text, bg, cmd, col):
    b = tk.Button(controls2, text=text, font=("Arial", 10, "bold"),
                  bg=bg, fg="white", activebackground=bg,
                  activeforeground="white", padx=10, pady=4,
                  cursor="hand2", command=cmd)
    b.grid(row=0, column=col, padx=4)
    return b

# ---------------- Canvas ----------------
canvas = tk.Canvas(root, width=int(BASE_W * S), height=int(BASE_H * S),
                   bg=WHITE, highlightthickness=0)
canvas.pack(padx=10, pady=4)

R = 25
X = [105, 265, 425, 585]
Y = {1: 150, 2: 340, 3: 530}
FAIL_DY = 72
ACCEPT = (830, 340)
LOCK = (1120, 530)

nodes, node_shapes = {}, {}
text_registry = []  # (item_id, size, style) so fonts can be scaled

def txt(x, y, text, size, style="normal", fill=TEXT, **kw):
    item = canvas.create_text(x, y, text=text, fill=fill,
                              font=("Arial", size, style), **kw)
    text_registry.append((item, size, style))
    return item

def add_node(key, label, x, y, fill=BLUE_LIGHT, outline=BLUE, accept=False, fsize=10):
    nodes[key] = (x, y)
    outer = canvas.create_oval(x-R, y-R, x+R, y+R,
                               fill=fill, outline=outline, width=3)
    if accept:
        canvas.create_oval(x-R+6, y-R+6, x+R-6, y+R-6,
                           outline=outline, width=2)
    txt(x, y, label, fsize, "italic", justify="center")
    node_shapes[key] = outer

edge_paths = {}     # (src, dst) -> polyline (base coords) the ball rolls along

def point_along(pts, t):
    """Point at fraction t of the total length of a polyline."""
    seg = [math.hypot(pts[k+1][0]-pts[k][0], pts[k+1][1]-pts[k][1])
           for k in range(len(pts)-1)]
    d = t * sum(seg)
    for k, L in enumerate(seg):
        if d <= L or k == len(seg) - 1:
            u = min(1, d / L) if L else 0
            return (pts[k][0] + (pts[k+1][0]-pts[k][0]) * u,
                    pts[k][1] + (pts[k+1][1]-pts[k][1]) * u)
        d -= L

def add_edge(src, dst, label="", color=MUTED, width=2, via=None, label_xy=None,
             label_t=0.5):
    x1, y1 = nodes[src]
    x2, y2 = nodes[dst]
    pts = [(x1, y1)] + (via or []) + [(x2, y2)]

    ax, ay = pts[1]
    bx, by = pts[-2]
    d1 = max(math.hypot(ax-x1, ay-y1), 1)
    d2 = max(math.hypot(x2-bx, y2-by), 1)
    pts[0] = (x1 + (ax-x1)*R/d1, y1 + (ay-y1)*R/d1)
    pts[-1] = (x2 - (x2-bx)*R/d2, y2 - (y2-by)*R/d2)

    coords = []
    for x, y in pts:
        coords += [x, y]
    canvas.create_line(*coords, fill=color, width=width,
                       arrow=tk.LAST, arrowshape=(9, 11, 4),
                       joinstyle=tk.ROUND)
    # the path the ball follows: centre of src -> along the arrow -> centre of dst
    edge_paths[(src, dst)] = [(x1, y1)] + pts + [(x2, y2)]
    if label:
        # every label sits in the MIDDLE of its line, on a small white pill
        mx, my = point_along(pts, label_t)
        w = 8 * len(label) + 12
        canvas.create_rectangle(mx - w/2, my - 10, mx + w/2, my + 10,
                                fill=WHITE, outline=color, width=1)
        txt(mx, my, label, 11, "bold", fill=color)

def q(a, i): return f"q{a},{i}"
def f(a, i): return f"f{a},{i}"

# ---------------- Build diagram ----------------
for a in (1, 2, 3):
    y = Y[a]
    canvas.create_rectangle(
        18, y-50, 1010, y+FAIL_DY+50,
        fill=("#f1f6ff" if a == 1 else "#f7f2ff" if a == 2 else "#fff4ec"),
        outline="")
    txt(30, y-34, f"ATTEMPT {a}", 10, "bold", anchor="w")
    for i in range(4):
        add_node(q(a, i), f"q{a},{i}", X[i], y)
    for i in (1, 2, 3):
        add_node(f(a, i), f"q′{a},{i}", X[i], y+FAIL_DY,
                 fill=FAIL_FILL, outline=FAIL)

add_node("ACCEPT", "q_\nACCEPT", *ACCEPT, fill=GREEN_LIGHT, outline=GREEN, accept=True, fsize=6)
add_node("LOCK", "q_\nLOCK", *LOCK, fill=RED_LIGHT, outline=RED, accept=True, fsize=6)

txt(24, Y[1], "START", 8, "bold", anchor="w")
canvas.create_line(62, Y[1], X[0]-R, Y[1], fill=TEXT, width=2, arrow=tk.LAST)
edge_paths[(None, "q1,0")] = [(62, Y[1]), (X[0], Y[1])]   # ball enters along START

for a in (1, 2, 3):
    y = Y[a]
    for i in range(3):
        add_edge(q(a, i), q(a, i+1), str(i+1), BLUE)
    for i in range(3):
        add_edge(q(a, i), f(a, i+1), f"Σ−{i+1}", ORANGE,
                 label_xy=(X[i]+45, y+38))
    add_edge(f(a, 1), f(a, 2), "Σ", FAIL)
    add_edge(f(a, 2), f(a, 3), "Σ", FAIL)

add_edge(q(1,3), "ACCEPT", "4", BLUE,
         via=[(650,120),(740,120),(790,300)], label_xy=(700,108))
add_edge(q(2,3), "ACCEPT", "4", BLUE,
         via=[(650,340),(790,340)], label_xy=(705,322))
add_edge(q(3,3), "ACCEPT", "4", BLUE,
         via=[(650,550),(740,550),(790,380)], label_xy=(700,570))

add_edge(q(1,3), q(2,0), "Σ−4", ORANGE,
         via=[(650,175),(680,220),(680,300),(80,300)], label_t=0.08)
add_edge(q(2,3), q(3,0), "Σ−4", ORANGE,
         via=[(650,365),(700,400),(700,490),(80,490)], label_t=0.08)
add_edge(f(1,3), q(2,0), "Σ", FAIL,
         via=[(650,245),(700,270),(700,300),(80,300)], label_xy=(720,275))
add_edge(f(2,3), q(3,0), "Σ", FAIL,
         via=[(650,435),(720,455),(720,490),(80,490)], label_xy=(735,460))
add_edge(q(3,3), "LOCK", "Σ−4", ORANGE,
         via=[(650,555),(850,575),(1020,550)], label_xy=(855,570))
add_edge(f(3,3), "LOCK", "Σ", FAIL,
         via=[(650,610),(850,620),(1020,560)], label_xy=(855,625))

txt(850, 390, "PIN CORRECT\nCARD UNLOCKED", 9, "bold", fill=GREEN, justify="center")
txt(1120, 590, "3 ATTEMPTS\nCARD LOCKED", 9, "bold", fill=RED, justify="center")

# ---- "PIN being entered" panel (empty space above q_LOCK) ----
PX = 1167                       # panel centre x
BOX_X0 = [PX - 115 + 60 * j for j in range(4)]
canvas.create_rectangle(1030, 28, 1305, 222, fill="#f8fafc", outline=BLUE, width=2)
txt(PX, 48, "PIN BEING ENTERED", 11, "bold", fill=BLUE)
pin_attempt_lbl = txt(PX, 72, "", 10, "bold", fill=MUTED)
pin_boxes, pin_texts = [], []
for _j in range(4):
    _x0 = BOX_X0[_j]
    pin_boxes.append(canvas.create_rectangle(_x0, 90, _x0 + 50, 142,
                                             fill=WHITE, outline=MUTED, width=2))
    pin_texts.append(txt(_x0 + 25, 116, "", 22, "bold"))
pin_pointer = txt(BOX_X0[0] + 25, 158, "▲", 16, "bold", fill=ORANGE, state="hidden")
pin_reading_lbl = txt(PX, 190, "", 10, "bold", fill=TEXT)

# ---- Apply scaling to the finished diagram ----
canvas.scale("all", 0, 0, S, S)
for item, size, style in text_registry:
    canvas.itemconfigure(item, font=("Arial", max(6, round(size * S)), style))

# ---- The ball that rolls from state to state ----
BALL_R = max(6, round(9 * S))
ball = canvas.create_oval(0, 0, 0, 0, fill="#ffb020", outline="#7a4a00",
                          width=2, state="hidden")
for _item, _s, _st in text_registry:      # keep every label readable on top of the ball
    canvas.tag_raise(_item)

# ---------------- Animation helpers ----------------
def reset_nodes():
    for key, oval in node_shapes.items():
        if key.startswith("f"):
            canvas.itemconfigure(oval, fill=FAIL_FILL, outline=FAIL, width=3)
        elif key == "ACCEPT":
            canvas.itemconfigure(oval, fill=GREEN_LIGHT, outline=GREEN, width=3)
        elif key == "LOCK":
            canvas.itemconfigure(oval, fill=RED_LIGHT, outline=RED, width=3)
        else:
            canvas.itemconfigure(oval, fill=BLUE_LIGHT, outline=BLUE, width=3)

def flash_node(key, fill, outline):
    reset_nodes()
    # every q(k,i) state is blue; the CURRENT one (and q_ACCEPT) glows green
    if key.startswith("q") or key == "ACCEPT":
        fill, outline = CUR_GREEN, DARK_GREEN
    canvas.itemconfigure(node_shapes[key], fill=fill, outline=outline, width=6)

# ---------------- Ball movement ----------------
MOVE_MS = 700       # time the ball takes to roll along one transition
DWELL_MS = 450      # pause after the ball arrives
cur_state = None    # state the ball is currently sitting in
moving = False      # True while the ball is rolling

def reset_ball():
    global cur_state
    cur_state = None
    canvas.itemconfigure(ball, state="hidden")

def move_ball(path, done):
    """Roll the ball along `path` (base coords), then call done()."""
    global after_id
    P = [(x * S, y * S) for x, y in path]
    seg = [math.hypot(P[k+1][0]-P[k][0], P[k+1][1]-P[k][1]) for k in range(len(P)-1)]
    total = sum(seg) or 1
    n = max(8, MOVE_MS // 16)
    canvas.itemconfigure(ball, state="normal")

    def pos(frac):
        d = frac * total
        for k, L in enumerate(seg):
            if d <= L or k == len(seg) - 1:
                u = min(1, d / L) if L else 0
                return (P[k][0] + (P[k+1][0]-P[k][0]) * u,
                        P[k][1] + (P[k+1][1]-P[k][1]) * u)
            d -= L

    def frame(k):
        global after_id
        t = k / n
        x, y = pos(t * t * (3 - 2 * t))          # smooth start and stop
        canvas.coords(ball, x - BALL_R, y - BALL_R, x + BALL_R, y + BALL_R)
        if k < n:
            after_id = root.after(16, lambda: frame(k + 1))
        else:
            done()
    frame(0)

def go_to(key, fill, outline, arrive):
    """Roll the ball from the current state to `key`, light it up, then arrive()."""
    global cur_state, moving
    src, cur_state = cur_state, key
    path = edge_paths.get((src, key))
    if src == key or path is None:       # already there (new attempt begins here)
        if src is None:
            x, y = nodes[key]
            canvas.coords(ball, x*S - BALL_R, y*S - BALL_R, x*S + BALL_R, y*S + BALL_R)
            canvas.itemconfigure(ball, state="normal")
        flash_node(key, fill, outline)
        arrive()
        return
    moving = True

    def done():
        global moving
        moving = False
        flash_node(key, fill, outline)
        arrive()
    move_ball(path, done)

# ---------------- PIN panel updates ----------------
def reset_pin_panel():
    canvas.itemconfigure(pin_attempt_lbl, text="")
    canvas.itemconfigure(pin_reading_lbl, text="")
    canvas.itemconfigure(pin_pointer, state="hidden")
    for j in range(4):
        canvas.itemconfigure(pin_boxes[j], fill=WHITE, outline=MUTED, width=2)
        canvas.itemconfigure(pin_texts[j], text="")

def show_pin(info):
    """info = (attempt, pin, index of the digit being read; -1 = none yet)."""
    if info is None:
        return
    a, pin, upto = info
    canvas.itemconfigure(pin_attempt_lbl, text=f"Attempt {a} of 3")
    mismatch = next((j for j in range(4) if pin[j] != PIN[j]), 4)
    for j in range(4):
        if j <= upto:
            if j < mismatch:
                fill, col = GREEN_LIGHT, GREEN
            elif j == mismatch:
                fill, col = RED_LIGHT, RED
            else:
                fill, col = ORANGE_LIGHT, ORANGE
            canvas.itemconfigure(pin_boxes[j], fill=fill, outline=col,
                                 width=4 if j == upto else 2)
            canvas.itemconfigure(pin_texts[j], text=pin[j], fill=col)
        else:
            canvas.itemconfigure(pin_boxes[j], fill=WHITE, outline=MUTED, width=2)
            canvas.itemconfigure(pin_texts[j], text="")
    if upto >= 0:
        canvas.coords(pin_pointer, (BOX_X0[upto] + 25) * S, 158 * S)
        canvas.itemconfigure(pin_pointer, state="normal")
        canvas.itemconfigure(pin_reading_lbl, text=f"Reading digit {upto + 1}:  {pin[upto]}")
    else:
        canvas.itemconfigure(pin_pointer, state="hidden")
        canvas.itemconfigure(pin_reading_lbl, text="Waiting for digit 1 …")

# ---------------- Status area ----------------
status = tk.Label(root, text="Choose a mode, then press Start (auto) or Step (one state at a time).",
                  font=("Arial", 12, "bold"), bg=BG, fg=TEXT)
status.pack(pady=(2, 0))
substatus = tk.Label(root, text="", font=("Arial", 10), bg=BG, fg=MUTED)
substatus.pack(pady=(0, 6))

# ---------------- Build steps from any list of attempts ----------------
def _build_steps_raw(attempts):
    """Simulate the DFA and return a list of animation steps."""
    steps = []  # (kind, key, fill, outline, main, sub)
    for a, pin in enumerate(attempts, start=1):
        steps.append(("node", q(a, 0), YELLOW_LIGHT, ORANGE,
                      f"Attempt {a}: entering {pin}", f"Starting at q{a},0"))
        cur = q(a, 0)
        i_state = 0          # number of correct digits so far
        failed = False
        for i, d in enumerate(pin):
            if not failed:
                if d == PIN[i]:
                    if i == 3:
                        steps.append(("node", "ACCEPT", GREEN_LIGHT, GREEN,
                                      "Digit 4 is correct — PIN CORRECT",
                                      f"{cur} -- 4 --> q_ACCEPT"))
                        steps.append(("pause", None, None, None,
                                      "CARD UNLOCKED — continue with transaction", ""))
                        return steps
                    nxt = q(a, i + 1)
                    steps.append(("node", nxt, GREEN_LIGHT, GREEN,
                                  f"Digit {i+1} ({d}) is correct",
                                  f"{cur} -- {d} --> {nxt}"))
                    cur = nxt
                else:
                    if i == 3:
                        # wrong 4th digit -> next attempt (or lock)
                        if a == 3:
                            steps.append(("node", "LOCK", RED_LIGHT, RED,
                                          f"Digit 4 ({d}) is incorrect — CARD LOCKED",
                                          f"{cur} -- {d} --> q_LOCK"))
                            steps.append(("pause", None, None, None,
                                          "3 ATTEMPTS USED — CARD LOCKED", ""))
                            return steps
                        nxt = q(a + 1, 0)
                        steps.append(("node", nxt, ORANGE_LIGHT, ORANGE,
                                      f"Digit 4 ({d}) is incorrect — attempt {a} failed",
                                      f"{cur} -- {d} --> {nxt}"))
                        cur = nxt
                        break
                    nxt = f(a, i + 1)
                    failed = True
                    steps.append(("node", nxt, RED_LIGHT, RED,
                                  f"Digit {i+1} ({d}) is incorrect — attempt failed",
                                  f"{cur} -- {d} --> {nxt}"))
                    cur = nxt
            else:
                if i == 3:
                    if a == 3:
                        steps.append(("node", "LOCK", RED_LIGHT, RED,
                                      f"Digit 4 ({d}) consumed — CARD LOCKED",
                                      f"{cur} -- Σ --> q_LOCK"))
                        steps.append(("pause", None, None, None,
                                      "3 ATTEMPTS USED — CARD LOCKED", ""))
                        return steps
                    nxt = q(a + 1, 0)
                    steps.append(("node", nxt, ORANGE_LIGHT, ORANGE,
                                  f"Digit 4 ({d}) completes failed attempt {a}",
                                  f"{cur} -- Σ --> {nxt}"))
                    cur = nxt
                else:
                    nxt = f(a, i + 1)
                    steps.append(("node", nxt, ORANGE_LIGHT, ORANGE,
                                  f"Digit {i+1} ({d}) is still consumed",
                                  f"{cur} -- Σ --> {nxt}"))
                    cur = nxt
    steps.append(("pause", None, None, None,
                  "PIN INCORRECT — waiting for the next attempt", ""))
    return steps

def build_steps(attempts):
    """Same steps, each extended with (attempt, pin, digit index) for the PIN panel.
    Every digit produces exactly one node step, so the digit index just counts up."""
    out, a, i = [], 0, -1
    for st in _build_steps_raw(attempts):
        info = None
        if st[0] == "node":
            if st[4].startswith("Attempt "):
                a, i = a + 1, -1
            else:
                i += 1
            info = (a, attempts[a - 1], i)
        out.append(st + (info,))
    return out

# ---------------- Runner ----------------
after_id = None
running = False
STEP_MS = 800
PAUSE_MS = 1500

def finish():
    global running
    running = False
    set_buttons("normal")
    reset_nodes()
    reset_ball()

def run_steps(steps, index=0):
    global after_id
    if index >= len(steps):
        finish()
        status.config(text="Animation complete — run again any time.", fg=TEXT)
        substatus.config(text="")
        return

    kind, key, fill, outline, main, small, info = steps[index]

    if kind == "pause":
        reset_nodes()
        color = GREEN if "UNLOCKED" in main else RED
        status.config(text=main, fg=color)
        substatus.config(text=small)
        after_id = root.after(PAUSE_MS, lambda: run_steps(steps, index + 1))
        return

    # describe the transition as the ball leaves; light the new state when it lands
    show_pin(info)
    status.config(text=main,
                  fg=GREEN if fill == GREEN_LIGHT else
                     RED if fill == RED_LIGHT else
                     ORANGE if fill == ORANGE_LIGHT else TEXT)
    substatus.config(text=small)

    def arrive():
        global after_id
        after_id = root.after(DWELL_MS, lambda: run_steps(steps, index + 1))
    go_to(key, fill, outline, arrive)

def start_attempts(attempts):
    global running
    if running:
        return
    running = True
    reset_step_state()
    set_buttons("disabled")
    reset_nodes()
    status.config(text="Starting DFA animation...", fg=TEXT)
    substatus.config(text="")
    steps = build_steps(attempts)
    root.after(400, lambda: run_steps(steps, 0))

# ---------------- Mode selection (drop-down) ----------------
MODES = {
    "Correct PIN": "1234",
    "Wrong PINs (locks the card)": "9234,1934,1299",
    "Fail then pass": "1934,1234",
    "Custom (use the text box)": None,
}
CUSTOM_MODE = "Custom (use the text box)"

tk.Label(controls2, text="Mode:", font=("Arial", 10, "bold"),
         bg=BG, fg=TEXT).grid(row=0, column=0, padx=(4, 2))
mode_box = ttk.Combobox(controls2, state="readonly", width=28,
                        font=("Arial", 10), values=list(MODES))
mode_box.current(0)
mode_box.grid(row=0, column=1, padx=4)

def apply_mode():
    """Copy the chosen mode's PIN list into the text box (Custom keeps it)."""
    text = MODES[mode_box.get()]
    if text is not None:
        entry.delete(0, tk.END)
        entry.insert(0, text)

def on_mode_change(event=None):
    if running or moving:
        return
    reset_step_state()
    apply_mode()
    reset_nodes()
    status.config(text=f"Mode: {mode_box.get()} — press Start or Step.", fg=TEXT)
    substatus.config(text="")

def on_entry_edit(event=None):
    if running or (event is not None and event.keysym in ("Return", "Tab")):
        return
    if mode_box.get() != CUSTOM_MODE:
        mode_box.set(CUSTOM_MODE)
    reset_step_state()

mode_box.bind("<<ComboboxSelected>>", on_mode_change)
entry.bind("<KeyRelease>", on_entry_edit)
apply_mode()

def parse_attempts():
    """Read the text box; return a list of up to 3 PINs, or None if invalid."""
    raw = entry.get().replace(" ", "")
    attempts = [p for p in raw.split(",") if p]
    if not attempts or any(len(p) != 4 or not p.isdigit() for p in attempts):
        status.config(text="Please enter 4-digit PINs, e.g.  1234  or  9234,1934,1299",
                      fg=RED)
        substatus.config(text="")
        return None
    return attempts[:3]

# ---------------- Start (auto-play) ----------------
def run_custom(event=None):
    if running or moving:
        return
    apply_mode()
    attempts = parse_attempts()
    if attempts is None:
        return
    start_attempts(attempts)

# ---------------- Step (one state at a time) ----------------
step_steps = None   # steps being walked through manually
step_idx = 0
step_done = False

def reset_step_state():
    global step_steps, step_idx, step_done, moving, after_id
    if after_id is not None:             # cancel a ball that is still rolling
        root.after_cancel(after_id)
        after_id = None
    moving = False
    step_steps, step_idx, step_done = None, 0, False
    reset_pin_panel()
    reset_ball()

def step_once():
    global step_steps, step_idx, step_done
    if running or moving:
        return
    if step_steps is None or step_done:
        apply_mode()
        attempts = parse_attempts()
        if attempts is None:
            return
        reset_step_state()
        reset_nodes()
        step_steps = build_steps(attempts)

    kind, key, fill, outline, main, small, info = step_steps[step_idx]
    step_idx += 1
    show_pin(info)
    color = (GREEN if fill == GREEN_LIGHT else
             RED if fill == RED_LIGHT else
             ORANGE if fill == ORANGE_LIGHT else TEXT)
    status.config(text=main, fg=color)
    substatus.config(text=small)

    # a trailing "pause" entry is only a result message: show it once the ball lands
    result = None
    if step_idx < len(step_steps) and step_steps[step_idx][0] == "pause":
        result = step_steps[step_idx][4]
        step_idx += 1
    if step_idx >= len(step_steps):
        step_done = True

    def arrive():
        if result:
            status.config(text=result, fg=GREEN if "UNLOCKED" in result else RED)
            substatus.config(text=f"{small}   (last step — press Step to start over)")
    go_to(key, fill, outline, arrive)

def stop():
    global running, after_id
    if after_id is not None:
        root.after_cancel(after_id)
        after_id = None
    running = False
    reset_step_state()
    set_buttons("normal")
    reset_nodes()
    status.config(text="Stopped. Choose a mode, then press Start or Step.", fg=TEXT)
    substatus.config(text="")

btn_start = mkbtn("▶ Start", GREEN, run_custom, 2)
btn_step = mkbtn("⏭ Step", BLUE, step_once, 3)
btn_stop = mkbtn("■ Stop", FAIL, stop, 4)

def set_buttons(state):
    for b in (btn_start, btn_step):
        b.config(state=state)
    mode_box.config(state="readonly" if state == "normal" else "disabled")

entry.bind("<Return>", run_custom)
root.protocol("WM_DELETE_WINDOW", root.destroy)
root.mainloop()