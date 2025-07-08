import tkinter as tk
from tkinter import messagebox
from core.hint_evaluator import HintEvaluator
from ui.labels import display_name


class PhaseHandler:
    """
    プレイヤーのクリックに応じてゲームの各フェーズ（質問・配置・探索）を処理するクラス。
    """

    def __init__(self, engine, canvas, root, turn_label,
                 terrain_imgs, radius, rows, cols, renderer, update_labels=None):
        self.engine = engine         # ゲーム進行管理エンジン
        self.canvas = canvas         # 描画キャンバス
        self.root = root             # Tkinterルートウィンドウ（終了やダイアログ用）
        self.turn_label = turn_label  # ターン表示ラベル
        self.terrain_imgs = terrain_imgs
        self.radius = radius
        self.rows = rows
        self.cols = cols
        self.renderer = renderer     # BoardRenderer インスタンス
        self.update_labels = update_labels  # プレイヤーラベル更新用コールバック
        self.pending_dialog = None

    def handle_click(self, coord):
        """
        プレイヤーがマスをクリックしたときの処理。
        フェーズに応じて分岐処理を行う。
        """

        """
        プレイヤーがマスをクリックしたときの処理。
        フェーズが未指定の場合は何も起こらない。
        """
        state = self.engine.state
        if self.engine.state.current_action not in {"question", "search", "place_cube", "place_disc"}:
            print(f"[DEBUG] フェーズ未設定のため無視: {self.engine.state.current_action}")
            return

        if not self.engine.board.is_valid_coord(coord):
            return

        if self.pending_dialog is not None:
            print("[DEBUG] プレイヤー選択中のためクリック無効")
            return

        current = self.engine.current_player()
        state = self.engine.state
        cell = self.engine.board.get_tile(coord)
        print(f"[DEBUG] タイル状態: {cell}")

        if cell.get("cube"):
            messagebox.showinfo("無効", "既にキューブが置いてあるマスは選択できません")
            return

        # 🎯 行動フェーズの分岐（phaseではなく current_action を使う）
        action = state.current_action

        if action == "question":
            self._handle_question(current, cell, coord)
        elif action == "place_disc":
            self._handle_disc_placement(current, cell, coord)
        elif action == "search":
            self._handle_search(current, cell, coord)
        elif action == "place_cube":
            self._handle_cube_placement(current, cell, coord)
        else:
            print(f"[DEBUG] 有効な行動フェーズではないため無視: {action}")
            return

    def _handle_question(self, current, cell, coord):
        # 質問対象選択ダイアログを表示
        self.show_player_selector(current, cell, coord)

    def show_player_selector(self, current, cell, coord):
        # 新しいウィンドウ（Toplevel）を生成してUI表示
        selector = tk.Toplevel(self.root)
        self.pending_dialog = selector  # ダイアログを保持しておく
        selector.title("質問対象を選択")
        selector.geometry("300x120")

        # 自分以外のプレイヤーを対象に選択肢を作成
        options = [p.id for p in self.engine.players if p.id != current.id]
        label_options = [self.engine.label_map[p] for p in options]

        # プルダウン選択用の変数を初期化
        selected = tk.StringVar()
        selected.set(label_options[0])  # デフォルト選択は最初のプレイヤー

        # ラベルとプルダウンメニューを配置
        tk.Label(selector, text="質問する相手:").pack()
        dropdown = tk.OptionMenu(selector, selected, *label_options)
        dropdown.pack(pady=5)

        # 💡 閉じたときの処理（×ボタン）
        def on_cancel():
            self.pending_dialog = None
            self.engine.state.current_action = None  # ← フェーズ未選択に戻す
            self.engine.state.set_phase("active")  # ゲーム進行フェーズは維持
            self.update_turn_label()  # ターン表示を更新
            selector.destroy()

        selector.protocol("WM_DELETE_WINDOW", on_cancel)

        # 「決定」ボタンを押したときの処理
        def confirm():
            label = selected.get()  # 表示名（例: プレイヤー1）を取得
            pid = next(k for k, v in self.engine.label_map.items()
                       if v == label)  # 対応するIDを取得
            target = self.engine.get_player_by_id(pid)  # プレイヤーインスタンスを取得

            selector.destroy()  # ダイアログを閉じる
            self.pending_dialog = None  # ダイアログを解放
            selector.destroy()  # Toplevelを閉じる
            self.evaluate_question(current, target, cell, coord)  # 質問判定へ移行

        tk.Button(selector, text="決定", command=confirm).pack(pady=5)

    def evaluate_question(self, asker, target, cell, coord):
        # 対象プレイヤーのヒントで、指定マスが合致するか判定
        applies = HintEvaluator.hint_applies(
            cell, target.hint, self.engine.board.tiles)

        if applies:
            # ✅ 合致 → ディスク配置 → ターン終了
            self.engine.board.place_disc(coord, target.id)
            target.add_disc()
            print(f"[DEBUG] コマ配置: player_id={target.id}, coord={coord}")

            print(
                f"[LOG] {asker.display_name} → {target.display_name}: 合致 → ディスク配置")
            self.engine.state.log(
                f"{asker.display_name} → {target.display_name}: 合致 → ディスク配置"
            )
            self._advance_turn()
        else:
            # ❌ 非合致 → 相手がキューブを配置し、質問者は次に自分のキューブを別マスに配置する
            self.engine.board.place_cube(coord, target.id)
            target.add_cube()
            print(
                f"[DEBUG] コマ配置: player_id={target.display_name}, coord={coord}")

            self.engine.state.current_action = "place_cube"  # 次は質問者のキューブ配置フェーズへ
            self.update_turn_label()
            self.engine.state.exploration_target = coord  # 対象座標を記録（UI表示などに使える）

            print(
                f"[LOG] {asker.display_name} → {target.display_name}: 非合致 → キューブ配置へ（質問者も配置）")
            self.engine.state.log(
                f"{asker.display_name} → {target.display_name}: 非合致 → キューブ配置へ（質問者も配置）"
            )

            # ターン表示更新
            self.turn_label.config(text=f"{asker.display_name} → キューブ配置フェーズ")

            cell = self.engine.board.get_tile(coord)
            print(f"[DEBUG] 配置対象マスのディスク状態: {cell.get('discs')}")

            # 🔍 デバッグ：全マスのディスク状態を確認
            for coord, cell in self.engine.board.tiles.items():
                if cell.get("discs"):
                    print(f"[DEBUG] マス {coord} にディスク配置: {cell['discs']}")

        # 🧠💡 ここで盤面のディスク状態を確認するログを入れる
        print("[DEBUG] 現在の盤面ディスク一覧:")
        for coord, cell in self.engine.board.tiles.items():
            if cell.get("discs"):
                print(f"  → {coord}: {cell['discs']}")

        # 盤面の再描画
        print(f"[DEBUG] 描画更新中: phase={self.engine.state.phase}")
        self.renderer.render(self.engine.board.tiles, self.rows, self.cols)

    def _handle_disc_placement(self, current, cell, coord):
        """
        ディスク配置フェーズの処理
        """
        success = self.engine.board.place_disc(coord, current.id)
        if success:
            current.add_disc()
            self.engine.state.log(f"{current.display_name}: 再配置 → {coord}")

            # ✅ 探索対象座標から探索処理を再開
            target_coord = self.engine.state.exploration_target
            target_cell = self.engine.board.get_tile(target_coord)
            responder_ids = [current.id] + self._player_order_from(current.id)
            self._animate_exploration(target_coord, responder_ids)

    def _handle_cube_placement(self, current, cell, coord):
        """
        キューブ配置フェーズの処理：探索フェーズへ進む
        """
        applies = HintEvaluator.hint_applies(
            cell, current.hint, self.engine.board.tiles)

        if applies:
            messagebox.showinfo("配置不可", "自分のヒントに合致するマスにはキューブを置けません")
            return

        self.engine.board.place_cube(coord, current.id)
        current.add_cube()
        self._advance_turn()

    def _handle_search(self, current, cell, coord):
        """
        探索フェーズの処理（ルール準拠）
        - 探索者がディスク配置（または他マスに配置）
        - 他プレイヤーが順にコマを配置
        - キューブが出たら即終了 → 探索者がキューブを配置
        - 全員がディスク配置 → 勝利
        """

        # 🚫 キューブがすでにある場合は探索できない
        if cell.get("cube"):
            messagebox.showwarning("無効", "既にキューブが置かれているため探索できません")
            return

        # ✅ 自分のヒントが探索対象マスに合致しているか確認
        if not HintEvaluator.hint_applies(cell, current.hint, self.engine.board.tiles):
            messagebox.showwarning("探索不可", "自分のヒントに合致しないマスは探索できません")
            return

        board = self.engine.board
        state = self.engine.state
        current_pid = current.id

        # 🎯 探索者自身のディスク配置
        if current_pid in cell.get("discs", []):
            # すでに置かれている → 自分のヒントに合致する別マスへ配置
            state.current_action = "place_disc"
            state.exploration_target = coord
            self.update_turn_label()
            state.log(f"{current.display_name}: 既にディスク済 → 別マスへ配置")
            return

        else:
            board.place_disc(coord, current_pid)
            current.add_disc()
            state.log(f"{current.display_name}: 探索対象にディスクを配置")

        # レスポンダー順：探索者 → 左隣から時計回り
        responder_ids = [current_pid] + self._player_order_from(current_pid)
        self._animate_exploration(coord, responder_ids)

    def _advance_turn(self):
        """
        次のプレイヤーへターンを進め、フェーズを初期化
        """
        self.engine.next_turn()

        # 行動選択フェーズに戻す
        self.engine.state.current_action = None
        self.engine.state.set_phase("active")  # ゲーム進行フェーズは維持

        if self.update_labels:
            self.update_labels()

        self.update_turn_label()  # ターン表示を更新

        self.renderer.render(self.engine.board.tiles, self.rows, self.cols)

    def update_turn_label(self):
        pid = self.engine.state.current_player
        player = self.engine.id_to_player[pid]
        label = self.engine.label_map[pid]
        color = player.color
        action = self.engine.state.current_action

        if action == "question":
            text = f"{label} - 質問フェーズ"
        elif action == "search":
            text = f"{label} - 探索フェーズ"
        elif action == "place_disc":
            text = f"{label} - ディスク配置フェーズ"
        elif action == "place_cube":
            text = f"{label} - キューブ配置フェーズ"
        elif action is None:
            text = f"{label} のターン"
        else:
            text = f"{label}（未定義フェーズ）"

        self.turn_label.config(text=text, fg=color)

    def _player_order_from(self, start_pid):
        """
        プレイヤーIDを探索者の左隣から順に並べる（時計回り）
        """
        order = self.engine.state.players
        idx = order.index(start_pid)
        return order[idx+1:] + order[:idx]

    def _animate_exploration(self, coord, responder_ids):
        """
        プレイヤーごとに順番にコマを描画するアニメーション処理
        """
        interval_ms = 1000
        board = self.engine.board
        tiles = board.tiles
        state = self.engine.state

        def step(index):
            if index >= len(responder_ids):
                # ✅ 全員一致 → 勝利
                current = self.engine.current_player()

                # ✅ フェーズ・アクションを更新
                state.set_phase("end")
                state.current_action = None

                # ✅ ラベル更新
                self.turn_label.config(text="探索成功！", fg=current.color)

                # ✅ 勝利メッセージ
                self.renderer.render(board.tiles, self.rows, self.cols)
                messagebox.showinfo("勝利！", f"{current.display_name} の勝利！")
                return

            pid = responder_ids[index]
            player = self.engine.id_to_player[pid]
            display = player.display_name

            if pid in tiles[coord].get("discs", []):
                state.log(f"{display}: 既にディスク済 → パス")
            elif HintEvaluator.hint_applies(tiles[coord], player.hint, tiles):
                board.place_disc(coord, pid)
                player.add_disc()
                state.log(f"{display}: 合致 → ディスク配置")
            else:
                board.place_cube(coord, pid)
                player.add_cube()
                state.log(f"{display}: 非合致 → キューブ配置 → 探索終了")

                # 🔄 探索者が自身のキューブを別マスに配置
                state.current_action = "place_cube"
                state.exploration_target = coord
                self.update_turn_label()

                self.renderer.render(board.tiles, self.rows, self.cols)
                return  # 探索終了のため中断

            self.renderer.render(board.tiles, self.rows, self.cols)
            self.root.after(interval_ms, lambda: step(index + 1))

        step(0)
