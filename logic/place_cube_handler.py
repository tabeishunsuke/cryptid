from core.hint_engine import hint_applies_to_cell
from ui.labels import display_name
from ui.board_view import create_hex_board
import tkinter.messagebox as messagebox


def handle_place_cube(coord, cell, pid, board_data, hints, game_state, player_ids,
                      canvas, radius, rows, cols, terrain_imgs, turn_label):

    hint = hints[player_ids.index(pid)]

    if cell["cube"] is not None:
        messagebox.showinfo("無効", "すでにキューブが置かれているマスには配置できません。")
        return

    if hint_applies_to_cell(cell, hint, board_data):
        messagebox.showinfo("無効", "自分のヒントに合致するマスにはキューブを置けません。")
        return

    cell["cube"] = pid
    game_state.cube_count[pid] += 1
    game_state.log(f"{display_name(pid)} は失敗処理で {coord} にキューブを配置。")
    game_state.current_action = None
    game_state.next_player()
    turn_label.config(text=f"{display_name(game_state.current_player)} のターン")
    create_hex_board(canvas, board_data, rows, cols, radius, terrain_imgs)
