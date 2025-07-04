import tkinter.messagebox as messagebox
from ui.labels import display_name
from core.hint_engine import hint_applies_to_cell
from actions.search_handler import begin_reveal_sequence
from ui.board_renderer import render_board


def handle_place_disc(selected_coord, player_ids, board_data, hints, game_state,
                      canvas, radius, rows, cols, terrain_imgs, root, turn_label):
    """
    ディスク再配置フェーズの処理：
    - 現在のフェーズ確認（place_disc であるか）
    - 対象マスが有効か判定
    - ディスク配置後、探索フェーズを再開（begin_reveal_sequence）
    """
    if game_state.current_action != "place_disc":
        messagebox.showinfo("アクション不可", "現在はディスク配置フェーズではありません。")
        return

    current = game_state.current_player
    own_hint = hints[player_ids.index(current)]
    cell = board_data.get(selected_coord)

    if not cell:
        messagebox.showinfo("無効な操作", "存在しないマスを選択しました。")
        return

    # 配置条件のチェック
    if (cell["cube"] is not None or
        current in cell["discs"] or
            not hint_applies_to_cell(cell, own_hint, board_data)):
        messagebox.showinfo("無効なマス", "このマスにはディスクを置けません。")
        return

    # ディスクを配置
    cell["discs"].append(current)
    game_state.disk_count[current] += 1
    game_state.log(
        f"{display_name(current)} は探索のため {selected_coord} にディスクを配置。")

    # 探索再開準備（pending_explore 情報から）
    pending = game_state.pending_explore
    if not pending:
        messagebox.showinfo("エラー", "探索対象の情報が見つかりません。")
        return

    game_state.pending_explore = None
    game_state.current_action = None  # フェーズ完了

    render_board(canvas, board_data, rows, cols, radius, terrain_imgs)

    begin_reveal_sequence(
        pending["coord"],     # 探索対象マス
        pending["cell"],      # セルデータ
        pending["current"],   # 探索者
        player_ids,
        board_data,
        hints,
        game_state,
        canvas,
        radius,
        rows,
        cols,
        terrain_imgs,
        root,
        turn_label
    )
