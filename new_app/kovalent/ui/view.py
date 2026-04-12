from __future__ import annotations

from dataclasses import dataclass

import pygame as pg

from ..config import BASE_HEIGHT, BASE_WIDTH
from ..domain.models import Point


@dataclass(frozen=True, slots=True)
class Viewport:
    scale: float
    offset_x: int
    offset_y: int
    draw_width: int
    draw_height: int
    base_width: int = BASE_WIDTH
    base_height: int = BASE_HEIGHT

    @classmethod
    def from_window(cls, window_size: tuple[int, int]) -> "Viewport":
        width, height = window_size
        scale = min(width / BASE_WIDTH, height / BASE_HEIGHT)
        draw_width = int(BASE_WIDTH * scale)
        draw_height = int(BASE_HEIGHT * scale)
        offset_x = (width - draw_width) // 2
        offset_y = (height - draw_height) // 2
        return cls(
            scale=scale,
            offset_x=offset_x,
            offset_y=offset_y,
            draw_width=draw_width,
            draw_height=draw_height,
        )

    def canvas_rect(self) -> pg.Rect:
        return pg.Rect(self.offset_x, self.offset_y, self.draw_width, self.draw_height)

    def to_screen(self, point: Point | tuple[float, float]) -> tuple[int, int]:
        if isinstance(point, Point):
            x, y = point.x, point.y
        else:
            x, y = point
        return (
            int(self.offset_x + x * self.scale),
            int(self.offset_y + y * self.scale),
        )

    def to_world(self, screen_pos: tuple[int, int]) -> Point:
        x, y = screen_pos
        return Point(
            (x - self.offset_x) / self.scale,
            (y - self.offset_y) / self.scale,
        )

    def rect(self, left: float, top: float, width: float, height: float) -> pg.Rect:
        x, y = self.to_screen((left, top))
        return pg.Rect(
            x,
            y,
            int(width * self.scale),
            int(height * self.scale),
        )

    def size(self, width: float, height: float) -> tuple[int, int]:
        return (max(1, int(width * self.scale)), max(1, int(height * self.scale)))

    def radius(self, value: float) -> int:
        return max(1, int(value * self.scale))

    def font_size(self, value: int) -> int:
        return max(12, int(value * self.scale * 1.5))
