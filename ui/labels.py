INTERNAL_LABELS = ["alpha", "beta", "gamma", "delta", "epsilon"]
DISPLAY_LABELS = [f"プレイヤー{i+1}" for i in range(len(INTERNAL_LABELS))]
LABEL_MAP = dict(zip(INTERNAL_LABELS, DISPLAY_LABELS))


def display_name(player_id):
    return LABEL_MAP.get(player_id, player_id)
