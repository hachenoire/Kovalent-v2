from __future__ import annotations

import unittest

from kovalent.domain.models import AtomSpec, BondChangeResult, Point, RuntimeAtom
from kovalent.domain.services import ChemistryService


class ChemistryServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.specs = {
            "H": AtomSpec("H", "Hydrogene", 1, (255, 255, 255), 25),
            "O": AtomSpec("O", "Oxygene", 2, (255, 0, 0), 40),
            "C": AtomSpec("C", "Carbone", 4, (50, 50, 50), 40),
        }
        self.service = ChemistryService(self.specs)

    def test_cycle_bond_creates_then_increments_then_removes(self) -> None:
        atoms = {
            1: RuntimeAtom(1, "C", Point(0, 0)),
            2: RuntimeAtom(2, "O", Point(50, 0)),
        }

        first = self.service.cycle_bond(atoms, 1, 2)
        second = self.service.cycle_bond(atoms, 1, 2)
        third = self.service.cycle_bond(atoms, 1, 2)

        self.assertIs(first, BondChangeResult.CREATED_OR_INCREMENTED)
        self.assertEqual(atoms[1].bond_order_to(2), 0, "The third click should remove the bond after reaching the max order.")
        self.assertIs(second, BondChangeResult.CREATED_OR_INCREMENTED)
        self.assertIs(third, BondChangeResult.REMOVED)

    def test_is_solved_requires_one_connected_molecule(self) -> None:
        disconnected = {
            1: RuntimeAtom(1, "H", Point(0, 0), {2: 1}),
            2: RuntimeAtom(2, "H", Point(20, 0), {1: 1}),
            3: RuntimeAtom(3, "H", Point(80, 0), {4: 1}),
            4: RuntimeAtom(4, "H", Point(100, 0), {3: 1}),
        }
        connected = {
            1: RuntimeAtom(1, "O", Point(0, 0), {2: 1, 3: 1}),
            2: RuntimeAtom(2, "H", Point(-20, 0), {1: 1}),
            3: RuntimeAtom(3, "H", Point(20, 0), {1: 1}),
        }

        self.assertFalse(self.service.is_solved(disconnected))
        self.assertTrue(self.service.is_solved(connected))


if __name__ == "__main__":
    unittest.main()
