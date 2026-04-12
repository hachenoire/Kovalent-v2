from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto


type Color = tuple[int, int, int]


class Screen(Enum):
    INTRO = auto()
    MAIN_MENU = auto()
    RULES = auto()
    LEVEL_SELECT = auto()
    GAMEPLAY = auto()


class BackgroundMode(Enum):
    NORMAL = auto()
    CIRCLES = auto()
    TRIANGLES = auto()
    DISABLED = auto()


class MusicTrack(Enum):
    MAIN = auto()
    DOOM = auto()


class SoundEffect(Enum):
    BUTTON = auto()
    LINK = auto()
    ERROR = auto()
    WIN = auto()


class BondChangeResult(Enum):
    CREATED_OR_INCREMENTED = auto()
    REMOVED = auto()
    REJECTED = auto()


@dataclass(frozen=True, slots=True)
class Point:
    x: float
    y: float

    def __add__(self, other: "Point") -> "Point":
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Point") -> "Point":
        return Point(self.x - other.x, self.y - other.y)

    def clamp(
        self,
        *,
        left: float,
        top: float,
        right: float,
        bottom: float,
    ) -> "Point":
        return Point(
            min(max(self.x, left), right),
            min(max(self.y, top), bottom),
        )

    def distance_squared_to(self, other: "Point") -> float:
        dx = self.x - other.x
        dy = self.y - other.y
        return dx * dx + dy * dy


@dataclass(frozen=True, slots=True)
class AtomSpec:
    symbol: str
    name: str
    valence: int
    color: Color
    radius: float


@dataclass(frozen=True, slots=True)
class LevelSpec:
    number: int
    name: str
    formula: str
    atom_symbols: tuple[str, ...]


@dataclass(slots=True)
class RuntimeAtom:
    atom_id: int
    symbol: str
    position: Point
    bonds: dict[int, int] = field(default_factory=dict)

    @property
    def used_valence(self) -> int:
        return sum(self.bonds.values())

    def remaining_capacity(self, maximum_valence: int) -> int:
        return maximum_valence - self.used_valence

    def bond_order_to(self, other_id: int) -> int:
        return self.bonds.get(other_id, 0)

    def set_bond(self, other_id: int, order: int) -> None:
        self.bonds[other_id] = order

    def remove_bond(self, other_id: int) -> None:
        self.bonds.pop(other_id, None)


@dataclass(slots=True)
class ActiveLevelState:
    level_number: int
    atoms: dict[int, RuntimeAtom]
    selected_atom_id: int | None = None
    dragged_atom_id: int | None = None
    drag_offset: Point = field(default_factory=lambda: Point(0.0, 0.0))
    solved: bool = False
    solved_at_ms: int | None = None


@dataclass(slots=True)
class SaveData:
    unlocked_standard_level: int = 1
    secret_level_unlocked: bool = False
    best_speedrun_time_ms: int | None = None
