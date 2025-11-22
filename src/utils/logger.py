# src/utils/logger.py
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

class GameLogger:
    def __init__(self, log_filepath: Path, agent_info: str = "unknown_agent"):
        self.log_filepath = log_filepath
        self.log_data: Dict[str, Any] = {
            "metadata": {
                "start_time": datetime.now().isoformat(),
                "agent": agent_info,
                "log_version": "1.0",
            },
            "steps": [],
        }

    def log_step(
        self,
        move: str,
        reward: int,
        score: int,
        max_tile: int,
        empty_cells: int,
        board: List[List[int]],
        move_time_s: Optional[float] = None, # NOWE: opcjonalny czas ruchu
    ) -> None:
        """Loguje stan gry po każdym ruchu."""
        step_entry = {
            "timestamp": datetime.now().isoformat(),
            "move": move,
            "reward": reward,
            "score": score,
            "max_tile": max_tile,
            "empty_cells": empty_cells,
            "board": board,
        }
        if move_time_s is not None: # Dodajemy tylko jeśli podano
            step_entry["move_time_s"] = move_time_s
        self.log_data["steps"].append(step_entry)

    def __del__(self):
        """Zapisuje log do pliku, gdy obiekt jest usuwany."""
        self.save_log()

    def save_log(self) -> None:
        """Wymusza zapis logu do pliku."""
        self.log_filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(self.log_filepath, "w", encoding="utf-8") as f:
            json.dump(self.log_data, f, indent=2)