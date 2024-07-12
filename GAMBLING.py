from tkinter import Tk, Frame, Entry, Label
from tkinter.ttk import Button, Style
import random

from ctypes import windll
windll.shcore.SetProcessDpiAwareness(1)

main = Tk()
screenWidth, screenHeight = main.winfo_screenwidth(), main.winfo_screenheight()
mainWidth, mainHeight = int(screenWidth // 4), int(screenHeight // 3)
main.geometry(f"{mainWidth}x{mainHeight}+{(screenWidth - mainWidth) // 2}+{(screenHeight - mainHeight) // 2}")
main.configure(background="light blue")
style = Style()
style.configure("TButton", font=("aptos", 10))
style.configure("TButton", background="light blue")


def gamble(g=True):
    global money
    gambled = int(entry.get()) if entry.get().strip() else 0
    if gambled > money:
        return
    gained = -gambled
    if g:
        if not random.randint(1, double_chance) - 1:
            gained *= -1  # Double what you gambled
        info_label.configure(text=f"${gambled} gambled, ${gained * (1 if gained >= 0 else -1)} {"gained" if gained >= 0 else "lost"}")
        money += gained
    money_label.configure(text=f"You have ${money}")


def tick():
    global money
    money += 1
    money_label.configure(text=f"You have ${money}")
    main.after(tick_rate, tick)


def only_numbers(chars):
    return (all(char.isdigit() for char in chars) or chars == "") and len(chars) <= 7


money = 100
double_chance = 2
frame = Frame(main)
frame.pack(side="bottom", pady=10)
frame.configure(background="light blue")
Label(frame, text="$", font=("aptos", 10), background="light blue").pack(side="left")
entry = Entry(frame, width=7, font=("aptos", 10), validate="key", validatecommand=(main.register(only_numbers), "%P"),
              justify="center")
entry.pack(side="left")
entry.insert("0", f"{money // 2}")
Button(frame, text=f"Gamble 1/{double_chance}%", command=gamble).pack(side="left", padx=10)
money_label = Label(main, font=("aptos", 12), background="light blue")
money_label.pack(side="top", pady=10)
info_label = Label(main, font=("aptos", 10), background="light blue")
info_label.pack(side="top", pady=10)
gamble(False)
tick_rate = 100
main.after(tick_rate, tick)

main.mainloop()
