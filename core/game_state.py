# core/game_state.py

class GameState:
    """
    ゲーム進行を管理するクラス。

    - プレイヤー順序・現在のターン
    - 各プレイヤーの色名（"alpha", "beta", ...）
    - 使用済みキューブ / ディスク数（上限に応じて）
    - 現在のアクション（"question", "search", None）
    - 行動フェーズや履歴もここで一元管理する
    """

    def __init__(self, player_colors):
        self.players = player_colors           # 例: ["alpha", "beta", "gamma"]
        self.n_players = len(player_colors)
        self.current_index = 0                # 現在ターン中のプレイヤー番号
        self.current_action = None            # "question", "search", or None
        self.target_player = None             # 質問時の相手プレイヤーインデックス
        self.phase = "init"                   # "init", "main", "end"

        # 各プレイヤーの残りコマ数（必要なら制限数を設定）
        self.cube_count = {p: 0 for p in player_colors}
        self.disk_count = {p: 0 for p in player_colors}

        # アクション履歴（ログ用）
        self.history = []

    @property
    def current_player(self):
        return self.players[self.current_index]

    def next_player(self):
        """
        手番を次のプレイヤーに移す。
        """
        self.current_index = (self.current_index + 1) % self.n_players
        self.current_action = None
        self.target_player = None

    def begin_question(self, target_index):
        """
        質問フェーズを開始する。
        """
        self.current_action = "question"
        self.target_player = target_index

    def begin_search(self):
        """
        探索フェーズを開始する。
        """
        self.current_action = "search"

    def log(self, message):
        """
        プレイ履歴にメッセージを追記する。
        """
        self.history.append(message)

    def reset(self):
        """
        ゲーム全体を初期状態に戻す（再試行用）
        """
        self.current_index = 0
        self.current_action = None
        self.phase = "init"
        self.cube_count = {p: 0 for p in self.players}
        self.disk_count = {p: 0 for p in self.players}
        self.history = []
