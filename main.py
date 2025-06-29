import os
import tkinter as tk

from core.board_loader import load_blocks, assemble_board
from core.map_loader import load_map_configs, select_random_map
from core.data_loader import (
    load_book_orders,
    load_generic_hints,
    load_map_player_hints
)
from core.hint_engine import apply_hint
from ui.board_view import (
    create_hex_board,
    grid_to_pixel,
    hex_corners
)

BLOCK_DIR = "assets/blocks"
CONFIG_DIR = "assets/configs"
IMAGE_DIR = "assets/terrain"
BLOCK_COLS = 2
BLOCK_ROWS = 3


def main():
    # 1. データ読み込み
    blocks = load_blocks(BLOCK_DIR)
    maps = load_map_configs(CONFIG_DIR)
    book_orders = load_book_orders(CONFIG_DIR)
    hints_def = load_generic_hints(CONFIG_DIR)
    mp_hints = load_map_player_hints(CONFIG_DIR)

    # 2. 任意の map_id とプレイヤー数を指定（デバッグ用）
    map_id = 10
    players = 3  # 必要に応じて 3～5 に変更可能

    map_info = maps.get(map_id)
    if not map_info:
        print(f"[!] map_id={map_id} が maps に存在しません")
        return

    # 3. マップヒント行を取得
    mp_row = next(
        (r for r in mp_hints if r["map_id"] == map_id and r["players"] == players), None)
    if not mp_row:
        print(f"[!] ヒントが定義されていない map_id={map_id}, players={players}")
        return

    # 4. プレイヤー順に列名と冊子positionのペアを抽出
    labels = ["alpha", "beta", "gamma", "delta", "epsilon"]
    positions_and_columns = []
    for label in labels:
        if len(positions_and_columns) >= players:
            break
        pos = mp_row.get(label)
        if pos is not None:
            positions_and_columns.append((pos, label))

    # 5. 各プレイヤーごとに、正しい冊子と列に対応するヒントIDを抽出
    hint_ids = []
    for pos, col in positions_and_columns:
        book = book_orders.get(pos)
        if book and col in book and book[col]:
            hint_ids.append(book[col])
        else:
            print(f"⚠ position={pos}, col={col} のヒントが見つかりません")

    # 6. hint_id → generic_hint を取得
    hints = []
    for hid in hint_ids:
        h = next((h for h in hints_def if h["hint_id"] == hid), None)
        if h:
            hints.append(h)
        else:
            print(f"⚠ ヒントID {hid} が generic_hints.csv に見つかりません")

    # 7. 盤面構築
    board_data = assemble_board(
        blocks, map_info["blocks"], BLOCK_COLS, BLOCK_ROWS)
    for s in map_info.get("structures", []):
        key = (s["col"], s["row"])
        if key in board_data:
            board_data[key]["structure"] = s["type"]
            board_data[key]["structure_color"] = s["color"]

    # 8. ヒント適用処理（途中ログ出力あり）
    candidates = set(board_data.keys())
    print(f"[開始] 候補タイル数: {len(candidates)}")
    for i, h in enumerate(hints):
        print(f"[{i+1}] ヒントID {h['hint_id']}: {h['text']}")
        candidates = apply_hint(board_data, h, candidates)
        print(f"     → 残り {len(candidates)} タイル")

    print(f"\n✅ map_id={map_id}, players={players} における正解タイル:")
    for coord in sorted(candidates):
        print(f"  {coord}")

    # 9. Tkinter 画面描画
    root = tk.Tk()
    root.title(f"Cryptid Map {map_id} — {players} players")
    canvas = tk.Canvas(root, width=800, height=600, bg="white")
    canvas.pack(fill="both", expand=True)

    # 地形画像読み込み
    terrain_imgs = {}
    for t in ("forest", "desert", "swamp", "sea", "mountain"):
        path = os.path.join(IMAGE_DIR, f"{t}.png")
        if os.path.exists(path):
            terrain_imgs[t] = tk.PhotoImage(file=path)
    canvas._terrain_imgs = terrain_imgs

    # 行列とサイズ
    sample = next(iter(blocks.values()))
    bw = max(c for c, _ in sample.keys()) + 1
    bh = max(r for _, r in sample.keys()) + 1
    rows = BLOCK_ROWS * bh
    cols = BLOCK_COLS * bw
    radius = 30

    # 盤面描画
    create_hex_board(canvas, board_data, rows, cols, radius, terrain_imgs)

    # 正解タイルをハイライト表示
    for c in candidates:
        x, y = grid_to_pixel(c[0], c[1], radius)
        pts = hex_corners(x, y, radius * 0.9)
        canvas.create_polygon(*pts, fill="yellow",
                              stipple="gray25", outline="")

    root.mainloop()


if __name__ == "__main__":
    main()
