from PIL import Image, ImageDraw
import os
import math  # 正確な三角関数を計算するためのモジュールをインポート

"""
指定フォルダ内の画像ファイル（"xxx_original.png"）を正六角形にトリミングし、
"_original" を除いた名前で新たに保存するツール。
六角形は指定された半径（side_length）を用いて描画される。
"""


def crop_to_hexagon(input_folder, side_length=30):
    """
    指定フォルダ内の *_original.png 画像を対象に、中央を正六角形にトリミングして保存する。

    引数:
        input_folder (str): 入力画像のあるフォルダパス
        side_length (int): 六角形の外接円半径（中央から頂点までの距離）
    """
    for filename in os.listdir(input_folder):
        if filename.endswith("_original.png"):
            # 入出力ファイルパスを定義
            input_path = os.path.join(input_folder, filename)
            output_filename = filename.replace("_original", "")
            output_path = os.path.join(input_folder, output_filename)

            # 入力画像を読み込み、RGBAモードに変換
            img = Image.open(input_path).convert("RGBA")
            width, height = img.size
            center_x, center_y = width // 2, height // 2

            # 正六角形のマスクを作成（白=表示、黒=非表示）
            mask = Image.new("L", (width, height), 0)
            draw = ImageDraw.Draw(mask)

            # 六角形の頂点を計算（60度間隔）
            points = [
                (
                    center_x + side_length * math.cos(math.radians(angle)),
                    center_y + side_length * math.sin(math.radians(angle))
                )
                for angle in range(0, 360, 60)
            ]

            # マスクに六角形を描画
            draw.polygon(points, fill=255)

            # 画像とマスクを合成（マスクで切り抜いたRGBA画像を得る）
            img_cropped = Image.composite(
                img, Image.new("RGBA", img.size), mask)

            # 六角形の囲まれた矩形領域でクロップ（± side_length 範囲）
            img_cropped = img_cropped.crop((
                center_x - side_length, center_y - side_length,
                center_x + side_length, center_y + side_length
            ))

            # PNG形式で保存
            img_cropped.save(output_path, format="PNG")
            print(f"Processed: {filename} -> {output_filename}")


# スクリプト単体で実行された場合に処理を実行する
if __name__ == "__main__":
    input_folder = "C://work/cryptid_tkinter/assets/terrain"
    crop_to_hexagon(input_folder, side_length=30)
