from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from ..domain.models import AtomSpec, LevelSpec, SaveData


@dataclass(frozen=True, slots=True)
class GameCatalog:
    atom_specs: dict[str, AtomSpec]
    levels: tuple[LevelSpec, ...]


class CatalogRepository(Protocol):
    def load(self) -> GameCatalog: ...


class SaveRepository(Protocol):
    def load(self) -> SaveData: ...

    def save(self, data: SaveData) -> None: ...
