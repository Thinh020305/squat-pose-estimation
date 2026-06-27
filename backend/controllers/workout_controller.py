from __future__ import annotations

import os
import subprocess
import sys
from datetime import date
from pathlib import Path

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from backend.controllers.auth_controller import admin_required, login_required
from backend.models.result_model import ResultModel
from backend.models.user_model import UserModel
from backend.models.workout_model import WorkoutModel


workout_bp = Blueprint("workout", __name__)
ROOT = Path(__file__).resolve().parents[2]


@workout_bp.route("/dashboard")
@login_required
def dashboard():
    user_id = session["user_id"]
    summary = WorkoutModel.summary(user_id)
    score_progress = WorkoutModel.score_progress(user_id)
    schedules = WorkoutModel.schedule(user_id)
    reminder = next(
        (item for item in schedules if not item["completed"] and item["scheduled_date"] <= date.today().isoformat()),
        None,
    )
    return render_template(
        "dashboard.html",
        summary=summary,
        score_progress=score_progress,
        schedules=schedules,
        reminder=reminder,
        is_admin=session.get("role") == "admin",
    )


@workout_bp.route("/schedule", methods=["POST"])
@login_required
def add_schedule():
    try:
        date.fromisoformat(request.form["scheduled_date"])
        target_reps = int(request.form["target_reps"])
        if target_reps <= 0:
            raise ValueError
        WorkoutModel.add_schedule(
            session["user_id"],
            request.form["scheduled_date"],
            target_reps,
            request.form.get("note", ""),
        )
    except ValueError:
        flash("Ngay hoac so rep muc tieu khong hop le.")
    return redirect(url_for("workout.dashboard"))


@workout_bp.route("/schedule/<int:schedule_id>/complete", methods=["POST"])
@login_required
def complete_schedule(schedule_id: int):
    WorkoutModel.complete_schedule(schedule_id, session["user_id"])
    return redirect(url_for("workout.dashboard"))


@workout_bp.route("/history")
@login_required
def history():
    sessions = WorkoutModel.history(session["user_id"])
    selected_id = request.args.get("session_id", type=int)
    reps = ResultModel.by_session(selected_id) if selected_id else []
    return render_template("history.html", sessions=sessions, reps=reps, selected_id=selected_id)


@workout_bp.route("/profile", methods=["POST"])
@login_required
def update_profile():
    UserModel.update_goal(session["user_id"], request.form.get("goal", ""))
    flash("Da cap nhat muc tieu.")
    return redirect(url_for("workout.dashboard"))


@workout_bp.route("/admin")
@admin_required
def admin_dashboard():
    return render_template(
        "admin.html",
        users=UserModel.all_users(),
        summary=WorkoutModel.summary(None),
    )


def _run_training(module_name: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", module_name],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


@workout_bp.route("/admin/train/svm", methods=["POST"])
@admin_required
def train_svm_model():
    result = _run_training("backend.services.train_svm")
    flash("Train SVM thanh cong." if result.returncode == 0 else f"Train SVM that bai: {result.stderr[-300:]}")
    return redirect(url_for("workout.admin_dashboard"))


@workout_bp.route("/admin/train/random-forest", methods=["POST"])
@admin_required
def train_random_forest_model():
    result = _run_training("backend.services.train_random_forest")
    flash(
        "Train Random Forest thanh cong."
        if result.returncode == 0
        else f"Train Random Forest that bai: {result.stderr[-300:]}"
    )
    return redirect(url_for("workout.admin_dashboard"))
