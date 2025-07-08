import math


def pixel_to_cell_coord(x, y, radius, margin_x=0, margin_y=0):
    """
    クリックされた画面座標 (x, y) を盤面のマス座標 (col, row) に変換する。

    対応する六角形は flat-top（平らな上辺）形式。
    マージン分を除いた位置で換算し、六角格子の縦横の間隔から算出する。

    Returns:
        (col, row): グリッド座標としてのマス位置
    """
    x -= margin_x
    y -= margin_y

    hex_height = math.sqrt(3) * radius
    horiz_spacing = 1.5 * radius

    col_f = x / horiz_spacing
    row_f = (y - 0.5 * hex_height * (round(col_f) % 2)) / hex_height

    col = round(col_f)
    row = round(row_f)
    return col, row


def is_point_in_polygon(px, py, vertices):
    """
    指定された点 (px, py) が、多角形 `vertices` の内部に含まれているか判定する。

    アルゴリズム：Ray casting 法に基づく交差数計算

    Returns:
        bool: True（内部） / False（外部）
    """
    inside = False
    n = len(vertices)
    for i in range(n):
        xi, yi = vertices[i]
        xj, yj = vertices[(i + 1) % n]
        if ((yi > py) != (yj > py)) and \
           (px < (xj - xi) * (py - yi) / (yj - yi + 1e-9) + xi):
            inside = not inside
    return inside


def is_point_in_hex(px, py, col, row, radius, margin_x=0, margin_y=0):
    """
    点 (px, py) が、指定マス (col, row) の六角形領域に含まれるか判定する。

    Flat-top形式の六角形の頂点座標を求めて、内部判定を行う。
    """
    cx, cy = grid_to_pixel(col, row, radius, margin_x, margin_y)

    vertices = []
    for i in range(6):
        angle = math.radians(60 * i - 30)
        vx = cx + radius * math.cos(angle)
        vy = cy + radius * math.sin(angle)
        vertices.append((vx, vy))

    return is_point_in_polygon(px, py, vertices)


def grid_to_pixel(col, row, radius, margin_x=0, margin_y=0):
    """
    マスのグリッド座標 (col, row) を、描画用のピクセル座標 (x, y) に変換する。

    Flat-top 六角形での配置ルールに従って、横方向1.5倍、縦方向 √3 間隔で換算する。
    """
    x = radius * 1.5 * col + margin_x
    y = radius * math.sqrt(3) * (row + 0.5 * (col % 2)) + margin_y
    return x, y


def draw_regular_polygon(canvas, x, y, radius, vertex, fill_color,
                         outline_color="black", outline_width=1):
    """
    指定された canvas 上に、正n角形（通常：六角形、三角形、八角形など）を描画する。

    Params:
        canvas: TkinterのCanvasインスタンス
        x, y: 中心座標
        radius: 頂点までの距離（外接円の半径）
        vertex: 頂点数（3=三角形, 6=六角形 等）
        fill_color: 塗りつぶしの色
        outline_color: 枠線の色
        outline_width: 枠線の太さ（px）
    """
    points = []

    # 偶数頂点なら角度を回転して整形（上辺が水平になるように）
    start_angle = math.pi / 2 + (math.pi / vertex if vertex % 2 == 0 else 0)

    for i in range(vertex):
        angle = 2 * math.pi * i / vertex - start_angle
        px = x + radius * math.cos(angle)
        py = y + radius * math.sin(angle)
        points.extend([px, py])

    canvas.create_polygon(
        points,
        fill=fill_color,
        outline=outline_color,
        width=outline_width
    )
