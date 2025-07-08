import tkinter as tk
from tkinter import messagebox
from core.map_config_loader import MapConfigLoader
from core.hint_loader import HintLoader
from core.game_engine import GameEngine
from ui.board_renderer import BoardRenderer
from actions.phase_handler import PhaseHandler
from ui.canvas_utils import pixel_to_cell_coord
from ui.image_loader import load_terrain_images


def find_solution_tile(engine):
    """
    ゲーム開始時に、すべてのヒントに合致する正解候補マスを探索・表示するデバッグ用関数
    """
    board = engine.board
    all_coords = list(board.tiles.keys())
    players = engine.players

    print("\n[DEBUG] プレイヤーのヒント一覧:")
    for player in players:
        print(f"  - {player.display_name}（{player.id}）: {player.hint}")

    solution_tiles = []
    for coord in all_coords:
        cell = board.get_tile(coord)
        if all(board.apply_hint(coord, p.hint) for p in players):
            solution_tiles.append(coord)

    print(f"\n[DEBUG] 正解候補マス（全ヒント一致）:")
    for coord in solution_tiles:
        print(f"  → {coord}")


def main():
    # 🧩 データローダーの準備
    map_loader = MapConfigLoader()
    hint_loader = HintLoader()

    # 🎲 使用マップとプレイヤー数の指定
    map_id = map_loader.get_available_map_ids()[15]
    player_count = 5
    board_data = map_loader.load_map(map_id)
    raw_players = hint_loader.get_players_for_map(map_id, player_count)

    # 🧠 プレイヤー定義（ID・ヒント・色・表示名）
    player_ids = [p["id"] for p in raw_players]
    hints = [p["hint"] for p in raw_players]
    label_map = {p["id"]: p["id"] for p in raw_players}  # ラベルマップ（任意で変更可）
    preset_colors = {
        "player1": "firebrick2",
        "player2": "aquamarine",
        "player3": "HotPink",
        "player4": "chocolate1",
        "player5": "dark magenta",
    }

    # 🎮 ゲームエンジンを初期化
    engine = GameEngine(player_ids, hints, board_data,
                        label_map, color_map=preset_colors)
    engine.state.set_phase("active")
    engine.state.current_action = None

    find_solution_tile(engine)  # デバッグ：正解候補探索

    # 🖼️ TkinterウィンドウとUIの初期化
    bg_color = "gray15"
    root = tk.Tk()
    root.title("Cryptid")
    root.configure(bg=bg_color)

    # 🔧 マップサイズとUI幅の設定
    terrain_imgs = load_terrain_images()
    radius = 50
    rows, cols = 9, 12
    map_width_px = radius * 3/2 * cols + radius / 2
    map_height_px = radius * (3**0.5) * (rows + 1)
    margin_x = int(map_width_px * 0.1)
    margin_y = int(map_height_px * 0.1)
    canvas_width = int(map_width_px + margin_x * 2)
    canvas_height = int(map_height_px + margin_y * 2)
    info_frame_width = 200
    total_width = canvas_width + info_frame_width
    total_height = canvas_height

    # 🎨 ウィンドウサイズ設定
    root.geometry(f"{total_width}x{total_height}")

    # 🔤 ターン表示ラベル（画面上部）
    turn_label = tk.Label(root, text="", font=("Helvetica", 20), bg=bg_color)
    turn_label.grid(row=0, column=0, columnspan=2, pady=10)

    # 🧱 メイン描画フレームの定義
    main_frame = tk.Frame(root, bg=bg_color)
    main_frame.grid(row=1, column=0, columnspan=2)
    main_frame.grid_columnconfigure(0, weight=1)
    main_frame.grid_rowconfigure(0, weight=1)

    # 🎨 キャンバス（マップ描画エリア）設定
    canvas = tk.Canvas(main_frame, width=canvas_width, height=canvas_height,
                       bg=bg_color, highlightthickness=0)
    canvas.grid(row=0, column=0, sticky="nsew")

    # 🎮 BoardRenderer 初期化 → 初期描画
    renderer = BoardRenderer(canvas=canvas, terrain_imgs=terrain_imgs,
                             radius=radius, margin_x=margin_x, margin_y=margin_y,
                             player_lookup=engine.id_to_player)
    renderer.render(engine.board.tiles, rows, cols)

    # 📋 情報パネル（右側：ボタンとラベル群）
    info_frame = tk.Frame(main_frame, width=info_frame_width, bg=bg_color)
    info_frame.grid(row=0, column=1, sticky="ns")
    info_frame.grid_propagate(False)

    inner_wrapper = tk.Frame(info_frame, bg=bg_color)
    inner_wrapper.place(relx=0.5, rely=0.5, anchor="center")

    # 🔘 行動選択ボタン群
    button_frame = tk.Frame(inner_wrapper, bg=bg_color)
    button_frame.pack()

    def set_phase(phase_type):
        """
        行動フェーズを設定するコールバック（質問／探索）
        - キューブ配置中は制限あり
        """
        if engine.state.current_action == "place_cube":
            messagebox.showwarning("無効な操作", "キューブ配置フェーズ中は行動変更できません")
            return

        engine.state.current_action = phase_type
        handler.update_turn_label()

        pid = engine.state.current_player
        turn_label.config(text=f"{label_map[pid]} - {phase_type}フェーズ",
                          fg=engine.id_to_player[pid].color)

    question_btn = tk.Button(button_frame, text="質問",
                             command=lambda: set_phase("question"),
                             width=10, bg="alice blue",
                             relief="flat", borderwidth=0, highlightthickness=0)
    search_btn = tk.Button(button_frame, text="探索",
                           command=lambda: set_phase("search"),
                           width=10, bg="alice blue",
                           relief="flat", borderwidth=0, highlightthickness=0)
    question_btn.pack(pady=5)
    search_btn.pack(pady=5)

    # 🎤 プレイヤーラベル生成関数と表示群
    def create_label(pid, is_active):
        weight = "bold" if is_active else "normal"
        size = 20 if is_active else 14
        player = engine.id_to_player[pid]
        return tk.Label(inner_wrapper, text=label_map[pid],
                        font=("Helvetica", size, weight),
                        fg=player.color, bg=bg_color,
                        highlightthickness=0)

    player_labels = {}
    for pid in player_ids:
        label = create_label(pid, is_active=(
            pid == engine.state.current_player))
        label.pack(anchor="center", pady=0)
        player_labels[pid] = label

    def update_player_labels():
        current_pid = engine.state.current_player
        for pid, label in player_labels.items():
            weight = "bold" if pid == current_pid else "normal"
            size = 20 if pid == current_pid else 14
            label.config(font=("Helvetica", size, weight))

    # 🧭 フェーズハンドラー初期化（ターン制御）
    handler = PhaseHandler(engine, canvas, root, turn_label,
                           terrain_imgs, radius, rows, cols,
                           renderer, update_labels=update_player_labels)

    # 🖱️ マスクリック処理（座標変換 → フェーズ処理へ委譲）
    def on_click(event):
        coord = pixel_to_cell_coord(event.x, event.y,
                                    radius, margin_x=margin_x, margin_y=margin_y)
        print(f"[DEBUG] マスクリック: ({event.x}, {event.y}) → {coord}")
        handler.handle_click(coord)

    canvas.bind("<Button-1>", on_click)

    # 🖱️ ホバー処理（マス座標に応じてハイライト表示）
    def on_motion(event):
        coord = pixel_to_cell_coord(event.x, event.y,
                                    radius, margin_x=margin_x, margin_y=margin_y)
        if engine.board.is_valid_coord(coord):
            renderer.highlight_cell(coord)
        else:
            renderer.clear_highlight()

    canvas.bind("<Motion>", on_motion)

    # 🧠 初期ターン表示
    pid = engine.state.current_player
    turn_label.config(text=f"{label_map[pid]} のターン",
                      fg=engine.id_to_player[pid].color)
    update_player_labels()

    # 🚀 メインループ開始
    root.mainloop()


if __name__ == "__main__":
    main()
