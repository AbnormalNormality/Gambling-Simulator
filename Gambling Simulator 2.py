from tkinter import Tk, Frame, Label, StringVar, messagebox, Scale, DoubleVar, Canvas
from tkinter.ttk import Button, OptionMenu, Style, Entry, Scrollbar
from random import random
from math import floor, ceil
from datetime import datetime
from json import loads, dumps
from os.path import exists
from copy import deepcopy
from base64 import b64decode, b64encode

from AliasTkFunctions.tkfunctions import resize_window, fix_resolution_issue, update_bg, CreateToolTip
from AliasHelpfulFunctions.generalFunctions import shorten_number

fix_resolution_issue()

main = Tk()
resize_window(main, 4, 3, False)
main.wm_resizable(False, False)
main.title("Gambling Simulator 2")
main.configure(background="#beefff")
main.after_idle(lambda: update_bg(main))
main.after_idle(lambda: update_ui(can_loop=True))

player = {
    # Linked to current run
    "money": 100,  # Money
    "total_money": 100,
    "max_money": 100,
    "money_gambled": 0,
    "money_won": 0,

    "run_start": datetime.now(),  # Time
    "run_time": {"years": 0, "months": 0, "weeks": 0, "days": 0, "hours": 0, "minutes": 0, "seconds": 0, "milliseconds":
                 0},

    "luck": 1,  # Modifiers
    "reward_multiplier": 1,

    "upgrades": {},
    "tables": {
        "Standard": {"tooltip": "1 in 4 chance to double your money.", "odds": 1 / 4, "reward": 2, "minimum": 0,
                     "unlocked": False, "cost": 0},
        "Standard 2": {"tooltip": "1 in 16 chance to triple your money.", "odds": 1 / 16, "reward": 3, "minimum": 0,
                       "unlocked": False, "cost": 400}
    },

    "marriage_status": DoubleVar(value=50),

    # Permanent across all runs
    "total_start": datetime.now(),  # Time
    "total_time": {"years": 0, "months": 0, "weeks": 0, "days": 0, "hours": 0, "minutes": 0, "seconds": 0,
                   "milliseconds": 0},

    "ascensions": 0,  # Ascensions
    "ascension_points": 0,
    "total_points": 0,
    "point_goal": 1000000000000,

    "permanent_upgrades": {},

    # Variable
    "income_amount": 1,  # Income
    "income_percent": 0.00005,
    "income_delay": 2000,

    "gamble_cooldown": 0,
}

default_player = deepcopy(player)

if exists("gambling_save.json"):
    base64_str = open("gambling_save.json", "r").read()
    json_bytes = b64decode(base64_str.encode('utf-8'))
    json_str = json_bytes.decode('utf-8')
    loaded_data = loads(json_str)

    for key, value in loaded_data.items():
        if key in ["run_start", "total_start"]:
            player[key] = datetime.fromisoformat(value)
        else:
            player[key] = value


def gamble(amount_gambled=0, odds_of_winning=0.0, winning_modifier=0, minimum=0):
    if amount_gambled > player["money"] or amount_gambled == 0 or amount_gambled < minimum:
        return

    money_gained = amount_gambled

    if random() < odds_of_winning * player["luck"]:
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

    odds_of_winning = player["tables"][selected_table.get()]["odds"]
    winning_modifier = player["tables"][selected_table.get()]["reward"]

    if selected_quick_option.get() == "Custom":
        amount_gambled = int(custom_amount_entry.get() if custom_amount_entry.get() else 0)

    else:
        amount_gambled = floor(player["money"] * int(selected_quick_option.get().rstrip("%")) / 100)

    gamble(amount_gambled=amount_gambled, odds_of_winning=odds_of_winning, winning_modifier=winning_modifier,
           minimum=player["tables"][selected_table.get()]["minimum"])


def number_check(chars, limit):
    return (all(char.isdigit() for char in chars) or chars == "") and len(chars) <= limit


