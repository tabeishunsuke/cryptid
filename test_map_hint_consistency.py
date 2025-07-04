from collections import defaultdict
from core.board_loader import load_blocks, assemble_board
from core.map_config_loader import load_map_configs
from core.hint_loader import load_book_orders, load_generic_hints, load_map_player_hints
from core.hint_engine import apply_hint

# 定数定義：ブロック構成やディレクトリパス
BLOCK_DIR = "assets/blocks"
CONFIG_DIR = "assets/configs"
BLOCK_COLS = 2
BLOCK_ROWS = 3


def validate_all_map_hints():
    """
    各マップID × プレイヤー人数の組み合わせに対して、
    ヒントを順に適用し、最終的な正解候補タイル数を検証する。

    - 候補数が1でないケースを収集して報告する。
    - 想定通りにヒントが定義・機能しているかどうかを確認できる。
    """
    blocks = load_blocks(BLOCK_DIR)
    maps = load_map_configs(CONFIG_DIR)
    book_orders = load_book_orders(CONFIG_DIR)
    hints_def = load_generic_hints(CONFIG_DIR)
    mp_hints = load_map_player_hints(CONFIG_DIR)

    summary = defaultdict(list)  # 候補数 → [(map_id, players, hint_ids), ...]

    for row in mp_hints:
        map_id = row["map_id"]
        players = row["players"]
        map_info = maps.get(map_id)
        if not map_info:
            continue  # 無効な map_id はスキップ

        # 冊子位置(position)と対応する列(label)を順に取得
        labels = ["alpha", "beta", "gamma", "delta", "epsilon"]
        pos_col_pairs = []
        for label in labels:
            if len(pos_col_pairs) >= players:
                break
            pos = row.get(label)
            if pos is not None:
                pos_col_pairs.append((pos, label))

        # 各プレイヤーから使用するヒントIDを取得
        hint_ids = []
        for pos, col in pos_col_pairs:
            book = book_orders.get(pos)
            if book and col in book and book[col]:
                hint_ids.append(book[col])

        # ヒントIDに対応するヒント定義を取得
        hints = []
        for hid in hint_ids:
            h = next((h for h in hints_def if h["hint_id"] == hid), None)
            if h:
                hints.append(h)

        # 盤面データ生成（構造物含む）
        board_data = assemble_board(
            blocks, map_info["blocks"], BLOCK_COLS, BLOCK_ROWS)
        for s in map_info.get("structures", []):
            key = (s["col"], s["row"])
            if key in board_data:
                board_data[key]["structure"] = s["type"]
                board_data[key]["structure_color"] = s["color"]

        # ヒントを順次適用して候補を絞り込む
        candidates = set(board_data.keys())
        for h in hints:
            candidates = apply_hint(board_data, h, candidates)

        # 結果を記録：正解タイルが一意でなければログに追加
        n = len(candidates)
        if n != 1:
            summary[n].append((map_id, players, hint_ids))

    # サマリ出力
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
