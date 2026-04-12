from __future__ import annotations

from abc import ABC, abstractmethod
from random import Random

import pygame as pg

from ..application.session import GameSession
from ..config import CONFIG
from ..domain.models import BackgroundMode, Screen
from ..domain.services import format_elapsed_time
from . import theme
from .widgets import (
    Button,
    UiContext,
    draw_atoms,
    draw_background,
    draw_image_in_rect,
    draw_particles,
    draw_text,
    spawn_victory_particles,
    update_particles,
)


RULES_PAGES = [
    (
        "Regles du jeu",
        [
            "Le but du jeu est de relier les atomes entre eux.",
            "Chaque atome doit respecter sa valence maximale.",
            "Tous les atomes doivent former une seule molecule.",
            "Les niveaux montent progressivement en difficulte.",
            "Pour debloquer un niveau, il faut resoudre le precedent.",
        ],
    ),
    (
        "Commandes",
        [
            "Clique gauche : selectionner et deplacer un atome.",
            "Clic droit : creer, renforcer ou retirer une liaison.",
            "Le bouton restart relance le niveau sans changer le chrono.",
            "Une fois le puzzle resolu, les interactions sont verrouillees.",
            "Le passage au niveau suivant se fait depuis l'ecran de victoire.",
        ],
    ),
    (
        "Atomes",
        [
            "Hydrogene : 1 liaison",
            "Oxygene et soufre : 2 liaisons",
            "Azote et phosphore : 3 liaisons",
            "Carbone : 4 liaisons",
            "Les doubles et triples liaisons sont supportees.",
        ],
    ),
    (
        "Credits",
        [
            "Projet original : KVTeam",
            "Reecriture : architecture modulaire moderne en Python",
            "Moteur d'affichage : Pygame",
            "Donnees et assets : reutilises depuis le projet source",
            "Objectif : un code testable, lisible et evolutif",
        ],
    ),
]


class Scene(ABC):
    def __init__(self, session: GameSession) -> None:
        self.session = session

    @abstractmethod
    def handle_event(self, event: pg.event.Event, ctx: UiContext, *, now_ms: int) -> bool | None:
        return True

    def update(self, dt_ms: int, *, now_ms: int) -> None:
        return None

    @abstractmethod
    def draw(self, ctx: UiContext, *, now_ms: int) -> None:
        return None


class IntroScene(Scene):
    def handle_event(self, event: pg.event.Event, ctx: UiContext, *, now_ms: int) -> bool | None:
        if event.type in {pg.KEYDOWN, pg.MOUSEBUTTONDOWN}:
            self.session.skip_intro()
        return True

    def update(self, dt_ms: int, *, now_ms: int) -> None:
        self.session.advance_intro(dt_ms)

    def draw(self, ctx: UiContext, *, now_ms: int) -> None:
        ctx.surface.fill(theme.BLACK)
        progress = min(self.session.intro_elapsed_ms / CONFIG.intro_duration_ms, 1.0)
        fade = 1.0 if progress < 0.7 else max(0.0, 1 - ((progress - 0.7) / 0.3))
        intensity = int(255 * min(progress * 1.8, 1.0) * fade)
        color = (intensity, intensity, intensity)
        draw_text(ctx, "KVTeam", (600, 330), 70, color, center=True)
        draw_text(ctx, "Kovalent Reforged", (600, 420), 34, color, center=True)
        draw_text(ctx, "Cliquez pour passer l'intro", (600, 700), 22, color, center=True)


