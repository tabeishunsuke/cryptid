from actions.phase_dispatcher import handle_canvas_click


def bind_canvas_events(canvas, board_data, hints, player_ids, game_state,
                       radius, rows, cols, terrain_imgs, root, turn_label):
    """
    キャンバスのクリックイベントをセットアップする。

    左クリック時に盤面マスに対するアクション処理を呼び出す。
    """
    def on_click(event):
        handle_canvas_click(
            event, canvas, board_data, hints, player_ids, game_state,
            radius, rows, cols, terrain_imgs, root, turn_label
        )

    canvas.bind("<Button-1>", on_click)
