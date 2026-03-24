# Responsible for decision_logging scheduling decisions for future ML training

import json
import time
from pathlib import Path


class DecisionLogger:
    def __init__(self, log_path="data/decision_logs.jsonl"):
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def log_decision(self, user_id, task_id, features):
        record = {
            "timestamp": time.time(),
            "user_id": user_id,
            "task_id": task_id,
            "features": features,
            "label": None
        }

        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")


    def update_label(self, user_id, task_id, label):
        updated_lines = []

        with open(self.log_path, "r", encoding="utf-8") as f:
            for line in f:
                record = json.loads(line)
                if (
                    record["user_id"] == user_id
                    and record["task_id"] == task_id
                    and record["label"] is None
                ):
                    record["label"] = label
                updated_lines.append(json.dumps(record))

        with open(self.log_path, "w", encoding="utf-8") as f:
            f.write("\n".join(updated_lines) + "\n")

