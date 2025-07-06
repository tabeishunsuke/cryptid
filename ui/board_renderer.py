import math
from ui.canvas_utils import (
    draw_regular_polygon,
    grid_to_pixel,
    is_point_in_polygon
)


class BoardRenderer:
    """
    Tkinterキャンバス上にマップを描画するクラス。
    地形・構造物・トークンを描画する。
    """

    def __init__(self, canvas, terrain_imgs, radius, margin_x=0, margin_y=0):
        self.canvas = canvas
        self.terrain_imgs = terrain_imgs
        self.radius = radius
        self.margin_x = margin_x
        self.margin_y = margin_y
        self.hovered_cell = None  # ホバー中のマス座標

    def render(self, tile_data, rows, cols):
        """全マップを一括描画"""
        self.canvas.delete("all")
        self.last_tile_data = tile_data
        self.last_rows = rows
        self.last_cols = cols

        for (col, row), cell in tile_data.items():
            x, y = grid_to_pixel(col, row, self.radius,
                                 self.margin_x, self.margin_y)
            terrain = cell.get("terrain", "")
            terrain_img = self.terrain_imgs.get(terrain)

            if terrain_img:
                self.canvas.create_image(x, y, image=terrain_img)

            for territory in cell.get("territories", []):
                self._draw_territory(x, y, territory)

            if cell.get("structure"):
                self._draw_structure(
                    x, y, cell["structure"], cell["structure_color"]
                )

            for i, pid in enumerate(cell.get("discs", [])):
                self._draw_disc(x, y, pid, offset=i)

            if cell.get("cube"):
                self._draw_cube(x, y, cell["cube"])

    def _draw_territory(self, x, y, territory_type):
        r = self.radius * 0.8
        vertices = []
        for i in range(6):
            angle = math.radians(60 * i)
            px = x + r * math.cos(angle)
            py = y + r * math.sin(angle)
            vertices.append((px, py))

        if territory_type == "bear":
            segments = [(0, 3/20), (7/20, 13/20), (17/20, 1)]
            for i in range(6):
                p_start = vertices[i]
                p_end = vertices[(i + 1) % 6]
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
            flat_points = [coord for pt in vertices for coord in pt]
            self.canvas.create_polygon(
                flat_points, outline="red", fill="", width=2)

    def _draw_structure(self, x, y, type_, color):
        r = 16
        if type_ == "ruin":
            draw_regular_polygon(self.canvas, x, y, r, 3, fill_color=color)
        elif type_ == "stone":
            draw_regular_polygon(self.canvas, x, y, r, 4, fill_color=color)

    def _draw_disc(self, x, y, player_id, offset=0):
        disc_colors = {
            "alpha": "red", "beta": "green", "gamma": "blue",
            "delta": "purple", "epsilon": "orange"
        }
        dx = offset * 5 - 10
        r = 5
        self.canvas.create_oval(
            x + dx - r, y + 15 - r, x + dx + r, y + 15 + r,
            fill=disc_colors.get(player_id, "gray"), outline="black"
        )

    def _draw_cube(self, x, y, player_id):
        cube_colors = {
            "alpha": "red", "beta": "green", "gamma": "blue",
            "delta": "purple", "epsilon": "orange"
        }
        r = 6
        self.canvas.create_rectangle(
            x - r, y + 20 - r, x + r, y + 20 + r,
            fill=cube_colors.get(player_id, "gray"), outline="black"
        )

    def highlight_cell(self, coord):
        """ホバーしているマスに黄色の透明六角形を描画"""
        if coord == self.hovered_cell:
            return  # 同じマスなら再描画不要

        self.hovered_cell = coord
        self.render_with_highlight()

    def render_with_highlight(self):
        self.render(self.last_tile_data, self.last_rows,
                    self.last_cols)  # 通常描画
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
        if self.hovered_cell is not None:
            self.hovered_cell = None
            self.render(self.last_tile_data, self.last_rows, self.last_cols)
