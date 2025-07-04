import tkinter as tk


def ask_player_selection(valid_display_names):
    """
    質問対象プレイヤーを選択するためのダイアログを表示。

    Args:
        valid_display_names: 選択候補となるプレイヤー表示名のリスト

    Returns:
        str or None: 選択されたプレイヤー名（キャンセル時は None）
    """
    selected = [None]  # リストでラップすることで内部関数から代入可能にする

    def confirm():
        selected[0] = var.get()
        top.destroy()

    top = tk.Toplevel()
    top.title("質問相手を選択")
    tk.Label(top, text="誰に質問しますか？").pack(padx=20, pady=(10, 5))

    var = tk.StringVar()
    var.set(valid_display_names[0])  # 初期選択

    tk.OptionMenu(top, var, *valid_display_names).pack(padx=10)
    tk.Button(top, text="OK", command=confirm).pack(pady=10)

    # モーダル化（親画面をロック）
    top.transient()
    top.grab_set()
    top.wait_window()

    return selected[0]