class MainMenuScene(Scene):
    def handle_event(self, event: pg.event.Event, ctx: UiContext, *, now_ms: int) -> bool | None:
        if event.type != pg.MOUSEBUTTONDOWN or event.button != 1:
            return True

        buttons = self._buttons()
        if buttons["play"].contains(ctx.viewport, event.pos):
            self.session.click_feedback()
            self.session.open_level_select()
        elif buttons["info"].contains(ctx.viewport, event.pos):
            self.session.click_feedback()
            self.session.open_rules()
        elif buttons["quit"].contains(ctx.viewport, event.pos):
            self.session.click_feedback()
            return False
        elif buttons["background"].contains(ctx.viewport, event.pos):
            self.session.click_feedback()
            self.session.toggle_background_mode()
        elif buttons["music"].contains(ctx.viewport, event.pos):
            self.session.click_feedback()
            self.session.toggle_music_enabled()
        return True

    def draw(self, ctx: UiContext, *, now_ms: int) -> None:
        ctx.surface.fill(theme.BLACK)
        draw_background(ctx, self.session.background_mode, theme.MID_GREY, elapsed_ms=now_ms)

        title = ctx.assets.image("title", ctx.viewport.size(800, 100))
        ctx.surface.blit(title, ctx.viewport.to_screen((200, 100)))
        draw_text(ctx, "Version reecrite avec scenes, services et tests", (600, 230), 22, theme.WHITE, center=True)

        buttons = self._buttons()
        for button in buttons.values():
            button.draw(ctx)

        draw_text(ctx, "Arriere-plan :", (15, 754), 36, theme.WHITE)
        draw_text(ctx, "Musique :", (15, 694), 36, theme.WHITE)

    def _buttons(self) -> dict[str, Button]:
        music_label = "On" if self.session.music_enabled else "Off"
        return {
            "play": Button((450, 300, 300, 100), "Jouer", 54, theme.LIGHT_GREY, theme.WHITE),
            "info": Button((400, 500, 400, 100), "Informations", 48, theme.LIGHT_GREY, theme.WHITE),
            "quit": Button((960, 730, 220, 50), "Quitter", 26, theme.RED, theme.lighten(theme.RED, 0.3)),
            "background": Button(
                (285, 745, 180, 50),
                theme.background_mode_label(self.session.background_mode),
                28,
                theme.GREEN if self.session.background_mode is not BackgroundMode.DISABLED else theme.LIGHT_GREY,
                theme.WHITE,
            ),
            "music": Button(
                (220, 685, 80, 50),
                music_label,
                28,
                theme.GREEN if self.session.music_enabled else theme.LIGHT_GREY,
                theme.WHITE,
            ),
        }


class RulesScene(Scene):
    def handle_event(self, event: pg.event.Event, ctx: UiContext, *, now_ms: int) -> bool | None:
        if event.type != pg.MOUSEBUTTONDOWN or event.button != 1:
            return True

        buttons = self._buttons()
        left_button = buttons["left"]
        if left_button.contains(ctx.viewport, event.pos):
            self.session.click_feedback()
            if self.session.rules_page == 1:
                self.session.open_main_menu()
            else:
                self.session.rules_page = max(1, self.session.rules_page - 1)
        elif buttons["next"].contains(ctx.viewport, event.pos):
            self.session.click_feedback()
            if self.session.rules_page < 4:
                self.session.rules_page = min(4, self.session.rules_page + 1)
            else:
                self.session.open_main_menu()
        return True

    def draw(self, ctx: UiContext, *, now_ms: int) -> None:
        ctx.surface.fill(theme.BLACK)
        draw_background(ctx, self.session.background_mode, theme.MID_GREY, elapsed_ms=now_ms)

        page_index = self.session.rules_page - 1
        title, lines = RULES_PAGES[page_index]
        draw_text(ctx, "Informations", (600, 100), 72, theme.WHITE, center=True)
        draw_text(ctx, title, (600, 190), 48, theme.WHITE, center=True)
        draw_text(ctx, f"Page {self.session.rules_page}/4", (600, 700), 32, theme.WHITE, center=True)

        y = 300
        for line in lines:
            draw_text(ctx, line, (135, y), 28, theme.WHITE)
            y += 58

        buttons = self._buttons()
        buttons["left"].draw(ctx)
        buttons["next"].draw(ctx)

    def _buttons(self) -> dict[str, Button]:
        return {
            "left": Button(
                (50, 650, 300, 100),
                "Menu" if self.session.rules_page == 1 else "Precedent",
                52 if self.session.rules_page == 1 else 48,
                theme.LIGHT_GREY,
                theme.WHITE,
            ),
            "next": Button(
                (850, 650, 300, 100),
                "Suivant" if self.session.rules_page < 4 else "Compris !",
                50,
                theme.LIGHT_GREY,
                theme.WHITE,
            ),
        }


