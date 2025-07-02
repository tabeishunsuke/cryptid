import tkinter.messagebox as messagebox
from ui.labels import display_name
from core.hint_engine import hint_applies_to_cell
from logic.explore_handler import begin_reveal_sequence  # ← 修正済み import
from ui.board_view import create_hex_board


def handle_place_disc(selected_coord, player_ids, board_data, hints, game_state,
                      canvas, radius, rows, cols, terrain_imgs, root, turn_label):
    if game_state.current_action != "place_disc":
        messagebox.showinfo("アクション不可", "現在はディスク配置フェーズではありません。")
        return

    current = game_state.current_player
    own_hint = hints[player_ids.index(current)]
    cell = board_data.get(selected_coord)

    if not cell:
        messagebox.showinfo("無効な操作", "存在しないマスを選択しました。")
        return

    # ✅ 配置条件のチェック
    if (cell["cube"] is not None or
        current in cell["discs"] or
            not hint_applies_to_cell(cell, own_hint, board_data)):
        print(f"[配置不可] {selected_coord} → 不正なマス")
        messagebox.showinfo("無効なマス", "このマスにはディスクを置けません。")
        return

    # ✅ ディスクを配置
    cell["discs"].append(current)
    game_state.disk_count[current] += 1
    game_state.log(
        f"{display_name(current)} は探索のため {selected_coord} にディスクを配置。")
    print(f"[ディスク配置] {display_name(current)} → {selected_coord}")

    # 🎯 探索に遷移：pending 情報から開始
    pending = game_state.pending_explore
    if not pending:
        messagebox.showinfo("エラー", "探索対象の情報が見つかりません。")
        return

    game_state.pending_explore = None
    game_state.current_action = None  # フェーズ終了

    # 盤面再描画（視覚確認のため）
    create_hex_board(canvas, board_data, rows, cols, radius, terrain_imgs)

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
