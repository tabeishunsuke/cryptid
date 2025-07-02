import os
import tkinter as tk
import math


def grid_to_pixel(col, row, radius):
    x = radius * 3 / 2 * col
    y = radius * math.sqrt(3) * (row + 0.5 * (col % 2))
    return x + radius + 10, y + radius + 10  # 左上に余白


def pixel_to_grid(x, y, radius):
    # 左上のオフセット補正（grid_to_pixel と一致）
    x -= radius + 10
    y -= radius + 10

    col = int(round(x / (1.5 * radius)))
    col_offset = 0.5 * radius * math.sqrt(3) if col % 2 else 0
    row = int(round((y - col_offset) / (radius * math.sqrt(3))))

    return col, row


def load_terrain_images(image_dir):
    terrain_imgs = {}
    for t in ("forest", "desert", "swamp", "sea", "mountain"):
        path = os.path.join(image_dir, f"{t}.png")
        if os.path.exists(path):
            terrain_imgs[t] = tk.PhotoImage(file=path)
    return terrain_imgs


def create_turn_label(root):
    frame = tk.Frame(root)
    frame.pack(side="top", fill="x")
    label = tk.Label(frame, text="", font=("Arial", 14))
    label.pack(side="left", padx=10)
    return label


def create_board_canvas(root):
    width, height = 1600, 800  # キャンバスサイズ
    background_color = "white"  # 背景色
    canvas = tk.Canvas(root, width=width, height=height, bg=background_color)
    canvas.pack(fill="both", expand=True)
    radius = 45  # タイルサイズ
    rows = 9  # 行数
    cols = 12  # 列数
    return canvas, radius, rows, cols
