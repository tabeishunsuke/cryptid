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
        if state.phase not in {"question", "place_disc", "search", "place_cube"}:
            print(f"[DEBUG] フェーズ未設定のため無視: {state.phase}")
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

        # --- 質問フェーズ ---
        if state.phase == "question":
            self._handle_question(current, cell, coord)

        # --- 配置フェーズ ---
        elif state.phase == "place_disc":
            self._handle_disc_placement(current, cell, coord)

        # --- 探索フェーズ ---
        elif state.phase == "search":
            self._handle_search(current, cell, coord)

        elif state.phase == "place_cube":
            self._handle_cube_placement(current, cell, coord)

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
            self.engine.state.set_phase(None)  # ← フェーズ未選択に戻す
            self.turn_label.config(
                text=f"{self.engine.label_map[self.engine.state.current_player]} のターン")
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
            self.engine.board.place_disc(coord, asker.id)
            asker.add_disc()
            print(f"[DEBUG] コマ配置: player_id={target.id}, coord={coord}")

            self.engine.state.log(
                f"{self.engine.label_map[asker.id]} → {self.engine.label_map[target.id]}: 合致 → ディスク配置"
            )
            self._advance_turn()
        else:
            # ❌ 非合致 → 相手がキューブを配置し、質問者は次に自分のキューブを別マスに配置する
            self.engine.board.place_cube(coord, target.id)
            target.add_cube()
            print(f"[DEBUG] コマ配置: player_id={asker.id}, coord={coord}")

            self.engine.state.set_phase("place_cube")  # 次は質問者のキューブ配置フェーズへ
            self.engine.state.exploration_target = coord  # 対象座標を記録（UI表示などに使える）

            self.engine.state.log(
                f"{self.engine.label_map[asker.id]} → {self.engine.label_map[target.id]}: 非合致 → キューブ配置へ（質問者も配置）"
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
            self._advance_turn()

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
            text=f"{display_name(current.id, self.engine.label_map)} のターン")

        if self.update_labels:
            self.update_labels()

        self.renderer.render(self.engine.board.tiles, self.rows, self.cols)
