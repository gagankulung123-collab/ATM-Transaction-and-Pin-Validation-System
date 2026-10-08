import tkinter as tk

# ============================================================
# ATM PIN VALIDATION SYSTEM
# Theory of Computation - DFA Machine Demonstration
#
# Correct PIN: 1234
# Maximum attempts: 3
#
# TWO WINDOWS:
# 1. DFA / Machine Flow screen - shows states and transitions
# 2. ATM User screen - shows only the normal ATM interface
# ============================================================

CORRECT_PIN = "1234"
MAX_ATTEMPTS = 3

# DFA variables
attempt = 1
digit_count = 0
entered_pin = ""
failed = False
finished = False


# ============================================================
# MAIN WINDOW
# ============================================================

root = tk.Tk()
root.title("ATM - User Screen")
root.configure(bg="#e8edf2")
root.resizable(False, False)


# ============================================================
# DFA / MACHINE FLOW WINDOW
# ============================================================

dfa_window = tk.Toplevel(root)
dfa_window.title("DFA Machine Flow - ATM PIN Validation")
dfa_window.configure(bg="#f4f6f8")
dfa_window.resizable(False, False)


# ============================================================
# POSITION TWO WINDOWS SIDE BY SIDE
# ============================================================

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

window_width = 600
window_height = 700
gap = 20

