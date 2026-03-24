import joblib
import numpy as np
import pandas as pd


def main():
    model = joblib.load("ml/models/logistic_v1.pkl")

    # Access the trained classifier
    clf = model.named_steps["clf"]
    preprocessor = model.named_steps["preprocess"]

    # Get feature names
    num_features = preprocessor.transformers_[0][2]
    cat_encoder = preprocessor.transformers_[1][1]
    cat_features = cat_encoder.get_feature_names_out(
        preprocessor.transformers_[1][2]
    )

    feature_names = list(num_features) + list(cat_features)

    weights = clf.coef_[0]

    df = pd.DataFrame({
        "feature": feature_names,
        "weight": weights,
        "abs_weight": np.abs(weights)
    })

    df = df.sort_values("abs_weight", ascending=False)

    print("\nFeature importance (sorted):\n")
    print(df[["feature", "weight"]])


if __name__ == "__main__":
    main()
