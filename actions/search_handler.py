import tkinter.messagebox as messagebox
from ui.labels import display_name
from core.hint_engine import hint_applies_to_cell
from ui.board_renderer import render_board


def handle_explore(coord, cell, current, player_ids, board_data, hints, game_state,
                   canvas, radius, rows, cols, terrain_imgs, root, turn_label):
    """
    探索フェーズの最初のクリック処理

    - ヒントに合致するか確認
    - 自身のディスクがある場合は再配置へ
    - それ以外は反証フェーズ（reveal）を開始
    """
    if game_state.current_action in ("place_cube", "place_disc", "reveal_check"):
        messagebox.showinfo("アクション不可", "まず現在のフェーズを完了してください。")
        return

    if cell["cube"] is not None:
        messagebox.showinfo("無効な探索", "このマスにはすでにキューブがあります。")
        return

    own_hint = hints[player_ids.index(current)]
    applies_to_self = hint_applies_to_cell(cell, own_hint, board_data)
    if not applies_to_self:
        messagebox.showinfo("無効な探索", "自分のヒントに合致しないマスは探索できません。")
        return

    if current in cell["discs"]:
        # 再配置フェーズへ遷移
        game_state.pending_explore = {
            "coord": coord,
            "cell": cell,
            "current": current
        }
        game_state.current_action = "place_disc"
        turn_label.config(text=f"{display_name(current)}：別のマスにディスクを配置してください")
        return

    # 通常の探索を開始
    begin_reveal_sequence(coord, cell, current, player_ids, board_data, hints,
                          game_state, canvas, radius, rows, cols, terrain_imgs, root, turn_label)


def begin_reveal_sequence(coord, cell, explorer, player_ids, board_data, hints,
                          game_state, canvas, radius, rows, cols, terrain_imgs, root, turn_label):
    explorer_index = player_ids.index(explorer)
    reveal_order = player_ids[explorer_index:] + player_ids[:explorer_index]

    game_state.exploration_target = coord
    game_state.reveal_index = 0
    game_state.current_action = "reveal_check"

    def reveal_step():
        idx = game_state.reveal_index
        if idx >= len(reveal_order):
            # 探索成功 → 勝利
            correct_coords = []
            for test_coord, test_cell in board_data.items():
                if all(hint_applies_to_cell(test_cell, hints[player_ids.index(pid)], board_data)
                       for pid in player_ids):
                    correct_coords.append(test_coord)

            for c in correct_coords:  # ← ローカル変数名を変更（coordと衝突しないように）
                print(f"✅ 正解座標: {c}")

            for pid in player_ids:
                hint = hints[player_ids.index(pid)]
                print(f"{display_name(pid)} → {hint['text']}")

            messagebox.showinfo(
                "ゲーム終了", f"{display_name(explorer)} の勝利！おめでとう！")
            root.quit()
            return

        pid = reveal_order[idx]
        hint = hints[player_ids.index(pid)]

        if idx == 0:
            if pid not in cell["discs"]:
                cell["discs"].append(pid)
                game_state.disk_count[pid] += 1
                game_state.log(f"{display_name(pid)} は探索対象にディスクを配置。")
            render_board(canvas, board_data, rows, cols, radius, terrain_imgs)
            game_state.reveal_index += 1
            root.after(800, reveal_step)
            return

        applies = hint_applies_to_cell(cell, hint, board_data)
        if not applies:
            board_data[coord]["cube"] = pid  # ✅ ここでエラーにならなくなる
            game_state.cube_count[pid] += 1
            game_state.log(f"{display_name(pid)} は反証できず、探索は中断。")
            game_state.current_index = player_ids.index(explorer)
            game_state.current_action = "place_cube"
            turn_label.config(
                text=f"{display_name(explorer)}：探索失敗 → キューブを置いてください")
            render_board(canvas, board_data, rows, cols, radius, terrain_imgs)
            return

        if pid not in cell["discs"]:
            cell["discs"].append(pid)
            game_state.disk_count[pid] += 1
            game_state.log(f"{display_name(pid)} のヒントに合致 → ディスク配置。")

        game_state.reveal_index += 1
        render_board(canvas, board_data, rows, cols, radius, terrain_imgs)
        root.after(800, reveal_step)

    reveal_step()
