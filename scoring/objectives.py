from dataclasses import dataclass
from typing import Dict


@dataclass
class ObjectiveScore:
    productivity: float
    balance: float
    wellbeing: float
    preferences: float

    def weighted_sum(self, weights: Dict[str, float]) -> float:
        return (
            self.productivity * weights["productivity"] +
            self.balance * weights["balance"] +
            self.wellbeing * weights["wellbeing"] +
            self.preferences * weights["preferences"]
        )


AUTONOMY_WEIGHTS = {
    "gentle": {
        "productivity": 0.3,
        "balance": 0.3,
        "wellbeing": 0.3,
        "preferences": 0.1
    },
    "balanced": {
        "productivity": 0.4,
        "balance": 0.3,
        "wellbeing": 0.2,
        "preferences": 0.1
    },
    "aggressive": {
        "productivity": 0.7,
        "balance": 0.15,
        "wellbeing": 0.1,
        "preferences": 0.05
    }
}
