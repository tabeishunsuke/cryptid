import tkinter as tk
from tkinter import messagebox
from core.hint_evaluator import HintEvaluator


class PhaseHandler:
    """
    ゲーム中の「フェーズごとの操作（質問・探索・配置など）」を処理するコントローラー。

    役割：
    - プレイヤーがマスをクリックしたときに、現在フェーズに応じた処理を分岐する
    - 探索や質問などのロジックの実行とUIの更新
    - ターンの進行、勝利判定、探索アニメーションの制御

    構成：
    - engine: ゲームの状態やプレイヤー情報を持つ GameEngine インスタンス
    - canvas: 描画領域（BoardRendererと連携）
    - renderer: ボード描画用の描画補助オブジェクト
    """

    def __init__(self, engine, canvas, root, turn_label,
                 terrain_imgs, radius, rows, cols, renderer, update_labels=None):
        self.engine = engine                # ゲーム状態管理エンジン
        self.canvas = canvas                # 描画キャンバス
        self.root = root                    # Tkinter ウィンドウ（ダイアログ用）
        self.turn_label = turn_label        # ターン表示ラベル（UI）
        self.terrain_imgs = terrain_imgs    # 地形画像群
        self.radius = radius                # 六角形サイズ
        self.rows = rows
        self.cols = cols
        self.renderer = renderer            # BoardRenderer インスタンス
        self.update_labels = update_labels  # プレイヤーラベル更新用のコールバック関数
        self.pending_dialog = None          # 質問対象選択中かどうか
        self.enable_buttons = None  # ボタン有効化関数（main.pyから注入）
        self.disable_buttons = None  # ボタン無効化関数

    def handle_click(self, coord):
        """
        プレイヤーがマスをクリックした時の処理。
        - 現在のフェーズ（action）に応じて、質問・探索・配置の処理を振り分ける
        - 無効な座標や操作中状態はスキップ
        """
        state = self.engine.state

        # 無効なフェーズや選択処理中なら無視
        if state.current_action not in {"question", "search", "place_cube", "place_disc"}:
            print(f"[DEBUG] 無効フェーズ: {state.current_action}")
            return

        if not self.engine.board.is_valid_coord(coord) or self.pending_dialog:
            return

        cell = self.engine.board.get_tile(coord)

        # キューブが既に置かれていたら探索／質問不可
        if cell.get("cube"):
            messagebox.showinfo("無効", "既にキューブが置かれているため選択できません")
            return

        current = self.engine.current_player()
        action = state.current_action

        # 現在のフェーズに応じて分岐
        if action == "question":
            self._start_question(current, cell, coord)
        elif action == "place_disc":
            self._place_disc(current, cell, coord)
        elif action == "search":
            self._start_search(current, cell, coord)
        elif action == "place_cube":
            self._place_cube(current, cell, coord)

    def _start_question(self, current, cell, coord):
        """
        質問フェーズ：対象プレイヤーを選ぶためのダイアログ表示
        """
        self._show_player_selector(current, cell, coord)

    def _show_player_selector(self, current, cell, coord):
        """
        質問対象を選ぶUIポップアップ。
        選択すると _evaluate_question() に渡して処理を継続。
        """
        if self.disable_buttons:
            self.disable_buttons()

        selector = tk.Toplevel(self.root)
        self.pending_dialog = selector
        selector.title("質問相手を選択")
        selector.geometry("300x120")

        options = [p.id for p in self.engine.players if p.id != current.id]
        label_options = [self.engine.label_map[p] for p in options]

        selected = tk.StringVar()
        selected.set(label_options[0])

        tk.Label(selector, text="質問する相手:").pack()
        dropdown = tk.OptionMenu(selector, selected, *label_options)
        dropdown.pack(pady=5)

        def cancel():
            # 閉じる時：状態をリセットしてフェーズ戻す
            self.pending_dialog = None
            self.engine.state.current_action = None
            self.engine.state.set_phase("active")
            self.update_turn_label()
            if self.enable_buttons:
                self.enable_buttons()
            selector.destroy()

        def confirm():
            # 質問対象が選ばれたら判定処理へ
            label = selected.get()
            pid = next(k for k, v in self.engine.label_map.items()
                       if v == label)
            target = self.engine.get_player_by_id(pid)
            if self.enable_buttons:
                self.enable_buttons()

            selector.destroy()
            self.pending_dialog = None
            self._evaluate_question(current, target, cell, coord)

        selector.protocol("WM_DELETE_WINDOW", cancel)
        tk.Button(selector, text="決定", command=confirm).pack(pady=5)

    def _evaluate_question(self, asker, target, cell, coord):
        """
        選ばれたプレイヤーのヒントが対象マスに適用されるか判定する。
        - 合致すればディスク配置
        - 不一致ならキューブ配置 → 質問者が自分のキューブを配置するフェーズへ移行
        """
        applies = HintEvaluator.hint_applies(
            cell, target.hint, self.engine.board.tiles)

        if applies:
            self.engine.board.place_disc(coord, target.id)
            target.add_disc()
            self.engine.state.log(
                f"{asker.display_name} → {target.display_name}: 合致 → ディスク")
            self._advance_turn()
        else:
            self.engine.board.place_cube(coord, target.id)
            target.add_cube()
            self.engine.state.current_action = "place_cube"
            self.engine.state.exploration_target = coord
            self.update_turn_label()
            self.engine.state.log(
                f"{asker.display_name} → {target.display_name}: 非合致 → キューブ配置へ")

            if self.disable_buttons:
                self.disable_buttons()

        self.renderer.render(self.engine.board.tiles, self.rows, self.cols)

    def _place_disc(self, current, cell, coord):
        """
        探索中で既に対象マスにディスクが置かれていた場合、別マスに再配置する処理。
        """
        success = self.engine.board.place_disc(coord, current.id)
        if success:
            current.add_disc()
            self.engine.state.log(f"{current.display_name}: 再配置 → {coord}")

            target = self.engine.state.exploration_target
            responder_ids = [current.id] + self._player_order_from(current.id)
            self._animate_exploration(target, responder_ids)

    def _place_cube(self, current, cell, coord):
        """
        プレイヤーが自分のキューブを置く処理（質問の不一致時や探索失敗時）
        """
        if HintEvaluator.hint_applies(cell, current.hint, self.engine.board.tiles):
            messagebox.showinfo("配置不可", "ヒントに合致するマスにはキューブを置けません")
            return

        self.engine.board.place_cube(coord, current.id)
        current.add_cube()
        self._advance_turn()

    def _start_search(self, current, cell, coord):
        """
        探索フェーズ：探索者が対象マスにディスクを配置し、他プレイヤーが順に反応
        """
        if cell.get("cube"):
            messagebox.showwarning("無効", "既にキューブがあるため探索できません")
            return

        if not HintEvaluator.hint_applies(cell, current.hint, self.engine.board.tiles):
            messagebox.showwarning("探索不可", "自分のヒントに合致しないマスは探索できません")
            return

        if current.id in cell.get("discs", []):
            self.engine.state.current_action = "place_disc"
            self.engine.state.exploration_target = coord
            self.update_turn_label()
            self.engine.state.log(f"{current.display_name}: 既にディスク済 → 再配置")

            if self.disable_buttons:
                self.disable_buttons()
            return

        # 探索者のディスク配置
        self.engine.board.place_disc(coord, current.id)
        current.add_disc()
        self.engine.state.log(f"{current.display_name}: 探索対象にディスク配置")

        if self.disable_buttons:
            self.disable_buttons()

        # 探索順のプレイヤー並び（探索者 → 左隣から順）
        responder_ids = [current.id] + self._player_order_from(current.id)
        self._animate_exploration(coord, responder_ids)

    def _advance_turn(self):
        """
        ターンを次のプレイヤーに進める。
        - 現アクションを解除し、表示や描画も更新
        """
        self.engine.next_turn()
        self.engine.state.current_action = None
        self.engine.state.set_phase("active")

        if self.update_labels:
            self.update_labels()

        self.update_turn_label()
        self.renderer.render(self.engine.board.tiles, self.rows, self.cols)

        if self.enable_buttons:
            self.enable_buttons()

    def update_turn_label(self):
        """
        ターン表示ラベルを現在のプレイヤーとアクションに応じて更新する。
        """
        pid = self.engine.state.current_player
        label = self.engine.label_map[pid]
        color = self.engine.id_to_player[pid].color
        action = self.engine.state.current_action

        phase_map = {
            "question": "質問フェーズ",
            "search": "探索フェーズ",
            "place_disc": "ディスクを置いてください",
            "place_cube": "【失敗】キューブを置いてください"
        }
        label_text = f"{label} - {phase_map.get(action, '行動を選択してください')}"
        self.turn_label.config(text=label_text, fg=color)

    def _player_order_from(self, start_pid):
        """
        探索時の順番：
        - 探索者を起点に、左隣のプレイヤーから時計回りで並べる
        """
        order = self.engine.state.players
        idx = order.index(start_pid)
        return order[idx + 1:] + order[:idx]

    def _animate_exploration(self, coord, responder_ids):
        """
        探索アニメーション処理：
        - responder_ids の順にヒント判定を行い、対応するディスク／キューブを配置
        - 誰かが非合致（キューブ）なら探索終了
        - 全員が合致（ディスク）なら勝利処理に移行
        """
        interval_ms = 1000
        board = self.engine.board
        tiles = board.tiles
        state = self.engine.state

        def step(index):
            if index >= len(responder_ids):
                # ✅ 全員合致 → 勝利
                current = self.engine.current_player()
                state.set_phase("end")
                state.current_action = None
                self.turn_label.config(text="探索成功！", fg=current.color)
                self.renderer.render(board.tiles, self.rows, self.cols)
                if self.enable_buttons:
                    self.enable_buttons()
                messagebox.showinfo("勝利！", f"{current.display_name} の勝利！")
                return

            pid = responder_ids[index]
            player = self.engine.id_to_player[pid]
            cell = tiles[coord]

            if pid in cell.get("discs", []):
                # 既にディスクがある → パス
                state.log(f"{player.display_name}: 既にディスク済 → パス")
            elif HintEvaluator.hint_applies(cell, player.hint, tiles):
                board.place_disc(coord, pid)
                player.add_disc()
                state.log(f"{player.display_name}: 合致 → ディスク配置")
            else:
                # 非合致 → 探索失敗（キューブ配置へ）
                board.place_cube(coord, pid)
                player.add_cube()
                state.log(f"{player.display_name}: 非合致 → キューブ配置 → 探索終了")

                if self.disable_buttons:
                    self.disable_buttons()

                # 🔁 探索者がキューブを別マスに配置するフェーズへ
                state.current_action = "place_cube"
                state.exploration_target = coord
                self.update_turn_label()
                self.renderer.render(board.tiles, self.rows, self.cols)
                return

            # 次のプレイヤーへ進行
            self.renderer.render(board.tiles, self.rows, self.cols)
            self.root.after(interval_ms, lambda: step(index + 1))

        step(0)
