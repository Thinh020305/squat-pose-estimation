from __future__ import annotations

from backend.database.db import get_db


class WorkoutModel:
    @staticmethod
    def start_session(user_id: int) -> int:
        db = get_db()
        cursor = db.execute("INSERT INTO workout_sessions(user_id) VALUES (?)", (user_id,))
        db.commit()
        return int(cursor.lastrowid)

    @staticmethod
    def finish_session(session_id: int, total_reps: int, average_score: float) -> None:
        db = get_db()
        db.execute(
            """
            UPDATE workout_sessions
            SET ended_at = CURRENT_TIMESTAMP, total_reps = ?, average_score = ?
            WHERE id = ?
            """,
            (total_reps, average_score, session_id),
        )
        db.commit()

    @staticmethod
    def summary(user_id: int | None = None):
        return get_db().execute(
            """
            SELECT COUNT(*) AS total_sessions,
                   COALESCE(SUM(total_reps), 0) AS total_reps,
                   COALESCE(AVG(NULLIF(average_score, 0)), 0) AS average_score
            FROM workout_sessions
            WHERE ended_at IS NOT NULL AND (? IS NULL OR user_id = ?)
            """,
            (user_id, user_id),
        ).fetchone()

    @staticmethod
    def history(user_id: int | None = None):
        return get_db().execute(
            """
            SELECT id, user_id, started_at, ended_at, total_reps, average_score
            FROM workout_sessions
            WHERE ended_at IS NOT NULL AND (? IS NULL OR user_id = ?)
            ORDER BY id DESC
            """,
            (user_id, user_id),
        ).fetchall()

    @staticmethod
    def score_progress(user_id: int, limit: int = 10):
        rows = get_db().execute(
            """
            SELECT id, started_at, total_reps, average_score
            FROM workout_sessions
            WHERE user_id = ? AND ended_at IS NOT NULL
            ORDER BY id ASC
            """,
            (user_id,),
        ).fetchall()
        recent_rows = rows[-limit:]
        progress = []
        previous_score = None

        for row in recent_rows:
            score = float(row["average_score"] or 0)
            change = None if previous_score is None else score - previous_score
            progress.append(
                {
                    "id": row["id"],
                    "started_at": row["started_at"],
                    "total_reps": row["total_reps"],
                    "average_score": score,
                    "score_change": change,
                }
            )
            previous_score = score

        return progress

    @staticmethod
    def add_schedule(user_id: int, scheduled_date: str, target_reps: int, note: str) -> None:
        db = get_db()
        db.execute(
            """
            INSERT INTO training_schedule(user_id, scheduled_date, workout_name, target_reps, note)
            VALUES (?, ?, 'Squat', ?, ?)
            """,
            (user_id, scheduled_date, target_reps, note.strip()),
        )
        db.commit()

    @staticmethod
    def schedule(user_id: int):
        return get_db().execute(
            """
            SELECT id, scheduled_date, workout_name, target_reps, note, completed
            FROM training_schedule WHERE user_id = ?
            ORDER BY date(scheduled_date), id
            """,
            (user_id,),
        ).fetchall()

    @staticmethod
    def complete_schedule(schedule_id: int, user_id: int) -> None:
        db = get_db()
        db.execute(
            "UPDATE training_schedule SET completed = 1 WHERE id = ? AND user_id = ?",
            (schedule_id, user_id),
        )
        db.commit()
