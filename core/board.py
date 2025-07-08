class Board:
    """
    盤面情報（地形／構造物／縄張り／トークン）を管理するクラス。
    - セル情報の取得・判定
    - トークンの配置処理
    """

    def __init__(self, tile_data):
        self.tiles = tile_data  # dict[(col, row)] → セル情報

    def get_tile(self, coord):
        """指定座標のセル情報を取得（None安全）"""
        return self.tiles.get(coord)

    def is_valid_coord(self, coord):
        """指定座標が盤面に存在するか判定"""
        return coord in self.tiles

    def apply_hint(self, coord, hint):
        """指定座標にヒントが適用されるか判定（HintEvaluatorへ委譲）"""
        cell = self.get_tile(coord)
        if not cell:
            return False
        from core.hint_evaluator import HintEvaluator
        return HintEvaluator.hint_applies(cell, hint, self.tiles)

    def place_disc(self, coord, player_id):
        """ディスク配置処理：重複配置不可。成功なら True を返す"""
        print(f"[DEBUG] place_disc 呼び出し: coord={coord}, player_id={player_id}")
        cell = self.get_tile(coord)
        if not cell:
            return False
        discs = cell.setdefault("discs", [])
        if player_id not in discs:
            discs.append(player_id)
            return True
        return False  # すでに配置済み

    def place_cube(self, coord, player_id):
        """キューブ配置処理：既存キューブがある場合は失敗"""
        print(f"[DEBUG] place_cube 呼び出し: coord={coord}, player_id={player_id}")
        cell = self.get_tile(coord)
        if not cell or cell.get("cube") is not None:
            return False
        cell["cube"] = player_id
        return True
