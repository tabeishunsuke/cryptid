class GameState:
    """
    ゲーム全体の進行状態を管理するクラス。

    管理する要素:
        - プレイヤーの順番・現在のターン
        - 現在のフェーズとアクション種別
        - キューブ／ディスクの配置数
        - 質問／探索に関するターゲットプレイヤーや配置フェーズ
        - アクション履歴（ログ）と再配置対象など

    フェーズ一覧:
        "init"   : 初期化中（まだ開始していない）
        "main"   : 通常プレイ中
        "end"    : 終了後（勝者決定）
    """

    def __init__(self, player_colors):
        # プレイヤーID例: ["alpha", "beta", "gamma"]
        self.players = player_colors
        self.n_players = len(player_colors)
        self.current_index = 0                        # ターン中プレイヤーのインデックス
        # "question", "search", "place_cube", etc.
        self.current_action = None
        self.target_player = None                     # 質問対象（インデックス）
        self.phase = "init"                           # "init", "main", "end"

        self.cube_count = {p: 0 for p in player_colors}   # キューブの配置数
        self.disk_count = {p: 0 for p in player_colors}   # ディスクの配置数

        self.history = []                             # ログ履歴（プレイ中の記録）
        self.pending_explore = None                   # ディスク再配置フェーズ用の仮探索情報
        self.exploration_target = None                # 現在探索対象の座標
        self.reveal_index = 0                         # 探索反証フェーズの順序管理

    @property
    def current_player(self):
        """現在ターンのプレイヤーIDを返す"""
        return self.players[self.current_index]

    def next_player(self):
        """手番を次のプレイヤーへ進める"""
        self.current_index = (self.current_index + 1) % self.n_players
        self.current_action = None
        self.target_player = None

    def begin_question(self, target_index):
        """質問フェーズの開始。対象プレイヤーのインデックスを設定"""
        self.current_action = "question"
        self.target_player = target_index

    def begin_search(self):
        """探索フェーズを開始"""
        self.current_action = "search"

    def log(self, message):
        """履歴ログに1件追加"""
        self.history.append(message)

    def reset(self):
        """ゲーム状態を初期化（リプレイ開始など）"""
        self.current_index = 0
        self.current_action = None
        self.phase = "init"
        self.cube_count = {p: 0 for p in self.players}
        self.disk_count = {p: 0 for p in self.players}
        self.history = []
        self.pending_explore = None
        self.exploration_target = None
        self.reveal_index = 0
