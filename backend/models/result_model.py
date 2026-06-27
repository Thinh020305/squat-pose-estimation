from __future__ import annotations

from backend.database.db import get_db


class ResultModel:
    @staticmethod
    def save_rep(session_id: int, rep) -> None:
        evaluation = rep.evaluation
        db = get_db()
        db.execute(
            """
            INSERT INTO squat_reps(
                session_id, rep_number, min_knee_angle, max_torso_lean,
                duration_seconds, depth_score, torso_score, tempo_score,
                total_score, feedback, label, confidence, evaluator
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                session_id,
                rep.number,
                rep.min_knee_angle,
                rep.max_torso_lean,
                rep.duration_seconds,
                evaluation.depth_score,
                evaluation.torso_score,
                evaluation.tempo_score,
                evaluation.total_score,
                "; ".join(evaluation.feedback),
                evaluation.label,
                evaluation.confidence,
                evaluation.evaluator,
            ),
        )
        db.commit()

    @staticmethod
    def by_session(session_id: int):
        return get_db().execute(
            """
            SELECT rep_number, depth_score, torso_score, tempo_score,
                   total_score, label, confidence, feedback
            FROM squat_reps WHERE session_id = ? ORDER BY rep_number
            """,
            (session_id,),
        ).fetchall()
