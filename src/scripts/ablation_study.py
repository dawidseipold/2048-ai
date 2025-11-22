from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Dict, List, Union

from src.agents.greedy import GreedyAgent
from src.heuristics.weights_loader import load_weights
from src.scripts.run_experiment import run_single_game, GameResult


def main() -> None:
    # Ustawienia badania
    num_games = 50
    base_weights_name = "balanced"
    output_dir = Path("results/ablation_greedy")
    output_dir.mkdir(parents=True, exist_ok=True)

    base_weights = load_weights(base_weights_name)
    features_to_ablate = list(base_weights.keys())  # ['empty', 'mono', 'smooth', 'corner']

    ablation_results: List[Dict[str, Union[str, float, int]]] = []

    print(f"Starting ablation study for {features_to_ablate} features.")

    # 1. Baseline (wszystkie cechy włączone)
    print(f"\n--- Baseline (all features enabled, from {base_weights_name}) ---")
    baseline_game_results: List[GameResult] = []
    for j in range(num_games):
        agent = GreedyAgent(weights=base_weights, fallback="up")
        game_result = run_single_game(agent, 4000 + j, game_logger=None)
        baseline_game_results.append(game_result)
        print(f"  Game {j + 1}/{num_games}... Score: {game_result['final_score']}")

    scores = [r["final_score"] for r in baseline_game_results if isinstance(r["final_score"], int)]
    num_2048_plus = sum(
        1 for tile in [r["max_tile"] for r in baseline_game_results if isinstance(r["max_tile"], int)] if tile >= 2048)
    ablation_entry = {
        "config_name": f"baseline_{base_weights_name}",
        "weights": json.dumps(base_weights),
        "avg_score": round(sum(scores) / len(scores), 2) if scores else 0,
        "2048_plus_percent": round((num_2048_plus / num_games) * 100, 2),
        "ablated_feature": "None"
    }
    ablation_results.append(ablation_entry)

    # 2. Ablacja każdej cechy po kolei
    for ablated_feature in features_to_ablate:
        current_weights = base_weights.copy()
        current_weights[ablated_feature] = 0.0  # Wyłączamy daną cechę

        print(f"\n--- Ablating '{ablated_feature}' (Weights: {current_weights}) ---")
        config_game_results: List[GameResult] = []
        for j in range(num_games):
            agent = GreedyAgent(weights=current_weights, fallback="up")
            game_result = run_single_game(agent, 5000 + j, game_logger=None)
            config_game_results.append(game_result)
            print(f"  Game {j + 1}/{num_games}... Score: {game_result['final_score']}")

        scores = [r["final_score"] for r in config_game_results if isinstance(r["final_score"], int)]
        num_2048_plus = sum(
            1 for tile in [r["max_tile"] for r in config_game_results if isinstance(r["max_tile"], int)] if
            tile >= 2048)
        ablation_entry = {
            "config_name": f"ablated_{ablated_feature}",
            "weights": json.dumps(current_weights),
            "avg_score": round(sum(scores) / len(scores), 2) if scores else 0,
            "2048_plus_percent": round((num_2048_plus / num_games) * 100, 2),
            "ablated_feature": ablated_feature
        }
        ablation_results.append(ablation_entry)

    # Zapis wszystkich wyników do jednego CSV
    ablation_summary_path = output_dir / f"ablation_summary_greedy_{base_weights_name}.csv"
    if ablation_results:
        with open(ablation_summary_path, "w", newline="", encoding="utf-8") as f:
            fieldnames = list(ablation_results[0].keys())
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(ablation_results)
        print(f"\nFinal ablation summary saved to {ablation_summary_path}")

    # Raportowanie w konsoli
    print("\n--- Ablation Study Results ---")
    for res in ablation_results:
        print(f"  {res['config_name']:<25} Avg Score: {res['avg_score']:<8.2f} 2048+%: {res['2048_plus_percent']}%")


if __name__ == "__main__":
    main()