import tkinter as tk
from core.board_loader import load_blocks, assemble_board
from core.map_loader import load_map_configs
from core.data_loader import load_book_orders, load_generic_hints, load_map_player_hints
from core.hint_engine import hint_applies_to_cell
from core.game_state import GameState
from ui.utils import load_terrain_images, create_turn_label, create_board_canvas
from ui.dialogs import ask_player_selection
from ui.labels import display_name, INTERNAL_LABELS
from handlers.canvas_handler import setup_canvas_bindings


def main():
    map_id, players = 10, 3
    player_ids = INTERNAL_LABELS[:players]
    game_state = GameState(player_ids)

    # データ読み込みと盤面構築
    blocks = load_blocks("assets/blocks")
    maps = load_map_configs("assets/configs")
    hints_def = load_generic_hints("assets/configs")
    book_orders = load_book_orders("assets/configs")
    mp_hints = load_map_player_hints("assets/configs")
    map_info = maps.get(map_id)

    label_order = ["alpha", "beta", "gamma", "delta", "epsilon"]
    mp_row = next(
        (r for r in mp_hints if r["map_id"] == map_id and r["players"] == players), None)
    used_labels = [label for label in label_order if mp_row.get(label)]
    selected_labels = used_labels[:players]

    hints = []
    for pid, label in zip(player_ids, selected_labels):
        pos = mp_row[label]
        hint_id = book_orders[pos][label]
        hint = next(h for h in hints_def if h["hint_id"] == hint_id)
        hints.append(hint)

    board_data = assemble_board(blocks, map_info["blocks"], 2, 3)
    # デバッグ用（main.py の初期化後などに）
    for coord, cell in board_data.items():
        if cell is None:
            print(f"警告: board_data に None が含まれています → {coord}")

    for (col, row), cell in board_data.items():
        cell.update({"col": col, "row": row, "cube": None, "discs": []})
    for s in map_info.get("structures", []):
        if (s["col"], s["row"]) in board_data:
            board_data[(s["col"], s["row"])].update({
                "structure": s["type"],
                "structure_color": s["color"]
            })

    # GUI構築
    root = tk.Tk()
    root.title("Cryptid Offline")
    turn_label = create_turn_label(root)
    terrain_imgs = load_terrain_images("assets/terrain")
    canvas, radius, rows, cols = create_board_canvas(root)

    # --- アクションボタンの追加 ---
    action_frame = tk.Frame(root)
    action_frame.pack(side="bottom", fill="x")

    def begin_question():
        game_state.begin_question(None)
        turn_label.config(
            text=f"{display_name(game_state.current_player)} のターン（行動: 質問）")

    def begin_search():
        game_state.begin_search()
        turn_label.config(
            text=f"{display_name(game_state.current_player)} のターン（行動: 探索）")

    tk.Button(action_frame, text="質問する", command=begin_question).pack(
        side="left", padx=10)
    tk.Button(action_frame, text="探索する", command=begin_search).pack(
        side="left", padx=10)

    setup_canvas_bindings(canvas, board_data, hints, player_ids, game_state,
                          radius, rows, cols, terrain_imgs, root, turn_label)

    turn_label.config(text=f"{display_name(game_state.current_player)} のターン")
    from ui.board_view import create_hex_board
    create_hex_board(canvas, board_data, rows, cols, radius, terrain_imgs)
    root.mainloop()


if __name__ == "__main__":
    main()