def update_ui(can_loop=False):
    for x in ["run", "total"]:
        current_time = datetime.now()
        elapsed_time = current_time - player[f"{x}_start"]

        player[f"{x}_time"]["years"] = elapsed_time.days // 365
        player[f"{x}_time"]["months"] = elapsed_time.days // 30
        player[f"{x}_time"]["weeks"] = elapsed_time.days // 7
        player[f"{x}_time"]["days"] = elapsed_time.days % 7
        player[f"{x}_time"]["hours"], remainder = divmod(elapsed_time.seconds, 3600)
        player[f"{x}_time"]["minutes"], player[f"{x}_time"]["seconds"] = divmod(remainder, 60)
        player[f"{x}_time"]["milliseconds"] = elapsed_time.microseconds // 1000

    run_time_text = ""
    for i in list(player["run_time"]):
        if player["run_time"][i] or i == "seconds":
            run_time_text = f"{player["run_time"][i]} {i}"
            break

    total_time_text = ""
    for i in list(player["total_time"]):
        if player["total_time"][i] or i == "seconds":
            total_time_text = f"{player["total_time"][i]} {i}"
            break

    status_bar_label.configure(text=f"Total: ${shorten_number(player["total_money"]).upper()}  |  Highest: ${
                                    shorten_number(player["max_money"]).upper()}  |  {run_time_text}\nGambled: ${
                                    shorten_number(player["money_gambled"]).upper()}  |  Won: ${
                                    shorten_number(player["money_won"]).upper()}  |  Luck modifier: {player["luck"]}")

    current_money.configure(text=f"${shorten_number(player["money"]).upper()}")

    if player["ascension_points"] >= 1 or player["ascensions"] >= 1:
        prestige_button["state"] = "normal"
    else:
        prestige_button["state"] = "disabled"

    stats.configure(text=f"Legacy started {run_time_text} ago\n"
                         f"Run started {total_time_text} ago\n"
                         f""f"Total: ${shorten_number(player["total_money"]).upper()}\n"
                         f"Highest: ${shorten_number(player["max_money"]).upper()}\n"
                         f"Gambled: ${shorten_number(player["money_gambled"]).upper()}\n"
                         f"Won: ${shorten_number(player["money_won"]).upper()}\n"
                         f"Ascensions: {shorten_number(player["ascensions"]).upper()}\n"
                         f"Ascend Points: {shorten_number(player["ascension_points"]).upper()}\n"
                         f"Total points: {shorten_number(player["total_points"]).upper()}\n"
                         f"Next point: ${shorten_number(player["point_goal"]).upper()}")

    if can_loop:
        main.after(min(player["income_delay"], 1000), lambda: update_ui(can_loop=True))


def update_money(amount):
    amount *= player["reward_multiplier"]
    if player["total_points"] > 0:
        amount += floor(player["money"] * player["total_points"] / 100)

    player["money"] = max(0, player["money"] + amount)
    player["total_money"] += max(0, amount)
    player["max_money"] = max(player["max_money"], player["money"])
    main.after_idle(update_ui)

    while player["total_money"] >= player["point_goal"]:
        player["ascension_points"] += 1
        player["point_goal"] += ceil(player["point_goal"] * 1.15)


