import os
import random
import tkinter as tk
from tkinter import messagebox

from core.board_loader import load_blocks, assemble_board
from core.map_config_loader import load_map_configs
from core.hint_loader import load_book_orders, load_generic_hints, load_map_player_hints
from core.game_state import GameState
from ui.canvas_utils import load_terrain_images
from ui.labels import display_name, INTERNAL_LABELS
from actions.canvas_handler import bind_canvas_events
from ui.board_renderer import render_board
from ui.canvas_utils import create_turn_label, create_board_canvas


def main():
    """ゲームのメインエントリーポイント"""
    players = 4

    # --- マップとプレイヤー準備 ---
    maps = load_map_configs("assets/configs")
    # map_id = random.choice(list(maps.keys()))
    map_id = 2
    map_info = maps.get(map_id)

    print(f"[INFO] 使用マップID → {map_id}")
    player_ids = INTERNAL_LABELS[:players]
    game_state = GameState(player_ids)

    # --- ヒント・構成読み込み ---
    blocks = load_blocks("assets/blocks")
    generic_hints = load_generic_hints("assets/configs")
    book_orders = load_book_orders("assets/configs")
    mp_hints = load_map_player_hints("assets/configs")

    # プレイヤーごとのヒント設定
    label_order = ["alpha", "beta", "gamma", "delta", "epsilon"]
    mp_row = next(
        (r for r in mp_hints if r["map_id"] == map_id and r["players"] == players), None)
    selected_labels = [
        label for label in label_order if mp_row.get(label)][:players]

    hints = []
    for pid, label in zip(player_ids, selected_labels):
        pos = mp_row[label]
        hint_id = book_orders[pos][label]
        hint = next(h for h in generic_hints if h["hint_id"] == hint_id)
        hints.append(hint)

    # --- 盤面構築 ---
    board_data = assemble_board(blocks, map_info["blocks"], 2, 3)
    for coord, cell in board_data.items():
        cell.update({
            "col": coord[0],
            "row": coord[1],
            "cube": None,
            "discs": [],
            "structure": None,
            "structure_color": None,
        })
        for t in cell.get("territories", []):
            if t in ("bear", "eagle"):
                cell["zone_marker"] = t

    for s in map_info.get("structures", []):
        key = (s["col"], s["row"])
        if key in board_data:
            board_data[key]["structure"] = s["type"]
            board_data[key]["structure_color"] = s["color"]

    # --- GUI構築 ---
    root = tk.Tk()
    root.title("Cryptid Offline")
    root.state("zoomed")  # 起動時に最大化

    turn_label = create_turn_label(root)
    terrain_imgs = load_terrain_images("assets/terrain")
    canvas, radius, rows, cols = create_board_canvas(root)

    # --- 背景画像の読み込み（ランダム） ---
    bg_img = None
    bg_dir = "assets/backgrounds"
    bg_files = [f for f in os.listdir(
        bg_dir) if f.lower().endswith((".png", ".gif"))]
    if bg_files:
        bg_path = os.path.join(bg_dir, random.choice(bg_files))
        print(f"[INFO] 背景画像 → {bg_path}")
        bg_img = tk.PhotoImage(file=bg_path)

    # --- アクションボタン ---
    action_frame = tk.Frame(root)
    action_frame.pack(side="bottom", fill="x")

    def start_question_phase():
        if game_state.current_action in ("place_cube", "place_disc", "reveal_check"):
            messagebox.showinfo("操作無効", "現在のフェーズを完了してください。")
            return
        game_state.current_action = "question"
        turn_label.config(
            text=f"{display_name(game_state.current_player)} のターン（行動: 質問）")

    def start_search_phase():
        if game_state.current_action in ("place_cube", "place_disc", "reveal_check"):
            messagebox.showinfo("操作無効", "現在のフェーズを完了してください。")
            return
        game_state.begin_search()
        turn_label.config(
            text=f"{display_name(game_state.current_player)} のターン（行動: 探索）")

    tk.Button(action_frame, text="質問する", command=start_question_phase).pack(
        side="left", padx=10)
    tk.Button(action_frame, text="探索する", command=start_search_phase).pack(
        side="left", padx=10)

    # --- イベント登録・盤面描画 ---
    bind_canvas_events(canvas, board_data, hints, player_ids, game_state,
                       radius, rows, cols, terrain_imgs, root, turn_label)

    turn_label.config(text=f"{display_name(game_state.current_player)} のターン")

    def delayed_draw():
        render_board(canvas, board_data, rows, cols, radius,
                     terrain_imgs, background_img=bg_img)

    root.after(100, delayed_draw)

    # --- リサイズ対応再描画 ---
    last_size = {"w": 0, "h": 0}

    def on_resize(event):
        w_now, h_now = canvas.winfo_width(), canvas.winfo_height()
        if (w_now, h_now) != (last_size["w"], last_size["h"]):
            last_size["w"], last_size["h"] = w_now, h_now
            render_board(canvas, board_data, rows, cols, radius,
                         terrain_imgs, background_img=bg_img)

    root.bind("<Configure>", on_resize)

    root.mainloop()


if __name__ == "__main__":
    main()
