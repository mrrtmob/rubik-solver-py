"""
Tests for rubik-solver-py.

Run with: pytest tests/ -v
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from rubik_solver import Cube, Center, Corner, Edge
from rubik_solver.math_utils import cnk, factorial, rotate_left, rotate_right


# ── Math utilities ─────────────────────────────────────────────────

class TestMathUtils:
    def test_cnk_basic(self):
        assert cnk(5, 2) == 10
        assert cnk(6, 3) == 20
        assert cnk(4, 0) == 1
        assert cnk(4, 4) == 1

    def test_cnk_edge(self):
        assert cnk(3, 5) == 0   # n < k → 0
        assert cnk(0, 0) == 1

    def test_factorial(self):
        assert factorial(0) == 1
        assert factorial(1) == 1
        assert factorial(5) == 120
        assert factorial(8) == 40320

    def test_rotate_left(self):
        arr = bytearray([1, 2, 3, 4, 5])
        rotate_left(arr, 1, 3)
        assert list(arr) == [1, 3, 4, 2, 5]

    def test_rotate_right(self):
        arr = bytearray([1, 2, 3, 4, 5])
        rotate_right(arr, 1, 3)
        assert list(arr) == [1, 4, 2, 3, 5]


# ── Cube construction ─────────────────────────────────────────────

class TestCubeConstruction:
    def test_solved_by_default(self):
        c = Cube()
        assert list(c.center) == [0, 1, 2, 3, 4, 5]
        assert list(c.cp)     == [0, 1, 2, 3, 4, 5, 6, 7]
        assert list(c.co)     == [0] * 8
        assert list(c.ep)     == list(range(12))
        assert list(c.eo)     == [0] * 12

    def test_clone_is_independent(self):
        c1 = Cube()
        c2 = c1.clone()
        c2.cp[0] = 5
        assert c1.cp[0] == 0   # original unchanged

    def test_is_solved_default(self):
        c = Cube()
        # Without init_solver, is_solved still works for identity
        assert c.is_solved()


# ── Serialization ─────────────────────────────────────────────────

class TestSerialization:
    SOLVED_STR = "UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB"

    def test_as_string_solved(self):
        c = Cube()
        assert c.as_string() == self.SOLVED_STR

    def test_from_string_roundtrip(self):
        c1 = Cube()
        s  = c1.as_string()
        c2 = Cube.from_string(s)
        assert c2.as_string() == s

    def test_from_string_solved(self):
        c = Cube.from_string(self.SOLVED_STR)
        assert list(c.cp) == [0, 1, 2, 3, 4, 5, 6, 7]
        assert list(c.co) == [0] * 8
        assert list(c.ep) == list(range(12))
        assert list(c.eo) == [0] * 12


# ── Inverse algorithm ─────────────────────────────────────────────

class TestInverse:
    def test_basic(self):
        assert Cube.inverse("R U R' U'") == "U R U' R'"

    def test_double_moves(self):
        assert Cube.inverse("R2 U2") == "U2 R2"

    def test_empty(self):
        assert Cube.inverse("") == ""

    def test_single_prime(self):
        assert Cube.inverse("R'") == "R"

    def test_single_plain(self):
        assert Cube.inverse("R") == "R'"


# ── Verify ────────────────────────────────────────────────────────

class TestVerify:
    def test_solved_cube_valid(self):
        assert Cube().verify() is True

    def test_bad_cp_detected(self):
        c = Cube()
        c.cp[0] = 1  # duplicate corner
        result = c.verify()
        assert result != True
        assert isinstance(result, str)


# ── Coordinates ───────────────────────────────────────────────────

class TestCoordinates:
    def test_twist_zero_for_solved(self):
        c = Cube()
        assert c.twist() == 0

    def test_flip_zero_for_solved(self):
        c = Cube()
        assert c.flip() == 0

    def test_corner_parity_zero_for_solved(self):
        c = Cube()
        assert c.corner_parity() == 0

    def test_edge_parity_zero_for_solved(self):
        c = Cube()
        assert c.edge_parity() == 0

    def test_FRtoBR_zero_for_solved(self):
        c = Cube()
        assert c.FRtoBR() == 0

    def test_twist_roundtrip(self):
        c = Cube()
        for val in [0, 100, 500, 1000, 2186]:
            c.twist(val)
            assert c.twist() == val

    def test_flip_roundtrip(self):
        c = Cube()
        for val in [0, 128, 512, 1024, 2047]:
            c.flip(val)
            assert c.flip() == val


# ── Randomize ─────────────────────────────────────────────────────

class TestRandomize:
    def test_randomize_produces_valid_cube(self):
        c = Cube.random()
        assert c.verify() is True

    def test_random_cubes_differ(self):
        states = set(Cube.random().as_string() for _ in range(5))
        assert len(states) > 1   # astronomically unlikely to collide


# ── Enums ─────────────────────────────────────────────────────────

class TestEnums:
    def test_center_values(self):
        assert Center.U == 0
        assert Center.B == 5

    def test_corner_values(self):
        assert Corner.URF == 0
        assert Corner.DRB == 7

    def test_edge_values(self):
        assert Edge.UR == 0
        assert Edge.BR == 11