total_width = window_width * 2 + gap
start_x = max(0, (screen_width - total_width) // 2)
start_y = max(0, (screen_height - window_height) // 2)

root.geometry(f"{window_width}x{window_height}+{start_x}+{start_y}")
dfa_window.geometry(
    f"{window_width}x{window_height}+{start_x + window_width + gap}+{start_y}"
)


# ============================================================
# USER SCREEN
# ============================================================

user_title = tk.Label(
    root,
    text="ATM",
    font=("Arial", 30, "bold"),
    bg="#e8edf2",
    fg="#17324d"
)
user_title.pack(pady=(25, 5))

user_subtitle = tk.Label(
    root,
    text="Enter your 4-digit PIN",
    font=("Arial", 18),
    bg="#e8edf2",
    fg="#394b59"
)
user_subtitle.pack(pady=(0, 20))

user_pin_frame = tk.Frame(root, bg="#e8edf2")
user_pin_frame.pack(pady=10)

user_pin_boxes = []

for _ in range(4):
    box = tk.Label(
        user_pin_frame,
        text="•",
        font=("Arial", 28, "bold"),
        width=3,
        height=1,
        bg="white",
        fg="#17324d",
        relief="solid",
        bd=1
    )
    box.pack(side="left", padx=6)
    user_pin_boxes.append(box)

user_message = tk.Label(
    root,
    text="",
    font=("Arial", 15, "bold"),
    bg="#e8edf2",
    fg="#394b59",
    wraplength=500
)
user_message.pack(pady=20)


# ============================================================
# USER KEYPAD
# ============================================================

keypad = tk.Frame(root, bg="#e8edf2")
keypad.pack(pady=10)

def make_user_button(parent, text, command, row, column):
    button = tk.Button(
        parent,
        text=text,
        command=command,
        font=("Arial", 18, "bold"),
        width=5,
        height=2,
        bg="white",
        fg="#17324d",
        activebackground="#dce8f2",
        relief="raised",
        bd=2
    )
    button.grid(row=row, column=column, padx=7, pady=7)
    return button


# ============================================================
# DFA SCREEN
# ============================================================

dfa_title = tk.Label(
    dfa_window,
    text="DFA MACHINE FLOW",
    font=("Arial", 25, "bold"),
    bg="#f4f6f8",
    fg="#17324d"
)
dfa_title.pack(pady=(18, 3))

dfa_subtitle = tk.Label(
    dfa_window,
    text="ATM PIN Validation",
    font=("Arial", 14),
    bg="#f4f6f8",
    fg="#607d8b"
)
dfa_subtitle.pack()

attempt_label = tk.Label(
    dfa_window,
    text="ATTEMPT 1 OF 3",
    font=("Arial", 15, "bold"),
    bg="#f4f6f8",
    fg="#37474f"
)
attempt_label.pack(pady=(15, 5))

# State display
state_frame = tk.Frame(
    dfa_window,
    bg="white",
    relief="solid",
    bd=1
)
state_frame.pack(fill="x", padx=25, pady=8)

current_state_title = tk.Label(
    state_frame,
    text="CURRENT DFA STATE",
    font=("Arial", 11, "bold"),
    bg="white",
    fg="#607d8b"
)
current_state_title.pack(pady=(12, 2))

current_state_label = tk.Label(
    state_frame,
    text="q1,0",
    font=("Arial", 30, "bold"),
    bg="white",
    fg="#17324d"
)
current_state_label.pack(pady=(0, 12))

# Entered digit boxes
dfa_pin_frame = tk.Frame(dfa_window, bg="#f4f6f8")
dfa_pin_frame.pack(pady=10)

dfa_pin_boxes = []

for _ in range(4):
    box = tk.Label(
        dfa_pin_frame,
        text="•",
        font=("Arial", 22, "bold"),
        width=3,
        height=1,
        bg="#e0e0e0",
        fg="#17324d",
        relief="solid",
        bd=1
    )
    box.pack(side="left", padx=5)
    dfa_pin_boxes.append(box)

# Transition explanation
transition_frame = tk.Frame(
    dfa_window,
    bg="white",
    relief="solid",
    bd=1
)
transition_frame.pack(fill="both", expand=False, padx=25, pady=10)

transition_title = tk.Label(
    transition_frame,
    text="DFA TRANSITION",
    font=("Arial", 11, "bold"),
    bg="white",
    fg="#607d8b"
)
transition_title.pack(pady=(12, 5))

transition_label = tk.Label(
    transition_frame,
    text="Waiting for input...",
    font=("Arial", 15, "bold"),
    bg="white",
    fg="#37474f",
    wraplength=500,
    justify="center"
)
transition_label.pack(padx=15, pady=(0, 15))

# Current input / result
status_label = tk.Label(
    dfa_window,
    text="Enter the first digit.",
    font=("Arial", 14, "bold"),
    bg="#f4f6f8",
    fg="#37474f",
    wraplength=530,
    justify="center"
)
status_label.pack(pady=10)

# Legend
legend = tk.Label(
    dfa_window,
    text="GREEN = correct digit     RED = wrong digit     C = clear",
    font=("Arial", 10),
    bg="#f4f6f8",
    fg="#607d8b"
)
legend.pack(pady=(2, 10))


# ============================================================
# DFA / USER DISPLAY UPDATE FUNCTIONS
# ============================================================

def get_state():
    """
    Returns the state that should be displayed.

    q1,0 = before the first digit
    q1,1 = first digit was correct
    q'1,1 = first digit was wrong
    q1,2 = first two digits were correct
    q'1,2 = a wrong digit has already occurred and two digits read
    etc.
    """

    if digit_count == 0:
        return f"q{attempt},0"

    if failed:
        return f"q'{attempt},{digit_count}"

    return f"q{attempt},{digit_count}"


def update_pin_boxes():
    # Update user screen
    for i, box in enumerate(user_pin_boxes):
        if i < len(entered_pin):
            box.config(text="●")
        else:
            box.config(text="•")

    # Update DFA screen
    for i, box in enumerate(dfa_pin_boxes):
        if i < len(entered_pin):
            box.config(text=entered_pin[i])
        else:
            box.config(text="•")


def reset_digit_colors():
    for box in dfa_pin_boxes:
        box.config(bg="#e0e0e0", fg="#17324d")


def set_digit_color(index, correct):
    if 0 <= index < 4:
        if correct:
            dfa_pin_boxes[index].config(
                bg="#b9f6b5",
                fg="#146b1e"
            )
        else:
            dfa_pin_boxes[index].config(
                bg="#ffc4c4",
                fg="#a50000"
            )


def update_state_display():
    current_state_label.config(text=get_state())
    attempt_label.config(text=f"ATTEMPT {attempt} OF {MAX_ATTEMPTS}")


# ============================================================
# PIN PROCESSING - THIS IS THE DFA LOGIC
# ============================================================

def enter_digit(digit):
    global attempt, digit_count, entered_pin, failed, finished

    if finished:
        return

    # A PIN can contain only 4 digits per attempt
    if digit_count >= 4:
        return

    # Add the input digit
    entered_pin += digit
    digit_count += 1

    # Compare this digit with the correct PIN
    position = digit_count - 1
    correct = digit == CORRECT_PIN[position]

    # Highlight digit
    set_digit_color(position, correct)

    if correct:
        # ----------------------------------------------------
        # CORRECT TRANSITION
        # ----------------------------------------------------
        if failed:
            # This situation is possible after a previous wrong
            # digit. The attempt remains failed.
            pass
        else:
            transition_label.config(
                text=(
                    f"The number {digit} is CORRECT.\n"
                    f"Moving to state q{attempt},{digit_count}."
                ),
                fg="#146b1e"
            )

            status_label.config(
                text=f"✓ Digit {digit} is correct.",
                fg="#146b1e"
            )
    else:
        # ----------------------------------------------------
        # WRONG TRANSITION
        # ----------------------------------------------------
        failed = True

        transition_label.config(
            text=(
                f"The number {digit} is INCORRECT.\n"
                f"Moving to state q'{attempt},{digit_count}."
            ),
            fg="#a50000"
        )

        status_label.config(
            text=f"✗ Digit {digit} is incorrect. This attempt has failed.",
            fg="#a50000"
        )

    update_pin_boxes()
    update_state_display()

    # --------------------------------------------------------
    # FOURTH DIGIT: DETERMINE FINAL RESULT OF THIS ATTEMPT
    # --------------------------------------------------------
    if digit_count == 4:
        root.after(700, finish_attempt)


def finish_attempt():
    global attempt, digit_count, entered_pin, failed, finished

    if not failed:
        # ----------------------------------------------------
        # ACCEPTING STATE
        # ----------------------------------------------------
        finished = True

        current_state_label.config(text="qf")
        transition_label.config(
            text="PIN CORRECT!\nMoving to accepting state qf.",
            fg="#146b1e"
        )

        status_label.config(
            text="✓ PIN CORRECT — CARD UNLOCKED",
            fg="#146b1e"
        )

        user_message.config(
            text="PIN CORRECT\nCard unlocked.\nContinue with transaction.",
            fg="#146b1e"
        )

        disable_keypad()

    else:
        # ----------------------------------------------------
        # FAILED ATTEMPT
        # ----------------------------------------------------
        if attempt < MAX_ATTEMPTS:

            transition_label.config(
                text=(
                    "PIN INCORRECT.\n"
                    "This attempt is complete.\n"
                    "Moving to the next attempt."
                ),
                fg="#a50000"
            )

            status_label.config(
                text="✗ PIN INCORRECT — GOING TO NEXT ATTEMPT",
                fg="#a50000"
            )

            user_message.config(
                text=f"Incorrect PIN.\nAttempt {attempt} failed.\nPlease try again.",
                fg="#a50000"
            )

            # Wait briefly so the audience can see the result
            root.after(1300, start_next_attempt)

        else:
            # ------------------------------------------------
            # LOCKED STATE
            # ------------------------------------------------
            finished = True

            current_state_label.config(text="q_lock")
            transition_label.config(
                text=(
                    "PIN INCORRECT.\n"
                    "3 attempts completed.\n"
                    "Moving to q_lock."
                ),
                fg="#a50000"
            )

            status_label.config(
                text="CARD LOCKED",
                fg="#a50000"
            )

            user_message.config(
                text="CARD LOCKED\n3 attempts done.\nPlease contact your bank.",
                fg="#a50000"
            )

            disable_keypad()


def start_next_attempt():
    global attempt, digit_count, entered_pin, failed

    attempt += 1
    digit_count = 0
    entered_pin = ""
    failed = False

    reset_digit_colors()
    update_pin_boxes()
    update_state_display()

    current_state_label.config(text=f"q{attempt},0")

    transition_label.config(
        text=(
            f"Attempt {attempt} started.\n"
            f"Initial state: q{attempt},0"
        ),
        fg="#37474f"
    )

    status_label.config(
        text="Enter the first digit.",
        fg="#37474f"
    )

    user_message.config(
        text=f"Attempt {attempt} of {MAX_ATTEMPTS}\nEnter your PIN.",
        fg="#394b59"
    )


# ============================================================
# CLEAR BUTTON
# ============================================================

def clear_current_pin():
    global digit_count, entered_pin, failed

    if finished:
        return

    digit_count = 0
    entered_pin = ""
    failed = False

    reset_digit_colors()
    update_pin_boxes()
    update_state_display()

    transition_label.config(
        text=(
            "CLEAR pressed.\n"
            f"Returning to initial state q{attempt},0."
        ),
        fg="#37474f"
    )

    status_label.config(
        text="PIN entry cleared. Enter the first digit.",
        fg="#37474f"
    )

    user_message.config(
        text=f"Attempt {attempt} of {MAX_ATTEMPTS}\nEnter your PIN.",
        fg="#394b59"
    )


# ============================================================
# RESET EVERYTHING
# ============================================================

def reset_system():
    global attempt, digit_count, entered_pin, failed, finished

    attempt = 1
    digit_count = 0
    entered_pin = ""
    failed = False
    finished = False

    reset_digit_colors()
    update_pin_boxes()
    update_state_display()

    current_state_label.config(text="q1,0")

    transition_label.config(
        text="System reset.\nInitial state: q1,0",
        fg="#37474f"
    )

    status_label.config(
        text="Enter the first digit.",
        fg="#37474f"
    )

    user_message.config(
        text="Enter your 4-digit PIN",
        fg="#394b59"
    )

    enable_keypad()


# ============================================================
# KEYPAD BUTTONS
# ============================================================

button_commands = {}

for number in range(1, 10):
    button_commands[str(number)] = lambda n=str(number): enter_digit(n)

button_commands["0"] = lambda: enter_digit("0")

for number in range(1, 10):
    row = (number - 1) // 3
    column = (number - 1) % 3
    make_user_button(
        keypad,
        str(number),
        button_commands[str(number)],
        row,
        column
    )

make_user_button(
    keypad,
    "C",
    clear_current_pin,
    3,
    0
)

make_user_button(
    keypad,
    "0",
    button_commands["0"],
    3,
    1
)

make_user_button(
    keypad,
    "Reset",
    reset_system,
    3,
    2
)


# ============================================================
# ENABLE / DISABLE KEYPAD
# ============================================================

def enable_keypad():
    for child in keypad.winfo_children():
        child.config(state="normal")


def disable_keypad():
    for child in keypad.winfo_children():
        child.config(state="disabled")


# ============================================================
# INITIAL STATE
# ============================================================

update_pin_boxes()
update_state_display()

root.protocol("WM_DELETE_WINDOW", root.destroy)
dfa_window.protocol("WM_DELETE_WINDOW", root.destroy)

root.mainloop()
