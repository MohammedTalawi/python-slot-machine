import random
import tkinter as tk
from tkinter import messagebox

ROWS = 3
COLS = 5

MIN_DEPOSIT = 10
MIN_BET = 1
MAX_BET = 100

BG = "#111111"
PANEL = "#1f1f1f"
TEXT = "#f5f5f5"
GOLD = "#d4af37"
RED = "#b30000"
GREEN = "#00aa55"
CELL_BG = "#2b2b2b"
WIN_BG = "#ffd700"

SYMBOLS = {
    "7": {"count": 2, "payout": 50},
    "BAR": {"count": 3, "payout": 25},
    "DIAM": {"count": 4, "payout": 15},
    "BELL": {"count": 5, "payout": 10},
    "STAR": {"count": 6, "payout": 7},
    "CHERRY": {"count": 8, "payout": 5},
    "LEMON": {"count": 10, "payout": 3},
}

PAYLINES = [
    ("Top row", [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4)]),
    ("Middle row", [(1, 0), (1, 1), (1, 2), (1, 3), (1, 4)]),
    ("Bottom row", [(2, 0), (2, 1), (2, 2), (2, 3), (2, 4)]),
    ("V diagonal", [(0, 0), (1, 1), (2, 2), (1, 3), (0, 4)]),
    ("Inverted V diagonal", [(2, 0), (1, 1), (0, 2), (1, 3), (2, 4)]),
]

balance = 0
last_win = 0


def build_reel():
    reel = []
    for symbol, data in SYMBOLS.items():
        reel.extend([symbol] * data["count"])
    return reel


def spin_reels():
    reel = build_reel()
    return [[random.choice(reel) for _ in range(COLS)] for _ in range(ROWS)]


def evaluate(machine, bet):
    total_win = 0
    winning_lines = []
    winning_positions = set()

    for line_name, positions in PAYLINES:
        line_symbols = [machine[row][col] for row, col in positions]
        first_symbol = line_symbols[0]
        matches = 1

        for symbol in line_symbols[1:]:
            if symbol == first_symbol:
                matches += 1
            else:
                break

        if matches >= 3:
            win = bet * SYMBOLS[first_symbol]["payout"] * (matches - 2)
            total_win += win
            winning_lines.append(f"{line_name}: {matches}x {first_symbol} = +{win} €")

            for i in range(matches):
                winning_positions.add(positions[i])

    return total_win, winning_lines, winning_positions


def update_balance():
    balance_label.config(text=f"Balance: {balance} €")


def reset_slot_colors():
    for row in range(ROWS):
        for col in range(COLS):
            slot_labels[row][col].config(bg=CELL_BG, fg=TEXT)


def show_machine(machine):
    for row in range(ROWS):
        for col in range(COLS):
            slot_labels[row][col].config(text=machine[row][col])


def deposit_money():
    global balance

    try:
        amount = int(deposit_entry.get())
    except ValueError:
        messagebox.showerror("Error", "Enter a valid deposit amount.")
        return

    if amount < MIN_DEPOSIT:
        messagebox.showerror("Error", f"Minimum deposit is {MIN_DEPOSIT} €.")
        return

    balance += amount
    update_balance()
    deposit_entry.delete(0, tk.END)
    spin_button.config(state="normal")
    status_label.config(text="Deposit accepted. You can spin now.", fg=GREEN)


def spin():
    global balance, last_win

    try:
        bet = int(bet_entry.get())
    except ValueError:
        messagebox.showerror("Error", "Enter a valid bet.")
        return

    if bet < MIN_BET or bet > MAX_BET:
        messagebox.showerror("Error", f"Bet must be between {MIN_BET} and {MAX_BET} €.")
        return

    if bet > balance:
        messagebox.showerror("Error", "Not enough balance.")
        return

    balance -= bet
    update_balance()
    reset_slot_colors()

    spin_button.config(state="disabled")
    status_label.config(text="Spinning...", fg=GOLD)

    for _ in range(20):
        temp_machine = spin_reels()
        show_machine(temp_machine)
        window.update()
        window.after(70)

    machine = spin_reels()
    show_machine(machine)

    winnings, winning_lines, winning_positions = evaluate(machine, bet)

    for row, col in winning_positions:
        slot_labels[row][col].config(bg=WIN_BG, fg="black")

    balance += winnings
    last_win = winnings
    update_balance()
    last_win_label.config(text=f"Last win: {last_win} €")

    result_text.config(state="normal")
    result_text.delete("1.0", tk.END)

    if winnings > 0:
        status_label.config(text="WIN!", fg=GOLD)
        result_text.insert(tk.END, "\n".join(winning_lines))
    else:
        status_label.config(text="No win. Try again.", fg=RED)
        result_text.insert(tk.END, "No winning line.")

    result_text.config(state="disabled")

    if balance >= MIN_BET:
        spin_button.config(state="normal")
    else:
        messagebox.showinfo("Game Over", "Your balance is too low. Deposit more money.")


