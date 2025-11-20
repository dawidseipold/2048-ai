import timeit
import random

from src.heuristics.evaluate import evaluate

# utwórz losową tablicę 4x4 z wartościami 0–1024
def random_board():
    vals = [0, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024]
    return [[random.choice(vals) for _ in range(4)] for _ in range(4)]

def main():
    setup = "from __main__ import random_board, evaluate"
    boards = [random_board() for _ in range(1000)]

    def run():
        for b in boards:
            evaluate(b)

    t = timeit.timeit(run, number=1)
    print(f"1000 evaluations took: {t:.4f} s | {t/1000:.6f} s per state")

if __name__ == "__main__":
    main()