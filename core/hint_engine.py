def hint_applies_to_cell(cell, hint, board_data):
    hint_type = hint["hint_type"]
    p1, p2 = hint["param1"], hint["param2"]
    print(
        f"[hint_engine] 判定: type={hint_type}, p1={p1}, p2={p2}, cell=({cell.get('col')}, {cell.get('row')})")

    if hint_type == "terrain_choice":
        return cell.get("terrain") in [p1, p2]

    elif hint_type == "neg_terrain_choice":
        return cell.get("terrain") not in [p1, p2]

    elif hint_type == "adjacent_terrain":
        return is_adjacent_to_terrain(cell, p1, int(p2), board_data)

    elif hint_type == "neg_adjacent_terrain":
        return not is_adjacent_to_terrain(cell, p1, int(p2), board_data)

    elif hint_type == "adjacent_structure":
        return is_adjacent_to_structure(cell, p1, int(p2), board_data)

    elif hint_type == "neg_adjacent_structure":
        return not is_adjacent_to_structure(cell, p1, int(p2), board_data)

    elif hint_type == "adjacent_structure_by_color":
        return is_adjacent_to_structure_color(cell, p1, int(p2), board_data)

    elif hint_type == "neg_adjacent_structure_by_color":
        return not is_adjacent_to_structure_color(cell, p1, int(p2), board_data)

    elif hint_type == "adjacent_territory":
        animals = [t.strip() for t in p1.split(",")]
        return is_adjacent_to_territory(cell, animals, int(p2), board_data)

    elif hint_type == "neg_adjacent_territory":
        animals = [t.strip() for t in p1.split(",")]
        return not is_adjacent_to_territory(cell, animals, int(p2), board_data)

    return False  # 安全なフォールバック


def offset_to_cube(col, row):
    x = col
    z = row - ((col - (col & 1)) // 2)
    y = -x - z
    return x, y, z


def hex_distance(a, b):
    x1, y1, z1 = offset_to_cube(*a)
    x2, y2, z2 = offset_to_cube(*b)
    return max(abs(x1 - x2), abs(y1 - y2), abs(z1 - z2))


def is_adjacent_to_structure_color(cell, color, distance, board_data):
    coord = (cell["col"], cell["row"])
    for (cx, cy), other in board_data.items():
        if other is None:
            continue
        if other.get("structure_color") and other["structure_color"].lower() == color.lower():
            if hex_distance(coord, (cx, cy)) <= distance:
                return True
    return False


def is_adjacent_to_structure(cell, structure, distance, board_data):
    coord = (cell["col"], cell["row"])
    for (cx, cy), other in board_data.items():
        if other.get("structure") == structure:
            if hex_distance(coord, (cx, cy)) <= distance:
                return True
    return False


def is_adjacent_to_terrain(cell, terrain, distance, board_data):
    coord = (cell["col"], cell["row"])
    for (cx, cy), other in board_data.items():
        if other.get("terrain") == terrain:
            if hex_distance(coord, (cx, cy)) <= distance:
                return True
    return False


def is_adjacent_to_territory(cell, animals, distance, board_data):
    coord = (cell["col"], cell["row"])
    for (cx, cy), other in board_data.items():
        if any(a in other.get("territories", []) for a in animals):
            if hex_distance(coord, (cx, cy)) <= distance:
                return True
    return False
