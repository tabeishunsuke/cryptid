class HintEvaluator:
    """
    ヒントが盤面のセルに合致するかを判定する静的クラス。
    地形・構造物・縄張り・距離などの条件に対応。
    """

    @staticmethod
    def offset_to_cube(col, row):
        """
        hex座標 (offset) を cube座標に変換（距離計算に使用）
        """
        x = col
        z = row - ((col - (col & 1)) // 2)
        y = -x - z
        return x, y, z

    @staticmethod
    def hex_distance(a, b):
        """
        2つの座標間の hex 距離を計算（最大差分を使用）
        """
        x1, y1, z1 = HintEvaluator.offset_to_cube(*a)
        x2, y2, z2 = HintEvaluator.offset_to_cube(*b)
        return max(abs(x1 - x2), abs(y1 - y2), abs(z1 - z2))

    @staticmethod
    def is_nearby(match, target, distance, board_data):
        """
        指定された distance 以内に target 条件に合致するセルが存在するか
        """
        coord = (match["col"], match["row"])
        for (cx, cy), other in board_data.items():
            if target(other) and HintEvaluator.hex_distance(coord, (cx, cy)) <= distance:
                return True
        return False

    @staticmethod
    def hint_applies(cell, hint, board_data):
        """
        ヒントが指定セルに適用されるか判定
        hint = {hint_type, param1, param2, text}
        """
        hint_type = hint["hint_type"]
        p1 = hint["param1"]
        p2 = hint["param2"]

        # 地形2択
        if hint_type == "terrain_choice":
            return cell.get("terrain") in [p1, p2]
        elif hint_type == "neg_terrain_choice":
            return cell.get("terrain") not in [p1, p2]

        # 地形の近接条件
        elif hint_type == "adjacent_terrain":
            return HintEvaluator.is_nearby(cell, lambda c: c.get("terrain") == p1, int(p2), board_data)
        elif hint_type == "neg_adjacent_terrain":
            return not HintEvaluator.is_nearby(cell, lambda c: c.get("terrain") == p1, int(p2), board_data)

        # 構造物の種類や色に関する近接条件
        elif hint_type == "adjacent_structure":
            return HintEvaluator.is_nearby(cell, lambda c: c.get("structure") == p1, int(p2), board_data)
        elif hint_type == "neg_adjacent_structure":
            return not HintEvaluator.is_nearby(cell, lambda c: c.get("structure") == p1, int(p2), board_data)
        elif hint_type == "adjacent_structure_by_color":
            return HintEvaluator.is_nearby(
                cell,
                lambda c: isinstance(
                    c.get("structure_color"), str) and c["structure_color"].lower() == p1.lower(),
                int(p2),
                board_data
            )
        elif hint_type == "neg_adjacent_structure_by_color":
            return not HintEvaluator.is_nearby(
                cell,
                lambda c: isinstance(
                    c.get("structure_color"), str) and c["structure_color"].lower() == p1.lower(),
                int(p2),
                board_data
            )

        # 縄張り関連の近接条件（territoriesに基づく）
        elif hint_type == "adjacent_territory":
            targets = [s.strip() for s in p1.split(",")]
            return HintEvaluator.is_nearby(cell, lambda c: any(t in c.get("territories", []) for t in targets), int(p2), board_data)
        elif hint_type == "neg_adjacent_territory":
            targets = [s.strip() for s in p1.split(",")]
            return not HintEvaluator.is_nearby(cell, lambda c: any(t in c.get("territories", []) for t in targets), int(p2), board_data)

        return False  # 未定義のヒントタイプ
