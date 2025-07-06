import csv
import os


class MapConfigLoader:
    """
    地形構成（blockA〜F）を読み込んで盤面を構築するローダークラス。
    - map_config.csv で各マップIDのブロック配置と回転情報を管理
    - 各ブロックCSVから座標・地形・縄張りを読み込む
    - structures.csv で構造物を盤面に追加する
    """

    def __init__(self,
                 map_csv="assets/configs/map_config.csv",
                 blocks_dir="assets/blocks/",
                 structures_csv="assets/configs/structures.csv"):
        self.map_csv = map_csv                    # ブロック構成CSV（マップごとの配置情報）
        self.blocks_dir = blocks_dir              # ブロックCSVの保存ディレクトリ
        self.structures_csv = structures_csv      # 構造物配置CSV
        self.maps = {}                            # map_id → {positions, tiles}
        self._load_maps()                         # マップ構築処理
        self._load_structures()                   # 構造物読み込み処理

    def _load_maps(self):
        """
        マップIDごとのブロック配置を読み込み、タイルデータ（盤面構成）を構築する。
        """
        with open(self.map_csv, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                mid = int(row["map_id"])
                positions = []
                for i in range(6):
                    block = row[f"pos{i}"].strip().lower()
                    rot = int(row[f"pos{i}_rot"])
                    positions.append((block, rot))
                self.maps[mid] = {"positions": positions, "tiles": {}}

        # 各マップごとにブロックCSVを読み込む
        for mid, map_info in self.maps.items():
            for i, (block, rot) in enumerate(map_info["positions"]):
                path = os.path.join(self.blocks_dir, f"{block}.csv")
                if not os.path.isfile(path):
                    continue

                with open(path, encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    tiles = []
                    for row in reader:
                        col = int(row["col"])
                        row_ = int(row["row"])
                        terrain = row["terrain"].strip()
                        territory = row.get("territory", "").strip()

                        tiles.append({
                            "col": col,
                            "row": row_,
                            "terrain": terrain,
                            "territory": territory
                        })

                # 🎯 回転処理（180度反転）← rot = 1 の場合
                if rot == 1:
                    tiles = [{
                        "col": 5 - t["col"],  # 0-indexed → 最大col=5
                        "row": 2 - t["row"],  # 最大row=2
                        "terrain": t["terrain"],
                        "territory": t["territory"]
                    } for t in tiles]

                # 🎯 配置位置計算（縦3 × 横2 → 6箇所にオフセット）
                col_offset = (i % 2) * 6      # 0 or 6
                row_offset = (i // 2) * 3     # 0, 3, 6

                for t in tiles:
                    col = t["col"] + col_offset
                    row_ = t["row"] + row_offset
                    key = (col, row_)

                    cell = {
                        "col": col,
                        "row": row_,
                        "terrain": t["terrain"],
                        "territories": [],
                        "structure": None,
                        "structure_color": None,
                        "discs": [],
                        "cube": None
                    }
                    if t["territory"]:
                        cell["territories"].append(t["territory"])

                    map_info["tiles"][key] = cell

    def _load_structures(self):
        """
        構造物CSVから各マップに構造物タイプ・色を追加する。
        """
        with open(self.structures_csv, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                mid = int(row["map_id"])
                key = (int(row["col"]), int(row["row"]))
                if mid in self.maps and key in self.maps[mid]["tiles"]:
                    self.maps[mid]["tiles"][key]["structure"] = row["type"].strip()
                    self.maps[mid]["tiles"][key]["structure_color"] = row["color"].strip()

    def get_available_map_ids(self):
        """
        利用可能なマップIDの一覧を返す。
        """
        return sorted(self.maps.keys())

    def load_map(self, map_id):
        """
        指定した map_id に対応する盤面データ（tiles）を返す。
        """
        return self.maps.get(map_id, {}).get("tiles", {})
