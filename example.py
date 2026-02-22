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
