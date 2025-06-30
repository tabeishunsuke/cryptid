import math


def grid_to_pixel(gc, gr, r):
    """
    グリッド座標 (gc, gr) をキャンバス上のピクセル座標 (x, y) に変換する。

    - 対象は「フラットトップ」六角形（横向きに平らな六角形）
    - gc, gr: グローバルグリッド上の列・行番号
    - r: 六角形の外接円の半径（= 頂点から中心までの距離）

    計算概要：
    - x座標は 1.5 * r 間隔で横に伸びる（各列）
    - y座標は √3 * r 間隔で縦に伸びるが、奇数列では半分ずれる
    - 左上の角に余白として r を加える
    """
    x = gc * (1.5 * r) + r
    y = gr * (math.sqrt(3) * r) + (gc % 2) * (math.sqrt(3) * r / 2) + r
    return x, y


def hex_corners(x, y, r):
    """
    六角形の各頂点座標を (x, y) 中心・半径 r で計算して返す。

    - 角度は 0°→60°→…→300° の順で、時計回りの6頂点を返す。
    - 使用用途：create_polygon() に渡すための座標リスト。
    """
    pts = []
    for i in range(6):
        theta = math.radians(60 * i)
        pts.append((x + math.cos(theta) * r,
                    y + math.sin(theta) * r))
    return pts


def shape_pts(x, y, r, sides, rot_deg=0):
    """
    中心 (x, y) を起点とした正 n 角形の頂点リストを作る。

    - sides: 辺の数（例：3=三角形, 8=八角形）
    - rot_deg: 回転角（度）。図形の向き調整に使う（例：三角形の頂点を上にする）
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
    盤面情報 board_data に基づいて、Tkinter Canvas 上に六角形マップを描画する。

    引数:
        canvas: Tkinter.Canvas インスタンス
        board_data: {(col, row): {"terrain", "structure", "structure_color", "territories"}}
        rows, cols: マップの縦横マス数（※ここでは未使用だが reserve 用かも）
        radius: 各ヘクスの半径（r）
        terrain_images: {terrain名: PhotoImage} 地形ごとの描画用画像

    描画内容:
        1. 地形ごとの画像（背景）
        2. 六角形の枠線（黒線）
        3. 構造物（廃墟＝正三角形 / 巨石＝正八角形）
        4. 縄張り（ワシ＝赤枠 / クマ＝黒破線枠）
    """
    # --- 1. 地形画像（背景タイル） ---
    for (gc, gr), info in board_data.items():
        x, y = grid_to_pixel(gc, gr, radius)
        img = terrain_images.get(info["terrain"])
        if img:
            canvas.create_image(x, y, image=img)

    # --- 2. 六角形タイルの枠線 + 構造物 + 縄張り ---
    for (gc, gr), info in board_data.items():
        x, y = grid_to_pixel(gc, gr, radius)

        # 枠線（透明塗りつぶし、黒線）
        pts = hex_corners(x, y, radius)
        canvas.create_polygon(*pts,
                              fill="",
                              outline="black",
                              width=1)

        # 構造物の描画
        st = info.get("structure")
        clr = info.get("structure_color", "black")

        if st == "ruin":
            # 廃墟は上向き正三角形
            tri = shape_pts(x, y, radius * 0.5, sides=3, rot_deg=270)
            canvas.create_polygon(*tri, fill=clr, outline="")
        elif st == "stone":
            # 巨石は45度回転した正八角形
            octa = shape_pts(x, y, radius * 0.4, sides=8, rot_deg=22.5)
            canvas.create_polygon(*octa, fill=clr, outline="")

        # 縄張りの重ね描き（六角形内側に少し縮小）
        terr = info.get("territories", [])
        inner = hex_corners(x, y, radius * 0.8)
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
