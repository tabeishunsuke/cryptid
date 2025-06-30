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

    各マスの構造物情報は本CSVには含まれないため、すべて None で初期化される。

    戻り値:
        dict[str, dict[(int, int), dict[str, Any]]]:
            ブロック名 → {(ローカル座標): {地形/構造物/縄張り}} の辞書
    """
    blocks = {}
    for fn in os.listdir(block_dir):
        if not fn.endswith(".csv"):
            continue  # CSVファイル以外は無視

        name = os.path.splitext(fn)[0]  # 例: "block_A.csv" → "block_A"
        grid = {}

        with open(os.path.join(block_dir, fn), newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # 座標と属性の取得
                lc = int(row["col"])        # ブロック内の列（ローカルX）
                lr = int(row["row"])        # ブロック内の行（ローカルY）
                terrain = row["terrain"]    # 地形タイプ
                structure = None            # 構造物は未定義（後付けされる）

                # 動物の縄張り：空欄にも対応しつつカンマで区切ってリスト化
                raw = (row.get("territory") or "").strip()
                territories = [t.strip() for t in raw.split(",") if t.strip()]

                # ローカル座標にマス情報を記録
                grid[(lc, lr)] = {
                    "terrain":     terrain,
                    "structure":   structure,
                    "territories": territories
                }

        # ブロック名で登録
        blocks[name] = grid

    return blocks


def assemble_board(blocks, layout, block_cols, block_rows):
    """
    ブロック情報をもとに全体盤面（board_data）を構築する。

    各ブロックはローカル座標系で記述されており、
    指定されたレイアウトと回転情報に従って、グローバルな盤面上に配置される。

    引数:
        blocks: load_blocks() の返り値。
            ブロック名 → {(lc, lr): {地形/構造物/縄張り}} の辞書。
        layout: ブロック配置のリスト。各要素は次の形式：
            {"name": "block_A", "rot": True} など
            rot=True で180度反転配置。
        block_cols (int): ブロックの横方向の並び数（例：3）
        block_rows (int): ブロックの縦方向の並び数（例：2）

    戻り値:
        dict[(int, int), dict[str, Any]]:
            グローバル座標 (col, row) → タイル属性辞書
    """
    # ブロックのサイズを取得（最初のブロックから推定）
    sample = next(iter(blocks.values()))
    block_w = max(c for c, _ in sample.keys()) + 1  # ブロックの横幅（列数）
    block_h = max(r for _, r in sample.keys()) + 1  # ブロックの縦幅（行数）

    board = {}

    for idx, plc in enumerate(layout):
        # ブロックの配置位置（グリッド上の列・行）
        bc = idx % block_cols
        br = idx // block_cols

        name = plc["name"]
        rot = plc.get("rot", False)

        # 対象ブロック内の各マスについて
        for (lc, lr), info in blocks[name].items():
            # 回転指定があれば180度反転
            if rot:
                lc2 = block_w - 1 - lc
                lr2 = block_h - 1 - lr
            else:
                lc2, lr2 = lc, lr

            # グローバル座標に変換
            gc = bc * block_w + lc2
            gr = br * block_h + lr2

            # 盤面上に登録（deep copy で安全確保）
            board[(gc, gr)] = dict(info)

    return board
