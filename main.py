import tkinter as tk
from tkinter import messagebox
from core.map_config_loader import MapConfigLoader
from core.hint_loader import HintLoader
from core.game_engine import GameEngine
from ui.board_renderer import BoardRenderer
from actions.phase_handler import PhaseHandler
from ui.canvas_utils import pixel_to_cell_coord
from ui.image_loader import load_terrain_images
from ui.labels import generate_display_labels


def find_solution_tile(engine):
    board = engine.board
    all_coords = list(board.tiles.keys())
    players = engine.players

    # プレイヤーごとのヒントを表示
    print("\n[DEBUG] プレイヤーのヒント一覧:")
    for player in players:
        print(f"  - {player.display_name}（{player.id}）: {player.hint}")

    # 正解候補マスを探索
    solution_tiles = []
    for coord in all_coords:
        cell = board.get_tile(coord)
        applies_all = True
        for player in players:
            applies = board.apply_hint(coord, player.hint)
            if not applies:
                applies_all = False
                break
        if applies_all:
            solution_tiles.append(coord)

    # 🔍 出力
    print(f"\n[DEBUG] 正解候補マス（全ヒントに一致）:")
    for coord in solution_tiles:
        print(f"  → {coord}")


def main():
    # 1️⃣ マップ構成とヒント情報をロード
    map_loader = MapConfigLoader()
    hint_loader = HintLoader()

    # 使用マップIDとプレイヤー数を指定
    map_id = map_loader.get_available_map_ids()[1]
    player_count = 4
    board_data = map_loader.load_map(map_id)

    # プレイヤー情報を取得
    raw_players = hint_loader.get_players_for_map(map_id, player_count)

    # プレイヤー情報とヒントを取得
    player_ids = [p["id"] for p in raw_players]
    preset_colors = {
        "player1": "red",
        "player2": "green",
        "player3": "blue",
        "player4": "orange",
        "player5": "purple"
    }
    hints = [p["hint"] for p in raw_players]
    books = [p["book"] for p in raw_players]

    label_map = {p["id"]: p["id"] for p in raw_players}

    # 2️⃣ GUI初期化（Tkinterウィンドウ）
    root = tk.Tk()
    root.title("Cryptid Inspired Game")

    # 画像・サイズ・行列数の定義
    terrain_imgs = load_terrain_images()
    radius = 30
    rows = 9
    cols = 12

    # 📐 マップのピクセルサイズ計算（六角形サイズから）
    map_width_px = radius * 3/2 * cols + radius / 2
    map_height_px = radius * (3**0.5) * (rows + 1)

    # 📏 マージン（マップサイズの比率で計算）
    margin_x = int(map_width_px * 0.20)   # 左右20%
    margin_y = int(map_height_px * 0.1)  # 上下10%

    # 🎨 キャンバスサイズ（マップ＋マージン）
    canvas_width = int(map_width_px + margin_x * 2)
    canvas_height = int(map_height_px + margin_y * 2)

    # 🧃 UI領域（ラベル＋ボタン分）
    ui_padding_height = 120
    total_height = canvas_height + ui_padding_height

    # 🖼 ウィンドウサイズを明示指定（起動時点で正確に表示）
    root.geometry(f"{canvas_width}x{total_height}")

    # 🔤 ターン表示ラベル（上部配置）
    turn_label = tk.Label(root, text="", font=("Helvetica", 14))
    turn_label.pack(side=tk.TOP, pady=10)

    # 🎮 ゲームエンジン・描画エンジン初期化
    engine = GameEngine(player_ids, hints, board_data,
                        label_map, color_map=preset_colors)

    # 🕹 ゲーム状態を初期化（開始直後）
    engine.state.set_phase("active")
    engine.state.current_action = None

    find_solution_tile(engine)  # 正解候補マスを探索
    renderer = BoardRenderer(canvas=None, terrain_imgs=terrain_imgs,
                             radius=radius, margin_x=margin_x, margin_y=margin_y, player_lookup=engine.id_to_player)

    # プレイヤー情報ビュー
    info_frame = tk.Frame(root)
    info_frame.pack(side=tk.RIGHT, padx=20, pady=0)

    player_labels = {}  # プレイヤーラベルを保持する辞書

    for pid in player_ids:
        player = engine.id_to_player[pid]
        display = label_map[pid]
        label = tk.Label(
            info_frame,
            text=display,
            font=("Helvetica", 12),
            fg=player.color
        )
        label.pack(anchor="n", pady=0)
        player_labels[pid] = label

    def update_player_labels():
        current_pid = engine.state.current_player
        for pid, label in player_labels.items():
            weight = "bold" if pid == current_pid else "normal"
            label.config(font=("Helvetica", 12, weight))

    # 🖼 キャンバス生成（中央配置）
    canvas = tk.Canvas(root, width=canvas_width, height=canvas_height)
    canvas.pack(side=tk.TOP)
    renderer.canvas = canvas  # Canvasをインスタンスに再設定
    renderer.render(engine.board.tiles, rows, cols)

    # 💡 初期ターン表示
    current_pid = engine.state.current_player
    color = engine.id_to_player[current_pid].color
    turn_label.config(
        text=f"{label_map[engine.state.current_player]} のターン", fg=color)
    update_player_labels()

    # 🔀 ゲームフェーズ制御
    handler = PhaseHandler(engine, canvas, root, turn_label,
                           terrain_imgs, radius, rows, cols, renderer, update_labels=update_player_labels)

    # 🖱 クリック処理
    def on_click(event):
        coord = pixel_to_cell_coord(
            event.x, event.y, radius, margin_x=margin_x, margin_y=margin_y)
        print(f"[DEBUG] クリック座標: ({event.x}, {event.y}) → マス座標: {coord}")
        handler.handle_click(coord)

    canvas.bind("<Button-1>", on_click)

    def on_motion(event):
        coord = pixel_to_cell_coord(
            event.x, event.y, radius, margin_x=margin_x, margin_y=margin_y)
        if engine.board.is_valid_coord(coord):
            renderer.highlight_cell(coord)
        else:
            renderer.clear_highlight()

    canvas.bind("<Motion>", on_motion)

    # 🔘 質問・探索ボタン（下部配置）
    def set_phase_question():
        if engine.state.current_action == "place_cube":
            messagebox.showwarning(
                "無効な操作", "キューブ配置フェーズ中は質問フェーズに移行できません")
            print("[DEBUG] キューブ配置フェーズ中は質問フェーズに移行不可")
            return

        engine.state.current_action = "question"
        handler.update_turn_label()
        current_pid = engine.state.current_player
        color = engine.id_to_player[current_pid].color
        turn_label.config(
            text=f"{label_map[engine.state.current_player]} - 質問フェーズ", fg=color)

    def set_phase_search():
        if engine.state.current_action == "place_cube":
            messagebox.showwarning(
                "無効な操作", "キューブを置いてください")
            print("[DEBUG] キューブ配置フェーズ中は探索フェーズに移行不可")
            return

        engine.state.current_action = "search"
        handler.update_turn_label()
        current_pid = engine.state.current_player
        color = engine.id_to_player[current_pid].color
        turn_label.config(
            text=f"{label_map[engine.state.current_player]} - 探索フェーズ", fg=color)

    btn_frame = tk.Frame(root)
    btn_frame.pack(side=tk.BOTTOM, pady=10)

    question_btn = tk.Button(btn_frame, text="質問",
                             command=set_phase_question, width=10)
    search_btn = tk.Button(btn_frame, text="探索",
                           command=set_phase_search, width=10)

    question_btn.pack(side=tk.LEFT, padx=5)
    search_btn.pack(side=tk.LEFT, padx=5)

    # 🚀 メインループ開始
    root.mainloop()


if __name__ == "__main__":
    main()
