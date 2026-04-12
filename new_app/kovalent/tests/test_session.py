from __future__ import annotations

import unittest

from kovalent.application.repositories import GameCatalog
from kovalent.application.session import GameSession
from kovalent.domain.models import AtomSpec, SaveData
from kovalent.domain.models import LevelSpec


class _MemorySaveRepository:
    def __init__(self, initial: SaveData | None = None) -> None:
        self.current = initial or SaveData()
        self.saved_snapshots: list[SaveData] = []

    def load(self) -> SaveData:
        return SaveData(
            unlocked_standard_level=self.current.unlocked_standard_level,
            secret_level_unlocked=self.current.secret_level_unlocked,
            best_speedrun_time_ms=self.current.best_speedrun_time_ms,
        )

    def save(self, data: SaveData) -> None:
        snapshot = SaveData(
            unlocked_standard_level=data.unlocked_standard_level,
            secret_level_unlocked=data.secret_level_unlocked,
            best_speedrun_time_ms=data.best_speedrun_time_ms,
        )
        self.current = snapshot
        self.saved_snapshots.append(snapshot)


def _build_catalog() -> GameCatalog:
    atom_specs = {
        "H": AtomSpec("H", "Hydrogene", 1, (255, 255, 255), 25),
    }
    levels = tuple(
        LevelSpec(number=index, name=f"Test {index}", formula="H2", atom_symbols=("H", "H"))
        for index in range(1, 52)
    )
    return GameCatalog(atom_specs=atom_specs, levels=levels)


class GameSessionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repository = _MemorySaveRepository()
        self.session = GameSession(
            catalog=_build_catalog(),
            save_repository=self.repository,
        )

    def test_solving_first_level_unlocks_the_next_one(self) -> None:
        self.session.start_level(1, now_ms=1_000)
        assert self.session.active_level is not None

        self.session.active_level.selected_atom_id = 1
        target = self.session.active_level.atoms[2].position
        self.session.cycle_bond_at(target, now_ms=1_250)

        self.assertTrue(self.session.active_level.solved)
        self.assertEqual(self.session.save.unlocked_standard_level, 2)
        self.assertEqual(len(self.repository.saved_snapshots), 1)

    def test_speedrun_result_updates_the_record(self) -> None:
        self.session.speedrun_enabled = True
        self.session.speedrun_started_at_ms = 10_000
        self.session._load_level(40, now_ms=10_000, preserve_speedrun=True)
        assert self.session.active_level is not None

        self.session.active_level.selected_atom_id = 1
        target = self.session.active_level.atoms[2].position
        self.session.cycle_bond_at(target, now_ms=45_000)

        self.assertEqual(self.session.speedrun_finished_time_ms, 35_000)
        self.assertEqual(self.session.best_speedrun_time_ms, 35_000)
        self.assertTrue(self.session.speedrun_new_record)


if __name__ == "__main__":
    unittest.main()
