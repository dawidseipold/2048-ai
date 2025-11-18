from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

def load_weights(name: str) -> Dict[str, float]:
    """
    name: "balanced" | "conservative" | "aggressive" | ścieżka do pliku .json
    """
    if name.endswith(".json"):
        path = Path(name)
    else:
        path = Path(__file__).with_suffix("")  # heuristics/
        path = path.parent / "weights" / f"{name}.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    # upewnij się, że wszystkie klucze są obecne
    defaults = {"empty": 250.0, "mono": 1.0, "smooth": 0.1, "corner": 1000.0}
    defaults.update({k: float(v) for k, v in data.items()})
    return defaults