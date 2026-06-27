from __future__ import annotations

import argparse
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline


LABEL_COLUMN = "label"
EXCLUDED_COLUMNS = {"label", "video_file", "frame"}
UNSUPPORTED_LABELS = {4, "4", "heels_off_ground"}
LABEL_MAPPING = {
    0: "correct",
    1: "shallow",
    2: "forward_lean",
    3: "knees_caving_in",
    5: "asymmetric",
}


def train(csv_path: Path, model_path: Path) -> None:
    data = pd.read_csv(csv_path)
    if LABEL_COLUMN not in data.columns:
        raise ValueError("Missing label column in training CSV.")

    data = data[~data[LABEL_COLUMN].isin(UNSUPPORTED_LABELS)].copy()

    feature_columns = [
        column
        for column in data.columns
        if column not in EXCLUDED_COLUMNS and pd.api.types.is_numeric_dtype(data[column])
    ]
    if not feature_columns:
        raise ValueError("No numeric feature columns found.")

    x = data[feature_columns]
    y = data[LABEL_COLUMN].map(LABEL_MAPPING).fillna(data[LABEL_COLUMN].astype(str))
    stratify = y if y.value_counts().min() >= 2 else None
    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=0.25,
        random_state=42,
        stratify=stratify,
    )

    pipeline = Pipeline(
        steps=[
            (
                "classifier",
                RandomForestClassifier(
                    n_estimators=300,
                    max_depth=None,
                    min_samples_leaf=2,
                    class_weight="balanced",
                    random_state=42,
                    n_jobs=-1,
                ),
            ),
        ]
    )
    pipeline.fit(x_train, y_train)

    print(classification_report(y_test, pipeline.predict(x_test), zero_division=0))
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {
            "model": pipeline,
            "feature_columns": feature_columns,
            "label_mapping": LABEL_MAPPING,
            "model_type": "random_forest",
        },
        model_path,
    )
    print(f"Saved model to {model_path}")
    print(f"Feature columns: {', '.join(feature_columns)}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Train squat quality Random Forest classifier.")
    parser.add_argument("--csv", type=Path, default=Path("data/squat_features_augmented.csv"))
    parser.add_argument("--model", type=Path, default=Path("ml_models/squat_random_forest_model.pkl"))
    args = parser.parse_args()
    train(args.csv, args.model)


if __name__ == "__main__":
    main()
