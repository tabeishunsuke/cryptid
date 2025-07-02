from logic.question_logic import handle_canvas_click


def setup_canvas_bindings(canvas, board_data, hints, player_ids, game_state,
                          radius, rows, cols, terrain_imgs, root, turn_label):
    def on_click(event):
        handle_canvas_click(
            event, canvas, board_data, hints, player_ids, game_state,
            radius, rows, cols, terrain_imgs, root, turn_label
        )
    canvas.bind("<Button-1>", on_click)
