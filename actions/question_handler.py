import tkinter.messagebox as messagebox
from core.hint_engine import hint_applies_to_cell
from ui.dialogs import ask_player_selection
from ui.labels import display_name
from ui.board_renderer import render_board


def handle_question(coord, cell, current, player_ids, board_data, hints, game_state,
                    canvas, radius, rows, cols, terrain_imgs, turn_label):
    """
    質問フェーズの処理：
    - 質問対象プレイヤーを選択
    - ヒントに合致するか判定
    - ディスク or キューブ配置し、次のアクションへ遷移
    """
    if game_state.current_action == "place_cube":
        messagebox.showinfo("アクション不可", "まずキューブを配置してください。")
        return

    if cell.get("cube") is not None:
        messagebox.showinfo("無効な操作", "すでにキューブが置かれているマスには質問できません。")
        return

    # プレイヤー選択ダイアログ（質問対象を決定）
    valid_display = [display_name(pid) for pid in player_ids if pid != current]
    selected_label = ask_player_selection(valid_display)
    if not selected_label:
        return  # キャンセル時

    # 対象プレイヤーの ID を取得
    idx = valid_display.index(selected_label)
    target_id = [pid for pid in player_ids if pid != current][idx]
    hint = hints[player_ids.index(target_id)]

    applies = hint_applies_to_cell(cell, hint, board_data)

    if applies:
        # 『はい』：ディスクを追加（未配置なら）
        if target_id not in cell["discs"]:
            cell["discs"].append(target_id)
            game_state.disk_count[target_id] += 1
            game_state.log(f"{selected_label} は『はい』と回答し、ディスクを配置。")
        game_state.next_player()
        game_state.current_action = None
        turn_label.config(
            text=f"{display_name(game_state.current_player)} のターン")
    else:
        # 『いいえ』：キューブを配置し、質問者がキューブフェーズへ
        cell["cube"] = target_id
        game_state.cube_count[target_id] += 1
        game_state.log(f"{selected_label} は『いいえ』と回答し、キューブを配置。")
        game_state.current_action = "place_cube"
        turn_label.config(
            text=f"{display_name(game_state.current_player)}：質問失敗 → キューブを置いてください")

    render_board(canvas, board_data, rows, cols, radius, terrain_imgs)
