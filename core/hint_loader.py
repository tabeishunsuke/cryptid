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

    def get_players_for_map(self, map_id, player_count):
        """
        指定マップIDとプレイヤー数に応じたプレイヤー情報リストを返す。

        Returns:
            List[Dict] → [{id: "player1", book: "alpha", hint: {...}}, ...]
        """
        order = ["alpha", "beta", "gamma", "delta", "epsilon"]

        with open(self.player_hint_csv, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                m_id = int(row["map_id"].strip())
                p_count = int(row["players"].strip())
                if m_id != map_id or p_count != player_count:
                    continue

                players = []
                idx = 0
                for book in order:
                    val = row.get(book, "").strip()
                    if val.isdigit():
                        position = int(val)
                        if position not in self.book_orders:
                            raise ValueError(
                                f"冊子ページ {position} が book_orders に存在しません")

                        hint_id = self.book_orders[position].get(book)
                        if hint_id not in self.generic_hints:
                            raise ValueError(
                                f"ヒントID {hint_id} が generic_hints に存在しません")

                        hint = self.generic_hints[hint_id]
                        players.append({
                            "id": f"player{idx + 1}",
                            "book": book,
                            "hint": hint
                        })
                        idx += 1

                if len(players) != player_count:
                    raise ValueError(f"{player_count}人分のプレイヤーデータが構成されませんでした")

                return players

        raise ValueError(
            f"map_id={map_id}, player_count={player_count} に一致する行が見つかりません")
