from ml.user_modeling.weights_extractor import extract_feature_weights
from ml.user_modeling.profile_builder import UserProfileBuilder


def main():
    weights = extract_feature_weights()
    profile = UserProfileBuilder.from_feature_weights(weights)

    print("\nUSER PROFILE\n")
    print(profile)


if __name__ == "__main__":
    main()
