from pathlib import Path
import joblib
import pandas as pd


class MLScorer:
    def __init__(self, model_path: str = "ml/models/logistic_v1.pkl"):
        self.model_path = Path(model_path)
        self.model = None
        self.is_available = False

        if not self.model_path.exists():
            return

        try:
            self.model = joblib.load(self.model_path)
            self.is_available = True
        except Exception as e:
            print(f"[MLScorer] Failed to load model from {self.model_path}: {e}")
            self.model = None
            self.is_available = False

    def available(self) -> bool:
        return self.is_available and self.model is not None

    def score(self, features: dict) -> float:
        if not self.available():
            return 0.0

        try:
            X = pd.DataFrame([features])

            if hasattr(self.model, "predict_proba"):
                prob = self.model.predict_proba(X)[0][1]
                return float(prob)

            if hasattr(self.model, "predict"):
                pred = self.model.predict(X)[0]
                return float(pred)

            return 0.0

        except Exception as e:
            print(f"[MLScorer] Prediction failed: {e}")
            return 0.0