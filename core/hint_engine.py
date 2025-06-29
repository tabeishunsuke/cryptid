import math


def offset_to_cube(col, row):
    x = col
    z = row - ((col - (col & 1)) // 2)
    y = -x - z
    return x, y, z


def hex_distance(a, b):
    x1, y1, z1 = offset_to_cube(*a)
    x2, y2, z2 = offset_to_cube(*b)
    return max(abs(x1 - x2), abs(y1 - y2), abs(z1 - z2))


def apply_hint(board_data, hint, candidates):
    new_cand = set()
    h = hint["hint_type"]
    p1 = hint["param1"]
    p2 = hint["param2"]

    if h in ("terrain_choice", "neg_terrain_choice"):
        allow = {p1, p2}
        for c in candidates:
            t = board_data[c]["terrain"]
            ok = t in allow
            if h.startswith("neg_"):
                ok = not ok
            if ok:
                new_cand.add(c)

    elif h in ("adjacent_terrain", "neg_adjacent_terrain"):
        dist = int(p2)
        targets = [c for c, i in board_data.items() if i["terrain"] == p1]
        for c in candidates:
            close = any(hex_distance(c, t) <= dist for t in targets)
            new_cand.add(c) if close == (h == "adjacent_terrain") else None

    elif h in ("adjacent_territory", "neg_adjacent_territory"):
        animals = [a.strip() for a in p1.split(",")]
        dist = int(p2)
        targets = [c for c, i in board_data.items() if any(
            a in i.get("territories", []) for a in animals)]
        for c in candidates:
            close = any(hex_distance(c, t) <= dist for t in targets)
            new_cand.add(c) if close == (h == "adjacent_territory") else None

    elif h in ("adjacent_structure", "neg_adjacent_structure"):
        dist = int(p2)
        targets = [c for c, i in board_data.items()
                   if i.get("structure") == p1]
        for c in candidates:
            close = any(hex_distance(c, t) <= dist for t in targets)
            new_cand.add(c) if close == (h == "adjacent_structure") else None

    elif h in ("adjacent_structure_by_color", "neg_adjacent_structure_by_color"):
        dist = int(p2)
        targets = [c for c, i in board_data.items() if i.get(
            "structure_color", "").lower() == p1.lower()]
        for c in candidates:
            close = any(hex_distance(c, t) <= dist for t in targets)
            new_cand.add(c) if close == (
                h == "adjacent_structure_by_color") else None

    else:
        # fallback (pass through)
        return candidates

    return new_cand
