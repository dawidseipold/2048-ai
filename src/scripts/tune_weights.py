from __future__ import annotations

import csv
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import argparse
import json
import random
from pathlib import Path
from typing import Dict, List, Optional, Union

from src.agents.greedy import GreedyAgent
from src.game.state import GameState
from src.heuristics.evaluate import evaluate
from src.heuristics.weights_loader import load_weights
from src.scripts.run_experiment import run_single_game, GameResult


def generate_random_weights(
        base_weights: Dict[str, float],
        variance_percent: float,
) -> Dict[str, float]:
    """Generuje losowe wagi na podstawie bazowych wag i procentu zmienności."""
    new_weights = {}
    for key, value in base_weights.items():
        min_val = value * (1 - variance_percent / 100)
        max_val = value * (1 + variance_percent / 100)
        new_weights[key] = round(random.uniform(min_val, max_val), 3)
    return new_weights


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Tune heuristic weights for a specified agent."
    )
    parser.add_argument("--num_configs", type=int, default=30, help="Number of weight configurations to test.")
    parser.add_argument("--games_per_config", type=int, default=20,
                        help="Number of games to run for each configuration.")
    parser.add_argument(
        "--agent_type",
        type=str,
        default="greedy",
        choices=["greedy", "expectimax"],
        help="Type of agent to use for tuning.",
    )
    parser.add_argument(
        "--base_weights",
        type=str,
        default="balanced",
        help='Base weights preset name (e.g., "balanced") or path to JSON.',
    )
    parser.add_argument(
        "--variance_percent",
        type=float,
        default=20.0,
        help="Percentage variance for random weight generation (e.g., 20.0 for +/-20%).",
    )
    parser.add_argument(
        "--start_seed", type=int, default=3000, help="Starting seed for games."
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="results/tuning",
        help="Directory to save tuning results.",
    )
    args = parser.parse_args()

    output_path = Path(args.output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    base_weights_dict = load_weights(args.base_weights)

    all_tuning_results: List[Dict[str, Union[str, float, int]]] = []

    print(f"Starting weight tuning with {args.num_configs} configurations, {args.games_per_config} games per config.")
    print(f"Base weights from: {args.base_weights}, Variance: +/-{args.variance_percent}%.")

    for i in range(args.num_configs):
        # Generuj losowe wagi
        current_weights = generate_random_weights(base_weights_dict, args.variance_percent)
        config_name = f"config_{i + 1:03d}"

        # Zapisz konfigurację wag do pliku (dla referencji)
        config_weights_path = output_path / f"{config_name}_weights.json"
        with open(config_weights_path, "w", encoding="utf-8") as f:
            json.dump(current_weights, f, indent=2)

        print(f"\n--- Running {config_name} (Weights: {current_weights}) ---")
        config_game_results: List[GameResult] = []

        for j in range(args.games_per_config):
            current_seed = args.start_seed + (i * args.games_per_config) + j
            # Tymczasowo tworzymy agenta dla każdej gry, by łatwiej zmieniać wagi
            # (W praktyce można tworzyć raz na konfigurację)
            if args.agent_type == "greedy":
                agent_instance = GreedyAgent(weights=current_weights, fallback="up")
            # elif args.agent_type == "expectimax":
            #    # W tym miejscu dodasz ExpectimaxAgent, gdy będzie gotowy
            #    # from src.agents.expectimax import ExpectimaxAgent
            #    agent_instance = ExpectimaxAgent(weights=current_weights, ...)
            else:
                raise NotImplementedError(f"Agent type {args.agent_type} not yet supported for tuning.")

            game_result = run_single_game(agent_instance, current_seed, game_logger=None)  # Logger pełnej gry wyłączony
            config_game_results.append(game_result)
            print(
                f"  Game {j + 1}/{args.games_per_config} (seed: {current_seed})... Score: {game_result['final_score']}, Max: {game_result['max_tile']}")

        # Agregacja wyników dla danej konfiguracji
        scores = [r["final_score"] for r in config_game_results if isinstance(r["final_score"], int)]
        max_tiles = [r["max_tile"] for r in config_game_results if isinstance(r["max_tile"], int)]

        avg_score = sum(scores) / len(scores) if scores else 0
        avg_max_tile = sum(max_tiles) / len(max_tiles) if max_tiles else 0

        # Zliczanie osiągniętych kafelków 2048 (i wyższych)
        num_2048_plus = sum(1 for tile in max_tiles if tile >= 2048)

        tuning_entry = {
            "config_name": config_name,
            "weights": json.dumps(current_weights),  # Zapis wag jako string JSON
            "avg_score": round(avg_score, 2),
            "max_score_overall": max(scores) if scores else 0,
            "min_score_overall": min(scores) if scores else 0,
            "avg_max_tile": round(avg_max_tile, 2),
            "2048_plus_count": num_2048_plus,
            "2048_plus_percent": round((num_2048_plus / args.games_per_config) * 100, 2)
        }
        all_tuning_results.append(tuning_entry)

    # Zapis wszystkich wyników tuningu do jednego CSV
    tuning_summary_path = output_path / f"tuning_summary_{args.agent_type}_{args.base_weights}.csv"
    if all_tuning_results:
        with open(tuning_summary_path, "w", newline="", encoding="utf-8") as f:
            fieldnames = list(all_tuning_results[0].keys())
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_tuning_results)
        print(f"\nFinal tuning summary saved to {tuning_summary_path}")

        # Raport top 3 konfiguracji w konsoli
        print("\n--- Top 3 Configurations (by Avg Score) ---")
        top_configs = sorted(all_tuning_results, key=lambda x: x["avg_score"], reverse=True)[:3]
        for config in top_configs:
            print(f"  Config: {config['config_name']}")
            print(f"    Weights: {config['weights']}")
            print(
                f"    Avg Score: {config['avg_score']}, Max Tile Avg: {config['avg_max_tile']}, 2048+ %: {config['2048_plus_percent']}%")
            print("-" * 20)


if __name__ == "__main__":
    main()