from ui.canvas_utils import is_point_in_hex, pixel_to_cell_coord
from ui.labels import display_name
from core.hint_engine import hint_applies_to_cell
import tkinter.messagebox as messagebox


def handle_canvas_click(event, canvas, board_data, hints, player_ids, game_state,
                        radius, rows, cols, terrain_imgs, root, turn_label):
    """
    キャンバスクリック時に、現在のゲームフェーズに応じたアクション処理を呼び出す。

    Args:
        event: Tkinterのマウスイベント
        canvas: キャンバス
        board_data: 盤面データ辞書
        hints: プレイヤー別ヒントリスト
        player_ids: プレイヤーID一覧
        game_state: 現在のゲーム進行状態
        terrain_imgs: 地形画像辞書
        root: Tkinterルートウィンドウ
        turn_label: ターン表示ラベル
    """
    center_col, center_row = pixel_to_cell_coord(
        event.x, event.y, radius, canvas)
    coord = None

    # クリック位置周辺を探索して、属する正確なマスを特定
    for dc in [-1, 0, 1]:
        for dr in [-1, 0, 1]:
            nc = center_col + dc
            nr = center_row + dr
            if (nc, nr) in board_data:
                if is_point_in_hex(event.x, event.y, nc, nr, radius, canvas):
                    coord = (nc, nr)
                    break
        if coord:
            break

    if coord not in board_data:
        return

    cell = board_data[coord]
    current = game_state.current_player

    # 現在のアクションに応じた処理を呼び分ける
    if game_state.current_action == "question":
        from actions.question_handler import handle_question
        handle_question(coord, cell, current, player_ids, board_data, hints,
                        game_state, canvas, radius, rows, cols, terrain_imgs, turn_label)

    elif game_state.current_action == "search":
        from actions.search_handler import handle_explore
        handle_explore(coord, cell, current, player_ids, board_data, hints,
                       game_state, canvas, radius, rows, cols, terrain_imgs, root, turn_label)

    elif game_state.current_action == "place_cube":
        from actions.place_cube_handler import handle_place_cube
        handle_place_cube(coord, cell, current, board_data, hints, game_state, player_ids,
                          canvas, radius, rows, cols, terrain_imgs, turn_label)

    elif game_state.current_action == "place_disc":
        from actions.place_disc_handler import handle_place_disc
        handle_place_disc(coord, player_ids, board_data, hints, game_state,
                          canvas, radius, rows, cols, terrain_imgs, root, turn_label)
