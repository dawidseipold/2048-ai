from __future__ import annotations

import argparse
import os
import sys
import time
import keyboard

from pathlib import Path
from typing import List, Literal, Optional

from src.agents.base import Agent
from src.agents.expectimax import ExpectimaxAgent
from src.agents.greedy import GreedyAgent
from src.game.state import GameState
from src.heuristics.weights_loader import load_weights

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def render_board(board: List[List[int]], score: int, max_tile: int, done: bool, moves_count: int) -> None:
    clear_console()

    print("--- 2048 AI Game ---")
    print(f"Moves: {moves_count:<4d} | Score: {score:<6d} | Max Tile: {max_tile:<4d}")
    print("--------------------")

    for row in board:
        print(" ".join(f"{val:4d}" if val != 0 else "." for val in row))

    print("--------------------")

    if done:
        print("GAME OVER!")

    print("\n")


def run_one(seed: int | None, delay_s: float | None, weights_name: str | None) -> None:
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

def run_one_interactive(
        agent_type: str,
        weights_name: str | None,
        seed: int | None,
        interactive_mode: Literal['live', 'step'],
        delay_s: float,
) -> None:
    import os, sys
    import time

    # proste getch cross‑platform
    if os.name == "nt":
        import msvcrt
        def getch():
            return msvcrt.getch().decode("utf-8").lower()
    else:
        import tty, termios
        def getch():
            fd = sys.stdin.fileno()
            old = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                ch = sys.stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old)
            return ch.lower()

    weights = load_weights(weights_name) if weights_name else None
    if agent_type == "greedy":
        agent_instance = GreedyAgent(weights=weights, fallback="up")
    elif agent_type == "expectimax":
        agent_instance = ExpectimaxAgent(
            weights=weights,
            max_depth=3,
            time_limit_ms=50,
            greedy_fallback=GreedyAgent(weights=weights, fallback="up"),
            cache_maxsize=100000,
        )
    else:
        raise ValueError(f"Unknown agent type: {agent_type}")

    state = GameState(seed=seed)
    moves_count = 0
    exit_flag = False

    try:
        while not state.is_terminal() and not exit_flag:
            render_board(state.board, state.score, state.max_tile(), state.done, moves_count)
            print("Press Enter for next step, press 'q' to quit.")

            if interactive_mode == "step":
                ch = getch()
                if ch == "\r" or ch == "\n":  # Enter
                    pass
                elif ch == "q":
                    exit_flag = True
                    print("\nExiting...")
                    break

            move = agent_instance.choose_move(state)
            res = state.step(move, spawn=True)
            moves_count += 1
            time.sleep(delay_s)

        if exit_flag:
            print("Simulation aborted by user")
        else:
            render_board(state.board, state.score, state.max_tile(), state.done, moves_count)
            print("Final score:", state.score)
            print("Max tile:", state.max_tile())
            print("Total Moves:", moves_count)

    except KeyboardInterrupt:
        print("\nExiting...")




def main() -> None:
    parser = argparse.ArgumentParser(description = "Run one 2048 game with Greedy Agent")
    parser.add_argument("--seed", type = int, default = None, help = "RNG seed for reproducibility")
    parser.add_argument("--delay", type = float, default = None, help = "Delay in seconds between moves")
    parser.add_argument(
        "--agent_type",
        type=str,
        default="greedy",
        choices=["greedy", "expectimax"],
        help="Type of agent to use.",
    )
    parser.add_argument(
        "--weights",
        type = str,
        default = "balanced",
        help = "Weights preset name or path to JSON"
    )
    parser.add_argument(
        "--mode",
        type=str,
        default="live",
        choices=["live", "step"],
        help="Interactive mode: 'live' for continuous play, 'step' for step-by-step.",
    )

    args = parser.parse_args()
    # run_one(seed = args.seed, delay_s = args.delay, weights_name = args.weights)

    run_one_interactive(
        agent_type=args.agent_type,
        weights_name=args.weights,
        seed=args.seed,
        delay_s=args.delay,
        interactive_mode=args.mode
    )

if __name__ == "__main__":
    main()