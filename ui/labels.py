def generate_display_labels(player_ids):
    """
    プレイヤーIDに対応する表示名を生成する。
    例: "alpha" → "プレイヤー1"
    """
    return {pid: f"プレイヤー{i + 1}" for i, pid in enumerate(player_ids)}


def display_name(pid, label_map=None):
    """
    表示名を取得（ラベルマップがある場合はそれを使用）
    """
    if label_map:
        return label_map.get(pid, pid)
    return pid
