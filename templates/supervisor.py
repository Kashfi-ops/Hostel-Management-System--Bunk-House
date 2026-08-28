from flask import Blueprint, render_template, session, redirect, url_for, flash

supervisor_bp = Blueprint("supervisor", __name__)


def supervisor_required():
    if "user_id" not in session:
        flash("Please log in first.", "error")
        return False

    if session.get("role") != "supervisor":
        flash("Supervisor access required.", "error")
        return False

    return True


@supervisor_bp.route("/supervisor/dashboard")
def dashboard():
    if not supervisor_required():
        return redirect(url_for("login"))

    return render_template(
        "supervisor_dashboard.html",
        username=session.get("username")
    )