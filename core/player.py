class Player:
    """
    プレイヤーの状態（ID・ヒント・トークン数など）を保持する。
    """

    def __init__(self, player_id, hint, display_name=None, color="gray"):
        self.id = player_id
        self.hint = hint
        self.display_name = display_name or player_id
        self.color = color
        self.disc_count = 0
        self.cube_count = 0

    def add_disc(self):
        """ディスク数を加算"""
        self.disc_count += 1

    def add_cube(self):
        """キューブ数を加算"""
        self.cube_count += 1

    def reset(self):
        """トークン数を初期化"""
        self.disc_count = 0
        self.cube_count = 0
