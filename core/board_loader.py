import csv
import os


def load_blocks(block_dir):
    """
    指定ディレクトリ内の各ブロックCSVファイルを読み込み、
    各ブロックをローカル座標 (col, row) をキーにした辞書形式で保持する。

    期待されるCSVのカラム構成：
      - col (int): ブロック内の列番号
      - row (int): ブロック内の行番号
      - terrain (str): 地形タイプ（例："swamp", "forest"）
      - territory (str): カンマ区切りの動物名（空欄の場合あり）

    各マスの構造物情報は本CSVには含まれないため、後で別途構築される。

    戻り値:
        dict[str, dict[(int, int), dict[str, Any]]]:
            ブロック名 → {(ローカル座標): {地形/構造物/縄張り/コマ}} の辞書
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
                lc = int(row["col"])
                lr = int(row["row"])
                terrain = row["terrain"]
                structure = None

                raw = (row.get("territory") or "").strip()
                territories = [t.strip() for t in raw.split(",") if t.strip()]

                # ⬇️ ここで盤面状態を初期化（構造物・コマは後で補完）
                grid[(lc, lr)] = {
                    "terrain":     terrain,
                    "structure":   structure,
                    "structure_color": None,
                    "territories": territories,
                    "cube":        None,    # ← プレイヤー名 or None
                    "discs":       []       # ← ["alpha", "gamma"] など
                }

        blocks[name] = grid

    return blocks


def assemble_board(blocks, layout, block_cols, block_rows):
    """
    ブロック情報と配置レイアウトに基づいて、全体盤面を構築する。

    各ブロックはローカル座標系で構成されており、ブロックの回転指定に応じて
    グローバル座標へ展開される。

    引数:
        blocks: load_blocks() の返り値
        layout: [{"name": ..., "rot": bool}, ...]
        block_cols: 横方向のブロック数
        block_rows: 縦方向のブロック数

    戻り値:
        dict[(int, int), dict[str, Any]]:
            グローバル座標 → タイル情報の辞書（terrain, structure などを含む）
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

        for (lc, lr), info in blocks[name].items():
            if rot:
                lc2 = block_w - 1 - lc
                lr2 = block_h - 1 - lr
            else:
                lc2, lr2 = lc, lr

            gc = bc * block_w + lc2
            gr = br * block_h + lr2

            # deep copy（安全に扱うため）
            board[(gc, gr)] = dict(info)

    return board
