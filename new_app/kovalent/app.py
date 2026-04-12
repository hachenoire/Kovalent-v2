from __future__ import annotations

import pygame as pg

from .application.session import GameSession
from .config import ATOM_DATA_PATH, CONFIG, LEGACY_PROGRESS_PATH, LEVEL_DATA_PATH, SAVE_DATA_PATH
from .domain.models import Screen
from .infrastructure.assets import AssetStore
from .infrastructure.repositories import JsonCatalogRepository, JsonSaveRepository
from .ui import theme
from .ui.scenes import SceneRegistry
from .ui.view import Viewport
from .ui.widgets import UiContext


class GameApp:
    def __init__(self) -> None:
        pg.init()
        pg.font.init()

        self.display_flags = pg.RESIZABLE | pg.DOUBLEBUF
        self.surface = pg.display.set_mode((CONFIG.base_width, CONFIG.base_height), self.display_flags)

        self.assets = AssetStore()
        pg.display.set_caption(CONFIG.window_title)
        pg.display.set_icon(self.assets.icon())

        catalog = JsonCatalogRepository(
            atom_data_path=ATOM_DATA_PATH,
            level_data_path=LEVEL_DATA_PATH,
        ).load()
        save_repository = JsonSaveRepository(
            save_path=SAVE_DATA_PATH,
            legacy_progress_path=LEGACY_PROGRESS_PATH,
        )
        self.session = GameSession(
            catalog=catalog,
            save_repository=save_repository,
        )
        self.scenes = SceneRegistry(self.session)
        self.clock = pg.time.Clock()

    def run(self) -> None:
        running = True
        previous_tick = pg.time.get_ticks()

        while running:
            now_ms = pg.time.get_ticks()
            dt_ms = max(1, now_ms - previous_tick)
            previous_tick = now_ms

            viewport = Viewport.from_window(self.surface.get_size())
            ctx = UiContext(
                surface=self.surface,
                viewport=viewport,
                assets=self.assets,
                mouse_screen_pos=pg.mouse.get_pos(),
            )

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                    break
                if event.type == pg.VIDEORESIZE:
                    self.surface = pg.display.set_mode(event.size, self.display_flags)
                    continue

                active_scene = self.scenes.get(self.session.screen)
                result = active_scene.handle_event(event, ctx, now_ms=now_ms)
                if result is False:
                    running = False
                    break

            self.scenes.get(self.session.screen).update(dt_ms, now_ms=now_ms)

            desired_track = None if self.session.screen is Screen.INTRO else self.session.current_music_track
            self.assets.sync_music(desired_track, enabled=self.session.music_enabled)

            for effect in self.session.drain_effects():
                self.assets.play_sound(effect)

            self.surface.fill(theme.BLACK)
            draw_ctx = UiContext(
                surface=self.surface,
                viewport=Viewport.from_window(self.surface.get_size()),
                assets=self.assets,
                mouse_screen_pos=pg.mouse.get_pos(),
            )
            self.scenes.get(self.session.screen).draw(draw_ctx, now_ms=now_ms)
            pg.display.flip()
            self.clock.tick(CONFIG.fps)

        self.shutdown()

    def shutdown(self) -> None:
        self.assets.shutdown()
        pg.display.quit()
        pg.font.quit()
        pg.quit()


def run() -> None:
    GameApp().run()
