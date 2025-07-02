import tkinter as tk


def create_play_layout(root, canvas_size=(1200, 900), radius=50):
    """
    プレイ画面のUIを構成するテンプレート。

    Returns:
        turn_label: ターン表示ラベル
        canvas: プレイエリアのキャンバス
        action_frame: ボタンエリア（下部）
        radius: タイルの初期サイズ
    """

    # ターン表示ラベル（上部）
    turn_label = tk.Label(root, font=("Helvetica", 16), pady=10)
    turn_label.pack()

    # プレイエリア（中央にキャンバス）
    play_area = tk.Frame(root, bg="black")
    play_area.pack(fill="both", expand=True)

    canvas = tk.Canvas(
        play_area, width=canvas_size[0], height=canvas_size[1], bg="white")
    canvas.pack(expand=True)

    # アクションボタン用フレーム（下部）
    action_frame = tk.Frame(root)
    action_frame.pack(fill="x", pady=5)

    return turn_label, canvas, action_frame, radius
