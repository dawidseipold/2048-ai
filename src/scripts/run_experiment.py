# scripts/run_experiment.py
from __future__ import annotations

import argparse
import csv
import json
import time
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Optional, Union

# Importujemy agentów i stan gry
from src.agents.greedy import GreedyAgent
# Tutaj zaimportujesz ExpectimaxAgent, gdy będzie zaimplementowany
# from src.agents.expectimax import ExpectimaxAgent
from src.game.state import GameState
from src.heuristics.weights_loader import load_weights
from src.utils.logger import GameLogger

if TYPE_CHECKING:
    from src.agents.base import Agent

# Typ do wyników gier (dodałem Union dla elastyczności)
GameResult = Dict[str, Union[int, float, str]]


def run_single_game(
    agent: Agent,
    initial_seed: int,
    game_logger: Optional[GameLogger] = None,
) -> GameResult:
    """Uruchamia jedną grę i zwraca jej wyniki."""
    state = GameState(seed=initial_seed)
    moves_count = 0
    game_start_time = time.monotonic()  # Czas startu całej gry
    move_decision_times: List[float] = []  # Lista do zbierania czasów podejmowania decyzji agenta

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
        move_start_time = time.perf_counter()  # Start pomiaru dla decyzji agenta
        move = agent.choose_move(state)
        move_end_time = time.perf_counter()  # Koniec pomiaru dla decyzji agenta
        move_duration = move_end_time - move_start_time
        move_decision_times.append(move_duration)  # Zapis czasu

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
                move_time_s=move_duration,  # Dodajemy czas ruchu do loga JSON
            )

    game_end_time = time.monotonic()  # Czas zakończenia całej gry
    game_duration = game_end_time - game_start_time

    # Obliczamy statystyki dla czasów podejmowania decyzji agenta w tej grze
    avg_move_time = sum(move_decision_times) / len(move_decision_times) if move_decision_times else 0.0
    
    # Sortujemy czasy, żeby znaleźć 95. percentyl
    sorted_move_times = sorted(move_decision_times)
    p95_index = min(len(sorted_move_times) - 1, int(0.95 * len(sorted_move_times)))
    p95_move_time = sorted_move_times[p95_index] if sorted_move_times else 0.0

    return {
        "seed": initial_seed,
        "final_score": state.score,
        "max_tile": state.max_tile(),
        "moves_count": moves_count,
        "game_duration_s": round(game_duration, 3),  # Całkowity czas trwania gry
        "end_state": "win" if state.max_tile() >= 2048 else "lose",
        "avg_move_decision_time_s": round(avg_move_time, 6),  # Nowe pole w CSV: średni czas decyzji
        "p95_move_decision_time_s": round(p95_move_time, 6),  # Nowe pole w CSV: 95 percentyl czasu decyzji
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
    # Dodatkowe argumenty dla Expectimax (jeśli potrzebne)
    # parser.add_argument("--max_depth", type=int, default=3, help="Max search depth for Expectimax.")
    # parser.add_argument("--time_limit_ms", type=int, default=60, help="Time limit per move for Expectimax (ms).")

    args = parser.parse_args()

    output_path = Path(args.output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Przygotowanie agenta (obecnie tylko Greedy, rozszerzysz o Expectimax)
    weights = load_weights(args.weights)
    agent_instance: Agent
    if args.agent_type == "greedy":
        agent_instance = GreedyAgent(weights=weights, fallback="up")
    elif args.agent_type == "expectimax":
        # Tutaj zaimportujesz i zainicjujesz ExpectimaxAgent
        # from src.agents.expectimax import ExpectimaxAgent
        # agent_instance = ExpectimaxAgent(
        #     weights=weights,
        #     max_depth=args.max_depth,
        #     time_limit_ms=args.time_limit_ms,
        #     greedy_fallback=GreedyAgent(weights=weights, fallback="up"),
        # )
        raise NotImplementedError("ExpectimaxAgent not yet implemented for experiments.")
    else:
        raise ValueError(f"Unknown agent type: {args.agent_type}")

    all_results: List[GameResult] = []  # Zaktualizuj typowanie listy
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
        # Zaktualizuj printowanie podsumowania, żeby pokazało czasy:
        print(
            f"Done. Score: {game_result['final_score']}, Max: {game_result['max_tile']}, "
            f"Avg Move Time: {game_result['avg_move_decision_time_s']:.6f} s, "
            f"P95 Move Time: {game_result['p95_move_decision_time_s']:.6f} s"
        )

    # Zapis zbiorczych wyników do CSV
    csv_filepath = output_path / f"{results_file_base}_summary.csv"
    if all_results:
        with open(csv_filepath, "w", newline="", encoding="utf-8") as f:
            # Upewnij się, że wszystkie nowe klucze są w fieldnames
            # Bierzemy klucze z pierwszego elementu, zakładając, że wszystkie są spójne
            fieldnames = list(all_results[0].keys())
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_results)
        print(f"\nSummary results saved to {csv_filepath}")

    # Opcjonalnie: proste statystyki podsumowujące w konsoli
    if all_results:
        scores = [r["final_score"] for r in all_results if isinstance(r["final_score"], int)]
        max_tiles = [r["max_tile"] for r in all_results if isinstance(r["max_tile"], int)]
        
        # Nowe statystyki dla czasów decyzji agenta
        all_avg_move_times = [r["avg_move_decision_time_s"] for r in all_results if isinstance(r["avg_move_decision_time_s"], float)]
        all_p95_move_times = [r["p95_move_decision_time_s"] for r in all_results if isinstance(r["p95_move_decision_time_s"], float)]

        print("\n--- Experiment Summary ---")
        print(f"Agent: {args.agent_type}, Weights: {args.weights}")
        print(f"Total Games: {args.num_games}")
        print(f"Average Score: {sum(scores) / len(scores):.2f}")
        print(f"Max Score: {max(scores)}")
        print(f"Min Score: {min(scores)}")
        
        max_tile_counts = {tile: max_tiles.count(tile) for tile in sorted(set(max_tiles))}
        print(f"Max Tile Distribution: {max_tile_counts}")
        
        if all_avg_move_times:
            # Uśredniamy średnie czasy ruchu z każdej gry, żeby dostać ogólny średni
            print(f"Overall Avg Move Decision Time: {sum(all_avg_move_times) / len(all_avg_move_times):.6f} s")
            # Podobnie dla 95 percentyla
            print(f"Overall P95 Move Decision Time: {sum(all_p95_move_times) / len(all_p95_move_times):.6f} s")


if __name__ == "__main__":
    main()