def save():
    save_data = deepcopy(player)

    for k in ["income_amount", "income_percent", "income_delay", "gamble_cooldown"]:
        del save_data[k]

    def datetime_serializer(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")

    open("gambling_save.json", "w").write(b64encode(dumps(save_data, default=datetime_serializer, indent=4).encode(
         "utf-8")).decode("utf-8"))

    exit()


# noinspection SpellCheckingInspection
def ascend(reset=False):
    global player
    if not reset:
        if messagebox.askokcancel(main.title(), f"Prestiging will reset your money to 100\nand reset your current "
                                                f"run time.\nAre you sure you want to prestige?\n\nPrestige level "
                                                f"{player["ascension_points"]}\nCurrent prestige modifier {
                                                floor(player["total_points"] / 100)}"):
            player.update({
                "money": 100,
                "total_money": 100,
                "max_money": 100,
                "money_gambled": 0,
                "money_won": 0,

                "run_start": datetime.now(),
                "run_time": {"years": 0, "months": 0, "weeks": 0, "days": 0, "hours": 0, "minutes": 0, "seconds": 0,
                             "milliseconds":
                                 0},

                "luck": 1,
                "reward_multiplier": 1,

                "upgrades": {},

                "tables": {k: {**v, "unlocked": False} for k, v in player["tables"].items()},

                "ascensions": player["ascensions"] + 1,
                "ascension_points": 0,
                "total_points": player["total_points"] + player["ascension_points"]
            })
    else:
        if messagebox.askokcancel(main.title(), "Resetting will delete all progress.\nAre you sure?"):
            if messagebox.askokcancel(main.title(), "Progress cannot be recovered after resetting.\nAre you sure?"):
                player = deepcopy(default_player)
                player.update({
                    "run_start": datetime.now(),
                    "total_start": datetime.now()
                })

    update_table()
    update_ui()


# noinspection PyUnusedLocal
def update_table(*event):
    CreateToolTip(table_menu, f"{player["tables"][selected_table.get()]["tooltip"]}\n${
                  player["tables"][selected_table.get()]["minimum"]} minimum", 130, 2)

    if player["tables"][selected_table.get()]["unlocked"] is False:
        gamble_button.configure(text="Buy", command=purchase_table)
        table_label.configure(text=f"Table (${shorten_number(player['tables'][selected_table.get()]['cost']).upper()})")
    else:
        gamble_button.configure(text="Gamble", command=process_gamble)
        table_label.configure(text="Table")


def resize_inner_frame(event):
    canvas_width = event.width
    canvas.itemconfig(canvas_window, width=canvas_width)
    canvas.configure(scrollregion=canvas.bbox("all"))


def purchase_table():
    if player["money"] >= player["tables"][selected_table.get()]["cost"]:
        player["money"] -= player["tables"][selected_table.get()]["cost"]
        player["tables"][selected_table.get()]["unlocked"] = True
    update_table()


main.after_idle(passive_income)
main.protocol("WM_DELETE_WINDOW", save)

# Money labels
status_bar = Frame(main)
status_bar.pack(side="top")
status_bar_label = Label(status_bar)
status_bar_label.pack(side="left")

current_money = Label(main, font=("TkDefaultFont", 14))
current_money.pack(side="top", pady=(5, 0))
status_label = Label(main, font=("TkDefaultFont", 10))
status_label.pack(side="top", pady=(5, 0))

Label(main, text="↓ ↓ ↓", font=("TkDefaultFont", 10)).pack(side="bottom", pady=(0, 5))

# Scrolling frame
frame = Frame(main)
frame.pack(side="top", fill="both", expand=True)
frame.pack_propagate(False)
canvas = Canvas(frame, highlightthickness=0)
canvas.grid(row=0, column=0, sticky="nsew")
scrollbar = Scrollbar(frame, orient="vertical", command=canvas.yview)
canvas.configure(yscrollcommand=scrollbar.set)
frame.grid_rowconfigure(0, weight=1)
frame.grid_columnconfigure(0, weight=1)
canvas_frame = Frame(canvas)
canvas_window = canvas.create_window((0, 0), window=canvas_frame, anchor="nw")
canvas.bind("<Configure>", resize_inner_frame)
canvas_frame.bind("<Configure>", lambda event: canvas.configure(scrollregion=canvas.bbox("all")))
canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(-1 if event.delta > 0 else 1, "units"))

# Tables list
frame = Frame(canvas_frame)
frame.pack(side="top", pady=(80, 0))
selected_table = StringVar()
table_menu = OptionMenu(frame, selected_table, list(player["tables"])[0], *list(player["tables"]))
table_menu.pack(side="left", padx=(0, 10))
table_label = Label(frame, text="Table", font=("TkDefaultFont", 11))
table_label.pack(side="left")

# Gambling amounts
frame = Frame(canvas_frame)
frame.pack(side="top")
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
OptionMenu(frame, selected_quick_option, quick_options[0], *quick_options).pack(side="left", padx=10)

# Gambling button
frame = Frame(canvas_frame)
frame.pack(side="top", pady=10)
Style().configure("TButton", font=("TkDefaultFont", 12))
gamble_button = Button(frame, text="Gamble", command=process_gamble, width=7)
gamble_button.pack(side="left")

# Finalise table list
selected_table.trace("w", update_table)
update_table()

# Prestige buttons
Style().configure("small.TButton", font=("TkDefaultFont", 10))
prestige_button = Button(canvas_frame, text="Prestige", command=ascend, width=8, style="small.TButton", state="disabled")
prestige_button.pack(side="top")
Style().configure("red.small.TButton", font=("TkDefaultFont", 10), foreground="#cc0000")
Button(canvas_frame, text="Reset", command=lambda: ascend(reset=True), width=8, style="red.small.TButton").pack(
    side="bottom", pady=5)

# Stats
stats = Label(canvas_frame, justify="left")
stats.pack(side="bottom")
Label(canvas_frame, text="Stats", font=("TkDefaultFont", 12, "underline")).pack(side="bottom", pady=(10, 5))

main.mainloop()
