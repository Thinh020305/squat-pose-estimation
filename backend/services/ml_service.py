from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import joblib
import pandas as pd

from .feedback_service import RepEvaluation, evaluate_rep


MODEL_PATH = Path("ml_models/squat_random_forest_model.pkl")
FALLBACK_MODEL_PATH = Path("ml_models/squat_error_model.pkl")
DEFAULT_FEATURE_COLUMNS = ["min_knee_angle", "max_torso_lean", "duration_seconds"]
UNSUPPORTED_LABELS = {"4", "heels_off_ground"}
LABEL_NAMES = {
    0: "correct",
    1: "shallow",
    2: "forward_lean",
    3: "knees_caving_in",
    5: "asymmetric",
    "0": "correct",
    "1": "shallow",
    "2": "forward_lean",
    "3": "knees_caving_in",
    "5": "asymmetric",
}
LABEL_TO_FEEDBACK = {
    "correct": "Tu the squat dung.",
    "0": "Tu the squat dung.",
    "good": "Tu the squat dung.",
    "shallow": "Phat hien squat chua du sau.",
    "1": "Phat hien squat chua du sau.",
    "forward_lean": "Phat hien than nguoi nghieng ve truoc.",
    "2": "Phat hien than nguoi nghieng ve truoc.",
    "unsafe_lean": "Phat hien than nguoi nghieng ve truoc.",
    "tempo_issue": "Phat hien nhip do chua on dinh.",
    "knees_caving_in": "Phat hien dau goi bi chup vao trong.",
    "3": "Phat hien dau goi bi chup vao trong.",
    "asymmetric": "Phat hien squat lech hai ben.",
    "5": "Phat hien squat lech hai ben.",
}


@dataclass(frozen=True)
class RepFeatures:
    min_knee_angle: float
    max_torso_lean: float
    duration_seconds: float
    model_features: dict[str, float] | None = None

    def as_vector(self) -> list[float]:
        return [self.min_knee_angle, self.max_torso_lean, self.duration_seconds]


class SquatMLClassifier:
    def __init__(self, model_path: Path = MODEL_PATH) -> None:
        self.model_path = model_path if model_path.exists() else FALLBACK_MODEL_PATH
        self.pipeline = None
        self.feature_columns = DEFAULT_FEATURE_COLUMNS
        if self.model_path.exists():
            artifact = joblib.load(self.model_path)
            if isinstance(artifact, dict) and "model" in artifact:
                self.pipeline = artifact["model"]
                self.feature_columns = artifact.get("feature_columns", DEFAULT_FEATURE_COLUMNS)
            else:
                self.pipeline = artifact

    @property
    def available(self) -> bool:
        return self.pipeline is not None

    def evaluate(self, features: RepFeatures) -> RepEvaluation | None:
        if self.pipeline is None:
            return None

        source = {
            "min_knee_angle": features.min_knee_angle,
            "max_torso_lean": features.max_torso_lean,
            "duration_seconds": features.duration_seconds,
        }
        if features.model_features:
            source.update(features.model_features)
        vector = pd.DataFrame([[source.get(column, 0.0) for column in self.feature_columns]], columns=self.feature_columns)
        label = str(self.pipeline.predict(vector)[0])
        label = LABEL_NAMES.get(label, label)
        if label in UNSUPPORTED_LABELS:
            return evaluate_rep(
                features.min_knee_angle,
                features.max_torso_lean,
                features.duration_seconds,
            )
        confidence = 0.0
        if hasattr(self.pipeline, "predict_proba"):
            confidence = float(max(self.pipeline.predict_proba(vector)[0]))

        result = evaluate_rep(
            features.min_knee_angle,
            features.max_torso_lean,
            features.duration_seconds,
        )
        ml_feedback = LABEL_TO_FEEDBACK.get(label, f"Ket qua phan loai: {label}.")
        result.feedback.insert(0, ml_feedback)
        result.label = label
        result.confidence = confidence
        result.evaluator = "machine_learning"
        return result


class HybridSquatEvaluator:
    def __init__(self, classifier: SquatMLClassifier | None = None) -> None:
        self.classifier = classifier or SquatMLClassifier()

    def evaluate(
        self,
        min_knee_angle: float,
        max_torso_lean: float,
        duration_seconds: float,
        model_features: dict[str, float] | None = None,
    ) -> RepEvaluation:
        features = RepFeatures(min_knee_angle, max_torso_lean, duration_seconds, model_features)
        ml_result = self.classifier.evaluate(features)
        if ml_result is not None:
            return ml_result

        result = evaluate_rep(min_knee_angle, max_torso_lean, duration_seconds)
        result.feedback = ["Rule fallback: " + item for item in result.feedback]
        return result
