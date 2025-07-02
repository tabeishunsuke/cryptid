import tkinter.messagebox as messagebox
from ui.labels import display_name
from core.hint_engine import hint_applies_to_cell
from ui.board_view import create_hex_board


def handle_explore(coord, cell, current, player_ids, board_data, hints, game_state,
                   canvas, radius, rows, cols, terrain_imgs, root, turn_label):
    if game_state.current_action == "place_cube":
        messagebox.showinfo("アクション不可", "まずキューブを配置してください。")
        return

    if game_state.current_action in ("place_cube", "place_disc", "reveal_check"):
        messagebox.showinfo("アクション不可", "まず現在のフェーズを完了してください。")
        return

    print(f"\n[探索開始] {display_name(current)} が探索 → マス {coord}")

    if cell["cube"] is not None:
        print("[探索無効] すでにキューブが配置されている")
        messagebox.showinfo("無効な探索", "このマスにはすでにキューブがあります。")
        return

    own_hint = hints[player_ids.index(current)]
    applies_to_self = hint_applies_to_cell(cell, own_hint, board_data)
    print(f"[ヒント自己確認] {display_name(current)} 自身のヒントに合致？ → {applies_to_self}")
    if not applies_to_self:
        messagebox.showinfo("無効な探索", "自分のヒントに合致しないマスは探索できません。")
        return

    if current in cell["discs"]:
        # ディスク再配置フェーズに遷移
        game_state.pending_explore = {
            "coord": coord,
            "cell": cell,
            "current": current
        }
        game_state.current_action = "place_disc"
        turn_label.config(text=f"{display_name(current)}：別のマスにディスクを配置してください")
        print(f"[探索中断] 自身のディスクが探索対象にある → place_disc フェーズへ")
        return

    # 通常の探索へ
    begin_reveal_sequence(coord, cell, current, player_ids, board_data, hints,
                          game_state, canvas, radius, rows, cols, terrain_imgs, root, turn_label)


def begin_reveal_sequence(coord, cell, current, player_ids, board_data, hints,
                          game_state, canvas, radius, rows, cols, terrain_imgs, root, turn_label):

    explorer = current
    explorer_index = player_ids.index(explorer)
    reveal_order = [explorer] + player_ids[explorer_index +
                                           1:] + player_ids[:explorer_index]

    game_state.exploration_target = coord
    game_state.reveal_index = 0
    game_state.current_action = "reveal_check"

    print(f"[探索登録] explorer={display_name(explorer)}")
    print(f"[反証順序] → {', '.join(display_name(p) for p in reveal_order)}")

    def reveal_step():
        idx = game_state.reveal_index
        if idx >= len(reveal_order):
            print(f"[探索成功] 全員合致 → {display_name(explorer)} 勝利")
            messagebox.showinfo(
                "ゲーム終了", f"{display_name(explorer)} の勝利！おめでとう！")
            root.quit()
            return

        pid = reveal_order[idx]
        hint = hints[player_ids.index(pid)]

        if idx == 0:
            if pid not in cell["discs"]:
                print(f"[ディスク配置] 探索者 {display_name(pid)} → ディスク配置")
                cell["discs"].append(pid)
                game_state.disk_count[pid] += 1
                game_state.log(f"{display_name(pid)} は探索対象にディスクを配置。")
            create_hex_board(canvas, board_data, rows,
                             cols, radius, terrain_imgs)
            game_state.reveal_index += 1
            root.after(800, reveal_step)
            return

        applies = hint_applies_to_cell(cell, hint, board_data)
        print(
            f"[ヒント照合] idx={idx}, プレイヤー={display_name(pid)} → applies={applies}")

        if not applies:
            print(f"[探索失敗] {display_name(pid)} → 探索中断／キューブを配置")
            board_data[coord]["cube"] = pid
            game_state.cube_count[pid] += 1
            game_state.log(f"{display_name(pid)} は反証できず、探索は中断。")
            game_state.current_index = player_ids.index(explorer)
            game_state.current_action = "place_cube"
            turn_label.config(
                text=f"{display_name(explorer)}：探索失敗 → キューブを置いてください")
            create_hex_board(canvas, board_data, rows,
                             cols, radius, terrain_imgs)
            return

        if pid not in cell["discs"]:
            print(f"[ディスク配置] {display_name(pid)} → このマスにディスクを追加")
            cell["discs"].append(pid)
            game_state.disk_count[pid] += 1
            game_state.log(f"{display_name(pid)} のヒントに合致 → ディスク配置。")

        game_state.reveal_index += 1
        create_hex_board(canvas, board_data, rows, cols, radius, terrain_imgs)
        root.after(800, reveal_step)

    reveal_step()
