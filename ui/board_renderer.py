import math


def render_board(canvas, board_data, rows, cols, radius, terrain_imgs, background_img=None):
    """
    ゲーム盤面を描画する（背景含む中央配置対応済）

    Args:
        canvas: Tkinter キャンバス
        board_data: (col, row) → セル情報の辞書
        rows, cols, radius: 配置用の構成情報
        terrain_imgs: 地形ごとの画像辞書
        background_img: 背景画像（中央配置）
    """
    canvas.update_idletasks()
    canvas_width = canvas.winfo_width()
    canvas_height = canvas.winfo_height()

    canvas.delete("all")

    # 🎨 背景画像の描画（中央）
    if background_img:
        canvas.create_image(canvas_width // 2, canvas_height //
                            2, image=background_img, anchor="center")
        canvas.bg_img = background_img  # ガベージコレクション対策

    # 🧠 全マスの中心座標を収集
    positions = []
    for (col, row) in board_data:
        cx = radius * 1.5 * col
        cy = radius * math.sqrt(3) * (row + 0.5 * (col % 2))
        positions.append((cx, cy))

    # 🧮 バウンディングボックス取得
    min_x = min(p[0] for p in positions)
    max_x = max(p[0] for p in positions)
    min_y = min(p[1] for p in positions)
    max_y = max(p[1] for p in positions)

    board_w = max_x - min_x
    board_h = max_y - min_y

    offset_x = (canvas_width / 2) - (min_x + board_w / 2)
    offset_y = (canvas_height / 2) - (min_y + board_h / 2)

    canvas.hex_offset = (offset_x, offset_y)  # クリック判定の座標補正用

    # 🔷 各タイルを描画
    for (col, row), cell in board_data.items():
        cx = radius * 1.5 * col + offset_x
        cy = radius * math.sqrt(3) * (row + 0.5 * (col % 2)) + offset_y

        # 地形描画
        terrain = cell.get("terrain")
        if terrain in terrain_imgs:
            canvas.create_image(cx, cy, image=terrain_imgs[terrain])

        # 縄張りマーカー（bear/eagle）
        zone = cell.get("zone_marker")
        if zone in ("bear", "eagle"):
            ratio = 0.8
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

        # 六角枠線
        hex_points = []
        for i in range(6):
            angle = math.radians(60 * i)
            px = cx + radius * math.cos(angle)
            py = cy + radius * math.sin(angle)
            hex_points.extend([px, py])
        canvas.create_polygon(hex_points, outline="gray", fill="", width=2)

        # 構造物（stone / ruin）
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
    """プレイヤーIDに対応する表示色"""
    colors = {
        "alpha": "#E74C3C", "beta": "#3498DB", "gamma": "#2ECC71",
        "delta": "#F1C40F", "epsilon": "#9B59B6"
    }
    return colors.get(player_id, "gray")
