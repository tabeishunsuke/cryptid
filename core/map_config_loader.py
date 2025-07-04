import csv
import os
import random


def load_map_configs(config_dir):
    """
    指定ディレクトリからマップ構成情報を読み込む。

    対象CSVファイル：
      - maps_config.csv : マップIDごとのブロック配置（最大6ブロック）と回転情報
      - structures.csv  : タイルごとの構造物配置と色

    戻り値：
        dict[int, dict[str, Any]]
          map_id → {
              "blocks": [ {"name": str, "rot": bool}, ... ],
              "structures": [ {"col": int, "row": int, "type": str, "color": str}, ... ]
          }
    """
    maps = {}

    # --- [1] ブロック配置構成読み込み ---
    config_path = os.path.join(config_dir, "maps_config.csv")
    with open(config_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            mid = int(row["map_id"])
            blocks = []
            for i in range(6):
                name_key = f"pos{i}"
                rot_key = f"pos{i}_rot"
                name = row[name_key].strip()
                raw_rot = row.get(rot_key, "0").strip().lower()
                rot = raw_rot in ("1", "true", "yes", "y")
                blocks.append({"name": name, "rot": rot})
            maps[mid] = {"blocks": blocks, "structures": []}

    # --- [2] 構造物配置構成読み込み ---
    structure_path = os.path.join(config_dir, "structures.csv")
    with open(structure_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            mid = int(row["map_id"])
            if mid not in maps:
                continue  # 無効な map_id は除外

            maps[mid]["structures"].append({
                "col": int(row["col"]),
                "row": int(row["row"]),
                "type": row["type"].strip(),
                "color": row["color"].strip()
            })

    return maps


def select_random_map(maps):
    """
    マップ設定からランダムに1つ選び、(map_id, map_info) を返す。

    Args:
        maps: load_map_configs() が返す dict

    Returns:
        (int, dict) : map_id と構成情報
    """
    mid = random.choice(list(maps.keys()))
    return mid, maps[mid]
