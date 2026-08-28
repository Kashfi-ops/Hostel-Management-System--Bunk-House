from flask import Blueprint, render_template, session, redirect, url_for, flash

staff_bp = Blueprint("staff", __name__)


def staff_required():
    if "user_id" not in session:
        flash("Please log in first.", "error")
        return False

    if session.get("role") != "staff":
        flash("Staff access required.", "error")
        return False

    return True


@staff_bp.route("/staff/dashboard")
def dashboard():
    if not staff_required():
        return redirect(url_for("login"))

    return render_template(
        "staff_dashboard.html",
        username=session.get("username")
    )
