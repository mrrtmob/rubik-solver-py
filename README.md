
# rubik-solver-py

A pure-Python implementation of **Kociemba's two-phase algorithm** for solving the Rubik's Cube optimally (≤22 moves). Port of the TypeScript [rubik-solver](https://www.npmjs.com/package/rubik-solver) library.

## Installation

```bash
pip install rubik-solver-py
```

## Quick Start

```python
from rubik_solver import Cube, init_solver, solve, scramble

# init_solver() pre-computes move and pruning tables (~30-60 s, one-time cost).
# Call it once at application startup before solving anything.
init_solver()

# Solve from a move sequence
cube = Cube().move("R U R' U' R' F R2 U' R' U' R U R' F'")
solution = solve(cube)
print(solution)  # e.g. "F R U R' U' F'"

# Generate a random scramble
print(scramble())
```

## API Reference

### `init_solver()`

Pre-computes all move and pruning tables required by the solver.

**Must be called once** before `solve()` or `scramble()`.

Safe to call multiple times — subsequent calls are no-ops.

---

### `solve(cube, max_depth=22) → str | None`

Solves the given `Cube` instance using Kociemba's two-phase algorithm.

| Parameter     | Type | Default | Description                                     |
| ------------- | ---- | ------- | ----------------------------------------------- |
| `cube`      | Cube | —      | The cube to solve                               |
| `max_depth` | int  | `22`  | Maximum move count; returns `None`if exceeded |

Returns a move string like `"R U R' U'"`, or `None` if no solution was found.

---

### `scramble() → str`

Returns a random scramble sequence as a move string.

---

### `Cube`

The main cube class.

| Method / Property       | Description                                            |
| ----------------------- | ------------------------------------------------------ |
| `Cube()`              | Creates a solved cube                                  |
| `.move(alg)`          | Applies an algorithm string in place; returns `self` |
| `.clone()`            | Returns a deep copy                                    |
| `.is_solved()`        | Returns `True`if the cube is solved                  |
| `.as_string()`        | Returns the 54-char facelet string                     |
| `.randomize()`        | Randomizes the cube in place; returns `self`         |
| `.verify()`           | Returns `True`if valid, or an error string           |
| `Cube.from_string(s)` | Parses a 54-char facelet string into a `Cube`        |
| `Cube.random()`       | Returns a new randomized `Cube`                      |
| `Cube.inverse(alg)`   | Inverts an algorithm string                            |

#### Supported Move Notation

Faces: `U R F D L B`

Slice moves: `E M S`

Rotations: `x y z`

Wide moves: `u r f d l b`

Modifiers: `'` (inverse), `2` (double)

---

## Usage Examples

### Build and verify a cube manually

```python
from rubik_solver import Cube

# Solved cube
cube = Cube()
print(cube.is_solved())    # True

# Apply moves
cube.move("R U R' U'")
print(cube.is_solved())    # False

# Serialize to 54-char facelet string
print(cube.as_string())
# "UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB"

# Parse from a facelet string
cube2 = Cube.from_string("UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB")

# Invert an algorithm
print(Cube.inverse("R U R' U'"))  # "U R U' R'"
```

### Solve a random cube

```python
from rubik_solver import Cube, init_solver, solve

init_solver()
cube = Cube.random()
solution = solve(cube)
print(f"Solution ({len(solution.split())} moves): {solution}")
```

### Validate a cube from facelet string

```python
from rubik_solver import Cube

cube = Cube.from_string("UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB")
result = cube.verify()
if result is True:
    print("Cube is valid!")
else:
    print(f"Invalid: {result}")
```

---

## Architecture

```
rubik_solver/
├── __init__.py        ← Public API exports
├── types.py           ← Enums (Center, Corner, Edge) and CubeState dataclass
├── constants.py       ← Table sizes, facelet mappings, base move data
├── math_utils.py      ← cnk, factorial, rotate_left, rotate_right
├── cube.py            ← Cube class (core logic, coordinates, serialization)
├── tables/
│   └── tables.py      ← Move table and pruning table generation
└── solver/
    ├── search_state.py ← SearchState used in phase 1 & 2 search
    └── solver.py       ← init_solver(), solve(), scramble(), two-phase search
```

## Performance

| Scenario                             | Time                                           |
| ------------------------------------ | ---------------------------------------------- |
| `init_solver()`— first ever call  | ~8 s (builds NumPy tables, writes cache)       |
| `init_solver()`— subsequent calls | ~15 ms (loads from `~/.cache/rubik_solver/`) |
| `solve()`per cube                  | ~0.1 – 1 s                                    |
| `scramble()`                       | ~0.5 – 2 s                                    |

Tables are cached automatically as `.npy` files. You can override the cache directory:

```bash
export RUBIK_SOLVER_CACHE_DIR=/path/to/your/cache
```

To force a rebuild:

```python
from rubik_solver import clear_cache, init_solver
clear_cache()
init_solver(verbose=True)  # prints progress
```

> **Why not 10 ms like JavaScript?**
>
> V8 JIT-compiles the table construction loops. Python uses NumPy for vectorised
> BFS (fast) but the coordinate-computation inner loop still runs in CPython.
> The disk cache makes the difference negligible in practice — after the first run
> startup is ~15 ms regardless.

## License

MIT
