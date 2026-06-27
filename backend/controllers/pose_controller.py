from __future__ import annotations

from flask import Blueprint, Response, flash, jsonify, redirect, render_template, session, url_for

from backend.controllers.auth_controller import login_required
from backend.models.result_model import ResultModel
from backend.models.workout_model import WorkoutModel
from backend.services.pose_service import pose_service


pose_bp = Blueprint("pose", __name__)


@pose_bp.route("/workout")
@login_required
def workout():
    user_id = session["user_id"]
    live = pose_service.get(user_id)
    if live is None:
        try:
            live = pose_service.start(user_id, WorkoutModel.start_session(user_id))
        except RuntimeError as exc:
            flash(str(exc))
            return redirect(url_for("workout.dashboard"))
    return render_template("workout.html")


@pose_bp.route("/workout/video")
@login_required
def video_feed():
    user_id = session["user_id"]
    if pose_service.get(user_id) is None:
        return Response(status=404)
    return Response(
        pose_service.frames(user_id),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )


@pose_bp.route("/workout/status")
@login_required
def workout_status():
    live = pose_service.get(session["user_id"])
    if live is None:
        return jsonify(reps=0, score=0, label="", feedback="")
    return jsonify(
        reps=live.counter.count,
        score=live.last_score,
        label=live.last_label,
        feedback=live.last_feedback,
    )


@pose_bp.route("/workout/stop", methods=["POST"])
@login_required
def stop_workout():
    live = pose_service.stop(session["user_id"])
    if live and live.session_id is not None:
        for rep in live.counter.results:
            ResultModel.save_rep(live.session_id, rep)
        scores = [rep.evaluation.total_score for rep in live.counter.results]
        average = sum(scores) / len(scores) if scores else 0
        WorkoutModel.finish_session(live.session_id, len(scores), average)
    return jsonify(ok=True)
