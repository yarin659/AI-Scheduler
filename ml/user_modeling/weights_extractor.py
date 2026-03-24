import joblib


def extract_feature_weights(model_path="ml/models/logistic_v1.pkl") -> dict:
    model = joblib.load(model_path)

    clf = model.named_steps["clf"]
    preprocessor = model.named_steps["preprocess"]

    num_features = preprocessor.transformers_[0][2]
    cat_encoder = preprocessor.transformers_[1][1]
    cat_features = cat_encoder.get_feature_names_out(
        preprocessor.transformers_[1][2]
    )

    feature_names = list(num_features) + list(cat_features)
    weights = clf.coef_[0]

    return dict(zip(feature_names, weights))
