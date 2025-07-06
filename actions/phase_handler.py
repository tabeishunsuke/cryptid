from tkinter import messagebox
from core.hint_evaluator import HintEvaluator
from ui.labels import display_name


class PhaseHandler:
    """
    プレイヤーのクリックに応じてゲームの各フェーズ（質問・配置・探索）を処理するクラス。
    """

    def __init__(self, engine, canvas, root, turn_label,
                 terrain_imgs, radius, rows, cols, renderer):
        self.engine = engine         # ゲーム進行管理エンジン
        self.canvas = canvas         # 描画キャンバス
        self.root = root             # Tkinterルートウィンドウ（終了やダイアログ用）
        self.turn_label = turn_label  # ターン表示ラベル
        self.terrain_imgs = terrain_imgs
        self.radius = radius
        self.rows = rows
        self.cols = cols
        self.renderer = renderer     # BoardRenderer インスタンス

    def handle_click(self, coord):
        """
        プレイヤーがマスをクリックしたときの処理。
        フェーズに応じて分岐処理を行う。
        """
        if not self.engine.board.is_valid_coord(coord):
            return

        current = self.engine.current_player()
        state = self.engine.state
        cell = self.engine.board.get_tile(coord)

        # --- 質問フェーズ ---
        if state.current_phase == "question":
            self._handle_question(current, cell, coord)

        # --- 配置フェーズ ---
        elif state.current_phase == "place_disc":
            self._handle_disc_placement(current, cell, coord)

        # --- 探索フェーズ ---
        elif state.current_phase == "search":
            self._handle_search(current, cell, coord)

    def _handle_question(self, current, cell, coord):
        """
        質問フェーズの処理：他プレイヤーに自分のヒントで照合
        """
        others = [p for p in self.engine.players if p != current]
        target = others[0]  # ← 本来は UI で選択させるべき
        applies = HintEvaluator.hint_applies(
            cell, target.hint, self.engine.board.tiles)

        # 判定結果に応じて配置フェーズへ
        if applies:
            self.engine.state.set_phase("place_disc")
        else:
            self.engine.state.set_phase("search")

        self.turn_label.config(
            text=f"{display_name(current.id, current.display_name)} - フェーズ: {self.engine.state.current_phase}")

    def _handle_disc_placement(self, current, cell, coord):
        """
        ディスク配置フェーズの処理
        """
        success = self.engine.board.place_disc(coord, current.id)
        if success:
            current.add_disc()
            self._advance_turn()

    def _handle_search(self, current, cell, coord):
        """
        探索フェーズの処理：全プレイヤーのヒント照合
        """
        all_match = True
        for player in self.engine.players:
            if not HintEvaluator.hint_applies(cell, player.hint, self.engine.board.tiles):
                self.engine.board.place_disc(coord, player.id)
                player.add_disc()
                all_match = False
        if all_match:
            self.engine.board.place_cube(coord, current.id)
            current.add_cube()
            self.renderer.render(self.engine.board.tiles, self.rows, self.cols)
            messagebox.showinfo(
                "勝利！", f"{display_name(current.id, self.engine.state.label_map)} の勝利！")
            # self.root.quit()
        else:
            self._advance_turn()

    def _advance_turn(self):
        """
        次のプレイヤーへターンを進め、フェーズを初期化
        """
        self.engine.next_turn()
        self.engine.state.set_phase("question")
        current = self.engine.current_player()
        self.turn_label.config(
            text=f"{display_name(current.id, current.display_name)} のターン")
        self.renderer.render(self.engine.board.tiles, self.rows, self.cols)
