from core.board import Board
from core.player import Player
from core.game_state import GameState


class GameEngine:
    """
    ゲーム全体を管理するコントローラークラス。
    - ボード状態の初期化と保持
    - プレイヤー情報の構築と ID マッピング
    - ターン・アクション状態の保持（GameStateと連携）
    """

    def __init__(self, player_ids, hints, board_data, label_map=None, color_map=None):
        # 🧱 ボード構築
        self.board = Board(board_data)

        # 🎭 プレイヤー構築（ID → ヒント → ラベル／カラー）
        self.players = []
        self.id_to_player = {}
        for i, pid in enumerate(player_ids):
            display = label_map.get(pid, pid) if label_map else pid
            color = color_map.get(pid, "gray") if color_map else "gray"
            player = Player(pid, hints[i], display_name=display, color=color)
            self.players.append(player)
            self.id_to_player[pid] = player

        # 🎯 ゲーム状態（フェーズ・ターンなど）初期化
        self.state = GameState(player_ids)
        self.label_map = label_map or {}

    def current_player(self):
        """現在手番のプレイヤーインスタンスを取得"""
        return self.id_to_player[self.state.current_player]

    def next_turn(self):
        """ターンを次プレイヤーに進める"""
        self.state.next_player()

    def get_player_by_id(self, pid):
        """指定IDのプレイヤーインスタンスを取得"""
        return self.id_to_player.get(pid)

    def reset_game(self):
        """ゲームの再初期化（トークン・状態のリセット）"""
        for player in self.players:
            player.reset()
        self.state.reset()
