import json
import os

import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline


def load_labeled_df(path="data/decision_logs.jsonl") -> pd.DataFrame:
    rows = []

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)

            if r.get("label") is None:
                continue

            feat = dict(r["features"])
            feat["label"] = int(r["label"])
            rows.append(feat)

    return pd.DataFrame(rows)


def main():
    df = load_labeled_df()

    if df.empty:
        raise RuntimeError("No labeled samples found. Add liked/disliked labels first.")

    # Basic sanity check
    print("Samples:", len(df))
    print("Label balance:", df["label"].value_counts().to_dict())

    X = df.drop("label", axis=1)
    y = df["label"]

    numeric_features = ["hour", "day_of_week", "task_duration"]
    categorical_features = ["task_category"]

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", "passthrough", numeric_features),
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
        ]
    )

    model = Pipeline(
        steps=[
            ("preprocess", preprocessor),
            ("clf", LogisticRegression(
                max_iter=2000,
                class_weight="balanced"  # critical for imbalanced labels
            )),
        ]
    )

    # Stratify keeps label ratio in both splits
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.25,
        random_state=42,
        stratify=y if y.nunique() > 1 else None
    )

    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    print("\nConfusion matrix:")
    print(confusion_matrix(y_test, y_pred))

    print("\nClassification report:")
    print(classification_report(y_test, y_pred, digits=3))

    os.makedirs("ml/models", exist_ok=True)
    joblib.dump(model, "ml/models/logistic_v1.pkl")
    print("\nSaved model to: ml/models/logistic_v1.pkl")


if __name__ == "__main__":
    main()
