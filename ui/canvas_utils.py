import math


def pixel_to_cell_coord(x, y, radius, canvas):
    """
    ピクセル座標 (x, y) を盤面の hex座標 (col, row) に変換する。
    radius = 六角形のサイズ（pixel単位）

    この変換は完璧ではないが、おおよそ正しく動作する。
    """
    q = (x * math.sqrt(3)/3 - y / 3) / radius
    r = y * 2/3 / radius
    col = round(q)
    row = round(r)
    return col, row


def draw_regular_polygon(canvas, x, y, radius, vertex, fill_color):
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

    canvas.create_polygon(points, fill=fill_color)
