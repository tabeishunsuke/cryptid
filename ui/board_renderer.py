import math
from utils.canvas_utils import (
    draw_regular_polygon,
    grid_to_pixel,
    is_point_in_polygon
)


class BoardRenderer:
    """
    Tkinter キャンバス上に盤面を描画する描画エンジン。
    - 地形画像、六角形タイル、縄張りマーク、構造物、トークン（キューブ／ディスク）などを描画
    - ホバー時のマス強調（ハイライト）演出にも対応
    """

    def __init__(self, canvas, terrain_imgs, radius, margin_x=0, margin_y=0, player_lookup=None):
        self.canvas = canvas
        self.terrain_imgs = terrain_imgs
        self.radius = radius
        self.margin_x = margin_x
        self.margin_y = margin_y
        self.player_lookup = player_lookup or {}  # プレイヤーID → Playerインスタンス
        self.hovered_cell = None  # ハイライト対象座標

    def render(self, tile_data, rows, cols):
        """
        タイルデータ（全マップセル）を一括描画。
        描画順：地形 → 六角形 → 縄張り → 構造物 → キューブ → ディスク群
        """
        self.canvas.delete("all")
        self.last_tile_data = tile_data
        self.last_rows = rows
        self.last_cols = cols

        for (col, row), cell in tile_data.items():
            x, y = grid_to_pixel(col, row, self.radius,
                                 self.margin_x, self.margin_y)
            terrain = cell.get("terrain", "")
            terrain_img = self.terrain_imgs.get(terrain)

            # 地形画像の描画（背景として）
            if terrain_img:
                self.canvas.create_image(x, y, image=terrain_img)

            # 六角形枠の描画
            draw_regular_polygon(
                self.canvas, x, y, self.radius, 6,
                fill_color="", outline_color="white", outline_width=3
            )

            # 縄張り（territory）演出の描画
            for territory in cell.get("territories", []):
                self._draw_territory(x, y, territory)

            # 構造物（種類＋色）
            if cell.get("structure"):
                self._draw_structure(
                    x, y, cell["structure"], cell["structure_color"])

            # キューブ（1個まで）
            if cell.get("cube"):
                self._draw_cube(x, y, cell["cube"])

            # ディスク群（最大複数）
            for i, pid in enumerate(cell.get("discs", [])):
                self._draw_disc(x, y, pid, offset=i,
                                total_discs=len(cell["discs"]))

    def _draw_territory(self, x, y, territory_type):
        """
        縄張りマークの描画。
        - bear: 六角辺の一部に線分を描画
        - eagle: 六角形を赤枠で囲む
        """
        r = self.radius * 0.8
        vertices = [
            (x + r * math.cos(math.radians(60 * i)),
             y + r * math.sin(math.radians(60 * i)))
            for i in range(6)
        ]

        if territory_type == "bear":
            segments = [(0, 3/20), (7/20, 13/20), (17/20, 1)]
            for i in range(6):
                p_start = vertices[i]
                p_end = vertices[(i + 1) % 6]
                dx = p_end[0] - p_start[0]
                dy = p_end[1] - p_start[1]
                for r0, r1 in segments:
                    sx = p_start[0] + dx * r0
                    sy = p_start[1] + dy * r0
                    ex = p_start[0] + dx * r1
                    ey = p_start[1] + dy * r1
                    self.canvas.create_line(
                        sx, sy, ex, ey, fill="black", width=2.1)

        elif territory_type == "eagle":
            flat_points = [coord for pt in vertices for coord in pt]
            self.canvas.create_polygon(
                flat_points, outline="red", fill="", width=2.1)

    def _draw_structure(self, x, y, type_, color):
        """
        構造物の描画（ruin: 三角形, stone: 八角形）
        """
        r = 25
        if type_ == "ruin":
            draw_regular_polygon(self.canvas, x, y, r, 3,
                                 fill_color=color, outline_color="")
        elif type_ == "stone":
            draw_regular_polygon(self.canvas, x, y, r, 8,
                                 fill_color=color, outline_color="")

    def _draw_cube(self, x, y, player_id):
        """
        キューブ描画（長方形として表現）
        """
        player = self.player_lookup.get(player_id)
        color = getattr(player, 'color', "gray")
        r = 15
        self.canvas.create_rectangle(x - r, y + 5 - r, x + r, y + 5 + r,
                                     fill=color, outline="")

    def _draw_disc(self, x, y, player_id, offset=0, total_discs=1):
        """
        ディスク描画（複数ある場合は横並びで配置）
        """
        player = self.player_lookup.get(player_id)
        color = getattr(player, 'color', "gray")
        r = 10
        spacing = r * 2
        center_offset = offset - (total_discs - 1) / 2
        disc_x = x + center_offset * spacing
        disc_y = y + 5
        self.canvas.create_oval(disc_x - r, disc_y - r, disc_x + r, disc_y + r,
                                fill=color, outline="")

    def highlight_cell(self, coord):
        """
        マウスホバー時に対象マスをハイライト表示（黄色の透過六角形）
        """
        if coord == self.hovered_cell:
            return
        self.hovered_cell = coord
        self.render_with_highlight()

    def render_with_highlight(self):
        """
        通常描画 → ハイライト描画を重ねる
        """
        self.render(self.last_tile_data, self.last_rows, self.last_cols)
        col, row = self.hovered_cell
        x, y = grid_to_pixel(col, row, self.radius,
                             self.margin_x, self.margin_y)

        vertices = []
        for i in range(6):
            angle = math.radians(60 * i)
            vx = x + self.radius * math.cos(angle)
            vy = y + self.radius * math.sin(angle)
            vertices.extend([vx, vy])

        self.canvas.create_polygon(
            vertices, fill="yellow", outline="", stipple="gray25", tags="hover"
        )

    def clear_highlight(self):
        """ハイライト解除（マウスがマス外に移動したとき）"""
        if self.hovered_cell is not None:
            self.hovered_cell = None
            self.render(self.last_tile_data, self.last_rows, self.last_cols)
