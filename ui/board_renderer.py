import math
from ui.canvas_utils import draw_regular_polygon


class BoardRenderer:
    """
    Tkinterキャンバス上にマップを描画するクラス。
    地形・構造物・トークンを描画する。
    """

    def __init__(self, canvas, terrain_imgs, radius, margin_x=0, margin_y=0):
        self.canvas = canvas                 # 描画対象のCanvas
        self.terrain_imgs = terrain_imgs     # 地形画像の辞書
        self.radius = radius                 # 六角形サイズ
        self.margin_x = margin_x             # 左右余白
        self.margin_y = margin_y             # 上下余白

    def render(self, tile_data, rows, cols):
        """
        全マップを一括描画
        """
        self.canvas.delete("all")

        for (col, row), cell in tile_data.items():
            x, y = self._hex_to_pixel(col, row)
            terrain = cell.get("terrain", "")
            terrain_img = self.terrain_imgs.get(terrain)

            # 🖼 地形画像の描画
            if terrain_img:
                self.canvas.create_image(x, y, image=terrain_img)

            # 🐻🦅 縄張り（territory）の描画
            for territory in cell.get("territories", []):
                self._draw_territory(x, y, territory)

            # 🏛️ 建造物（stone, ruin）の描画
            if cell.get("structure"):
                self._draw_structure(
                    x, y, cell["structure"], cell["structure_color"])

            # 🔴 ディスク（プレイヤーごとに複数対応）
            for i, pid in enumerate(cell.get("discs", [])):
                self._draw_disc(x, y, pid, offset=i)

            # 🟦 キューブ（1人1つのマーカー）
            if cell.get("cube"):
                self._draw_cube(x, y, cell["cube"])

    def _hex_to_pixel(self, col, row):
        """
        六角形の座標(col, row) → ピクセル座標(x, y) に変換
        余白を考慮して中央配置になるよう調整
        """
        x = self.radius * 3/2 * col
        y = self.radius * (3**0.5) * (row + 0.5 * (col % 2))
        return x + self.margin_x, y + self.margin_y

    def _draw_territory(self, x, y, territory_type):
        import math
        r = self.radius * 0.8

        # 六角形頂点（フラットトップ）
        vertices = []
        for i in range(6):
            angle = math.radians(60 * i)
            px = x + r * math.cos(angle)
            py = y + r * math.sin(angle)
            vertices.append((px, py))

        if territory_type == "bear":
            # 各辺に対して点線描画（3本の実線セグメント）
            segments = [(0, 3/20), (7/20, 13/20), (17/20, 1)]
            for i in range(6):
                p_start = vertices[i]
                p_end = vertices[(i + 1) % 6]

                # ベクトル q（辺の方向）
                qx = p_end[0] - p_start[0]
                qy = p_end[1] - p_start[1]

                for r0, r1 in segments:
                    sx = p_start[0] + qx * r0
                    sy = p_start[1] + qy * r0
                    ex = p_start[0] + qx * r1
                    ey = p_start[1] + qy * r1
                    self.canvas.create_line(
                        sx, sy, ex, ey, fill="black", width=1)

        elif territory_type == "eagle":
            # ワシは実線六角形描画
            flat_points = [coord for pt in vertices for coord in pt]
            self.canvas.create_polygon(
                flat_points, outline="red", fill="", width=2)

    def _draw_structure(self, x, y, type_, color):
        """
        建造物の見た目をタイプに応じて描画。
        - ruin → 上向き三角形
        - stone → フラットトップの正八角形
        - その他 → 円
        """
        r = 16  # サイズ共通半径

        if type_ == "ruin":
            draw_regular_polygon(self.canvas, x, y, r, 3, fill_color=color)
        elif type_ == "stone":
            draw_regular_polygon(self.canvas, x, y, r, 4, fill_color=color)

    def _draw_disc(self, x, y, player_id, offset=0):
        """ディスクをプレイヤー色で描画（複数対応）"""
        disc_colors = {
            "alpha": "red", "beta": "green", "gamma": "blue",
            "delta": "purple", "epsilon": "orange"
        }
        dx = offset * 5 - 10
        r = 5
        self.canvas.create_oval(x + dx - r, y + 15 - r, x + dx + r, y + 15 + r,
                                fill=disc_colors.get(player_id, "gray"), outline="black")

    def _draw_cube(self, x, y, player_id):
        """キューブをプレイヤー色で描画（正方形）"""
        cube_colors = {
            "alpha": "red", "beta": "green", "gamma": "blue",
            "delta": "purple", "epsilon": "orange"
        }
        r = 6
        self.canvas.create_rectangle(x - r, y + 20 - r, x + r, y + 20 + r,
                                     fill=cube_colors.get(player_id, "gray"), outline="black")
