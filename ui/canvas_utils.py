import math


def pixel_to_cell_coord(x, y, radius, margin_x=0, margin_y=0):
    """
    Flat-top 六角形のクリック座標 (x, y) → マス座標 (col, row) を返す。
    マージン補正付き。
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
    点(px, py) が多角形 vertices 内にあるかどうかを判定。
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
    マス(col, row) の六角形領域に (px, py) が含まれるか判定
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
    グリッド座標 (col, row) → ピクセル座標 (x, y)
    Flat-top 六角形の描画中心座標を算出
    """
    x = radius * 1.5 * col + margin_x
    y = radius * math.sqrt(3) * (row + 0.5 * (col % 2)) + margin_y
    return x, y


def draw_regular_polygon(canvas, x, y, radius, vertex, fill_color, outline_color="black", outline_width=1):
    """
    正多角形を描画するユーティリティ関数
    - canvas: TkinterのCanvasオブジェクト
    - x, y: 中心座標
    - radius: 中心から頂点までの距離
    - sides: 頂点の数（3=三角形、4=四角形、8=八角形など）
    - fill_color: 塗りつぶし色
    """
    points = []

    if vertex % 2 == 0:
        start_angle = math.pi / 2 + math.pi / vertex
    else:
        start_angle = math.pi / 2

    for i in range(vertex):
        angle = 2 * math.pi * i / vertex - start_angle
        px = x + radius * math.cos(angle)
        py = y + radius * math.sin(angle)
        points.extend([px, py])

    canvas.create_polygon(points, fill=fill_color,
                          outline=outline_color, width=outline_width)
