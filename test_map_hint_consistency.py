from collections import defaultdict
from core.board_loader import load_blocks, assemble_board
from core.map_loader import load_map_configs
from core.data_loader import load_book_orders, load_generic_hints, load_map_player_hints
from core.hint_engine import apply_hint

BLOCK_DIR = "assets/blocks"
CONFIG_DIR = "assets/configs"
BLOCK_COLS = 2
BLOCK_ROWS = 3


def validate_all_map_hints():
    blocks = load_blocks(BLOCK_DIR)
    maps = load_map_configs(CONFIG_DIR)
    book_orders = load_book_orders(CONFIG_DIR)
    hints_def = load_generic_hints(CONFIG_DIR)
    mp_hints = load_map_player_hints(CONFIG_DIR)

    summary = defaultdict(list)

    for row in mp_hints:
        map_id = row["map_id"]
        players = row["players"]
        map_info = maps.get(map_id)
        if not map_info:
            continue

        # 冊子positionと列をプレイヤー順に取得
        labels = ["alpha", "beta", "gamma", "delta", "epsilon"]
        pos_col_pairs = []
        for label in labels:
            if len(pos_col_pairs) >= players:
                break
            pos = row.get(label)
            if pos is not None:
                pos_col_pairs.append((pos, label))

        # hint_id抽出
        hint_ids = []
        for pos, col in pos_col_pairs:
            book = book_orders.get(pos)
            if book and col in book and book[col]:
                hint_ids.append(book[col])

        # ヒント定義取得
        hints = []
        for hid in hint_ids:
            h = next((h for h in hints_def if h["hint_id"] == hid), None)
            if h:
                hints.append(h)

        # 盤面と構造物
        board_data = assemble_board(
            blocks, map_info["blocks"], BLOCK_COLS, BLOCK_ROWS)
        for s in map_info.get("structures", []):
            key = (s["col"], s["row"])
            if key in board_data:
                board_data[key]["structure"] = s["type"]
                board_data[key]["structure_color"] = s["color"]

        # ヒント適用
        candidates = set(board_data.keys())
        for h in hints:
            candidates = apply_hint(board_data, h, candidates)

        # 結果まとめ
        n = len(candidates)
        if n != 1:
            summary[n].append((map_id, players, hint_ids))

    # 結果表示
    if not summary:
        print("🎉 全ての map_id / players 組み合わせで正解タイルが1つでした！")
    else:
        print("\n✅ 正解が1つでないケース:")
        for n, items in sorted(summary.items()):
            print(f"候補数={n} のケース数={len(items)}")
            for mid, p, hids in items:
                print(f"  map_id={mid}, players={p} → hints={hids}")


if __name__ == "__main__":
    validate_all_map_hints()
