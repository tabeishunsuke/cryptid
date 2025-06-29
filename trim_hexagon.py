from PIL import Image, ImageDraw
import os
import math  # 正確な三角関数を計算するためのモジュールをインポート

"""
    画像を正六角形にトリミングして保存する関数
    ファイル名にxxx_original.pngが含まれる画像を対象とし、
    _originalを削除した名前で保存
"""


def crop_to_hexagon(input_folder, side_length=30):
    for filename in os.listdir(input_folder):
        if filename.endswith("_original.png"):  # "_original"付きのファイルを処理
            # 入力ファイルと出力ファイルのパス
            input_path = os.path.join(input_folder, filename)
            output_filename = filename.replace("_original", "")
            output_path = os.path.join(input_folder, output_filename)

            # 画像を開く
            img = Image.open(input_path).convert("RGBA")
            width, height = img.size
            center_x, center_y = width // 2, height // 2  # 画像の中心

            # マスク画像を作成（正六角形を定義）
            mask = Image.new("L", (width, height), 0)
            draw = ImageDraw.Draw(mask)

            # 正六角形の頂点を計算
            r = side_length  # 半径
            points = [
                (
                    center_x + r * math.cos(math.radians(angle)),
                    center_y + r * math.sin(math.radians(angle))
                )
                for angle in range(0, 360, 60)  # 60度間隔で計算
            ]

            # マスクに正六角形を描画
            draw.polygon(points, fill=255)

            # マスクを適用して画像をトリミング
            img_cropped = Image.composite(
                img, Image.new("RGBA", img.size), mask)

            # 正六角形の範囲だけを切り出す
            img_cropped = img_cropped.crop((
                center_x - side_length, center_y - side_length,
                center_x + side_length, center_y + side_length
            ))

            # PNG形式で保存
            img_cropped.save(output_path, format="PNG")
            print(f"Processed: {filename} -> {output_filename}")


# 実行部分
if __name__ == "__main__":
    input_folder = "C://work/cryptid_tkinter/assets/terrain"
    crop_to_hexagon(input_folder, side_length=30)
