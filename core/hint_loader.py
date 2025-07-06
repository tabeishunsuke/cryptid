import csv


class HintLoader:
    """
    Cryptidのヒント情報ローダー。
    - map_player_hints.csv: マップIDごとの冊子使用ページ定義
    - book_orders.csv: 冊子ページ → 冊子ごとの hint_id 定義
    - generic_hints.csv: hint_id → ヒントの詳細内容
    """

    def __init__(self,
                 generic_hint_csv="assets/configs/generic_hints.csv",
                 book_order_csv="assets/configs/book_orders.csv",
                 player_hint_csv="assets/configs/map_player_hints.csv"):
        self.generic_hint_csv = generic_hint_csv
        self.book_order_csv = book_order_csv
        self.player_hint_csv = player_hint_csv

        self.generic_hints = {}           # hint_id → hint情報
        self.book_orders = {}             # position → {alpha〜epsilon: hint_id}
        self.map_hint_mapping = {}        # map_id → {alpha〜epsilon: position}
        self.map_player_count = {}        # map_id → プレイヤー数

        # 初期化
        self._load_generic_hints()
        self._load_book_orders()
        self._load_player_hints()

    def _load_generic_hints(self):
        """
        generic_hints.csv を読み込み、hint_id をキーに辞書構造へ。
        """
        with open(self.generic_hint_csv, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    hid = int(row["hint_id"].strip())
                    self.generic_hints[hid] = {
                        "hint_type": row["hint_type"].strip(),
                        "param1": row["param1"].strip(),
                        "param2": row["param2"].strip(),
                        "text": row["text"].strip()
                    }
                except Exception as e:
                    print(f"[Hint Load Error] {e} → 行: {row}")

    def _load_book_orders(self):
        """
        book_orders.csv を読み込み、position（冊子ページ）ごとの冊子ごとの hint_id を格納。
        """
        with open(self.book_order_csv, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    position = int(row["position"].strip())
                    hint_map = {}
                    for pid in ["alpha", "beta", "gamma", "delta", "epsilon"]:
                        val = row.get(pid, "").strip()
                        if val.isdigit():
                            hint_map[pid] = int(val)
                    self.book_orders[position] = hint_map
                except Exception as e:
                    print(f"[Book Order Load Error] {e} → 行: {row}")

    def _load_player_hints(self):
        """
        map_player_hints.csv を読み込み、map_idごとの冊子使用ページを保持。
        """
        with open(self.player_hint_csv, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    map_id = int(row["map_id"].strip())
                    players = int(row["players"].strip())
                    hint_positions = {}
                    for pid in ["alpha", "beta", "gamma", "delta", "epsilon"]:
                        val = row.get(pid, "").strip()
                        if val.isdigit():
                            hint_positions[pid] = int(val)
                    self.map_hint_mapping[map_id] = hint_positions
                    self.map_player_count[map_id] = players
                except Exception as e:
                    print(f"[Map Hint Load Error] {e} → 行: {row}")

    def get_hint_for_map(self, map_id):
        """
        指定map_idに対応するプレイヤーID順とヒント情報を返す。

        Returns:
            player_ids: [str] 使用プレイヤー順
            hint_list: [dict] generic_hintsベースのヒント内容
        """
        if map_id not in self.map_hint_mapping:
            raise ValueError(f"マップID {map_id} に対する冊子情報が見つかりません")

        # 冊子使用ページ
        hint_pos_map = self.map_hint_mapping[map_id]

        player_ids = list(hint_pos_map.keys())[:self.map_player_count[map_id]]
        hint_list = []

        for pid in player_ids:
            position = hint_pos_map.get(pid)
            if position not in self.book_orders:
                raise ValueError(f"冊子ページ {position} の内容が見つかりません（プレイヤー {pid}）")

            hint_id = self.book_orders[position].get(pid)
            if hint_id not in self.generic_hints:
                raise ValueError(f"ヒントID {hint_id} が見つかりません（プレイヤー {pid}）")

            hint = self.generic_hints[hint_id]
            hint_list.append(hint)

        return player_ids, hint_list
