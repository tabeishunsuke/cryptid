import tkinter as tk


def create_play_layout(root, canvas_size=(1200, 900), radius=50):
    """
    プレイ画面のUI要素（ラベル・キャンバス・ボタンエリア）を構築する。

    Args:
        root: Tkinterのルートウィンドウ
        canvas_size: 初期キャンバスサイズ (width, height)
        radius: タイル半径（初期値）

    Returns:
        turn_label: ターン表示ラベル（Tk.Label）
        canvas: メインプレイ領域のキャンバス
        action_frame: アクションボタン用フレーム（下部）
        radius: タイル半径
    """

    # ターン表示ラベル（上部）
    turn_label = tk.Label(root, font=("Helvetica", 16), pady=10)
    turn_label.pack()

    # プレイエリア（中央にキャンバスを配置）
    play_area = tk.Frame(root, bg="black")
    play_area.pack(fill="both", expand=True)

    canvas = tk.Canvas(
        play_area,
        width=canvas_size[0],
        height=canvas_size[1],
        bg="white"
    )
    canvas.pack(expand=True)

    # アクションボタン領域（下部に配置）
    action_frame = tk.Frame(root)
    action_frame.pack(fill="x", pady=5)

    return turn_label, canvas, action_frame, radius
