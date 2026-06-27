from __future__ import annotations

from functools import wraps

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from backend.models.user_model import UserModel
from backend.services.auth_service import hash_password, verify_password


auth_bp = Blueprint("auth", __name__)


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)

    return wrapped


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if session.get("role") != "admin":
            flash("Ban khong co quyen truy cap chuc nang admin.")
            return redirect(url_for("workout.dashboard"))
        return view(*args, **kwargs)

    return wrapped


@auth_bp.route("/")
def index():
    return redirect(url_for("workout.dashboard") if "user_id" in session else url_for("auth.login"))


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = UserModel.find_by_username(request.form["username"])
        if user is None or not user["password_hash"] or not verify_password(
            request.form["password"], user["password_hash"]
        ):
            flash("Sai username hoac mat khau.")
        else:
            session.clear()
            session.update(
                user_id=user["id"],
                username=user["username"],
                name=user["name"],
                role=user["role"],
            )
            return redirect(url_for("workout.dashboard"))
    return render_template("login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip().lower()
        password = request.form["password"]
        if UserModel.find_by_username(username):
            flash("Username da ton tai.")
        elif len(password) < 6:
            flash("Mat khau can it nhat 6 ky tu.")
        else:
            UserModel.create(
                username,
                request.form["name"],
                hash_password(password),
                request.form.get("goal", ""),
                "user",
            )
            flash("Dang ky thanh cong. Hay dang nhap.")
            return redirect(url_for("auth.login"))
    return render_template("register.html", role="user")


@auth_bp.route("/admin/register", methods=["GET", "POST"])
def register_admin():
    if request.method == "POST":
        username = request.form["username"].strip().lower()
        password = request.form["password"]
        if UserModel.find_by_username(username):
            flash("Username da ton tai.")
        elif len(password) < 6:
            flash("Mat khau can it nhat 6 ky tu.")
        else:
            UserModel.create(username, request.form["name"], hash_password(password), "Quan tri he thong", "admin")
            flash("Da tao tai khoan admin.")
            return redirect(url_for("auth.login"))
    return render_template("register.html", role="admin")


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
