import itertools
import random
from collections import defaultdict
from dataclasses import dataclass
from time import perf_counter

from skeleton_tree import SkeletonTree


@dataclass(frozen=True)
class Point:
    x: int
    y: int

    def __le__(self, other):
        return self.x <= other.x

    def __lt__(self, other):
        return self.x < other.x


class SquareGrid:
    def __init__(self, grid):
        self.grid = grid
        self.side_length = len(grid)

    def diagonals(self):
        for top_offset in range(self.side_length):
            yield self.yield_diagonal_from_x_and_y(self.side_length - top_offset - 1, 0)
        for side_offset in range(1, self.side_length):
            yield self.yield_diagonal_from_x_and_y(0, -side_offset)

    def yield_diagonal_from_x_and_y(self, x, y):
        while x < self.side_length and abs(y) < self.side_length:
            yield Point(x=x, y=y)
            x += 1
            y -= 1

    def __getitem__(self, pt):
        return self.grid[-pt.y][pt.x]


def test_indexing():
    grid = SquareGrid([
        [1, 0, 2],
        [2, 3, 4],
        [5, 6, 7]
    ])
    diagonals = [
        [grid[pt] for pt in diagonal]
        for diagonal in grid.diagonals()
    ]
    assert diagonals == [
        [2],
        [0, 4],
        [1, 3, 7],
        [2, 6],
        [5]
    ]


@dataclass
class RawPixelRun:
    up: int
    down: int
    left: int
    right: int


@dataclass
class Ells:
    down_right: int
    up_left: int


def compute_runs(grid):
    runs = SquareGrid([
        [RawPixelRun(up=0, down=0, left=0, right=0) for x in range(grid.side_length)]
        for y in range(grid.side_length)
    ])
    for i in range(grid.side_length):
        for j in range(grid.side_length):
            top_point = Point(x=i, y=-j)
            if grid[top_point]:
                value_from_top = j if j == 0 else runs[Point(x=i, y=1 - j)].up
                runs[top_point].up = value_from_top + 1
            bottom_point = Point(x=i, y=j - grid.side_length + 1)

            if grid[bottom_point]:
                value_from_bottom = 0 if j == 0 else runs[Point(x=i, y=j - grid.side_length)].down
                runs[bottom_point].down = value_from_bottom + 1

            left_point = Point(x=j, y=-i)
            if grid[left_point]:
                value_from_left = j if j == 0 else runs[Point(x=j - 1, y=-i)].left
                runs[left_point].left = value_from_left + 1

            right_point = Point(x=grid.side_length - 1 - j, y=-i)
            if grid[right_point]:
                value_from_right = 0 if j == 0 else runs[Point(x=grid.side_length - j, y=-i)].right
                runs[right_point].right = value_from_right + 1
    return runs


def compute_ells(grid):
    runs = compute_runs(grid)

    result = SquareGrid([
        [Ells(down_right=0, up_left=0) for _ in range(grid.side_length)]
        for _ in range(grid.side_length)
    ])
    for x in range(grid.side_length):
        for y in range(grid.side_length):
            p = Point(x=x, y=-y)
            result[p].down_right = min(runs[p].down, runs[p].right)
            result[p].up_left = min(runs[p].up, runs[p].left)
    return result


def find_largest_square_v1(grid):
    runs = compute_runs(grid)
    for size in range(grid.side_length, 0, -1):
        max_candidate = grid.side_length - size + 1
        for x, y in itertools.product(range(max_candidate), range(max_candidate)):
            # print(x, y)
            p = runs[Point(x=x, y=-y)]
            bottom_left = runs[Point(x=x, y=-(y + size - 1))]
            top_right = runs[Point(x=x + size - 1, y=-y)]
            if all(run >= size for run in [p.right, p.down, bottom_left.right, top_right.down]):
                return size
    return 0


def find_largest_square_v2(grid):
    return max(yield_squares(grid))


def yield_squares(grid):
    ells = compute_ells(grid)
    for diagonal in grid.diagonals():
        diagonal = list(diagonal)

        critical_points = defaultdict(list)
        for q in diagonal:
            if leg_length := ells[q].up_left:
                critical_points[Point(x=q.x - leg_length + 1, y=q.y + leg_length - 1)].append(q)

        q_candidates = SkeletonTree.from_sorted_list(diagonal)
        for p in diagonal:
            for q in critical_points[p]:
                q_candidates.insert(q)
            farthest_reachable_x = Point(x=p.x + ells[p].down_right - 1, y=p.y - ells[p].down_right + 1)
            if (best_q := q_candidates.find_value_or_predecessor(farthest_reachable_x)) is not None:
                yield best_q.x - p.x + 1


def test_runs():
    grid = SquareGrid([
        [True, True, False, False],
        [True, False, True, True],
        [True, True, True, True],
        [False, False, True, False]
    ])
    runs = compute_ells(grid)
    for row in runs.grid:
        print(row)

def test_original_alg():
    grid = SquareGrid([
        [True, True, False, False],
        [True, False, True, True],
        [True, True, True, True],
        [False, False, True, True]
    ])
    assert find_largest_square_v1(grid) == 2
    assert find_largest_square_v2(grid) == 2

    grid = SquareGrid([
        [True, True, False, False],
        [True, True, True, True],
        [True, True, True, True],
        [False, True, True, True]
    ])
    assert find_largest_square_v1(grid) == 3
    assert find_largest_square_v2(grid) == 3


def test_random_grid(size, p):
    grid = SquareGrid([
        [random.random() <= p for _ in range(size)]
        for _ in range(size)
    ])
    start = perf_counter()
    ans1 = find_largest_square_v1(grid)
    print(f'Original algorithm ran on size {size} with density {p} in {perf_counter() - start:.3f} s. Solution: {ans1}')
    start = perf_counter()
    ans2 = find_largest_square_v2(grid)
    print(f'Modified algorithm ran on size {size} with density {p} in {perf_counter() - start:.3f} s. Solution: {ans2}')
    assert ans1 == ans2, f'{ans1} != {ans2}'


def random_tests():
    for size in [10, 50, 100, 200, 400, 800, 1000]:
        for p in [0.1, 0.3, 0.5, 0.8, 0.95]:
            for _ in range(1):
                test_random_grid(size, p)


if __name__ == '__main__':
    random_tests()

