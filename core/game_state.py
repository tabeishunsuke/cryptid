class GameState:
    """
    ゲーム全体の進行状態を管理するクラス。

    - ゲームフェーズ (phase): 全体進行管理 → "init", "active", "end"
    - プレイヤーアクション (current_action): ターン内操作 → "question", "search", "place_disc", "place_cube"
    """
    # ゲームフェーズ定義（進行管理用）
    PHASE_INIT = "init"
    PHASE_ACTIVE = "active"
    PHASE_END = "end"
    ALLOWED_PHASES = {PHASE_INIT, PHASE_ACTIVE, PHASE_END}

    # プレイヤーアクション定義（操作フェーズ用）
    ACTION_QUESTION = "question"
    ACTION_SEARCH = "search"
    ACTION_PLACE_DISC = "place_disc"
    ACTION_PLACE_CUBE = "place_cube"
    ALLOWED_ACTIONS = {ACTION_QUESTION, ACTION_SEARCH,
                       ACTION_PLACE_DISC, ACTION_PLACE_CUBE}

    def __init__(self, player_ids):
        # プレイヤーID例: ["alpha", "beta", "gamma"]
        self.players = player_ids                  # プレイヤーIDのリスト
        self.n_players = len(player_ids)          # プレイヤー数
        self.current_index = 0                        # ターン中プレイヤーのインデックス

        # "question", "search", "place_cube", etc.
        self.phase = GameState.PHASE_INIT  # ゲームフェーズ（初期状態は "init"）
        self.current_action = None                     # 現在のアクションフェーズ
        self.target_player = None                      # 質問対象プレイヤーのインデックス

        self.cube_count = {p: 0 for p in player_ids}   # キューブの配置数
        self.disk_count = {p: 0 for p in player_ids}   # ディスクの配置数

        self.history = []                             # ログ履歴（プレイ中の記録）
        self.pending_explore = None                   # ディスク再配置フェーズ用の仮探索情報
        self.exploration_target = None                # 現在探索対象の座標
        self.reveal_index = 0                         # 探索反証フェーズの順序管理

    @property
    def current_player(self):
        """現在ターンのプレイヤーIDを返す"""
        return self.players[self.current_index]

    def set_phase(self, phase_name):
        if phase_name in GameState.ALLOWED_PHASES:
            self.phase = phase_name
        else:
            raise ValueError(f"[GameState] 不正なフェーズ指定: '{phase_name}'")

    def set_action(self, action_name):
        if action_name in GameState.ALLOWED_ACTIONS or action_name is None:
            self.current_action = action_name
        else:
            raise ValueError(f"[GameState] 不正なアクション指定: '{action_name}'")

    def next_player(self):
        """手番を次のプレイヤーへ進める"""
        self.current_index = (self.current_index + 1) % self.n_players
        self.current_action = None
        self.target_player = None

    def begin_question(self, target_index):
        """質問フェーズの開始。対象プレイヤーのインデックスを設定"""
        self.set_action(GameState.ACTION_QUESTION)
        self.target_player = target_index

    def begin_search(self):
        """探索フェーズを開始"""
        self.set_action(GameState.ACTION_SEARCH)

    def log(self, message):
        """履歴ログに1件追加"""
        self.history.append(message)

    def reset(self):
        """ゲーム状態を初期化（リプレイ開始など）"""
        self.current_index = 0
        self.current_action = None
        self.set_phase(GameState.PHASE_INIT)
        self.cube_count = {p: 0 for p in self.players}
        self.disk_count = {p: 0 for p in self.players}
        self.history.clear()
        self.pending_explore = None
        self.exploration_target = None
        self.reveal_index = 0
