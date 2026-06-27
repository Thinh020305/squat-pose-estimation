from __future__ import annotations

from dataclasses import dataclass, field

from .feedback_service import RepEvaluation
from .ml_service import HybridSquatEvaluator


@dataclass
class RepResult:
    number: int
    min_knee_angle: float
    max_torso_lean: float
    duration_seconds: float
    evaluation: RepEvaluation


@dataclass
class SquatCounter:
    standing_threshold: float = 155.0
    descent_threshold: float = 145.0
    valid_depth_threshold: float = 100.0
    min_rep_seconds: float = 0.5
    state: str = "standing"
    count: int = 0
    rep_start_ts: float | None = None
    min_knee_angle: float = 180.0
    max_torso_lean: float = 0.0
    bottom_model_features: dict[str, float] | None = None
    latest_result: RepResult | None = None
    results: list[RepResult] = field(default_factory=list)
    evaluator: HybridSquatEvaluator = field(default_factory=HybridSquatEvaluator)

    def update(
        self,
        knee_angle: float,
        torso_lean: float,
        timestamp: float,
        model_features: dict[str, float] | None = None,
    ) -> RepResult | None:
        self.latest_result = None

        if self.state == "standing" and knee_angle < self.descent_threshold:
            self.state = "down"
            self.rep_start_ts = timestamp
            self.min_knee_angle = knee_angle
            self.max_torso_lean = torso_lean
            self.bottom_model_features = model_features
            return None

        if self.state == "down":
            if knee_angle < self.min_knee_angle:
                self.min_knee_angle = knee_angle
                self.bottom_model_features = model_features
            self.max_torso_lean = max(self.max_torso_lean, torso_lean)

            if knee_angle > self.standing_threshold:
                duration = timestamp - (self.rep_start_ts or timestamp)
                if self.min_knee_angle > self.valid_depth_threshold or duration < self.min_rep_seconds:
                    self.state = "standing"
                    return None

                self.count += 1
                evaluation = self.evaluator.evaluate(
                    self.min_knee_angle,
                    self.max_torso_lean,
                    duration,
                    self.bottom_model_features,
                )
                result = RepResult(
                    number=self.count,
                    min_knee_angle=self.min_knee_angle,
                    max_torso_lean=self.max_torso_lean,
                    duration_seconds=duration,
                    evaluation=evaluation,
                )
                self.results.append(result)
                self.latest_result = result
                self.state = "standing"
                return result

        return None
