from core.board import Board
from core.player import Player
from core.game_state import GameState


class GameEngine:
    """
    ゲーム全体を統括するエンジンクラス。
    - ボードの初期化と管理
    - プレイヤー管理とターン操作
    - ゲーム状態の保持（current_player, phase など）
    """

    def __init__(self, player_ids, hints, board_data, label_map=None):
        # 🔧 ボード構築（盤面データを元に Board インスタンス化）
        self.board = Board(board_data)

        # 🎭 プレイヤーの初期化（ヒントと表示名の付与）
        self.players = []
        self.id_to_player = {}
        for i, pid in enumerate(player_ids):
            display = label_map.get(pid, pid) if label_map else pid
            player = Player(pid, hints[i], display_name=display)
            self.players.append(player)
            self.id_to_player[pid] = player

        # ⏱ ゲームのターン状態を持つ GameState を生成
        self.state = GameState(player_ids)

    def current_player(self):
        """現在のプレイヤーインスタンスを取得"""
        return self.id_to_player[self.state.current_player]

    def next_turn(self):
        """ターンを次プレイヤーへ進める"""
        self.state.next_player()

    def get_player_by_id(self, pid):
        """プレイヤーIDからインスタンスを取得"""
        return self.id_to_player.get(pid)

    def reset_game(self):
        """ゲーム全体を初期化（トークン数・ターン状態をリセット）"""
        for player in self.players:
            player.reset()
        self.state.reset()
