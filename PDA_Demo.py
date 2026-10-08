"""Bank Account PDA simulator with two screens (Tkinter, standard library only).

Left screen : background work (state, stack, last transition, trace)
Right screen: user interface (ATM)

Run:  python bank_pda_gui.py
"""
import tkinter as tk

F = ("Arial", 15)
FB = ("Arial", 16, "bold")
FH = ("Arial", 20, "bold")

# state -> (active background, active foreground)
COLORS = {
    "qs": ("#E5E7EB", "#111827"),
    "q0": ("#DBEAFE", "#1D4ED8"),
    "qf": ("#DCFCE7", "#15803D"),
    "qr": ("#FEE2E2", "#B91C1C"),
}
NAMES = {"qs": "qs", "q0": "q0", "qf": "qf (accept)", "qr": "qr (reject)"}


class BankPDA:
    """The machine itself: states, stack, and the six transitions."""

    def __init__(self, b0):
        self.state = "qs"
        self.stack = ["Z0"]
        self.log = [("start", "", "Machine in qs, stack holds Z0 only")]
        # qs -> q0 : epsilon, Z0 / B0 Z0
        self.stack.append(b0)
        self.state = "q0"
        self.log.append(("qs -> q0", "e, Z0 / B0 Z0", f"Push B0 = {b0:,}"))

    @property
    def X(self):
        return self.stack[-1]

    def deposit(self, d):
        old = self.X
        self.stack[-1] = old + d
        self.log.append(("q0 -> q0", "deposit(d), X / X+d", f"X: {old:,} -> {old + d:,}"))
        return f"Deposited {d:,}.", ""

    def check(self):
        self.log.append(("q0 -> q0", "balance-check, X / X", f"X stays {self.X:,}"))
        return f"Your balance is {self.X:,}.", ""

    def withdraw(self, w):
        old = self.X
        if w <= old:
            self.stack[-1] = old - w
            self.log.append(("q0 -> q0", "withdraw(w), w <= X, X / X-w",
                             f"X: {old:,} -> {old - w:,}"))
            return f"Withdrew {w:,}.", ""
        self.state = "qr"
        self.log.append(("q0 -> qr", "withdraw(w), w > X, X / X",
                         f"{w:,} > {old:,}, X unchanged"))
        return "Insufficient funds. Session rejected.", "bad"

    def end(self):
        self.state = "qf"
        self.log.append(("q0 -> qf", "end-session [X >= 0], X / X", f"X = {self.X:,} >= 0"))
        return f"Session ended. Final balance {self.X:,}. Accepted.", "done"


