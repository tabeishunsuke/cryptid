import math

# --- 位置変換・距離計算（ヘクスグリッド用） ---


def offset_to_cube(col, row):
    """
    偶数縦長オフセット座標（col, row）を
    立方体座標系（x, y, z）に変換する

    ヘクスの距離計算を簡潔に行うために使用される。
    対象のオフセットは「列ごとに縦にずれるタイプ（even-q）」。
    """
    x = col
    z = row - ((col - (col & 1)) // 2)  # 偶数列補正（列が偶数なら0、奇数なら1）
    y = -x - z
    return x, y, z


def hex_distance(a, b):
    """
    ヘクスグリッド上の2点a, bの間の距離を算出する。

    対象：a, b は (col, row) 形式のタプル
    戻値：マンハッタン距離のような値（≒ マス数）
    """
    x1, y1, z1 = offset_to_cube(*a)
    x2, y2, z2 = offset_to_cube(*b)
    return max(abs(x1 - x2), abs(y1 - y2), abs(z1 - z2))


# --- ヒント適用エンジン（候補タイルの絞り込み） ---


def apply_hint(board_data, hint, candidates):
    """
    与えられたヒント1つに対して、現在の候補タイル集合をフィルタする。

    board_data:
        {(col, row): {
            "terrain": str,            # 地形種別（例："swamp"）
            "structure": str | None,   # 構造物の種類（例："shed"）
            "structure_color": str,    # 構造物の色（例："green"）
            "territories": list[str],  # 縄張り動物のリスト（例：["bear", "cougar"]）
        }}

    hint:
        {
            "hint_id": int,
            "hint_type": str,  # 条件タイプ（例："adjacent_terrain"）
            "param1": str,
            "param2": str,
            "text": str
        }

    candidates:
        {(col, row), ...}：現在の正解候補マス集合

    戻り値:
        new_cand: フィルタ後の候補マス集合
    """
    new_cand = set()
    h = hint["hint_type"]
    p1 = hint["param1"]
    p2 = hint["param2"]

    # -- [1] 地形が特定の種類（p1 or p2）かどうか --
    if h in ("terrain_choice", "neg_terrain_choice"):
        allow = {p1, p2}
        for c in candidates:
            t = board_data[c]["terrain"]
            ok = t in allow
            if h.startswith("neg_"):  # 否定ヒントなら反転
                ok = not ok
            if ok:
                new_cand.add(c)

    # -- [2] 特定地形が近くにある/ないか（p1: 地形名, p2: 距離） --
    elif h in ("adjacent_terrain", "neg_adjacent_terrain"):
        dist = int(p2)
        targets = [c for c, i in board_data.items() if i["terrain"] == p1]
        for c in candidates:
            close = any(hex_distance(c, t) <= dist for t in targets)
            if close == (h == "adjacent_terrain"):
                new_cand.add(c)

    # -- [3] 特定動物の縄張りに近い/遠いか（p1: "bear,cougar"等, p2: 距離） --
    elif h in ("adjacent_territory", "neg_adjacent_territory"):
        animals = [a.strip() for a in p1.split(",")]
        dist = int(p2)
        targets = [c for c, i in board_data.items()
                   if any(a in i.get("territories", []) for a in animals)]
        for c in candidates:
            close = any(hex_distance(c, t) <= dist for t in targets)
            if close == (h == "adjacent_territory"):
                new_cand.add(c)

    # -- [4] 特定種類の構造物に近い/遠いか（p1: "shed"等, p2: 距離） --
    elif h in ("adjacent_structure", "neg_adjacent_structure"):
        dist = int(p2)
        targets = [c for c, i in board_data.items()
                   if i.get("structure") == p1]
        for c in candidates:
            close = any(hex_distance(c, t) <= dist for t in targets)
            if close == (h == "adjacent_structure"):
                new_cand.add(c)

    # -- [5] 特定の構造物の色に近い/遠いか（p1: "green"等, p2: 距離） --
    elif h in ("adjacent_structure_by_color", "neg_adjacent_structure_by_color"):
        dist = int(p2)
        targets = [c for c, i in board_data.items()
                   if i.get("structure_color", "").lower() == p1.lower()]
        for c in candidates:
            close = any(hex_distance(c, t) <= dist for t in targets)
            if close == (h == "adjacent_structure_by_color"):
                new_cand.add(c)

    # 未知のヒントタイプはフィルタを行わずスルー
    else:
        return candidates

    return new_cand