class LevelSelectScene(Scene):
    def handle_event(self, event: pg.event.Event, ctx: UiContext, *, now_ms: int) -> bool | None:
        if event.type != pg.MOUSEBUTTONDOWN or event.button != 1:
            return True

        base_buttons = self._base_buttons()
        if base_buttons["back"].contains(ctx.viewport, event.pos):
            self.session.click_feedback()
            self.session.open_main_menu()
            return True
        if base_buttons["speedrun"].contains(ctx.viewport, event.pos):
            self.session.click_feedback()
            self.session.toggle_speedrun_enabled()
            return True
        if base_buttons["help"].contains(ctx.viewport, event.pos):
            self.session.click_feedback()
            self.session.toggle_speedrun_help()
            return True

        for button, level_number in self._level_buttons():
            if button.contains(ctx.viewport, event.pos):
                self.session.click_feedback()
                self.session.start_level(level_number, now_ms=now_ms)
                return True
        return True

    def draw(self, ctx: UiContext, *, now_ms: int) -> None:
        ctx.surface.fill(theme.BLACK)
        draw_background(ctx, self.session.background_mode, theme.MID_GREY, elapsed_ms=now_ms)

        draw_text(ctx, "Selectionnez un niveau", (600, 80), 62, theme.WHITE, center=True)

        for button in self._base_buttons().values():
            button.draw(ctx)

        for button, level_number in self._level_buttons():
            button.draw(ctx)
            if not self.session.is_level_unlocked(level_number):
                draw_image_in_rect(ctx, "lock", (button.rect[0] + 8, button.rect[1] + 7, 44, 46), padding=0)

        draw_text(ctx, "Mode speedrun :", (710, 725), 34, theme.WHITE)
        if self.session.show_speedrun_help:
            draw_text(ctx, "Resoudre les niveaux 1 a 40 le plus vite possible.", (420, 700), 22, theme.WHITE)
            draw_text(ctx, "Le chrono commence au niveau 1 et le restart ne le remet pas a zero.", (360, 732), 22, theme.WHITE)
            draw_text(ctx, "Seul le niveau 1 est selectionnable en speedrun.", (460, 764), 22, theme.WHITE)
        elif self.session.best_speedrun_time_ms is not None:
            draw_text(
                ctx,
                f"Meilleur temps : {format_elapsed_time(self.session.best_speedrun_time_ms)}",
                (710, 765),
                26,
                theme.WHITE,
            )

        if self.session.can_open_secret_level():
            draw_text(ctx, "Le niveau secret se debloque depuis le niveau 50.", (40, 745), 22, theme.WHITE)

    def _base_buttons(self) -> dict[str, Button]:
        return {
            "back": Button((20, 680, 300, 100), "Retour", 54, theme.LIGHT_GREY, theme.WHITE),
            "speedrun": Button(
                (1050, 720, 70, 50),
                "On" if self.session.speedrun_enabled else "Off",
                28,
                theme.GREEN if self.session.speedrun_enabled else theme.LIGHT_GREY,
                theme.WHITE,
            ),
            "help": Button(
                (1140, 720, 30, 30),
                "?",
                24,
                theme.GREEN if self.session.show_speedrun_help else theme.LIGHT_GREY,
                theme.WHITE,
            ),
        }

    def _level_buttons(self) -> list[tuple[Button, int]]:
        buttons: list[tuple[Button, int]] = []
        level_number = 1
        for row in range(5):
            for column in range(10):
                color = theme.difficulty_color(level_number)
                unlocked = self.session.is_level_unlocked(level_number)
                base_color = theme.mix_colors(color, theme.LIGHT_GREY, 0.55) if unlocked else theme.mix_colors(color, theme.BLACK, 0.55)
                hover_color = theme.mix_colors(base_color, theme.WHITE, 0.35)
                label = str(level_number) if unlocked else ""
                buttons.append(
                    (
                        Button(
                            (120 + column * 100, 170 + row * 90, 60, 60),
                            label,
                            26,
                            base_color,
                            hover_color,
                        ),
                        level_number,
                    )
                )
                level_number += 1
        return buttons


