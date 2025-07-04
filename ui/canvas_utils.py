import os
import tkinter as tk
import math


def grid_to_pixel(col, row, radius):
    """
    グリッド座標（col, row）をピクセル座標に変換する。
    """
    x = radius * 1.5 * col
    y = radius * math.sqrt(3) * (row + 0.5 * (col % 2))
    return x, y


def pixel_to_cell_coord(x, y, radius, canvas=None):
    """
    ピクセル座標 → ヘックスのグリッド座標（col, row）に変換する。

    キャンバスの中央オフセットを補正して正確な座標を得る。
    """
    if canvas and hasattr(canvas, "hex_offset"):
        ox, oy = canvas.hex_offset
        x -= ox
        y -= oy
    else:
        x -= radius + 10
        y -= radius + 10

    col = int(round(x / (1.5 * radius)))
    col_offset = 0.5 * radius * math.sqrt(3) if col % 2 else 0
    row = int(round((y - col_offset) / (radius * math.sqrt(3))))
    return col, row


def is_point_in_polygon(px, py, vertices):
    """
    点(px, py) が多角形 vertices 内にあるかを判定。
    射影法（偶数交差）に基づいている。
    """
    n = len(vertices)
    inside = False
    for i in range(n):
        x0, y0 = vertices[i]
        x1, y1 = vertices[(i + 1) % n]
        if ((y0 > py) != (y1 > py)) and (px < (x1 - x0) * (py - y0) / (y1 - y0 + 1e-9) + x0):
            inside = not inside
    return inside


def is_point_in_hex(px, py, col, row, radius, canvas):
    """
    マス(col, row) の六角形領域内に (px, py) が含まれるかを判定。
    中心座標と頂点からポリゴン境界で判断。
    """
    ox, oy = getattr(canvas, "hex_offset", (0, 0))
    cx = radius * 1.5 * col + ox
    cy = radius * math.sqrt(3) * (row + 0.5 * (col % 2)) + oy

    vertices = []
    for i in range(6):
        angle = math.radians(60 * i)
        vx = cx + radius * math.cos(angle)
        vy = cy + radius * math.sin(angle)
        vertices.append((vx, vy))

    return is_point_in_polygon(px, py, vertices)


def load_terrain_images(image_dir):
    """
    指定ディレクトリから地形画像（.png）を読み込む。
    """
    terrain_imgs = {}
    for t in ("forest", "desert", "swamp", "sea", "mountain"):
        path = os.path.join(image_dir, f"{t}.png")
        if os.path.exists(path):
            terrain_imgs[t] = tk.PhotoImage(file=path)
    return terrain_imgs


def create_turn_label(root):
    """
    ターン表示用のラベルを作成して返す。
    """
    frame = tk.Frame(root)
    frame.pack(side="top", fill="x")
    label = tk.Label(frame, text="", font=("Arial", 14))
    label.pack(side="left", padx=10)
    return label


def create_board_canvas(root):
    """
    盤面描画用のキャンバス領域を構築する。
    """
    canvas = tk.Canvas(root, bg="white")
    canvas.pack(fill="both", expand=True)
    radius = 45
    rows = 9
    cols = 12
    return canvas, radius, rows, cols
