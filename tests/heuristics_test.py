from src.heuristics.evaluate import evaluate
from src.heuristics.weights_loader import load_weights

def print_eval(board, name):
    w = load_weights("balanced")
    val = evaluate(board, w)
    print(f"{name:<20} -> score: {val:10.2f}")

def main():
    # Prosty test sanity: im lepiej wygląda plansza, tym większy wynik.
    boards = {
        "empty start": [
            [2, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 2],
        ],
        "ordered snake": [
            [1024, 512, 256, 128],
            [0, 0, 0, 64],
            [0, 0, 0, 32],
            [0, 0, 0, 16],
        ],
        "messy midgame": [
            [2, 16, 4, 8],
            [64, 32, 16, 8],
            [2, 4, 0, 2],
            [0, 0, 0, 0],
        ],
        "full board lose": [
            [2, 4, 8, 16],
            [32, 64, 128, 256],
            [512, 1024, 512, 256],
            [128, 64, 32, 16],
        ],
    }

    for name, b in boards.items():
        print_eval(b, name)

if __name__ == "__main__":
    main()