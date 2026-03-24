# ml/train_logistic_model.py
import joblib


from pathlib import Path
import json
import pandas as pd

from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

# ---------------------------
# Load data
# ---------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "decision_logs.jsonl"

records = []

with open(DATA_PATH, "r") as f:
    for line in f:
        r = json.loads(line)
        if r["label"] is not None:
            row = r["features"].copy()
            row["label"] = r["label"]
            records.append(row)

df = pd.DataFrame(records)

# ---------------------------
# Prepare X, y
# ---------------------------
X = df.drop("label", axis=1)
y = df["label"]

numeric_features = ["hour", "day_of_week", "task_duration"]
categorical_features = ["task_category"]

preprocessor = ColumnTransformer(
    transformers=[
        ("num", "passthrough", numeric_features),
        ("cat", OneHotEncoder(), categorical_features)
    ]
)

# ---------------------------
# Train model
# ---------------------------
model = Pipeline(
    steps=[
        ("preprocess", preprocessor),
        ("classifier", LogisticRegression())
    ]
)

model.fit(X, y)

joblib.dump(model, "ml/models/logistic_model.pkl")
print("Model trained successfully")
