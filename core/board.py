class Board:
    """
    盤面上のタイル情報を管理するクラス。
    タイル情報（terrain, structure 等）は初期構築時に渡される。
    """

    def __init__(self, tile_data):
        self.tiles = tile_data  # dict[(col, row)] → セル情報

    def get_tile(self, coord):
        """指定座標のタイルを取得"""
        return self.tiles.get(coord)

    def is_valid_coord(self, coord):
        """指定座標が存在するか判定"""
        return coord in self.tiles

    def apply_hint(self, coord, hint):
        """
        ヒントがそのマスに適用されるか判定（HintEvaluator に委譲）
        """
        cell = self.get_tile(coord)
        if not cell:
            return False
        from core.hint_evaluator import HintEvaluator
        return HintEvaluator.hint_applies(cell, hint, self.tiles)

    def place_disc(self, coord, player_id):
        """ディスク配置（重複防止）"""
        cell = self.get_tile(coord)
        if not cell:
            return False
        discs = cell.setdefault("discs", [])
        if player_id not in discs:
            discs.append(player_id)
        return True

    def place_cube(self, coord, player_id):
        """キューブ配置（既存キューブがある場合は配置不可）"""
        cell = self.get_tile(coord)
        if not cell or cell.get("cube") is not None:
            return False
        cell["cube"] = player_id
        return True
