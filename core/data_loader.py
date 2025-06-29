import csv
import os


def load_book_orders(config_dir):
    """
    book_orders.csv を読み込み。
    - position（1〜96）ごとの冊子内容（alpha〜epsilon）を dict 形式で返す。
    - 空欄やスペースも許容。
    """
    import csv
    import os
    path = os.path.join(config_dir, "book_orders.csv")
    books = {}
    with open(path, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                pos = int(row["position"].strip())
                books[pos] = {
                    "alpha": int(row["alpha"].strip()) if row.get("alpha", "").strip() else None,
                    "beta":  int(row["beta"].strip()) if row.get("beta", "").strip() else None,
                    "gamma": int(row["gamma"].strip()) if row.get("gamma", "").strip() else None,
                    "delta": int(row["delta"].strip()) if row.get("delta", "").strip() else None,
                    "epsilon": int(row["epsilon"].strip()) if row.get("epsilon", "").strip() else None,
                }
            except Exception:
                continue  # 不正な行は無視
    return books


def load_generic_hints(config_dir):
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
                "hint_id":   int(rec["hint_id"]),
                "hint_type": rec["hint_type"].strip(),
                "param1":    rec.get("param1", "").strip(),
                "param2":    rec.get("param2", "").strip(),
                "text":      rec.get("text", "").strip(),
            })
        except Exception:
            continue
    return hints


def load_map_player_hints(config_dir):
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
                "alpha": int(rec["alpha"].strip()) if rec.get("alpha", "").strip() else None,
                "beta":  int(rec["beta"].strip()) if rec.get("beta", "").strip() else None,
                "gamma": int(rec["gamma"].strip()) if rec.get("gamma", "").strip() else None,
                "delta": int(rec["delta"].strip()) if rec.get("delta", "").strip() else None,
                "epsilon": int(rec["epsilon"].strip()) if rec.get("epsilon", "").strip() else None,
            })
        except Exception:
            continue
    return rows
