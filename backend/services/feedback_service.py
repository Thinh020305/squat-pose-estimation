from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RepEvaluation:
    depth_score: int
    torso_score: int
    tempo_score: int
    total_score: int
    feedback: list[str]
    label: str = "rule_based"
    confidence: float = 0.0
    evaluator: str = "rule_based"


def score_depth(min_knee_angle: float) -> tuple[int, str | None]:
    """Depth score, max 40 points."""
    if min_knee_angle <= 95:
        return 40, None
    if min_knee_angle <= 110:
        return 32, "Do sau tam duoc, co the ha hong them."
    if min_knee_angle <= 125:
        return 24, "Squat chua du sau."
    if min_knee_angle <= 140:
        return 16, "Can ha hong thap hon."
    return 8, "Do sau qua nong, chua dat squat."


def score_torso(max_torso_lean: float) -> tuple[int, str | None]:
    """Torso posture score, max 35 points."""
    if max_torso_lean <= 20:
        return 35, None
    if max_torso_lean <= 30:
        return 28, "Than nguoi hoi nghieng ve truoc."
    if max_torso_lean <= 40:
        return 20, "Can giu than nguoi thang va on dinh hon."
    return 10, "Than nguoi nghieng qua muc, co nguy co sai ky thuat."


def score_tempo(duration_seconds: float) -> tuple[int, str | None]:
    """Tempo score, max 25 points."""
    if 1.5 <= duration_seconds <= 3.5:
        return 25, None
    if 1.0 <= duration_seconds < 1.5:
        return 18, "Nhip do hoi nhanh, nen kiem soat pha xuong/len."
    if 3.5 < duration_seconds <= 5.0:
        return 18, "Nhip do hoi cham, nen giu chuyen dong deu hon."
    return 10, "Nhip do chua on dinh."


def evaluate_rep(
    min_knee_angle: float,
    max_torso_lean: float,
    duration_seconds: float,
) -> RepEvaluation:
    feedback: list[str] = []

    depth_score, depth_feedback = score_depth(min_knee_angle)
    torso_score, torso_feedback = score_torso(max_torso_lean)
    tempo_score, tempo_feedback = score_tempo(duration_seconds)
    feedback.extend(item for item in (depth_feedback, torso_feedback, tempo_feedback) if item)

    total = depth_score + torso_score + tempo_score
    if not feedback:
        feedback.append("Tu the tot.")

    return RepEvaluation(depth_score, torso_score, tempo_score, total, feedback)
