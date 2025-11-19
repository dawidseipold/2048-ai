from __future__ import annotations

import argparse
import time

from src.agents.greedy import GreedyAgent
from src.game.state import GameState
from src.heuristics.weights_loader import load_weights

print("RUN_ONE MODULE LOADED")

def run_one(seed: int | None, delay_s: float | None, weights_name: str | None) -> None:

    print("RUN_ONE MAIN START")
    state = GameState(seed = seed)

    if weights_name:
        weights = load_weights(weights_name)
    else:
        weights = None

    agent = GreedyAgent(weights = weights, fallback = "up")
    moves_count = 0

    while not state.is_terminal():
        move = agent.choose_move(state)
        res = state.step(move, spawn = True)
        moves_count += 1

        print(f"Move {moves_count:4d}: {move:>5s} | reward = {res.reward:4d} | score = {state.score} | max = {state.max_tile()}")

        if delay_s:
            time.sleep(delay_s)

    print("\n=== GAME OVER ===")
    print(f"Final score: {state.score}")
    print(f"Max tile:    {state.max_tile()}")
    print(f"Moves:       {moves_count}")

def main() -> None:
    parser = argparse.ArgumentParser(description = "Run one 2048 game with Greedy Agent")
    parser.add_argument("--seed", type = int, default = None, help = "RNG seed for reproducibility")
    parser.add_argument("--delay", type = float, default = None, help = "Delay in seconds between moves")
    parser.add_argument(
        "--weights",
        type = str,
        default = "balanced",
        help = "Weights preset name or path to JSON"
    )

    args = parser.parse_args()
    run_one(seed = args.seed, delay_s = args.delay, weights_name = args.weights)

    print("RUN_ONE MAIN END")

if __name__ == "__main__":
    main()