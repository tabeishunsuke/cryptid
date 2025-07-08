from tkinter import PhotoImage
import os


def load_terrain_images(folder="assets/terrain"):
    """
    指定フォルダ内の地形画像を読み込み、地形名をキーとした辞書として返す。

    Returns:
        dict[str, PhotoImage]: 地形名（例: "forest"） → 読み込んだ画像
    """
    terrain_types = ["forest", "desert", "mountain", "swamp", "sea"]
    terrain_imgs = {}

    for terrain in terrain_types:
        path = os.path.join(folder, f"{terrain}.png")
        try:
            terrain_imgs[terrain] = PhotoImage(file=path)
        except Exception as e:
            print(f"[Image Load Error] {terrain} の画像読込に失敗: {e}")

    return terrain_imgs
