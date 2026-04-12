from __future__ import annotations

from collections import deque
from random import Random

from ..config import CONFIG
from ..domain.models import (
    ActiveLevelState,
    BackgroundMode,
    BondChangeResult,
    MusicTrack,
    Point,
    SaveData,
    Screen,
    SoundEffect,
)
from ..domain.services import ChemistryService, create_level_layout
from .repositories import GameCatalog, SaveRepository


class GameSession:
    """Owns mutable game state and keeps the UI layer thin.

    The scenes only ask the session to perform intent-based actions such as
    "start level 3" or "cycle the bond under the cursor". That keeps business
    rules testable without a running window.
    """

    def __init__(
        self,
        *,
        catalog: GameCatalog,
        save_repository: SaveRepository,
        randomizer: Random | None = None,
    ) -> None:
        self.catalog = catalog
        self.save_repository = save_repository
        self.random = randomizer or Random()
        self.chemistry = ChemistryService(catalog.atom_specs)
        self.pending_effects: deque[SoundEffect] = deque()

        self.save = self._normalize_save(save_repository.load())
        self.screen = (
            Screen.MAIN_MENU
            if self.save.unlocked_standard_level >= 4
            else Screen.INTRO
        )
        self.intro_elapsed_ms = (
            CONFIG.intro_duration_ms
            if self.screen is Screen.MAIN_MENU
            else 0
        )

        self.rules_page = 1
        self.background_mode = BackgroundMode.NORMAL
        self.music_enabled = True
        self.speedrun_enabled = False
        self.show_speedrun_help = False
        self.speedrun_started_at_ms: int | None = None
        self.speedrun_finished_time_ms: int | None = None
        self.speedrun_new_record = False
        self.active_level: ActiveLevelState | None = None

    def _normalize_save(self, save_data: SaveData) -> SaveData:
        unlocked = min(
            max(1, save_data.unlocked_standard_level),
            CONFIG.standard_level_count,
        )
        return SaveData(
            unlocked_standard_level=unlocked,
            secret_level_unlocked=save_data.secret_level_unlocked,
            best_speedrun_time_ms=save_data.best_speedrun_time_ms,
        )

    @property
    def current_music_track(self) -> MusicTrack:
        if self.active_level and self.active_level.level_number >= 50:
            return MusicTrack.DOOM
        return MusicTrack.MAIN

    @property
    def best_speedrun_time_ms(self) -> int | None:
        return self.save.best_speedrun_time_ms

    @property
    def current_level_number(self) -> int | None:
        return self.active_level.level_number if self.active_level else None

    @staticmethod
    def difficulty_label(level_number: int) -> str:
        if level_number <= 10:
            return "Facile"
        if level_number <= 20:
            return "Normal"
        if level_number <= 30:
            return "Difficile"
        if level_number <= 40:
            return "Expert"
        if level_number <= 49:
            return "Maitre"
        return "Impossible"

    def level_spec(self, level_number: int):
        return self.catalog.levels[level_number - 1]

    def drain_effects(self) -> tuple[SoundEffect, ...]:
        effects = tuple(self.pending_effects)
        self.pending_effects.clear()
        return effects

    def advance_intro(self, dt_ms: int) -> None:
        if self.screen is not Screen.INTRO:
            return
        self.intro_elapsed_ms = min(
            self.intro_elapsed_ms + dt_ms,
            CONFIG.intro_duration_ms,
        )
        if self.intro_elapsed_ms >= CONFIG.intro_duration_ms:
            self.screen = Screen.MAIN_MENU

    def skip_intro(self) -> None:
        self.intro_elapsed_ms = CONFIG.intro_duration_ms
        self.screen = Screen.MAIN_MENU

    def open_main_menu(self) -> None:
        self.active_level = None
        self.screen = Screen.MAIN_MENU

    def open_rules(self, page: int = 1) -> None:
        self.rules_page = max(1, min(page, 4))
        self.screen = Screen.RULES

    def open_level_select(self) -> None:
        self.active_level = None
        self.screen = Screen.LEVEL_SELECT

    def leave_gameplay(self) -> None:
        if (
            self.speedrun_enabled
            and self.active_level
            and self.active_level.level_number <= CONFIG.speedrun_last_level
            and not (
                self.active_level.level_number == CONFIG.speedrun_last_level
                and self.active_level.solved
            )
        ):
            self.speedrun_started_at_ms = None
            self.speedrun_finished_time_ms = None
            self.speedrun_new_record = False

        self.open_level_select()

    def toggle_background_mode(self) -> None:
        order = list(BackgroundMode)
        index = order.index(self.background_mode)
        self.background_mode = order[(index + 1) % len(order)]

    def toggle_music_enabled(self) -> None:
        self.music_enabled = not self.music_enabled

    def toggle_speedrun_enabled(self) -> None:
        if self.active_level is not None:
            return
        self.speedrun_enabled = not self.speedrun_enabled
        self.speedrun_started_at_ms = None
        self.speedrun_finished_time_ms = None
        self.speedrun_new_record = False

    def toggle_speedrun_help(self) -> None:
        self.show_speedrun_help = not self.show_speedrun_help

    def is_level_unlocked(self, level_number: int) -> bool:
        if level_number < 1 or level_number > CONFIG.standard_level_count:
            return False
        if self.speedrun_enabled:
            return level_number == 1
        return level_number <= self.save.unlocked_standard_level

    def start_level(self, level_number: int, *, now_ms: int) -> bool:
        if level_number == CONFIG.secret_level:
            if not self.save.secret_level_unlocked:
                return False
        elif not self.is_level_unlocked(level_number):
            return False

        preserve_speedrun = (
            self.speedrun_enabled
            and self.speedrun_started_at_ms is not None
            and level_number > 1
        )
        self._load_level(level_number, now_ms=now_ms, preserve_speedrun=preserve_speedrun)
        return True

    def restart_level(self, *, now_ms: int) -> None:
        if self.active_level is None:
            return
        self._load_level(
            self.active_level.level_number,
            now_ms=now_ms,
            preserve_speedrun=self.speedrun_started_at_ms is not None,
        )

    def _load_level(
        self,
        level_number: int,
        *,
        now_ms: int,
        preserve_speedrun: bool,
    ) -> None:
        level = self.level_spec(level_number)
        self.active_level = ActiveLevelState(
            level_number=level_number,
            atoms=create_level_layout(
                level,
                rng=self.random,
                play_area=CONFIG.play_area,
            ),
        )
        self.screen = Screen.GAMEPLAY

        if self.speedrun_enabled and not preserve_speedrun and level_number == 1:
            self.speedrun_started_at_ms = now_ms
            self.speedrun_finished_time_ms = None
            self.speedrun_new_record = False

    def can_open_secret_level(self) -> bool:
        return self.save.secret_level_unlocked

    def next_level_number(self) -> int | None:
        if self.active_level is None:
            return None
        next_level = self.active_level.level_number + 1
        if next_level > len(self.catalog.levels):
            return None
        if self.speedrun_enabled and self.active_level.level_number >= CONFIG.speedrun_last_level:
            return None
        return next_level

    def advance_to_next_level(self, *, now_ms: int) -> None:
        next_level = self.next_level_number()
        if next_level is None:
            return
        self._load_level(next_level, now_ms=now_ms, preserve_speedrun=self.speedrun_enabled)

    def begin_drag(self, pointer: Point) -> None:
        if self.active_level is None or self.active_level.solved:
            return

        atom = self.find_atom_at(pointer)
        if atom is None:
            self.active_level.selected_atom_id = None
            return

        self.active_level.selected_atom_id = atom.atom_id
        self.active_level.dragged_atom_id = atom.atom_id
        self.active_level.drag_offset = pointer - atom.position

    def drag_selected(self, pointer: Point) -> None:
        if self.active_level is None or self.active_level.dragged_atom_id is None:
            return

        atom = self.active_level.atoms[self.active_level.dragged_atom_id]
        candidate = (pointer - self.active_level.drag_offset).clamp(
            left=CONFIG.play_area[0],
            top=CONFIG.play_area[1],
            right=CONFIG.play_area[2],
            bottom=CONFIG.play_area[3],
        )
        atom.position = candidate

    def end_drag(self) -> None:
        if self.active_level is None:
            return
        self.active_level.dragged_atom_id = None

    def find_atom_at(self, pointer: Point):
        if self.active_level is None:
            return None

        # Iterating in reverse makes the most recently created atoms feel
        # "on top", which matches player expectations during drag interactions.
        for atom in reversed(tuple(self.active_level.atoms.values())):
            radius = self.catalog.atom_specs[atom.symbol].radius
            if atom.position.distance_squared_to(pointer) <= radius * radius:
                return atom
        return None

    def cycle_bond_at(self, pointer: Point, *, now_ms: int) -> None:
        if self.active_level is None or self.active_level.solved:
            return
        if self.active_level.selected_atom_id is None:
            return

        target = self.find_atom_at(pointer)
        if target is None or target.atom_id == self.active_level.selected_atom_id:
            return

        result = self.chemistry.cycle_bond(
            self.active_level.atoms,
            self.active_level.selected_atom_id,
            target.atom_id,
        )

        if result is BondChangeResult.CREATED_OR_INCREMENTED:
            self.pending_effects.append(SoundEffect.LINK)
        else:
            self.pending_effects.append(SoundEffect.ERROR)

        if result is not BondChangeResult.REJECTED:
            self._refresh_victory_state(now_ms=now_ms)

    def _refresh_victory_state(self, *, now_ms: int) -> None:
        if self.active_level is None or self.active_level.solved:
            return
        if not self.chemistry.is_solved(self.active_level.atoms):
            return

        self.active_level.solved = True
        self.active_level.solved_at_ms = now_ms
        self.pending_effects.append(SoundEffect.WIN)

        save_changed = False
        level_number = self.active_level.level_number

        if level_number < CONFIG.standard_level_count:
            if level_number >= self.save.unlocked_standard_level:
                self.save.unlocked_standard_level = min(
                    level_number + 1,
                    CONFIG.standard_level_count,
                )
                save_changed = True
        elif level_number == CONFIG.standard_level_count:
            if not self.save.secret_level_unlocked:
                self.save.secret_level_unlocked = True
                save_changed = True

        if (
            self.speedrun_enabled
            and level_number == CONFIG.speedrun_last_level
            and self.speedrun_started_at_ms is not None
        ):
            final_time = now_ms - self.speedrun_started_at_ms
            self.speedrun_finished_time_ms = final_time
            if (
                self.save.best_speedrun_time_ms is None
                or final_time < self.save.best_speedrun_time_ms
            ):
                self.save.best_speedrun_time_ms = final_time
                self.speedrun_new_record = True
                save_changed = True
            else:
                self.speedrun_new_record = False

        if save_changed:
            self.save_repository.save(self.save)

    def active_speedrun_time_ms(self, *, now_ms: int) -> int | None:
        if not self.speedrun_enabled or self.speedrun_started_at_ms is None:
            return None
        if self.speedrun_finished_time_ms is not None:
            return self.speedrun_finished_time_ms
        return now_ms - self.speedrun_started_at_ms

    def click_feedback(self) -> None:
        self.pending_effects.append(SoundEffect.BUTTON)
