import csv
import os


class MapConfigLoader:
    """
    地形構成（ブロックA〜F）を読み込んで盤面を構築するローダー。
    - map_config.csv: 各マップIDに対応するブロック配置と回転情報
    - assets/blocks/*.csv: 各ブロックの地形・縄張り情報
    - structures.csv: 構造物の種類と配置座標を追加
    """

    def __init__(self,
                 map_csv="assets/configs/map_config.csv",
                 blocks_dir="assets/blocks/",
                 structures_csv="assets/configs/structures.csv"):
        self.map_csv = map_csv
        self.blocks_dir = blocks_dir
        self.structures_csv = structures_csv
        self.maps = {}  # map_id → {positions, tiles}

        self._load_maps()
        self._load_structures()

    def _load_maps(self):
        """
        マップ構成CSVからブロック配置と回転を読み込み、全マップの盤面を生成する。
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

        # 🔁 各マップごとの構成からブロックデータ読込 → タイル展開
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

                # 🔄 rot==1 の場合は180度反転（左右＋上下反転）
                if rot == 1:
                    tiles = [{
                        "col": 5 - t["col"],  # 最大col=5（0-indexed）
                        "row": 2 - t["row"],  # 最大row=2
                        "terrain": t["terrain"],
                        "territory": t["territory"]
                    } for t in tiles]

                # 🧮 ブロック配置位置のオフセット計算
                col_offset = (i % 2) * 6  # 偶奇で横方向：0 or 6
                row_offset = (i // 2) * 3  # 3行ブロックごとに上下方向：0, 3, 6

                for t in tiles:
                    col = t["col"] + col_offset
                    row_ = t["row"] + row_offset
                    key = (col, row_)
                    cell = {
                        "col": col,
                        "row": row_,
                        "terrain": t["terrain"],
                        "territories": [t["territory"]] if t["territory"] else [],
                        "structure": None,
                        "structure_color": None,
                        "discs": [],
                        "cube": None
                    }
                    map_info["tiles"][key] = cell

    def _load_structures(self):
        """
        構造物CSVから、各マップの該当セルに構造物情報（種類／色）を追加する。
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
        """使用可能なマップID一覧を返す"""
        return sorted(self.maps.keys())

    def load_map(self, map_id):
        """指定マップIDに対応するタイル情報を返す"""
        return self.maps.get(map_id, {}).get("tiles", {})
