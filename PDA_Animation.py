"""Animated Bank Account PDA: watch the state diagram change on example sessions.

Left : the state diagram. The active state lights up, the active transition
       is highlighted, and a token travels along it.
Right: the stack (X on top of Z0), the current input and a plain-English caption.

Run:  python bank_pda_animation.py
Needs only the standard library (Tkinter).
"""
import math
import tkinter as tk
from tkinter import ttk

W, H = 940, 580
DARK, MUTED = "#374151", "#6B7280"

# (centre x, centre y, radius)
NODES = {"qs": (100, 320, 40), "q0": (380, 320, 50),
         "qf": (830, 150, 58), "qr": (830, 490, 58)}
STATE_COLORS = {"qs": ("#E5E7EB", "#111827"), "q0": ("#DBEAFE", "#1D4ED8"),
                "qf": ("#DCFCE7", "#15803D"), "qr": ("#FEE2E2", "#B91C1C")}
LABELS = {
    "init": ("ε, Z0 / B0 Z0", "#6D28D9"),
    "dep": ("deposit(d), X / X+d", "#15803D"),
    "chk": ("balance-check, X / X", "#1D4ED8"),
    "wd": ("withdraw(w), w ≤ X, X / X−w", "#B45309"),
    "qf": ("end-session [X ≥ 0], X / X", "#15803D"),
    "qr": ("withdraw(w), w > X, X / X", "#B91C1C"),
}
LOOP_KEYS = ("dep", "chk", "wd")

# (title, initial balance B0, list of (input, amount))
EXAMPLES = [
    ("1. Normal session (accepted)", 5000,
     [("deposit", 2000), ("withdraw", 1500), ("check", 0), ("end", 0)]),
    ("2. Overdraft (rejected)", 5000,
     [("deposit", 1000), ("withdraw", 9000), ("end", 0)]),
    ("3. Withdraw everything (still accepted)", 1000,
     [("withdraw", 1000), ("check", 0), ("end", 0)]),
    ("4. Overdraft by one unit (rejected)", 300,
     [("withdraw", 100), ("withdraw", 201)]),
    ("5. Check only, then leave (accepted)", 2500,
     [("check", 0), ("check", 0), ("end", 0)]),
    ("6. Many small steps (accepted)", 100,
     [("deposit", 50), ("withdraw", 30), ("deposit", 200), ("withdraw", 120),
      ("check", 0), ("end", 0)]),
]


# ---------------------------------------------------------------- the PDA
def build_steps(b0, ops):
    """Run the PDA on one example and return a list of animation steps."""
    steps = [dict(key="init", to="q0", inp="ε (no input read)", x_before=None,
                  x_after=b0, caption=f"Push B0 = {b0:,} on top of Z0")]
    X = b0
    for op, a in ops:
        if op == "deposit":
            steps.append(dict(key="dep", to="q0", inp=f"deposit({a:,})", x_before=X,
                              x_after=X + a, caption=f"Deposit: X goes {X:,} → {X + a:,}"))
            X += a
        elif op == "check":
            steps.append(dict(key="chk", to="q0", inp="balance-check", x_before=X,
                              x_after=X, caption=f"Balance check: X stays {X:,}"))
        elif op == "withdraw" and a <= X:
            steps.append(dict(key="wd", to="q0", inp=f"withdraw({a:,})", x_before=X,
                              x_after=X - a,
                              caption=f"{a:,} ≤ {X:,}, allowed: X goes {X:,} → {X - a:,}"))
            X -= a
        elif op == "withdraw":
            steps.append(dict(key="qr", to="qr", inp=f"withdraw({a:,})", x_before=X,
                              x_after=X,
                              caption=f"{a:,} > {X:,}: overdraft, go to qr, X unchanged"))
            break
        elif op == "end":
            steps.append(dict(key="qf", to="qf", inp="end-session", x_before=X,
                              x_after=X, caption=f"X = {X:,} ≥ 0, go to qf"))
            break
    return steps


# ---------------------------------------------------------------- geometry
def edge_line(a, b):
    ax, ay, ar = NODES[a]
    bx, by, br = NODES[b]
    L = math.hypot(bx - ax, by - ay)
    ux, uy = (bx - ax) / L, (by - ay) / L
    return (ax + ux * ar, ay + uy * ar, bx - ux * (br + 4), by - uy * (br + 4))


