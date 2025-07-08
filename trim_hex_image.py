import math
from PIL import Image, ImageDraw
from PIL import Image, ImageDraw
from PIL.Image import Resampling
"""
    正六角形の画像をトリミングして、余白を削除し、横幅100pxにリサイズする関数

    元画像の横幅の99%を正六角形の幅として使用し、マスクを生成してトリミング
    """


def trim_hex_image(input_path, output_path):
    # 1️⃣ 元画像読み込み
    img = Image.open(input_path).convert("RGBA")
    w, h = img.size

    # 2️⃣ 正六角形マスク生成（横幅の99%に調整）
    hex_width = w * 0.99
    radius = hex_width / 2
    center_x, center_y = w / 2, h / 2
    hex_points = []

    for i in range(6):
        angle_deg = 60 * i
        angle_rad = math.radians(angle_deg)
        x = center_x + radius * math.cos(angle_rad)
        y = center_y + radius * math.sin(angle_rad)
        hex_points.append((x, y))

    # 3️⃣ マスク作成
    mask = Image.new("L", img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.polygon(hex_points, fill=255)

    # 4️⃣ トリミング：画像にマスク適用
    hex_img = Image.new("RGBA", img.size)
    hex_img.paste(img, (0, 0), mask)

    # 5️⃣ クロップして余白を消す（正六角形だけ残す）
    bbox = mask.getbbox()
    hex_img = hex_img.crop(bbox)

    # 6️⃣ 横幅100pxにリサイズ（縦は比率で自動）
    final_img = hex_img.resize(
        (100, int(hex_img.height * 100 / hex_img.width)), Resampling.LANCZOS)

    # 7️⃣ PNG保存（透過あり）
    final_img.save(output_path, format="PNG")


terrain = "mountain"
input_path = f"assets/terrain/{terrain}_org.png"
output_path = f"assets/terrain/{terrain}.png"
# 使用例
trim_hex_image(input_path, output_path)
