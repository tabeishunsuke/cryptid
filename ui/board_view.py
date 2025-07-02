import math


def grid_to_pixel(col, row, radius):
    x = radius * 3 / 2 * col
    y = radius * math.sqrt(3) * (row + 0.5 * (col % 2))
    return x + radius + 10, y + radius + 10


def create_hex_board(canvas, board_data, rows, cols, radius, terrain_imgs, background_img=None):
    canvas.delete("all")

    # 背景描画（画像があれば）
    if background_img:
        canvas_width = int(canvas["width"])
        canvas_height = int(canvas["height"])
        canvas.create_image(canvas_width // 2, canvas_height //
                            2, image=background_img, anchor="center")
        canvas.bg_img = background_img

    # --- 🔧 中央配置用オフセット計算 ---
    cols_ = [col for col, _ in board_data]
    rows_ = [row for _, row in board_data]
    min_col, max_col = min(cols_), max(cols_)
    min_row, max_row = min(rows_), max(rows_)

    canvas_width = int(canvas["width"])
    canvas_height = int(canvas["height"])

    board_width = radius * 1.5 * (max_col - min_col + 1)
    board_height = radius * math.sqrt(3) * (max_row - min_row + 1)

    offset_x = (canvas_width - board_width) / 2 - \
        radius * 1.5 * min_col + radius
    offset_y = (canvas_height - board_height) / 2 - radius * \
        math.sqrt(3) * (min_row + 0.5 * (min_col % 2)) + radius

    canvas.hex_offset = (offset_x, offset_y)

    for (col, row), cell in board_data.items():
        cx = radius * 3 / 2 * col + offset_x
        cy = radius * math.sqrt(3) * (row + 0.5 * (col % 2)) + offset_y

        # 地形
        terrain = cell.get("terrain")
        if terrain in terrain_imgs:
            canvas.create_image(cx, cy, image=terrain_imgs[terrain])

        # 縄張り（zone_marker）
        zone = cell.get("zone_marker")
        ratio = 0.8
        if zone in ("bear", "eagle"):
            points = []
            for i in range(6):
                angle = math.radians(60 * i)
                px = cx + radius * ratio * math.cos(angle)
                py = cy + radius * ratio * math.sin(angle)
                points.extend([px, py])
            if zone == "bear":
                canvas.create_polygon(
                    points, outline="black", fill="", width=2, dash=(15, 8))
            elif zone == "eagle":
                canvas.create_polygon(points, outline="red", fill="", width=2)

        # 六角形の枠線
        hex_points = []
        for i in range(6):
            angle = math.radians(60 * i)
            px = cx + radius * math.cos(angle)
            py = cy + radius * math.sin(angle)
            hex_points.extend([px, py])
        canvas.create_polygon(hex_points, outline="gray", fill="", width=2)

        # 建造物
        structure = cell.get("structure")
        if structure in ("stone", "ruin"):
            color = cell.get("structure_color", "gray")
            shape = []
            if structure == "stone":
                for i in range(8):
                    angle = math.radians(45 * i + 22.5)
                    px = cx + radius * 0.5 * math.cos(angle)
                    py = cy + radius * 0.5 * math.sin(angle)
                    shape.extend([px, py])
            elif structure == "ruin":
                for i in range(3):
                    angle = math.radians(120 * i - 90)
                    px = cx + radius * 0.6 * math.cos(angle)
                    py = cy + radius * 0.6 * math.sin(angle)
                    shape.extend([px, py])
            canvas.create_polygon(shape, fill=color, outline="black", width=2)

        # キューブ
        cube_owner = cell.get("cube")
        if cube_owner:
            color = cube_color(cube_owner)
            canvas.create_rectangle(
                cx - radius * 0.35, cy - radius * 0.35,
                cx + radius * 0.35, cy + radius * 0.35,
                fill=color, outline="black", width=1
            )

        # ディスク
        discs = cell.get("discs", [])
        for i, pid in enumerate(discs):
            offset = (i - len(discs) / 2 + 0.5) * radius * 0.3
            canvas.create_oval(
                cx + offset - radius * 0.15, cy + radius * 0.3 - radius * 0.15,
                cx + offset + radius * 0.15, cy + radius * 0.3 + radius * 0.15,
                fill=cube_color(pid), outline="black"
            )


def cube_color(player_id):
    colors = {
        "alpha": "#E74C3C", "beta": "#3498DB", "gamma": "#2ECC71",
        "delta": "#F1C40F", "epsilon": "#9B59B6"
    }
    return colors.get(player_id, "gray")
