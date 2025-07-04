# プレイヤーIDの内部表現と表示名の対応関係
INTERNAL_LABELS = ["alpha", "beta", "gamma", "delta", "epsilon"]
DISPLAY_LABELS = [f"プレイヤー{i + 1}" for i in range(len(INTERNAL_LABELS))]

# マッピング辞書（例: "alpha" → "プレイヤー1"）
LABEL_MAP = dict(zip(INTERNAL_LABELS, DISPLAY_LABELS))


def display_name(player_id):
    """
    内部ID（alpha〜epsilon）を表示用のラベルに変換する。

    Args:
        player_id (str): プレイヤー識別子（例: "alpha"）

    Returns:
        str: 表示名（例: "プレイヤー1"）
    """
    return LABEL_MAP.get(player_id, player_id)