class App:
    def __init__(self, root):
        root.title("Bank Account PDA Simulator")
        root.configure(bg="white")
        tk.Label(root, text="Bank Account PDA Simulator", font=FH, bg="white").grid(
            row=0, column=0, columnspan=2, pady=10)
        root.columnconfigure((0, 1), weight=1, uniform="half")
        root.rowconfigure(1, weight=1)

        left = tk.LabelFrame(root, text=" Background: PDA at work ", font=FB,
                             bg="white", padx=12, pady=8)
        right = tk.LabelFrame(root, text=" User interface: ATM ", font=FB,
                              bg="white", padx=12, pady=8)
        left.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        right.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)

        # ---- left screen ----
        tk.Label(left, text="Current state", font=F, bg="white", fg="#4B5563").pack(anchor="w")
        row = tk.Frame(left, bg="white")
        row.pack(anchor="w", pady=4)
        self.pills = {}
        for s in ("qs", "q0", "qf", "qr"):
            lbl = tk.Label(row, text=NAMES[s], font=FB, padx=10, pady=4, bd=2, relief="groove")
            lbl.pack(side="left", padx=4)
            self.pills[s] = lbl

        tk.Label(left, text="Stack (top at the top)", font=F, bg="white",
                 fg="#4B5563").pack(anchor="w", pady=(12, 2))
        box = tk.Frame(left, bg="white")
        box.pack()
        self.top = tk.Label(box, font=FH, width=16, pady=10, bd=3, relief="solid",
                            bg="#DBEAFE", fg="#1D4ED8")
        self.top.pack()
        tk.Label(box, text="Z0", font=FH, width=16, pady=10, bd=3, relief="solid",
                 bg="#E5E7EB", fg="#111827").pack()

        tk.Label(left, text="Last transition", font=F, bg="white",
                 fg="#4B5563").pack(anchor="w", pady=(12, 2))
        self.last = tk.Label(left, font=F, bg="white", justify="left", anchor="w",
                             bd=2, relief="groove", padx=8, pady=6, wraplength=420)
        self.last.pack(fill="x")

        tk.Label(left, text="Trace", font=F, bg="white", fg="#4B5563").pack(anchor="w", pady=(12, 2))
        self.trace = tk.Listbox(left, font=("Arial", 12), height=7)
        self.trace.pack(fill="both", expand=True)

        # ---- right screen ----
        self.screen = tk.Label(right, font=FH, wraplength=420, justify="left",
                               anchor="w", padx=14, pady=20, highlightthickness=4)
        self.screen.pack(fill="x")

        tk.Label(right, text="Amount", font=F, bg="white", fg="#4B5563").pack(anchor="w", pady=(14, 2))
        self.amt = tk.Entry(right, font=FH, bd=2, relief="solid")
        self.amt.pack(fill="x")

        grid = tk.Frame(right, bg="white")
        grid.pack(fill="x", pady=12)
        grid.columnconfigure((0, 1), weight=1)
        self.buttons = []
        specs = [("Deposit", "#15803D", self.on_deposit),
                 ("Withdraw", "#B45309", self.on_withdraw),
                 ("Balance check", "#1D4ED8", self.on_check),
                 ("End session", "#475569", self.on_end)]
        for i, (text, color, cmd) in enumerate(specs):
            b = tk.Button(grid, text=text, font=FB, bg=color, fg="white",
                          activebackground=color, activeforeground="white",
                          pady=10, command=cmd)
            b.grid(row=i // 2, column=i % 2, sticky="ew", padx=5, pady=5)
            self.buttons.append(b)

        tk.Label(right, text="New account: initial balance B0", font=F, bg="white",
                 fg="#4B5563").pack(anchor="w", pady=(10, 2))
        row2 = tk.Frame(right, bg="white")
        row2.pack(fill="x")
        self.b0 = tk.Entry(row2, font=FH, bd=2, relief="solid")
        self.b0.insert(0, "5000")
        self.b0.pack(side="left", fill="x", expand=True)
        tk.Button(row2, text="Restart", font=FB, bg="#111827", fg="white",
                  activebackground="#111827", activeforeground="white",
                  command=self.restart).pack(side="left", padx=8)

        self.restart()

    # ---- helpers ----
    def say(self, text, kind=""):
        bg, fg, border = {"": ("#DBEAFE", "#111827", "#1D4ED8"),
                          "bad": ("#FEE2E2", "#111827", "#B91C1C"),
                          "done": ("#DCFCE7", "#111827", "#15803D")}[kind]
        self.screen.config(text=text, bg=bg, fg=fg, highlightbackground=border)

    def amount(self):
        try:
            a = int(self.amt.get())
        except ValueError:
            a = 0
        if a <= 0:
            self.say("Enter a whole amount greater than 0.", "bad")
            return None
        return a

    def finish(self, result):
        text, kind = result
        self.say(text, kind)
        self.amt.delete(0, tk.END)
        self.render()

    # ---- actions ----
    def restart(self):
        try:
            b0 = int(self.b0.get())
            if b0 < 0:
                raise ValueError
        except ValueError:
            b0 = 5000
            self.b0.delete(0, tk.END)
            self.b0.insert(0, "5000")
        self.pda = BankPDA(b0)
        self.say("Welcome. Choose an action.")
        self.render()

    def on_deposit(self):
        a = self.amount()
        if a:
            self.finish(self.pda.deposit(a))

    def on_withdraw(self):
        a = self.amount()
        if a:
            self.finish(self.pda.withdraw(a))

    def on_check(self):
        self.finish(self.pda.check())

    def on_end(self):
        self.finish(self.pda.end())

    # ---- drawing the background screen ----
    def render(self):
        p = self.pda
        for s, lbl in self.pills.items():
            if s == p.state:
                bg, fg = COLORS[s]
                lbl.config(bg=bg, fg=fg)
            else:
                lbl.config(bg="#F3F4F6", fg="#9CA3AF")
        self.top.config(text=f"X = {p.X:,}")
        edge, label, note = p.log[-1]
        self.last.config(text=f"{edge}\n{label}\n{note}".strip())
        self.trace.delete(0, tk.END)
        for e, l, n in p.log:
            self.trace.insert(tk.END, f"{e} | {l} | {n}" if l else f"{e} | {n}")
        self.trace.see(tk.END)
        live = "normal" if p.state == "q0" else "disabled"
        for b in self.buttons:
            b.config(state=live)


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1150x720")
    App(root)
    root.mainloop()
