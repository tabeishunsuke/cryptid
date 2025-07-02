from ui.utils import pixel_to_grid
from ui.dialogs import ask_player_selection
from ui.labels import display_name
from core.hint_engine import hint_applies_to_cell
from ui.board_view import create_hex_board
import tkinter.messagebox as messagebox


def handle_canvas_click(event, canvas, board_data, hints, player_ids, game_state,
                        radius, rows, cols, terrain_imgs, root, turn_label):
    col, row = pixel_to_grid(event.x, event.y, radius)
    coord = (col, row)
    print(
        f"クリック位置: pixel=({event.x}, {event.y}) → grid={coord} → 有効？ {coord in board_data}")

    if coord not in board_data:
        return

    cell = board_data[coord]
    current = game_state.current_player

    if game_state.current_action == "question":
        from .question_handler import handle_question
        handle_question(coord, cell, current, player_ids, board_data, hints,
                        game_state, canvas, radius, rows, cols, terrain_imgs, turn_label)

    elif game_state.current_action == "search":
        from .explore_handler import handle_explore
        handle_explore(coord, cell, current, player_ids, board_data, hints,
                       game_state, canvas, radius, rows, cols, terrain_imgs, root, turn_label)

    elif game_state.current_action == "place_kube":
        from .place_cube_handler import handle_place_kube
        handle_place_kube(coord, cell, current, board_data, hints, game_state, player_ids,
                          canvas, radius, rows, cols, terrain_imgs, turn_label)

    elif game_state.current_action == "place_disc":
        from .place_disc_handler import handle_place_disc
        handle_place_disc(coord, player_ids, board_data, hints, game_state,
                          canvas, radius, rows, cols, terrain_imgs, root, turn_label)
