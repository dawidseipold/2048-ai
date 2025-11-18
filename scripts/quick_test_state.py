# scripts/quick_test_state.py
from game.state import GameState

def main():
    s = GameState(seed=42)
    print("Start:")
    print(s)
    for mv in ["left", "up", "left", "down", "right"]:
        res = s.step(mv, spawn=True)
        print(f"\nMove {mv} -> reward={res.reward}, done={res.done}")
        print(s)
    print("Legal moves:", s.legal_moves())
    print("Terminal:", s.is_terminal(), "Max tile:", s.max_tile())

if __name__ == "__main__":
    main()