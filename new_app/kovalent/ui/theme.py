from __future__ import annotations

from ..domain.models import BackgroundMode, Color


BLACK: Color = (0, 0, 0)
DARK_GREY: Color = (55, 60, 70)
MID_GREY: Color = (105, 112, 126)
LIGHT_GREY: Color = (220, 225, 235)
WHITE: Color = (255, 255, 255)
YELLOW: Color = (230, 230, 0)
GREEN: Color = (0, 200, 0)
ORANGE: Color = (200, 100, 0)
RED: Color = (200, 0, 0)
PURPLE: Color = (100, 0, 150)
BLUE: Color = (0, 0, 150)


def mix_colors(first: Color, second: Color, ratio: float = 0.5) -> Color:
    inverse = 1 - ratio
    return (
        int(first[0] * inverse + second[0] * ratio),
        int(first[1] * inverse + second[1] * ratio),
        int(first[2] * inverse + second[2] * ratio),
    )


def lighten(color: Color, amount: float) -> Color:
    return mix_colors(color, WHITE, amount)


def difficulty_color(level_number: int) -> Color:
    if level_number <= 10:
        return GREEN
    if level_number <= 20:
        return YELLOW
    if level_number <= 30:
        return ORANGE
    if level_number <= 40:
        return RED
    if level_number <= 49:
        return PURPLE
    return BLUE


def background_mode_label(mode: BackgroundMode) -> str:
    return {
        BackgroundMode.NORMAL: "Carres",
        BackgroundMode.CIRCLES: "Cercles",
        BackgroundMode.TRIANGLES: "Triangles",
        BackgroundMode.DISABLED: "Desactive",
    }[mode]