window = tk.Tk()
window.title("Realistic Python Slot Machine")
window.geometry("950x700")
window.resizable(False, False)
window.config(bg=BG)

title = tk.Label(
    window,
    text="REALISTIC SLOT MACHINE",
    font=("Arial", 28, "bold"),
    bg=BG,
    fg=GOLD,
)
title.pack(pady=15)

top_frame = tk.Frame(window, bg=BG)
top_frame.pack(pady=5)

balance_label = tk.Label(top_frame, text="Balance: 0 €", font=("Arial", 18, "bold"), bg=BG, fg=TEXT)
balance_label.grid(row=0, column=0, padx=25)

last_win_label = tk.Label(top_frame, text="Last win: 0 €", font=("Arial", 18), bg=BG, fg=TEXT)
last_win_label.grid(row=0, column=1, padx=25)

slot_frame = tk.Frame(window, bg=GOLD, bd=6, relief="ridge")
slot_frame.pack(pady=25)

slot_labels = []

for row in range(ROWS):
    row_labels = []
    for col in range(COLS):
        label = tk.Label(
            slot_frame,
            text="?",
            font=("Arial", 24, "bold"),
            width=7,
            height=2,
            bg=CELL_BG,
            fg=TEXT,
            relief="groove",
            bd=3,
        )
        label.grid(row=row, column=col, padx=5, pady=5)
        row_labels.append(label)
    slot_labels.append(row_labels)

control_frame = tk.Frame(window, bg=BG)
control_frame.pack(pady=10)

deposit_label = tk.Label(control_frame, text="Deposit:", font=("Arial", 14), bg=BG, fg=TEXT)
deposit_label.grid(row=0, column=0, padx=5)

deposit_entry = tk.Entry(control_frame, font=("Arial", 14), width=10, justify="center")
deposit_entry.grid(row=0, column=1, padx=5)

deposit_button = tk.Button(
    control_frame,
    text="Deposit Money",
    font=("Arial", 14, "bold"),
    bg=GREEN,
    fg="white",
    command=deposit_money,
)
deposit_button.grid(row=0, column=2, padx=10)

bet_label = tk.Label(control_frame, text="Bet per spin:", font=("Arial", 14), bg=BG, fg=TEXT)
bet_label.grid(row=1, column=0, padx=5, pady=10)

bet_entry = tk.Entry(control_frame, font=("Arial", 14), width=10, justify="center")
bet_entry.insert(0, "10")
bet_entry.grid(row=1, column=1, padx=5)

spin_button = tk.Button(
    control_frame,
    text="SPIN",
    font=("Arial", 18, "bold"),
    width=12,
    bg=GOLD,
    fg="black",
    command=spin,
    state="disabled",
)
spin_button.grid(row=1, column=2, padx=10)

status_label = tk.Label(window, text="Deposit money to start.", font=("Arial", 16, "bold"), bg=BG, fg=TEXT)
status_label.pack(pady=15)

result_text = tk.Text(window, width=60, height=5, font=("Arial", 12), bg=PANEL, fg=TEXT)
result_text.pack(pady=10)
result_text.insert(tk.END, "Winning lines will appear here.")
result_text.config(state="disabled")

paytable = tk.Label(
    window,
    text="Paytable: 7=x50 | BAR=x25 | DIAM=x15 | BELL=x10 | STAR=x7 | CHERRY=x5 | LEMON=x3",
    font=("Arial", 12),
    bg=BG,
    fg=TEXT,
)
paytable.pack(pady=5)

window.mainloop()