from __future__ import annotations

import argparse
import csv
import json
import time
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Literal, Optional, Tuple

from src.agents.greedy import GreedyAgent  # Później: ExpectimaxAgent
from src.agents.expectimax import ExpectimaxAgent
from src.game.state import GameState
from src.heuristics.weights_loader import load_weights  # Ładowanie wag
from src.utils.logger import GameLogger  # Logger dla pojedynczej gry

if TYPE_CHECKING:
    # Tylko dla podpowiedzi typów, nie dla importu w runtime
    from src.agents.base import Agent


def run_single_game(
    agent: Agent,
    initial_seed: int,
    game_logger: Optional[GameLogger] = None,
) -> Dict[str, int | float]:
    """Uruchamia jedną grę i zwraca jej wyniki."""
    state = GameState(seed=initial_seed)
    moves_count = 0
    start_time = time.monotonic()

    if game_logger:
        game_logger.log_step(
            move="INITIAL",
            reward=0,
            score=state.score,
            max_tile=state.max_tile(),
            empty_cells=len(state.empty_cells()),
            board=state.board,
        )

    while not state.is_terminal():
        move = agent.choose_move(state)
        res = state.step(move, spawn=True)
        moves_count += 1

        if game_logger:
            game_logger.log_step(
                move=move,
                reward=res.reward,
                score=state.score,
                max_tile=state.max_tile(),
                empty_cells=len(state.empty_cells()),
                board=state.board,
            )

    end_time = time.monotonic()
    duration = end_time - start_time

    return {
        "seed": initial_seed,
        "final_score": state.score,
        "max_tile": state.max_tile(),
        "moves_count": moves_count,
        "duration_s": round(duration, 3),
        "end_state": "win" if state.max_tile() >= 2048 else "lose",
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run N 2048 games with a specified agent and save results."
    )
    parser.add_argument("--num_games", type=int, default=10, help="Number of games to run.")
    parser.add_argument(
        "--agent_type",
        type=str,
        default="greedy",
        choices=["greedy", "expectimax"],  # Rozszerzysz później
        help="Type of agent to use.",
    )
    parser.add_argument(
        "--weights",
        type=str,
        default="balanced",
        help='Weights preset name or path to JSON (e.g., "balanced").',
    )
    parser.add_argument(
        "--start_seed", type=int, default=1000, help="Starting seed for games."
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="results",
        help="Directory to save results (CSV/JSON).",
    )
    parser.add_argument(
        "--log_full_games",
        action="store_true",
        help="If set, saves full step-by-step logs for each game.",
    )
    parser.add_argument(
        "--max_depth",
        type=int,
        default=3
    )
    parser.add_argument(
        "--time_limit_ms",
        type=int,
        default=60
    )

    args = parser.parse_args()

    output_path = Path(args.output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    weights = load_weights(args.weights)
    agent_instance: Agent

    if args.agent_type == "greedy":
        agent_instance = GreedyAgent(weights=weights, fallback="up")
    elif args.agent_type == "expectimax":
        agent_instance = ExpectimaxAgent(
            weights = weights,
            max_depth = args.max_depth,
            time_limit_ms = args.time_limit_ms,
            greedy_fallback = GreedyAgent(weights = weights, fallback = "up")
        )
    else:
        raise ValueError(f"Unknown agent type: {args.agent_type}")

    all_results: List[Dict[str, int | float]] = []
    run_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file_base = f"{args.agent_type}_{args.weights}_{args.num_games}_games_{run_timestamp}"

    print(f"Running {args.num_games} games with {args.agent_type} agent...")
    for i in range(args.num_games):
        current_seed = args.start_seed + i
        print(f"  Game {i+1}/{args.num_games} (seed: {current_seed})... ", end="", flush=True)

        game_logger: Optional[GameLogger] = None
        if args.log_full_games:
            full_log_file = output_path / f"{results_file_base}_game_{current_seed}.json"
            game_logger = GameLogger(log_filepath=full_log_file, agent_info=args.agent_type)

        game_result = run_single_game(agent_instance, current_seed, game_logger)
        all_results.append(game_result)
        print(
            f"Done. Score: {game_result['final_score']}, Max: {game_result['max_tile']}"
        )

    # Zapis zbiorczych wyników do CSV
    csv_filepath = output_path / f"{results_file_base}_summary.csv"
    if all_results:
        with open(csv_filepath, "w", newline="", encoding="utf-8") as f:
            fieldnames = list(all_results[0].keys())
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_results)
        print(f"\nSummary results saved to {csv_filepath}")

    if all_results:
        scores = [r["final_score"] for r in all_results if isinstance(r["final_score"], int)]
        max_tiles = [r["max_tile"] for r in all_results if isinstance(r["max_tile"], int)]
        print("\n--- Experiment Summary ---")
        print(f"Agent: {args.agent_type}, Weights: {args.weights}")
        print(f"Total Games: {args.num_games}")
        print(f"Average Score: {sum(scores) / len(scores):.2f}")
        print(f"Max Score: {max(scores)}")
        print(f"Min Score: {min(scores)}")
        print(f"Average Max Tile: {sum(max_tiles) / len(max_tiles):.2f}")
        max_tile_counts = {tile: max_tiles.count(tile) for tile in sorted(set(max_tiles))}
        print(f"Max Tile Distribution: {max_tile_counts}")


if __name__ == "__main__":
    main()