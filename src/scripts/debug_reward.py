import copy
from src.game.state import GameState

def manual_board():
    # ustaw sytuację: dwa sąsiadujące 2 po lewej, ruch LEFT powinien dać merge=4
    return [
        [2, 2, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ]

def main():
    s = GameState(seed=1, board=manual_board(), score=0)
    print("Before:", s.board, "sum=", sum(map(sum, s.board)))
    res = s.step("left", spawn=False)
    print("After :", s.board, "sum=", sum(map(sum, s.board)))
    print("Moved:", res.done, "Reward:", res.reward, "Score:", s.score)

if __name__ == "__main__":
    main()