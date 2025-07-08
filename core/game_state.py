class GameState:
    """
    ゲームの状態管理クラス。
    - 現在のフェーズ（init / active / end）
    - プレイヤーのアクション（質問 / 探索 / キューブ配置 等）
    - ターン順・進行ログ・探索進行フラグなど
    """

    # ゲーム全体の進行フェーズ
    PHASE_INIT = "init"
    PHASE_ACTIVE = "active"
    PHASE_END = "end"
    ALLOWED_PHASES = {PHASE_INIT, PHASE_ACTIVE, PHASE_END}

    # ターン内でのプレイヤーの操作フェーズ（行動タイプ）
    ACTION_QUESTION = "question"
    ACTION_SEARCH = "search"
    ACTION_PLACE_DISC = "place_disc"
    ACTION_PLACE_CUBE = "place_cube"
    ALLOWED_ACTIONS = {ACTION_QUESTION, ACTION_SEARCH,
                       ACTION_PLACE_DISC, ACTION_PLACE_CUBE}

    def __init__(self, player_ids):
        # 🧠 プレイヤー管理と順序定義
        self.players = player_ids
        self.n_players = len(player_ids)
        self.current_index = 0  # ターンプレイヤーのインデックス

        # 🎯 ゲーム状態フィールド
        self.phase = GameState.PHASE_INIT
        self.current_action = None
        self.target_player = None

        # 🧩 各プレイヤーのトークン配置履歴
        self.cube_count = {p: 0 for p in player_ids}
        self.disk_count = {p: 0 for p in player_ids}

        # 📝 プレイログ履歴（行動記録用）
        self.history = []

        # 🔍 探索フェーズ中の補助状態
        self.pending_explore = None
        self.exploration_target = None
        self.reveal_index = 0

    @property
    def current_player(self):
        """現在のターンプレイヤーIDを取得"""
        return self.players[self.current_index]

    def set_phase(self, phase_name):
        """ゲームフェーズを変更（init / active / end）"""
        if phase_name in GameState.ALLOWED_PHASES:
            self.phase = phase_name
        else:
            raise ValueError(f"[GameState] 不正なフェーズ: '{phase_name}'")

    def set_action(self, action_name):
        """ターン内のプレイヤー操作フェーズを変更"""
        if action_name in GameState.ALLOWED_ACTIONS or action_name is None:
            self.current_action = action_name
        else:
            raise ValueError(f"[GameState] 不正なアクション: '{action_name}'")

    def next_player(self):
        """次のプレイヤーにターンを移す"""
        self.current_index = (self.current_index + 1) % self.n_players
        self.current_action = None
        self.target_player = None

    def begin_question(self, target_index):
        """質問フェーズ開始：対象プレイヤーの記録をセット"""
        self.set_action(GameState.ACTION_QUESTION)
        self.target_player = target_index

    def begin_search(self):
        """探索フェーズ開始"""
        self.set_action(GameState.ACTION_SEARCH)

    def log(self, message):
        """プレイ履歴に1件追加"""
        self.history.append(message)

    def reset(self):
        """ゲーム状態全体を初期化（ゲーム再スタート時）"""
        self.current_index = 0
        self.current_action = None
        self.set_phase(GameState.PHASE_INIT)
        self.cube_count = {p: 0 for p in self.players}
        self.disk_count = {p: 0 for p in self.players}
        self.history.clear()
        self.pending_explore = None
        self.exploration_target = None
        self.reveal_index = 0
