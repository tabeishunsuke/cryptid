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
    map_id = map_loader.get_available_map_ids()[10]
    player_count = 5
    board_data = map_loader.load_map(map_id)

    # プレイヤー情報を取得
    raw_players = hint_loader.get_players_for_map(map_id, player_count)

    # プレイヤー情報とヒントを取得
    player_ids = [p["id"] for p in raw_players]
    preset_colors = {
        "player1": "firebrick2",
        "player2": "aquamarine",
        "player3": "HotPink",
        "player4": "chocolate1",
        "player5": "dark magenta",
    }
    hints = [p["hint"] for p in raw_players]
    label_map = {p["id"]: p["id"] for p in raw_players}

    # 2️⃣ GUI初期化（Tkinterウィンドウ）
    bg_color = "gray15"
    root = tk.Tk()
    root.title("Cryptid")
    root.configure(bg=bg_color)

    # 画像・サイズ・行列数の定義
    terrain_imgs = load_terrain_images()
    radius = 50
    rows = 9
    cols = 12

    # 📐 マップのピクセルサイズ計算（六角形サイズから）
    map_width_px = radius * 3/2 * cols + radius / 2
    map_height_px = radius * (3**0.5) * (rows + 1)

    # 📏 マージン（マップサイズの比率で計算）
    margin_x = int(map_width_px * 0.1)   # 左右20%
    margin_y = int(map_height_px * 0.1)  # 上下10%

    # 🎨 キャンバスサイズ（マップ＋マージン）
    canvas_width = int(map_width_px + margin_x)
    canvas_height = int(map_height_px + margin_y)
    info_frame_width = 200  # ボタン＋プレイヤーラベルの横幅
    total_width = canvas_width + info_frame_width

    # 🧃 UI領域（ラベル＋ボタン分）
    ui_padding_height = 0
    total_height = canvas_height + ui_padding_height

    # 🖼 ウィンドウサイズを明示指定（起動時点で正確に表示）
    root.geometry(f"{total_width}x{total_height}")

    # 🔤 ターン表示ラベル（上部配置）
    turn_label = tk.Label(root, text="", font=("Helvetica", 20), bg=bg_color)
    turn_label.grid(row=0, column=0, columnspan=2, pady=10)

    # 🎮 ゲームエンジン・描画エンジン初期化
    engine = GameEngine(player_ids, hints, board_data,
                        label_map, color_map=preset_colors)

    # 🕹 ゲーム状態を初期化（開始直後）
    engine.state.set_phase("active")
    engine.state.current_action = None

    find_solution_tile(engine)  # 正解候補マスを探索

    renderer = BoardRenderer(canvas=None, terrain_imgs=terrain_imgs,
                             radius=radius, margin_x=margin_x, margin_y=margin_y, player_lookup=engine.id_to_player)

    # 🔲 メイン描画エリア
    main_frame = tk.Frame(root, bg=bg_color)
    main_frame.grid(row=1, column=0, columnspan=2)
    main_frame.grid_columnconfigure(0, weight=1)
    main_frame.grid_rowconfigure(0, weight=1)

    # 🎨 左：マップキャンバス
    canvas = tk.Canvas(main_frame, width=canvas_width,
                       height=canvas_height, bg=bg_color, highlightthickness=0)
    canvas.grid(row=0, column=0, sticky="nsew")
    renderer.canvas = canvas
    renderer.render(engine.board.tiles, rows, cols)

    # 📋 右：操作・情報パネル
    info_frame = tk.Frame(main_frame, width=info_frame_width, bg=bg_color)
    info_frame.grid(row=0, column=1, sticky="ns")

    info_frame.grid_propagate(False)

    inner_wrapper = tk.Frame(info_frame, bg=bg_color)
    inner_wrapper.place(relx=0.5, rely=0.5, anchor="center")

    # 🔘 ボタン群（上部配置）
    button_frame = tk.Frame(inner_wrapper, bg=bg_color)
    button_frame.pack()

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

    question_btn = tk.Button(button_frame, text="質問",
                             command=set_phase_question, width=10, bg="alice blue", relief="flat", borderwidth=0, highlightthickness=0)
    search_btn = tk.Button(button_frame, text="探索",
                           command=set_phase_search, width=10, bg="alice blue", relief="flat", borderwidth=0, highlightthickness=0)
    question_btn.pack(side=tk.TOP, pady=5)
    search_btn.pack(side=tk.TOP, pady=5)

    # 🧃 ラベル生成関数
    def create_label(pid, is_active):
        weight = "bold" if is_active else "normal"
        player = engine.id_to_player[pid]
        return tk.Label(inner_wrapper,
                        text=label_map[pid],
                        font=("Helvetica", 10, weight),
                        fg=player.color,
                        bg=bg_color,
                        highlightthickness=0)

    # 🧃 プレイヤーラベル群
    player_labels = {}
    for pid in player_ids:
        is_active = pid == engine.state.current_player
        label = create_label(pid, is_active)
        label.pack(anchor="center", pady=0)
        player_labels[pid] = label

    def update_player_labels():
        current_pid = engine.state.current_player
        for pid, label in player_labels.items():
            size = 20 if pid == current_pid else 15
            weight = "bold" if pid == current_pid else "normal"
            label.config(font=("Helvetica", size, weight))

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

    # 💡 初期ターン表示
    current_pid = engine.state.current_player
    color = engine.id_to_player[current_pid].color
    turn_label.config(
        text=f"{label_map[engine.state.current_player]} のターン", fg=color)
    update_player_labels()

    # 🚀 メインループ開始
    root.mainloop()


if __name__ == "__main__":
    main()
