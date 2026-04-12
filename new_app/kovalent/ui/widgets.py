from __future__ import annotations

from dataclasses import dataclass
from math import cos, hypot, radians, sin
from random import Random
from typing import Iterable, Mapping

import pygame as pg

from ..domain.models import AtomSpec, BackgroundMode, Color, Point, RuntimeAtom
from ..infrastructure.assets import AssetStore
from . import theme
from .view import Viewport


@dataclass(frozen=True, slots=True)
class UiContext:
    surface: pg.Surface
    viewport: Viewport
    assets: AssetStore
    mouse_screen_pos: tuple[int, int]


@dataclass(frozen=True, slots=True)
class Button:
    rect: tuple[float, float, float, float]
    label: str
    text_size: int
    base_color: Color
    hover_color: Color
    text_color: Color = theme.BLACK
    enabled: bool = True

    def screen_rect(self, viewport: Viewport) -> pg.Rect:
        return viewport.rect(*self.rect)

    def contains(self, viewport: Viewport, mouse_screen_pos: tuple[int, int]) -> bool:
        return self.enabled and self.screen_rect(viewport).collidepoint(mouse_screen_pos)

    def draw(self, ctx: UiContext) -> pg.Rect:
        rect = self.screen_rect(ctx.viewport)
        hovered = self.contains(ctx.viewport, ctx.mouse_screen_pos)
        color = self.hover_color if hovered else self.base_color

        pg.draw.rect(ctx.surface, color, rect, border_radius=ctx.viewport.radius(12))
        pg.draw.rect(
            ctx.surface,
            theme.mix_colors(color, theme.BLACK, 0.25),
            rect,
            width=max(2, ctx.viewport.radius(2)),
            border_radius=ctx.viewport.radius(12),
        )
        if self.label:
            draw_text(
                ctx,
                self.label,
                (self.rect[0] + self.rect[2] / 2, self.rect[1] + self.rect[3] / 2),
                self.text_size,
                self.text_color,
                center=True,
            )
        return rect


@dataclass(slots=True)
class Particle:
    color: Color
    position: Point
    velocity: Point
    radius: float


def draw_text(
    ctx: UiContext,
    text: str,
    position: tuple[float, float],
    size: int,
    color: Color,
    *,
    center: bool = False,
) -> pg.Rect:
    font = ctx.assets.font(ctx.viewport.font_size(size))
    surface = font.render(text, True, color)
    rect = surface.get_rect()
    screen_pos = ctx.viewport.to_screen(position)
    if center:
        rect.center = screen_pos
    else:
        rect.topleft = screen_pos
    ctx.surface.blit(surface, rect)
    return rect


def draw_background(
    ctx: UiContext,
    mode: BackgroundMode,
    base_color: Color,
    *,
    elapsed_ms: int,
) -> None:
    canvas = ctx.viewport.canvas_rect()
    pg.draw.rect(ctx.surface, theme.DARK_GREY, canvas)

    if mode is BackgroundMode.DISABLED:
        return

    center = Point(600, 450)
    tick = elapsed_ms / 12.0
    line_width = ctx.viewport.radius(5)

    if mode is BackgroundMode.NORMAL:
        for ring in range(6):
            modifier = 0.2 + ring / 15
            radius = 350 + ring * 80
            points = [
                (
                    center.x + cos(radians(90 + tick * modifier)) * radius,
                    center.y + sin(radians(90 + tick * modifier)) * radius,
                ),
                (
                    center.x + cos(radians(180 + tick * modifier)) * radius,
                    center.y + sin(radians(180 + tick * modifier)) * radius,
                ),
                (
                    center.x + cos(radians(270 + tick * modifier)) * radius,
                    center.y + sin(radians(270 + tick * modifier)) * radius,
                ),
                (
                    center.x + cos(radians(tick * modifier)) * radius,
                    center.y + sin(radians(tick * modifier)) * radius,
                ),
            ]
            color = theme.lighten(base_color, min(0.12 + ring * 0.08, 0.75))
            pg.draw.lines(
                ctx.surface,
                color,
                True,
                [ctx.viewport.to_screen(point) for point in points],
                line_width,
            )
    elif mode is BackgroundMode.CIRCLES:
        for ring in range(6):
            radius = 50 + ring * 100 + sin((elapsed_ms / 1000) * 2 + ring * 2) * 5
            color = theme.lighten(base_color, min(0.15 + ring * 0.08, 0.75))
            pg.draw.circle(
                ctx.surface,
                color,
                ctx.viewport.to_screen(center),
                ctx.viewport.radius(radius),
                line_width,
            )
    elif mode is BackgroundMode.TRIANGLES:
        for ring in range(5):
            modifier = 0.2 + ring / 15
            radius = 350 + ring * 90
            points = [
                (
                    center.x + cos(radians(tick * modifier)) * radius,
                    center.y + sin(radians(tick * modifier)) * radius,
                ),
                (
                    center.x + cos(radians(120 + tick * modifier)) * radius,
                    center.y + sin(radians(120 + tick * modifier)) * radius,
                ),
                (
                    center.x + cos(radians(240 + tick * modifier)) * radius,
                    center.y + sin(radians(240 + tick * modifier)) * radius,
                ),
            ]
            color = theme.lighten(base_color, min(0.12 + ring * 0.10, 0.75))
            pg.draw.lines(
                ctx.surface,
                color,
                True,
                [ctx.viewport.to_screen(point) for point in points],
                line_width,
            )


