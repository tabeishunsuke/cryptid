import csv
import os
import random


def load_map_configs(config_dir):
    """
    指定ディレクトリからマップ構成ファイルを読み込む。

    対象ファイル:
      - maps_config.csv : マップIDごとのブロック配置（最大6ブロック）と回転情報
      - structures.csv  : マップID・タイル座標に配置する構造物とその色

    返り値:
        dict[int, dict[str, Any]] : 
            map_id → {
                "blocks": [{"name": str, "rot": bool}, ...],
                "structures": [{"col": int, "row": int, "type": str, "color": str}, ...]
            }
    """
    maps = {}

    # --- [1] maps_config.csv の読み込み ---
    cfg = os.path.join(config_dir, "maps_config.csv")
    with open(cfg, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            mid = int(row["map_id"])
            blocks = []
            for i in range(6):
                name_key = f"pos{i}"         # ブロック名カラム（例: "block_A"）
                rot_key = f"pos{i}_rot"      # 回転フラグカラム（例: "1", "yes", ...）
                name = row[name_key].strip()
                raw = row.get(rot_key, "0").strip().lower()
                rot = raw in ("1", "true", "yes", "y")  # ブール値へ変換
                blocks.append({"name": name, "rot": rot})

            # 各map_id に初期構造を追加
            maps[mid] = {"blocks": blocks, "structures": []}

    # --- [2] structures.csv の読み込み ---
    s_cfg = os.path.join(config_dir, "structures.csv")
    with open(s_cfg, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            mid = int(row["map_id"])
            if mid not in maps:
                continue  # maps_config に存在しない map_id は無視

            # タイルの構造物情報を抽出
            col = int(row["col"])
            row_i = int(row["row"])
            typ = row["type"].strip()
            clr = row["color"].strip()

            maps[mid]["structures"].append({
                "col":   col,
                "row":   row_i,
                "type":  typ,
                "color": clr
            })

    return maps


def select_random_map(maps):
    """
    マップ設定の中からランダムに1つを選び、(map_id, マップ情報) を返す。

    引数:
        maps: load_map_configs() が返す辞書
    戻り値:
        (int, dict) → map_id, map内容（ブロックと構造物情報）
    """
    mid = random.choice(list(maps.keys()))
    return mid, maps[mid]
