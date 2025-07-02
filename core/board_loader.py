import csv
import os


def load_blocks(block_dir):
    blocks = {}
    for fn in os.listdir(block_dir):
        if not fn.endswith(".csv"):
            continue
        name = os.path.splitext(fn)[0]
        grid = {}
        with open(os.path.join(block_dir, fn), newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                lc = int(row["col"])
                lr = int(row["row"])
                terrain = row["terrain"]
                raw = (row.get("territory") or "").strip()
                territories = [t.strip().lower()
                               for t in raw.split(",") if t.strip()]
                grid[(lc, lr)] = {
                    "terrain": terrain,
                    "territories": territories,
                }
        blocks[name] = grid
    return blocks


def assemble_board(blocks, layout, block_cols, block_rows):
    sample = next(iter(blocks.values()))
    block_w = max(c for c, _ in sample.keys()) + 1
    block_h = max(r for _, r in sample.keys()) + 1
    board = {}
    for idx, plc in enumerate(layout):
        bc = idx % block_cols
        br = idx // block_cols
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
            board[(gc, gr)] = dict(info)  # deepcopy安全策
    return board