def draw_image_in_rect(ctx: UiContext, image_key: str, rect: tuple[float, float, float, float], *, padding: float = 8) -> None:
    width = rect[2] - padding * 2
    height = rect[3] - padding * 2
    image = ctx.assets.image(image_key, ctx.viewport.size(width, height))
    position = ctx.viewport.to_screen((rect[0] + padding, rect[1] + padding))
    ctx.surface.blit(image, position)


def draw_atoms(
    ctx: UiContext,
    atoms: Mapping[int, RuntimeAtom],
    atom_specs: Mapping[str, AtomSpec],
    *,
    selected_atom_id: int | None,
) -> None:
    ordered_atoms = tuple(atoms.values())
    for atom in ordered_atoms:
        for other_id, order in atom.bonds.items():
            if other_id <= atom.atom_id:
                continue
            _draw_bond(ctx, atom.position, atoms[other_id].position, order)

    for atom in ordered_atoms:
        spec = atom_specs[atom.symbol]
        center = ctx.viewport.to_screen(atom.position)
        radius = ctx.viewport.radius(spec.radius)

        pg.draw.circle(ctx.surface, spec.color, center, radius)
        text_color = theme.WHITE if atom.symbol == "C" else theme.BLACK
        draw_text(ctx, atom.symbol, (atom.position.x, atom.position.y), int(spec.radius * 1.2), text_color, center=True)

        if atom.atom_id == selected_atom_id:
            pg.draw.circle(
                ctx.surface,
                theme.YELLOW,
                center,
                radius + ctx.viewport.radius(10),
                width=max(2, ctx.viewport.radius(5)),
            )


def _draw_bond(ctx: UiContext, start: Point, end: Point, order: int) -> None:
    dx = end.x - start.x
    dy = end.y - start.y
    length = max(hypot(dx, dy), 1.0)
    normal_x = -dy / length
    normal_y = dx / length

    if order == 1:
        offsets = [0.0]
        width = 10
    elif order == 2:
        offsets = [-8.0, 8.0]
        width = 8
    elif order == 3:
        offsets = [-11.0, 0.0, 11.0]
        width = 7
    else:
        offsets = [-16.0, -5.0, 5.0, 16.0]
        width = 6

    for offset in offsets:
        shifted_start = Point(start.x + normal_x * offset, start.y + normal_y * offset)
        shifted_end = Point(end.x + normal_x * offset, end.y + normal_y * offset)
        pg.draw.line(
            ctx.surface,
            theme.LIGHT_GREY,
            ctx.viewport.to_screen(shifted_start),
            ctx.viewport.to_screen(shifted_end),
            ctx.viewport.radius(width),
        )


def spawn_victory_particles(rng: Random) -> list[Particle]:
    particles: list[Particle] = []
    for start_x, direction in ((0.0, 1.0), (1200.0, -1.0)):
        for _ in range(rng.randint(12, 18)):
            tint = rng.randint(150, 255)
            particles.append(
                Particle(
                    color=(tint, tint, tint),
                    position=Point(start_x, 800.0),
                    velocity=Point(direction * rng.uniform(120, 420), rng.uniform(-850, -520)),
                    radius=rng.uniform(7, 14),
                )
            )
    return particles


def update_particles(particles: Iterable[Particle], dt_ms: int) -> list[Particle]:
    dt = dt_ms / 1000
    evolved: list[Particle] = []
    for particle in particles:
        next_velocity = Point(particle.velocity.x * 0.99, particle.velocity.y + 420 * dt)
        next_position = Point(
            particle.position.x + next_velocity.x * dt,
            particle.position.y + next_velocity.y * dt,
        )
        if next_position.y <= 840:
            evolved.append(
                Particle(
                    color=particle.color,
                    position=next_position,
                    velocity=next_velocity,
                    radius=particle.radius,
                )
            )
    return evolved


def draw_particles(ctx: UiContext, particles: Iterable[Particle]) -> None:
    for particle in particles:
        pg.draw.circle(
            ctx.surface,
            particle.color,
            ctx.viewport.to_screen(particle.position),
            ctx.viewport.radius(particle.radius),
        )
