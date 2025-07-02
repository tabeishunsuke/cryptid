import tkinter as tk


def ask_player_selection(valid_display_names):
    selected = [None]

    def confirm():
        selected[0] = var.get()
        top.destroy()

    top = tk.Toplevel()
    top.title("質問相手を選択")
    tk.Label(top, text="誰に質問しますか？").pack(padx=20, pady=(10, 5))

    var = tk.StringVar()
    var.set(valid_display_names[0])
    tk.OptionMenu(top, var, *valid_display_names).pack(padx=10)
    tk.Button(top, text="OK", command=confirm).pack(pady=10)

    top.transient()
    top.grab_set()
    top.wait_window()
    return selected[0]