def loop_point(t):
    """Cubic Bezier for the self-loop above q0."""
    x0, y0, _ = NODES["q0"]
    p = [(x0 - 35, y0 - 36), (x0 - 95, y0 - 170), (x0 + 95, y0 - 170), (x0 + 35, y0 - 36)]
    u = 1 - t
    x = u**3 * p[0][0] + 3 * u * u * t * p[1][0] + 3 * u * t * t * p[2][0] + t**3 * p[3][0]
    y = u**3 * p[0][1] + 3 * u * u * t * p[1][1] + 3 * u * t * t * p[2][1] + t**3 * p[3][1]
    return x, y


class App:
    BASE_FRAMES = 70   # frames per transition at speed 1 (16 ms each)
    BASE_PAUSE = 45

    def __init__(self, root):
        self.root = root
        root.title("Bank Account PDA - State Transition Animation")
        root.configure(bg="white")
        self.geom = {"init": edge_line("qs", "q0"),
                     "qf": edge_line("q0", "qf"),
                     "qr": edge_line("q0", "qr")}
        self.playing = False
        self.anim = None
        self.pause = 0
        self.idx = 0
        self.steps = []
        self.i = 0
        self.X = None
        self.state = "qs"

        main = tk.Frame(root, bg="white")
        main.pack(padx=10, pady=10)
        self.c = tk.Canvas(main, width=W, height=H, bg="white",
                           highlightthickness=2, highlightbackground="#CBD5E1")
        self.c.grid(row=0, column=0)
        side = tk.Frame(main, bg="white")
        side.grid(row=0, column=1, sticky="n", padx=(12, 0))

        io = tk.Frame(side, bg="white")
        io.pack(anchor="w")
        cur = tk.Frame(io, bg="white", width=135, height=70)
        cur.pack(side="left", anchor="n")
        cur.pack_propagate(False)
        tk.Label(cur, text="Current input", font=("Arial", 13), bg="white",
                 fg=MUTED).pack(anchor="w")
        self.inp = tk.Label(cur, text="-", font=("Arial", 14, "bold"), bg="white",
                            fg="#111827", wraplength=130, justify="left", anchor="nw")
        self.inp.pack(anchor="w")
        nxt = tk.Frame(io, bg="white", width=125, height=70)
        nxt.pack(side="left", anchor="n", padx=(0, 0))
        nxt.pack_propagate(False)
        tk.Label(nxt, text="Next input", font=("Arial", 13), bg="white",
                 fg=MUTED).pack(anchor="w")
        self.next_inp = tk.Label(nxt, text="-", font=("Arial", 14, "bold"), bg="white",
                                 fg="#6D28D9", wraplength=120, justify="left", anchor="nw")
        self.next_inp.pack(anchor="w")
        self.sc = tk.Canvas(side, width=260, height=330, bg="white",
                            highlightthickness=2, highlightbackground="#CBD5E1")
        self.sc.pack(pady=8)
        tk.Label(side, text="What happened", font=("Arial", 14), bg="white",
                 fg=MUTED).pack(anchor="w")
        self.cap = tk.Label(side, text="", font=("Arial", 16, "bold"), bg="white",
                            wraplength=250, justify="left", anchor="nw", height=4)
        self.cap.pack(anchor="w")

        bar = tk.Frame(root, bg="white")
        bar.pack(pady=(0, 10))
        self.combo = ttk.Combobox(bar, state="readonly", width=38, font=("Arial", 13),
                                  values=[e[0] for e in EXAMPLES])
        self.combo.current(0)
        self.combo.bind("<<ComboboxSelected>>", lambda e: self.load(self.combo.current()))
        self.combo.pack(side="left", padx=6)
        self.play_btn = tk.Button(bar, text="▶ Play", width=9, font=("Arial", 13, "bold"),
                                  command=self.toggle)
        self.play_btn.pack(side="left", padx=4)
        tk.Button(bar, text="Step", width=7, font=("Arial", 13, "bold"),
                  command=self.step_once).pack(side="left", padx=4)
        tk.Button(bar, text="Restart", width=8, font=("Arial", 13, "bold"),
                  command=lambda: self.load(self.idx)).pack(side="left", padx=4)
        self.playall = tk.BooleanVar(value=True)
        tk.Checkbutton(bar, text="Play all examples", variable=self.playall, bg="white",
                       font=("Arial", 13)).pack(side="left", padx=8)
        tk.Label(bar, text="Speed", bg="white", font=("Arial", 13)).pack(side="left")
        self.speed = tk.Scale(bar, from_=0.5, to=3, resolution=0.25, orient="horizontal",
                              length=120, bg="white", highlightthickness=0)
        self.speed.set(1)
        self.speed.pack(side="left")

        self.draw_diagram()
        self.load(0)
        self.tick()

    # ------------------------------------------------------------ drawing
    def draw_diagram(self):
        c = self.c
        c.create_text(W / 2, 28, text="Bank Account PDA", font=("Arial", 26, "bold"),
                      fill="#111827")
        c.create_line(8, 320, 56, 320, width=4, arrow=tk.LAST, fill=DARK)
        c.create_text(30, 296, text="start", font=("Arial", 14), fill=DARK)

        self.lines = {}
        for key in ("init", "qf", "qr"):
            self.lines[key] = c.create_line(*self.geom[key], width=4, arrow=tk.LAST,
                                            fill=DARK)
        pts = [loop_point(k / 30) for k in range(31)]
        self.lines["loop"] = c.create_line(*[v for p in pts for v in p], width=4,
                                           arrow=tk.LAST, fill=DARK)

        self.nodes, self.texts = {}, {}
        for name, (x, y, r) in NODES.items():
            self.nodes[name] = c.create_oval(x - r, y - r, x + r, y + r, width=4,
                                             fill="#F3F4F6", outline=MUTED)
            self.texts[name] = c.create_text(x, y, text=name, font=("Arial", 24, "bold"),
                                             fill=MUTED)
        x, y, r = NODES["qf"]
        self.qf_inner = c.create_oval(x - r + 9, y - r + 9, x + r - 9, y + r - 9,
                                      width=4, outline=MUTED)
        c.tag_raise(self.texts["qf"])
        c.create_text(x, y + r + 20, text="accept", font=("Arial", 15), fill="#15803D")
        x, y, r = NODES["qr"]
        self.qr_inner = c.create_oval(x - r + 9, y - r + 9, x + r - 9, y + r - 9,
                                      width=4, outline=MUTED)
        c.tag_raise(self.texts["qr"])
        c.create_text(x, y + r + 20, text="reject", font=("Arial", 15), fill="#B91C1C")

        self.labels = {}
        gx1, gy1, gx2, gy2 = self.geom["init"]
        self.labels["init"] = c.create_text((gx1 + gx2) / 2, gy1 - 22, text=LABELS["init"][0])
        for k, ypos in zip(LOOP_KEYS, (68, 98, 128)):
            self.labels[k] = c.create_text(NODES["q0"][0], ypos, text=LABELS[k][0])
        for k, sign in (("qf", 1), ("qr", -1)):
            x1, y1, x2, y2 = self.geom[k]
            L = math.hypot(x2 - x1, y2 - y1)
            ux, uy = (x2 - x1) / L, (y2 - y1) / L
            nx, ny = (uy, -ux) if sign == 1 else (-uy, ux)
            self.labels[k] = c.create_text((x1 + x2) / 2 + nx * 24, (y1 + y2) / 2 + ny * 24,
                                           text=LABELS[k][0],
                                           angle=math.degrees(math.atan2(-(y2 - y1), x2 - x1)))
        for k in self.labels:
            self.highlight(k, False)

        self.banner = c.create_text(W / 2, H - 28, text="", font=("Arial", 28, "bold"))
        self.token = c.create_oval(0, 0, 0, 0, fill="#F59E0B", outline="#111827", width=3)

    def highlight(self, key, on):
        color = LABELS[key][1]
        self.c.itemconfig(self.labels[key],
                          fill=color if on else MUTED,
                          font=("Arial", 19 if on else 15, "bold"))
        line = self.lines["loop" if key in LOOP_KEYS else key]
        self.c.itemconfig(line, fill=color if on else DARK, width=7 if on else 4)

    def set_state(self, name):
        self.state = name
        for n, item in self.nodes.items():
            if n == name:
                bg, fg = STATE_COLORS[n]
                self.c.itemconfig(item, fill=bg, outline=fg)
                self.c.itemconfig(self.texts[n], fill=fg)
            else:
                self.c.itemconfig(item, fill="#F3F4F6", outline=MUTED)
                self.c.itemconfig(self.texts[n], fill=MUTED)
        self.c.itemconfig(self.qf_inner, outline=STATE_COLORS["qf"][1] if name == "qf" else MUTED)
        self.c.itemconfig(self.qr_inner, outline=STATE_COLORS["qr"][1] if name == "qr" else MUTED)

    def place_token(self, x, y):
        self.c.coords(self.token, x - 12, y - 12, x + 12, y + 12)
        self.c.tag_raise(self.token)

    def token_home(self, name):
        x, y, r = NODES[name]
        self.place_token(x, y + r * 0.58)

    def draw_stack(self, X=None, flash=None):
        c = self.sc
        c.delete("all")
        c.create_text(130, 20, text="STACK", font=("Arial", 15, "bold"), fill=MUTED)
        c.create_rectangle(35, 260, 225, 315, fill="#E5E7EB", outline=DARK, width=3)
        c.create_text(130, 288, text="Z0", font=("Arial", 22, "bold"))
        if X is None:
            return
        fill = {"up": "#BBF7D0", "down": "#FED7AA", None: "#DBEAFE"}[flash]
        c.create_rectangle(35, 195, 225, 260, fill=fill, outline="#1D4ED8", width=3)
        c.create_text(130, 228, text=f"X = {X:,}", font=("Arial", 22, "bold"),
                      fill="#1E3A8A")
        c.create_text(130, 178, text="top", font=("Arial", 14), fill=MUTED)

    # ------------------------------------------------------------ control
    def update_next(self):
        """Show the input that will be read by the following transition."""
        if self.i < len(self.steps):
            self.next_inp.config(text=self.steps[self.i]["inp"])
        else:
            self.next_inp.config(text="(none)")

    def frames(self, base):
        return max(2, int(base / self.speed.get()))

    def load(self, idx):
        self.idx = idx
        self.combo.current(idx)
        _, b0, ops = EXAMPLES[idx]
        self.steps = build_steps(b0, ops)
        self.i = 0
        self.anim = None
        self.pause = 0
        self.X = None
        for k in self.labels:
            self.highlight(k, False)
        self.set_state("qs")
        self.token_home("qs")
        self.draw_stack(None)
        self.c.itemconfig(self.banner, text="")
        self.inp.config(text="-")
        self.update_next()
        self.cap.config(text=f"Ready. Starting balance B0 = {b0:,}")

    def finished(self):
        return self.i >= len(self.steps) and self.anim is None

    def toggle(self):
        if self.playing:
            self.playing = False
        else:
            if self.finished():
                self.load(self.idx)
            self.playing = True
        self.play_btn.config(text="⏸ Pause" if self.playing else "▶ Play")

    def step_once(self):
        if self.anim is None and not self.finished():
            self.pause = 0
            self.begin_step()

    def begin_step(self):
        s = self.steps[self.i]
        self.i += 1
        if self.X is not None:
            self.draw_stack(self.X)
        self.highlight(s["key"], True)
        self.inp.config(text=s["inp"])
        self.update_next()
        self.cap.config(text=s["caption"])
        self.anim = dict(step=s, f=0, n=self.frames(self.BASE_FRAMES))

    def finish_step(self, s):
        self.highlight(s["key"], False)
        self.set_state(s["to"])
        flash = None
        if s["x_before"] is not None and s["x_after"] != s["x_before"]:
            flash = "up" if s["x_after"] > s["x_before"] else "down"
        self.X = s["x_after"]
        self.draw_stack(self.X, flash)
        self.token_home(s["to"])
        if s["to"] == "qf":
            self.c.itemconfig(self.banner, text="ACCEPTED", fill="#15803D")
        elif s["to"] == "qr":
            self.c.itemconfig(self.banner, text="REJECTED", fill="#B91C1C")
        self.pause = self.frames(self.BASE_PAUSE * (3 if self.i >= len(self.steps) else 1))

    def tick(self):
        if self.anim:
            a = self.anim
            a["f"] += 1
            t = min(1.0, a["f"] / a["n"])
            key = a["step"]["key"]
            if key in LOOP_KEYS:
                x, y = loop_point(t)
            else:
                x1, y1, x2, y2 = self.geom[key]
                x, y = x1 + (x2 - x1) * t, y1 + (y2 - y1) * t
            self.place_token(x, y)
            if t >= 1.0:
                s = a["step"]
                self.anim = None
                self.finish_step(s)
        elif self.pause > 0:
            self.pause -= 1
        elif self.playing:
            if self.i < len(self.steps):
                self.begin_step()
            elif self.playall.get() and self.idx + 1 < len(EXAMPLES):
                self.load(self.idx + 1)
                self.pause = self.frames(self.BASE_PAUSE)
            else:
                self.playing = False
                self.play_btn.config(text="▶ Play")
        self.root.after(16, self.tick)


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
