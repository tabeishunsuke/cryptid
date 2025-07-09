class HintEvaluator:
    """
    ヒントが盤面セルに合致するかどうかを判定するユーティリティクラス。

    対応ヒント種別：
    - 地形選択（terrain_choice / neg_terrain_choice）
    - 地形の近接条件
    - 構造物の近接条件（種類／色）
    - 縄張りの近接条件
    """

    @staticmethod
    def offset_to_cube(col, row):
        """
        Hex座標系（offset） → Cube座標系への変換
        - 距離計算で使用
        """
        x = col
        z = row - ((col - (col & 1)) // 2)
        y = -x - z
        return x, y, z

    @staticmethod
    def hex_distance(a, b):
        """
        Cube座標間の距離：3軸の最大差分を使用
        """
        x1, y1, z1 = HintEvaluator.offset_to_cube(*a)
        x2, y2, z2 = HintEvaluator.offset_to_cube(*b)
        return max(abs(x1 - x2), abs(y1 - y2), abs(z1 - z2))

    @staticmethod
    def is_nearby(match, target, distance, board_data):
        """
        指定座標 `match` の周囲に `target` 条件に合致するセルが存在するか判定
        - `target` は判定用のラムダ関数
        """
        coord = (match["col"], match["row"])
        for (cx, cy), other in board_data.items():
            if other is not None and target(other) and HintEvaluator.hex_distance(coord, (cx, cy)) <= distance:
                return True
        return False

    @staticmethod
    def hint_applies(cell, hint, board_data):
        """
        与えられたヒントがセル `cell` に適用されるか判定する。
        ヒント形式：{hint_type, param1, param2, text}
        """
        hint_type = hint["hint_type"]
        p1 = hint["param1"]
        p2 = hint["param2"]

        # 地形2択（大文字小文字考慮）
        if hint_type == "terrain_choice":
            terrain = cell.get("terrain", "")
            return isinstance(terrain, str) and terrain.lower() in [p1.lower(), p2.lower()]

        elif hint_type == "neg_terrain_choice":
            terrain = cell.get("terrain", "")
            return isinstance(terrain, str) and terrain.lower() not in [p1.lower(), p2.lower()]

        # 地形近接
        elif hint_type == "adjacent_terrain":
            return HintEvaluator.is_nearby(
                cell,
                lambda c: isinstance(c, dict) and isinstance(c.get("terrain"), str) and
                c.get("terrain").lower() == p1.lower(),
                int(p2), board_data
            )

        elif hint_type == "neg_adjacent_terrain":
            return not HintEvaluator.is_nearby(
                cell,
                lambda c: isinstance(c, dict) and isinstance(c.get("terrain"), str) and
                c.get("terrain").lower() == p1.lower(),
                int(p2), board_data
            )

        # 構造物の種類による近接
        elif hint_type == "adjacent_structure":
            return HintEvaluator.is_nearby(
                cell,
                lambda c: isinstance(c, dict) and isinstance(c.get("structure"), str) and
                c.get("structure").lower() == p1.lower(),
                int(p2), board_data
            )

        elif hint_type == "neg_adjacent_structure":
            return not HintEvaluator.is_nearby(
                cell,
                lambda c: isinstance(c, dict) and isinstance(c.get("structure"), str) and
                c.get("structure").lower() == p1.lower(),
                int(p2), board_data
            )

        # 構造物の色による近接
        elif hint_type == "adjacent_structure_by_color":
            return HintEvaluator.is_nearby(
                cell,
                lambda c: isinstance(c, dict) and isinstance(c.get("structure_color"), str) and
                c.get("structure_color").lower() == p1.lower(),
                int(p2), board_data
            )

        elif hint_type == "neg_adjacent_structure_by_color":
            return not HintEvaluator.is_nearby(
                cell,
                lambda c: isinstance(c, dict) and isinstance(c.get("structure_color"), str) and
                c.get("structure_color").lower() == p1.lower(),
                int(p2), board_data
            )

        # 縄張りの近接（配列比較）
        elif hint_type == "adjacent_territory":
            targets = [t.strip().lower() for t in p1.split(",")]
            return HintEvaluator.is_nearby(
                cell,
                lambda c: isinstance(c, dict) and isinstance(c.get("territories"), list) and
                any(t in [tt.lower() for tt in c.get("territories")
                    if isinstance(tt, str)] for t in targets),
                int(p2), board_data
            )

        elif hint_type == "neg_adjacent_territory":
            targets = [t.strip().lower() for t in p1.split(",")]
            return not HintEvaluator.is_nearby(
                cell,
                lambda c: isinstance(c, dict) and isinstance(c.get("territories"), list) and
                any(t in [tt.lower() for tt in c.get("territories")
                    if isinstance(tt, str)] for t in targets),
                int(p2), board_data
            )

        return False  # 未定義ヒントタイプは常に不一致
