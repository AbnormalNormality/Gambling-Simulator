from tkinter import Tk, Frame, Label, StringVar
from tkinter.ttk import Button, OptionMenu, Style, Entry
from random import random
from math import floor
from datetime import datetime

from AliasTkFunctions.tkfunctions import resize_window, fix_resolution_issue, update_bg, CreateToolTip
from AliasHelpfulFunctions.generalFunctions import shorten_number

fix_resolution_issue()

main = Tk()
resize_window(main, 4, 3, False)
main.title("Gambling Simulator 2")
main.configure(background="#add8e6")
main.after_idle(lambda: update_bg(main))
main.after_idle(lambda: passive_income())

player = {
    "money": 100,
    "total_money": 100,
    "max_money": 100,
    "money_gambled": 0,
    "money_won": 0,

    "income_amount": 1,
    "income_percent": 0.00005,
    "income_delay": 100,

    "run_start": datetime.now(),
    "run_time": {"years": 0, "months": 0, "weeks": 0, "days": 0, "hours": 0, "minutes": 0, "seconds": 0, "milliseconds":
                 0},

    "gamble_cooldown": 100,
}


def gamble(amount_gambled=0, odds_of_winning=0.0, winning_modifier=2):
    if amount_gambled > player["money"] or amount_gambled == 0:
        return

    money_gained = amount_gambled

    if random() < odds_of_winning:
        money_gained *= winning_modifier
    else:
        money_gained *= -1

    update_money(money_gained)
    player["money_gambled"] += amount_gambled
    player["money_won"] += money_gained

    status_label.configure(text=f"You gambled ${amount_gambled} and {"gained" if money_gained >= 0 else "lost"} {"$" if 
                           player["money"] != 0 else ""}{"it all" if player["money"] == 0 else money_gained if 
                           money_gained >= 0 else money_gained * -1}")

    def clear_status():
        status_label.configure(text="")

    if hasattr(gamble, "after_id") and gamble.after_id:
        main.after_cancel(gamble.after_id)

    gamble.after_id = main.after(10000, clear_status)


def passive_income():
    update_money(max(player["income_amount"], floor(player["money"] * player["income_percent"])))
    main.after_idle(update_ui)
    main.after(player["income_delay"], passive_income)


# noinspection PyUnusedLocal
def disable_custom_amount(*event):
    if selected_quick_option.get() == "Custom":
        state = "normal"
    else:
        state = "disabled"

    custom_amount_entry["state"] = state
    custom_amount_label["state"] = state


def process_gamble():
    if player["gamble_cooldown"]:
        gamble_button["state"] = "disabled"

        def update_cooldown(current=0):
            if current == player["gamble_cooldown"]:
                gamble_button["state"] = "enabled"
                gamble_button.configure(text="Gamble")
            else:
                if player["gamble_cooldown"] > 10:
                    gamble_button.configure(text=f"{((player["gamble_cooldown"] - current) / 1000):.2f}")
                main.after(1, lambda: update_cooldown(current + 1))

        update_cooldown()

    if selected_quick_option.get() == "Custom":
        amount_gambled = int(custom_amount_entry.get() if custom_amount_entry.get() else 0)

    else:
        amount_gambled = floor(player["money"] * int(selected_quick_option.get().rstrip("%")) / 100)

    gamble(amount_gambled=amount_gambled, odds_of_winning=0.5)


def number_check(chars, limit):
    return (all(char.isdigit() for char in chars) or chars == "") and len(chars) <= limit


def update_ui():
    current_time = datetime.now()
    elapsed_time = current_time - player["run_start"]

    player["run_time"]["years"] = elapsed_time.days // 365
    player["run_time"]["months"] = elapsed_time.days // 30
    player["run_time"]["weeks"] = elapsed_time.days // 7
    player["run_time"]["days"] = elapsed_time.days % 7
    player["run_time"]["hours"], remainder = divmod(elapsed_time.seconds, 3600)
    player["run_time"]["minutes"], player["run_time"]["seconds"] = divmod(remainder, 60)
    player["run_time"]["milliseconds"] = elapsed_time.microseconds // 1000

    run_time_text = ""
    for i in list(player["run_time"]):
        if player["run_time"][i] or i == "seconds":
            run_time_text = f"Length: {player["run_time"][i]} {i}"
            break

    status_bar_label.configure(text=f"Total: ${shorten_number(player["money"]).upper()}  |  Highest: ${shorten_number(
                               player["money"]).upper()}  |  {run_time_text}\nGambled: ${shorten_number(player
                               ["money_gambled"]).upper()}  |  Won: ${shorten_number(player["money_won"]).upper()}")

    current_money.configure(text=f"${shorten_number(player["money"]).upper()}")


def update_money(amount):
    player["money"] = max(0, player["money"] + amount)
    player["total_money"] += max(0, amount)
    player["max_money"] = max(player["max_money"], player["money"])


status_bar = Frame(main)
status_bar.pack(side="top")
status_bar_label = Label(status_bar)
status_bar_label.pack(side="left")

current_money = Label(main, font=("TkDefaultFont", 14))
current_money.pack(side="top", pady=(5, 0))
status_label = Label(main, font=("TkDefaultFont", 10))
status_label.pack(side="top", pady=(5, 0))

Style().configure("TButton", font=("TkDefaultFont", 12))
gamble_button = Button(main, text="Gamble", command=process_gamble, width=7)
gamble_button.pack(side="bottom", pady=(10, 15))

frame = Frame()
frame.pack(side="bottom")
custom_amount_entry = Entry(frame, width=8, font=("TkDefaultFont", 11), justify="center", validate="key",
                            validatecommand=(main.register(lambda chars: number_check(chars, 7)), "%P"))
custom_amount_entry.pack(side="right")
custom_amount_entry.insert("0", "50")
custom_amount_label = Label(frame, text="$", font=("TkDefaultFont", 11))
custom_amount_label.pack(side="right")
CreateToolTip(custom_amount_label, "Game made by github.com/AbnormalNormality\nNote that I do not endorse gambling"
                                   " in any kind.", 20, 2)
quick_options = ["Custom", "10%", "25%", "50%", "100%"]
selected_quick_option = StringVar()
selected_quick_option.trace("w", disable_custom_amount)
Style().configure("TMenubutton", font=("TkDefaultFont", 11))
OptionMenu(frame, selected_quick_option, quick_options[0], *quick_options).pack(side="left", padx=(0, 10))

main.mainloop()
