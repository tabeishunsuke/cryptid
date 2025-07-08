class Player:
    """
    プレイヤーの状態（ID／ヒント／表示名／色／トークン数）を管理するクラス
    - UI表示や探索判定に使用
    """

    def __init__(self, player_id, hint, display_name=None, color="gray"):
        self.id = player_id
        self.hint = hint
        self.display_name = display_name or player_id
        self.color = color
        self.disc_count = 0  # 配置したディスク数
        self.cube_count = 0  # 配置したキューブ数

    def add_disc(self):
        """ディスク配置時にカウントを加算"""
        self.disc_count += 1

    def add_cube(self):
        """キューブ配置時にカウントを加算"""
        self.cube_count += 1

    def reset(self):
        """ゲームリセット時にトークン数を初期化"""
        self.disc_count = 0
        self.cube_count = 0
