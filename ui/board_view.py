import math


def grid_to_pixel(col, row, radius):
    x = radius * 3 / 2 * col
    y = radius * math.sqrt(3) * (row + 0.5 * (col % 2))
    return x + radius + 10, y + radius + 10  # 左上に余白


def pixel_to_grid(x, y, radius):
    x -= radius + 10
    y -= radius + 10
    col = int(round(x / (1.5 * radius)))
    col_offset = 0.5 * radius * math.sqrt(3) if col % 2 else 0
    row = int(round((y - col_offset) / (radius * math.sqrt(3))))
    return col, row


def cube_color(player_id):
    colors = {
        "alpha": "#E74C3C",
        "beta": "#3498DB",
        "gamma": "#2ECC71",
        "delta": "#F1C40F",
        "epsilon": "#9B59B6"
    }
    return colors.get(player_id, "gray")


def create_hex_board(canvas, board_data, rows, cols, radius, terrain_imgs):
    canvas.delete("all")

    for (col, row), cell in board_data.items():
        cx, cy = grid_to_pixel(col, row, radius)

        # 地形
        terrain = cell.get("terrain")
        if terrain in terrain_imgs:
            canvas.create_image(cx, cy, image=terrain_imgs[terrain])

        # 🐾 縄張りの描画（zone_marker に基づく）
        zone = cell.get("zone_marker")
        if zone in ("bear", "eagle"):
            points = []
            for i in range(6):
                angle = math.radians(60 * i)
                px = cx + radius * 0.75 * math.cos(angle)
                py = cy + radius * 0.75 * math.sin(angle)
                points.extend([px, py])
            if zone == "bear":
                canvas.create_polygon(
                    points, outline="black", fill="", width=2, dash=(4, 2)
                )
            elif zone == "eagle":
                canvas.create_polygon(
                    points, outline="red", fill="", width=2
                )

        # 六角形の枠線
        hex_points = []
        for i in range(6):
            angle = math.radians(60 * i)
            px = cx + radius * math.cos(angle)
            py = cy + radius * math.sin(angle)
            hex_points.extend([px, py])
        canvas.create_polygon(hex_points, outline="gray", fill="", width=1)

        # 構造物（stone/ruin）
        structure = cell.get("structure")
        if structure in ("stone", "ruin"):
            color = cell.get("structure_color", "gray")
            shape = []
            if structure == "stone":
                for i in range(8):
                    angle = math.radians(45 * i)
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

        # キューブ（中央の四角）
        cube_owner = cell.get("cube")
        if cube_owner:
            color = cube_color(cube_owner)
            canvas.create_rectangle(
                cx - radius * 0.35, cy - radius * 0.35,
                cx + radius * 0.35, cy + radius * 0.35,
                fill=color, outline="black", width=1
            )

        # ディスク（下部に並列）
        discs = cell.get("discs", [])
        for i, pid in enumerate(discs):
            offset = (i - len(discs) / 2 + 0.5) * radius * 0.3
            canvas.create_oval(
                cx + offset - radius * 0.15, cy + radius * 0.3 - radius * 0.15,
                cx + offset + radius * 0.15, cy + radius * 0.3 + radius * 0.15,
                fill=cube_color(pid), outline="black"
            )
