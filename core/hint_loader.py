import csv
import os


def load_book_orders(config_dir):
    """
    config_dir/book_orders.csv を読み込み、位置ごとの冊子対応表を返す。

    構造:
        position, alpha, beta, gamma, delta, epsilon

    戻り値:
        dict[int, dict[str, Optional[int]]]
            例）{ 1: { "alpha": 12, "beta": None, ... }, ... }
    """
    path = os.path.join(config_dir, "book_orders.csv")
    book_orders = {}

    with open(path, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                pos = int(row["position"].strip())
                book_orders[pos] = {
                    label: int(row[label].strip()) if row.get(
                        label, "").strip() else None
                    for label in ["alpha", "beta", "gamma", "delta", "epsilon"]
                }
            except Exception:
                continue
    return book_orders


def load_generic_hints(config_dir):
    """
    config_dir/generic_hints.csv を読み込み、一般ヒントの一覧を返す。

    ヒント形式:
        hint_id, hint_type, param1, param2, text
    """
    path = os.path.join(config_dir, "generic_hints.csv")
    with open(path, encoding="utf-8-sig") as f:
        lines = [line for line in f if line.strip(
        ) and not line.lstrip().startswith("#")]

    if not lines:
        return []

    header = [h.strip() for h in lines[0].split(",")]
    reader = csv.reader(lines[1:], skipinitialspace=True)

    hints = []
    for row in reader:
        if len(row) != len(header):
            continue
        rec = dict(zip(header, row))
        try:
            hints.append({
                "hint_id": int(rec["hint_id"]),
                "hint_type": rec["hint_type"].strip(),
                "param1": rec.get("param1", "").strip(),
                "param2": rec.get("param2", "").strip(),
                "text": rec.get("text", "").strip(),
            })
        except Exception:
            continue
    return hints


def load_map_player_hints(config_dir):
    """
    config_dir/map_player_hints.csv を読み込み、
    各マップIDとプレイヤー数に対応するヒント割り当てを返す。

    構造:
        map_id, players, alpha, beta, gamma, delta, epsilon
    """
    path = os.path.join(config_dir, "map_player_hints.csv")
    with open(path, encoding="utf-8-sig") as f:
        lines = [line for line in f if line.strip(
        ) and not line.lstrip().startswith("#")]

    if not lines:
        return []

    header = [h.strip() for h in lines[0].split(",")]
    reader = csv.reader(lines[1:], skipinitialspace=True)

    rows = []
    for row in reader:
        if len(row) != len(header):
            continue
        rec = dict(zip(header, row))
        try:
            rows.append({
                "map_id": int(rec["map_id"].strip()),
                "players": int(rec["players"].strip()),
                **{
                    label: int(rec[label].strip()) if rec.get(
                        label, "").strip() else None
                    for label in ["alpha", "beta", "gamma", "delta", "epsilon"]
                }
            })
        except Exception:
            continue
    return rows
