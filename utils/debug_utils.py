def find_solution_tiles(engine):
    """
    すべてのプレイヤーのヒントに一致するセル座標を抽出する（デバッグ用）
    Returns: List[(col, row)]
    """
    board = engine.board
    candidates = []
    for coord, cell in board.tiles.items():
        if all(board.apply_hint(coord, p.hint) for p in engine.players):
            candidates.append(coord)
    return candidates
