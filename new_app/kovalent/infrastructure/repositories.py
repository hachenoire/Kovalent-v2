from __future__ import annotations

import json
from pathlib import Path

from ..application.repositories import GameCatalog
from ..domain.models import AtomSpec, LevelSpec, SaveData


class JsonCatalogRepository:
    """Loads static atom and level data from JSON files."""

    def __init__(self, *, atom_data_path: Path, level_data_path: Path) -> None:
        self.atom_data_path = atom_data_path
        self.level_data_path = level_data_path

    def load(self) -> GameCatalog:
        atom_payload = json.loads(self.atom_data_path.read_text(encoding="utf-8"))
        level_payload = json.loads(self.level_data_path.read_text(encoding="utf-8"))

        atom_specs = {
            item["symbole"]: AtomSpec(
                symbol=item["symbole"],
                name=item["nom"],
                valence=int(item["valence"]),
                color=tuple(item["couleur"]),
                radius=float(item["rayon"]),
            )
            for item in atom_payload["atome"]
        }

        levels = tuple(
            LevelSpec(
                number=index,
                name=item["nom"],
                formula=item["formule brute"],
                atom_symbols=tuple(item["atomes"]),
            )
            for index, item in enumerate(level_payload["niveau"], start=1)
        )

        return GameCatalog(atom_specs=atom_specs, levels=levels)


class JsonSaveRepository:
    """Persists player progression in a dedicated save file for the rewrite.

    The loader also understands the legacy `progress.txt` format so existing
    players keep their progression when moving to the rewritten version.
    """

    def __init__(self, *, save_path: Path, legacy_progress_path: Path | None = None) -> None:
        self.save_path = save_path
        self.legacy_progress_path = legacy_progress_path

    def load(self) -> SaveData:
        if self.save_path.exists():
            try:
                payload = json.loads(self.save_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                return SaveData()
            return SaveData(
                unlocked_standard_level=int(payload.get("unlocked_standard_level", 1)),
                secret_level_unlocked=bool(payload.get("secret_level_unlocked", False)),
                best_speedrun_time_ms=(
                    int(payload["best_speedrun_time_ms"])
                    if payload.get("best_speedrun_time_ms") is not None
                    else None
                ),
            )

        legacy_value = self._read_legacy_progress()
        if legacy_value is None:
            return SaveData()

        return SaveData(
            unlocked_standard_level=max(1, min(legacy_value - 1, 50)),
            secret_level_unlocked=legacy_value >= 52,
        )

    def save(self, data: SaveData) -> None:
        payload = {
            "file_version": 1,
            "unlocked_standard_level": data.unlocked_standard_level,
            "secret_level_unlocked": data.secret_level_unlocked,
            "best_speedrun_time_ms": data.best_speedrun_time_ms,
        }
        self.save_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _read_legacy_progress(self) -> int | None:
        if self.legacy_progress_path is None or not self.legacy_progress_path.exists():
            return None
        try:
            return int(self.legacy_progress_path.read_text(encoding="utf-8").strip())
        except ValueError:
            return None
