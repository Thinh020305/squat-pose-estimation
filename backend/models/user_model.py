from __future__ import annotations

from backend.database.db import get_db


class UserModel:
    @staticmethod
    def find_by_username(username: str):
        return get_db().execute(
            """
            SELECT id, username, name, goal, password_hash, role, created_at
            FROM users WHERE lower(username) = lower(?)
            """,
            (username.strip(),),
        ).fetchone()

    @staticmethod
    def find_by_id(user_id: int):
        return get_db().execute(
            "SELECT id, username, name, goal, role, created_at FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()

    @staticmethod
    def create(username: str, name: str, password_hash: str, goal: str, role: str = "user") -> int:
        db = get_db()
        cursor = db.execute(
            """
            INSERT INTO users(username, name, goal, password_hash, role)
            VALUES (?, ?, ?, ?, ?)
            """,
            (username.strip().lower(), name.strip(), goal.strip(), password_hash, role),
        )
        db.commit()
        return int(cursor.lastrowid)

    @staticmethod
    def update_goal(user_id: int, goal: str) -> None:
        db = get_db()
        db.execute("UPDATE users SET goal = ? WHERE id = ?", (goal.strip(), user_id))
        db.commit()

    @staticmethod
    def all_users():
        return get_db().execute(
            "SELECT id, username, name, goal, role, created_at FROM users ORDER BY id"
        ).fetchall()
