from __future__ import annotations

import os
from pathlib import Path

from flask import Flask

from backend.controllers.auth_controller import auth_bp
from backend.controllers.pose_controller import pose_bp
from backend.controllers.workout_controller import workout_bp
from backend.database.db import init_database


ROOT = Path(__file__).resolve().parent


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(
        __name__,
        template_folder=str(ROOT / "frontend" / "templates"),
        static_folder=str(ROOT / "frontend" / "static"),
    )
    app.config.update(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-secret-change-me"),
        DATABASE=str(ROOT / "backend" / "database" / "squat_coach.sqlite3"),
    )
    if test_config:
        app.config.update(test_config)
    init_database(app)
    app.register_blueprint(auth_bp)
    app.register_blueprint(workout_bp)
    app.register_blueprint(pose_bp)
    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True, threaded=True)

