import csv
import os
import random


def load_map_configs(config_dir):
    """
    config_dir/maps_config.csv (map_id,pos0,pos0_rot,...,pos5,pos5_rot)
    と config_dir/structures.csv を読み込み、
    { map_id: {"blocks":[…], "structures":[…]} } を返す。
    """
    maps = {}

    # 1) maps_config.csv の読み込み
    cfg = os.path.join(config_dir, "maps_config.csv")
    with open(cfg, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            mid = int(row["map_id"])
            blocks = []
            for i in range(6):
                name_key = f"pos{i}"
                rot_key = f"pos{i}_rot"
                name = row[name_key].strip()
                raw = row.get(rot_key, "0").strip().lower()
                rot = raw in ("1", "true", "yes", "y")
                blocks.append({"name": name, "rot": rot})
            maps[mid] = {"blocks": blocks, "structures": []}

    # 2) structures.csv の読み込み
    s_cfg = os.path.join(config_dir, "structures.csv")
    with open(s_cfg, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            mid = int(row["map_id"])
            if mid not in maps:
                continue
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
    maps: load_map_configs() が返す dict
    ランダムに (map_id, map_info) を返す
    """
    mid = random.choice(list(maps.keys()))
    return mid, maps[mid]
