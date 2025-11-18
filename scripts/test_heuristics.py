from heuristics.evaluate import evaluate
from heuristics.weights_loader import load_weights

def main():
    w = load_weights("conservative")
    board = [
        [2, 4, 8, 16],
        [0, 0, 0, 32],
        [0, 0, 0, 64],
        [0, 0, 0, 128],
    ]
    print("score:", evaluate(board, w))

if __name__ == "__main__":
    main()