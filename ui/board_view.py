import math


def grid_to_pixel(gc, gr, r):
    """
    フラットトップ六角形の (gc,gr) → (x,y)
      ・横間隔 = 1.5 * r
      ・縦間隔 = √3 * r
      ・奇数列: y += (√3/2)*r
    左上にマージン r を足す
    """
    x = gc * (1.5 * r) + r
    y = gr * (math.sqrt(3) * r) + (gc % 2) * (math.sqrt(3) * r / 2) + r
    return x, y


def hex_corners(x, y, r):
    """
    true flat-top 六角形の6頂点
    角度: 0°,60°,120°,180°,240°,300°
    """
    pts = []
    for i in range(6):
        theta = math.radians(60 * i)
        pts.append((x + math.cos(theta) * r,
                    y + math.sin(theta) * r))
    return pts


def shape_pts(x, y, r, sides, rot_deg=0):
    """
    正 n 角形頂点リスト。中心(x,y), 半径 r, 回転オフセット rot_deg
    """
    pts = []
    for i in range(sides):
        theta = math.radians(rot_deg + 360 / sides * i)
        pts.append((x + math.cos(theta) * r,
                    y + math.sin(theta) * r))
    return pts


def create_hex_board(canvas,
                     board_data,
                     rows, cols,
                     radius,
                     terrain_images):
    """
    canvas: Tkinter.Canvas
    board_data: {(gc,gr):{"terrain","structure","structure_color","territories"}}
    terrain_images: {terrain:PhotoImage,…}
    """
    # 1) 地形画像貼り付け
    for (gc, gr), info in board_data.items():
        x, y = grid_to_pixel(gc, gr, radius)
        img = terrain_images.get(info["terrain"])
        if img:
            canvas.create_image(x, y, image=img)

    # 2) 枠線・構造物・縄張りを重ね描き
    for (gc, gr), info in board_data.items():
        x, y = grid_to_pixel(gc, gr, radius)

        # 六角形枠線
        pts = hex_corners(x, y, radius)
        canvas.create_polygon(*pts,
                              fill="",
                              outline="black",
                              width=1)

        # 構造物: 廃墟(ruin)=正三角形(頂点上向き), 巨石(stone)=正八角形
        st = info.get("structure")
        clr = info.get("structure_color", "black")
        if st == "ruin":
            tri = shape_pts(x, y, radius*0.5, sides=3, rot_deg=270)
            canvas.create_polygon(*tri,
                                  fill=clr, outline="")
        elif st == "stone":
            octa = shape_pts(x, y, radius*0.4, sides=8, rot_deg=22.5)
            canvas.create_polygon(*octa,
                                  fill=clr, outline="")

        # ワシ/クマ縄張り
        inner = hex_corners(x, y, radius*0.8)
        terr = info.get("territories", [])
        if "eagle" in terr:
            canvas.create_polygon(*inner,
                                  fill="",
                                  outline="red",
                                  width=2)
        if "bear" in terr:
            canvas.create_polygon(*inner,
                                  fill="",
                                  outline="black",
                                  dash=(30, 30),
                                  width=2)
