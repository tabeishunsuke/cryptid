from tkinter import PhotoImage


def load_terrain_images():
    """
    地形タイプに対応する画像を読み込み、辞書として返す。
    画像は assets/terrain/ に保存されている。
    """
    terrain_imgs = {
        "forest": PhotoImage(file="assets/terrain/forest.png"),
        "desert": PhotoImage(file="assets/terrain/desert.png"),
        "mountain": PhotoImage(file="assets/terrain/mountain.png"),
        "swamp": PhotoImage(file="assets/terrain/swamp.png"),
        "sea": PhotoImage(file="assets/terrain/sea.png")  # CSVでは "sea" 表記
    }
    return terrain_imgs
