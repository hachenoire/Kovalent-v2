from __future__ import annotations

from math import cos, radians, sin
from random import Random
from typing import Mapping

from .models import (
    AtomSpec,
    BondChangeResult,
    LevelSpec,
    Point,
    RuntimeAtom,
)


class ChemistryService:
    """Encapsulates chemistry rules so rendering code stays dumb and reusable."""

    def __init__(
        self,
        atom_specs: Mapping[str, AtomSpec],
        *,
        max_bond_order: int = 3,
    ) -> None:
        self._atom_specs = atom_specs
        self._max_bond_order = max_bond_order

    def cycle_bond(
        self,
        atoms: Mapping[int, RuntimeAtom],
        source_id: int,
        target_id: int,
    ) -> BondChangeResult:
        if source_id == target_id:
            return BondChangeResult.REJECTED

        source = atoms[source_id]
        target = atoms[target_id]
        source_spec = self._atom_specs[source.symbol]
        target_spec = self._atom_specs[target.symbol]
        current_order = source.bond_order_to(target_id)

        if current_order == 0:
            if (
                source.remaining_capacity(source_spec.valence) >= 1
                and target.remaining_capacity(target_spec.valence) >= 1
            ):
                source.set_bond(target_id, 1)
                target.set_bond(source_id, 1)
                return BondChangeResult.CREATED_OR_INCREMENTED
            return BondChangeResult.REJECTED

        can_increase = (
            current_order < min(source_spec.valence, target_spec.valence, self._max_bond_order)
            and source.remaining_capacity(source_spec.valence) >= 1
            and target.remaining_capacity(target_spec.valence) >= 1
        )

        if can_increase:
            source.set_bond(target_id, current_order + 1)
            target.set_bond(source_id, current_order + 1)
            return BondChangeResult.CREATED_OR_INCREMENTED

        source.remove_bond(target_id)
        target.remove_bond(source_id)
        return BondChangeResult.REMOVED

    def is_solved(self, atoms: Mapping[int, RuntimeAtom]) -> bool:
        if not atoms:
            return False

        for atom in atoms.values():
            maximum_valence = self._atom_specs[atom.symbol].valence
            if atom.used_valence != maximum_valence:
                return False

        start_atom_id = next(iter(atoms))
        visited: set[int] = set()
        stack = [start_atom_id]

        while stack:
            atom_id = stack.pop()
            if atom_id in visited:
                continue
            visited.add(atom_id)
            stack.extend(neighbor for neighbor in atoms[atom_id].bonds if neighbor not in visited)

        return len(visited) == len(atoms)


def create_level_layout(
    level: LevelSpec,
    *,
    rng: Random,
    play_area: tuple[float, float, float, float],
) -> dict[int, RuntimeAtom]:
    """Create atoms on a stable ellipse to keep the start readable and fair."""

    left, top, right, bottom = play_area
    center_x = (left + right) / 2
    center_y = (top + bottom) / 2
    radius_x = (right - left) * 0.33
    radius_y = (bottom - top) * 0.36

    symbols = list(level.atom_symbols)
    rng.shuffle(symbols)

    atoms: dict[int, RuntimeAtom] = {}
    total_atoms = len(symbols)
    for index, symbol in enumerate(symbols, start=1):
        angle = radians((360 / total_atoms) * (index - 1))
        atoms[index] = RuntimeAtom(
            atom_id=index,
            symbol=symbol,
            position=Point(
                center_x + cos(angle) * radius_x,
                center_y + sin(angle) * radius_y,
            ),
        )
    return atoms


def format_elapsed_time(milliseconds: int) -> str:
    minutes = milliseconds // 60_000
    seconds = (milliseconds % 60_000) // 1_000
    centiseconds = (milliseconds % 1_000) // 10
    if minutes == 0:
        return f"{seconds}.{centiseconds:02d}"
    return f"{minutes}:{seconds:02d}.{centiseconds:02d}"
