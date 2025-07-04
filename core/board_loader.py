import csv
import os


def load_blocks(block_dir):
    """
    指定ディレクトリ内の CSV ファイル群を読み込み、
    ブロック名 → タイル情報マップとして返す。

    各ファイルは以下の形式を想定：
        col,row,terrain,territory
    """
    blocks = {}
    for fn in os.listdir(block_dir):
        if not fn.endswith(".csv"):
            continue
        name = os.path.splitext(fn)[0]
        grid = {}
        with open(os.path.join(block_dir, fn), newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                col = int(row["col"])
                row_i = int(row["row"])
                terrain = row["terrain"]
                raw = (row.get("territory") or "").strip()
                territories = [t.strip().lower()
                               for t in raw.split(",") if t.strip()]
                grid[(col, row_i)] = {
                    "terrain": terrain,
                    "territories": territories,
                }
        blocks[name] = grid
    return blocks


def assemble_board(blocks, layout, block_cols, block_rows):
    """
    ブロック配置レイアウトに従い、盤面を構築する。

    Args:
        blocks: 読み込んだブロックデータ
        layout: [{"name": str, "rot": bool}, ...] で構成される配置情報
        block_cols: 横方向のブロック数
        block_rows: 縦方向のブロック数

    Returns:
        dict[(col, row)] → タイル情報
    """
    sample = next(iter(blocks.values()))
    block_w = max(c for c, _ in sample.keys()) + 1
    block_h = max(r for _, r in sample.keys()) + 1

    board = {}

    for idx, plc in enumerate(layout):
        bc = idx % block_cols
        br = idx // block_cols
        name = plc["name"]
        rot = plc.get("rot", False)

        for (col, row), info in blocks[name].items():
            rotated_col = block_w - 1 - col if rot else col
            rotated_row = block_h - 1 - row if rot else row

            global_col = bc * block_w + rotated_col
            global_row = br * block_h + rotated_row

            board[(global_col, global_row)] = dict(info)  # copy safety
    return board
