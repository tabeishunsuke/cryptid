# core/tile.py

class Tile:
    """
    ゲーム盤面の1タイルを表現するクラス。

    プロパティ:
      col, row         : グローバル座標
      center           : (x,y) 中心座標（Canvas 描画用）
      canvas_id        : 六角形ポリゴンのキャンバスID
      selected         : クリック選択フラグ
      terrain          : 地形タイプ文字列 ("forest"等)
      terrain_image_id : 地形画像のキャンバスID
      structure        : 構造物タイプ ("stone"/"ruin")
      structure_image_id: 構造物マークのキャンバスID
    """

    def __init__(self, col, row, center, canvas_id):
        self.col = col
        self.row = row
        self.center = center
        self.canvas_id = canvas_id
        self.selected = False
        self.terrain = None
        self.terrain_image_id = None
        self.structure = None
        self.structure_image_id = None

    def toggle_selected(self):
        """選択状態を反転し、UI で色を変えたいときに呼び出す"""
        self.selected = not self.selected