class GameplayScene(Scene):
    def __init__(self, session: GameSession) -> None:
        super().__init__(session)
        self.random = Random()
        self.particles = []
        self._active_level_token: int | None = None
        self._celebrated_level_token: int | None = None

    def handle_event(self, event: pg.event.Event, ctx: UiContext, *, now_ms: int) -> bool | None:
        if self.session.active_level is None:
            return True

        buttons = self._buttons()

        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if buttons["menu"].contains(ctx.viewport, event.pos):
                self.session.click_feedback()
                self.session.leave_gameplay()
                return True
            if buttons["restart"].contains(ctx.viewport, event.pos):
                self.session.click_feedback()
                self.session.restart_level(now_ms=now_ms)
                return True
            if buttons["top_next"] and buttons["top_next"].contains(ctx.viewport, event.pos):
                self.session.click_feedback()
                self.session.advance_to_next_level(now_ms=now_ms)
                return True
            if buttons["victory_next"] and buttons["victory_next"].contains(ctx.viewport, event.pos):
                self.session.click_feedback()
                self.session.advance_to_next_level(now_ms=now_ms)
                return True

            self.session.begin_drag(ctx.viewport.to_world(event.pos))
            return True

        if event.type == pg.MOUSEBUTTONUP and event.button == 1:
            self.session.end_drag()
            return True

        if event.type == pg.MOUSEMOTION and pg.mouse.get_pressed()[0]:
            self.session.drag_selected(ctx.viewport.to_world(event.pos))
            return True

        if event.type == pg.MOUSEBUTTONDOWN and event.button == 3:
            self.session.cycle_bond_at(ctx.viewport.to_world(event.pos), now_ms=now_ms)
            return True

        return True

    def update(self, dt_ms: int, *, now_ms: int) -> None:
        active = self.session.active_level
        token = id(active) if active else None
        if token != self._active_level_token:
            self._active_level_token = token
            self._celebrated_level_token = None
            self.particles = []

        if active and active.solved and token != self._celebrated_level_token:
            self.particles.extend(spawn_victory_particles(self.random))
            self._celebrated_level_token = token

        self.particles = update_particles(self.particles, dt_ms)

    def draw(self, ctx: UiContext, *, now_ms: int) -> None:
        active = self.session.active_level
        if active is None:
            return

        level_color = theme.difficulty_color(active.level_number)
        ctx.surface.fill(theme.BLACK)
        draw_background(ctx, self.session.background_mode, theme.mix_colors(level_color, theme.DARK_GREY, 0.25), elapsed_ms=now_ms)

        pg.draw.rect(ctx.surface, theme.LIGHT_GREY, ctx.viewport.rect(0, 0, 1200, 90))
        draw_particles(ctx, self.particles)
        draw_atoms(
            ctx,
            active.atoms,
            self.session.catalog.atom_specs,
            selected_atom_id=active.selected_atom_id,
        )
        self._draw_header(ctx)
        self._draw_controls(ctx)
        self._draw_victory_overlay(ctx, now_ms=now_ms)
        self._draw_speedrun_timer(ctx, now_ms=now_ms)

    def _draw_header(self, ctx: UiContext) -> None:
        active = self.session.active_level
        if active is None:
            return

        level_spec = self.session.level_spec(active.level_number)
        draw_text(ctx, f"Niveau {active.level_number}", (1045, 30), 28, theme.BLACK, center=True)
        draw_text(ctx, self.session.difficulty_label(active.level_number), (1045, 62), 24, theme.difficulty_color(active.level_number), center=True)
        draw_text(ctx, level_spec.name, (600, 28), 30, theme.BLACK, center=True)
        draw_text(ctx, level_spec.formula, (600, 62), 26, theme.BLACK, center=True)

    def _draw_controls(self, ctx: UiContext) -> None:
        buttons = self._buttons()
        for button in ("menu", "restart", "top_next"):
            widget = buttons.get(button)
            if widget is None:
                continue
            widget.draw(ctx)

        draw_image_in_rect(ctx, "restart", buttons["restart"].rect, padding=10)

        victory_next = buttons.get("victory_next")
        if victory_next is not None:
            victory_next.draw(ctx)
            draw_image_in_rect(ctx, "next", victory_next.rect, padding=20)

    def _draw_victory_overlay(self, ctx: UiContext, *, now_ms: int) -> None:
        active = self.session.active_level
        if active is None or not active.solved:
            return

        if self.session.speedrun_enabled and active.level_number == CONFIG.speedrun_last_level:
            draw_text(ctx, "Speedrun termine !", (600, 300), 70, theme.GREEN, center=True)
            if self.session.speedrun_finished_time_ms is not None:
                draw_text(
                    ctx,
                    f"Temps final : {format_elapsed_time(self.session.speedrun_finished_time_ms)}",
                    (600, 480),
                    46,
                    theme.GREEN,
                    center=True,
                )
            if self.session.speedrun_new_record:
                draw_text(ctx, "Nouveau record !", (600, 570), 38, theme.GREEN, center=True)
            elif self.session.best_speedrun_time_ms is not None:
                draw_text(
                    ctx,
                    f"Record : {format_elapsed_time(self.session.best_speedrun_time_ms)}",
                    (600, 570),
                    38,
                    theme.GREEN,
                    center=True,
                )
            return

        draw_text(ctx, "Niveau resolu !", (600, 300), 70, theme.WHITE, center=True)

    def _draw_speedrun_timer(self, ctx: UiContext, *, now_ms: int) -> None:
        timer = self.session.active_speedrun_time_ms(now_ms=now_ms)
        if timer is None:
            return
        draw_text(ctx, format_elapsed_time(timer), (1010, 748), 42, theme.GREEN)

    def _buttons(self) -> dict[str, Button | None]:
        active = self.session.active_level
        if active is None:
            return {"menu": None, "restart": None, "top_next": None, "victory_next": None}

        abandon = (
            self.session.speedrun_enabled
            and active.level_number <= CONFIG.speedrun_last_level
            and not (
                active.level_number == CONFIG.speedrun_last_level
                and active.solved
            )
        )
        menu_label = "Abandonner" if abandon else "Menu"

        top_next: Button | None = None
        if not self.session.speedrun_enabled:
            if active.level_number < self.session.save.unlocked_standard_level:
                top_next = Button((15, 50, 190, 30), "Niveau suivant", 18, theme.LIGHT_GREY, theme.WHITE)

        if not self.session.speedrun_enabled and active.level_number == CONFIG.standard_level_count and self.session.can_open_secret_level():
            top_next = Button((15, 50, 190, 30), "Niveau secret", 18, theme.LIGHT_GREY, theme.WHITE)

        victory_next: Button | None = None
        if active.solved and self.session.next_level_number() is not None:
            victory_next = Button((520, 540, 160, 120), "", 20, theme.LIGHT_GREY, theme.WHITE)

        return {
            "menu": Button((15, 15, 190, 30), menu_label, 18, theme.LIGHT_GREY, theme.WHITE),
            "restart": Button((215, 15, 60, 60), "", 18, theme.LIGHT_GREY, theme.WHITE),
            "top_next": top_next,
            "victory_next": victory_next,
        }


class SceneRegistry:
    def __init__(self, session: GameSession) -> None:
        self._scenes = {
            Screen.INTRO: IntroScene(session),
            Screen.MAIN_MENU: MainMenuScene(session),
            Screen.RULES: RulesScene(session),
            Screen.LEVEL_SELECT: LevelSelectScene(session),
            Screen.GAMEPLAY: GameplayScene(session),
        }

    def get(self, screen: Screen) -> Scene:
        return self._scenes[screen]
