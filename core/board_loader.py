import csv
import os


def load_blocks(block_dir):
    """
    各ブロック CSV (col,row,terrain,territory) を読み込み、
    {(lc,lr):{"terrain","territories"}} を返す。
    structure はすべて None に。
    """
    blocks = {}
    for fn in os.listdir(block_dir):
        if not fn.endswith(".csv"):
            continue
        name = os.path.splitext(fn)[0]
        grid = {}
        with open(os.path.join(block_dir, fn),
                  newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                lc = int(row["col"])
                lr = int(row["row"])
                terrain = row["terrain"]
                # structure は CSV 側では未定義なので常に None
                structure = None

                raw = (row.get("territory") or "").strip()
                territories = [t.strip() for t in raw.split(",") if t.strip()]

                grid[(lc, lr)] = {
                    "terrain":     terrain,
                    "structure":   structure,
                    "territories": territories
                }
        blocks[name] = grid
    return blocks


def assemble_board(blocks, layout, block_cols, block_rows):
    """
    blocks: load_blocks() の返り値
    layout: [{'name':'block_X','rot':bool},…]
    block_cols/block_rows: ブロック配置の列数・行数
    """
    # ブロック内のタイル数を自動取得
    sample = next(iter(blocks.values()))
    block_w = max(c for c, _ in sample.keys()) + 1
    block_h = max(r for _, r in sample.keys()) + 1

    board = {}
    for idx, plc in enumerate(layout):
        bc, br = idx % block_cols, idx // block_cols
        name = plc["name"]
        rot = plc.get("rot", False)
        for (lc, lr), info in blocks[name].items():
            if rot:
                lc2 = block_w - 1 - lc
                lr2 = block_h - 1 - lr
            else:
                lc2, lr2 = lc, lr
            gc = bc * block_w + lc2
            gr = br * block_h + lr2
            board[(gc, gr)] = dict(info)
    return board
