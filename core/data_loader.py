import csv
import os


def load_book_orders(config_dir):
    """
    指定ディレクトリ内の book_orders.csv を読み込み、各 position（1〜96）ごとに
    使用する冊子の種類（alpha〜epsilon）を記録した辞書を返す。

    各行には以下のような形式が想定される：
      position, alpha, beta, gamma, delta, epsilon

    空欄セルは None として扱い、スペースなども安全に除去する。
    不正な行（パース不可、列不足など）はスキップされる。

    戻り値:
        dict[int, dict[str, Optional[int]]]:
            例）{ 1: { "alpha": 12, "beta": None, ... }, ... }
    """
    path = os.path.join(config_dir, "book_orders.csv")
    books = {}

    with open(path, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                pos = int(row["position"].strip())  # 位置キー（1〜96）
                books[pos] = {
                    "alpha": int(row["alpha"].strip()) if row.get("alpha", "").strip() else None,
                    "beta":  int(row["beta"].strip()) if row.get("beta", "").strip() else None,
                    "gamma": int(row["gamma"].strip()) if row.get("gamma", "").strip() else None,
                    "delta": int(row["delta"].strip()) if row.get("delta", "").strip() else None,
                    "epsilon": int(row["epsilon"].strip()) if row.get("epsilon", "").strip() else None,
                }
            except Exception:
                continue  # 不正なデータ行は無視
    return books


def load_generic_hints(config_dir):
    """
    指定ディレクトリ内の generic_hints.csv を読み込み、一般ヒント情報を辞書リストとして返す。

    CSVファイルの構造（想定）：
      hint_id, hint_type, param1, param2, text
    - 空行および '#' で始まるコメント行は無視
    - param1, param2, text は空欄が許容される

    戻り値:
        list[dict[str, Any]]:
            各行の内容が辞書化され、整数IDや文字列のパラメータとして整形される。
    """
    path = os.path.join(config_dir, "generic_hints.csv")
    with open(path, encoding="utf-8-sig") as f:
        # 空行・コメント行を除外
        lines = [line for line in f if line.strip(
        ) and not line.lstrip().startswith("#")]

    if not lines:
        return []

    header = [h.strip() for h in lines[0].split(",")]
    reader = csv.reader(lines[1:], skipinitialspace=True)

    hints = []
    for row in reader:
        if len(row) != len(header):
            continue  # 列数が一致しない行はスキップ
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
            continue  # パースに失敗した行は除外
    return hints


def load_map_player_hints(config_dir):
    """
    指定ディレクトリ内の map_player_hints.csv を読み込み、
    各マップID・プレイヤー数に対応したヒントID群を辞書リストとして返す。

    各行は以下の形式を想定：
      map_id, players, alpha, beta, gamma, delta, epsilon
    空欄は None として処理される。コメント・空行は無視される。

    戻り値:
        list[dict[str, Any]]:
            例）{ "map_id": 1, "players": 3, "alpha": 14, ... }
    """
    path = os.path.join(config_dir, "map_player_hints.csv")
    with open(path, encoding="utf-8-sig") as f:
        # 空行・コメント行を除外
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
