from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import mysql.connector

shaj_bp = Blueprint("shaj", __name__)

db_config = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "bunk_house"
}

def get_db_connection():
    return mysql.connector.connect(**db_config)


@shaj_bp.route("/complaint", methods=["GET", "POST"])
def submit_complaint():
    if "user_id" not in session:
        flash("Please log in to submit a complaint.", "error")
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        room_no = request.form["room_no"].strip()
        description = request.form["description"].strip()
        supervisor_id = request.form["supervisor_id"]

        if not room_no or not description or not supervisor_id:
            flash("Please fill in all fields.", "error")
        else:
            cursor.execute(
                "INSERT INTO complaints (room_no, description, student_id, supervisor_id) VALUES (%s, %s, %s, %s)",
                (room_no, description, session["user_id"], supervisor_id)
            )
            conn.commit()
            flash("Complaint submitted to supervisor successfully!", "success")
            cursor.close()
            conn.close()
            return redirect(url_for("shaj.my_complaints"))

    cursor.execute("SELECT * FROM supervisors")
    supervisors = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("complaint.html", supervisors=supervisors)


@shaj_bp.route("/my-complaints")
def my_complaints():
    if "user_id" not in session:
        flash("Please log in to view your complaints.", "error")
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT c.complaint_id, c.room_no,c.description, c.status, c.remark,c.created_at,
               s.supervisor_name
        FROM complaints c
        JOIN supervisors s ON c.supervisor_id = s.supervisor_id
        WHERE c.student_id = %s
        ORDER BY c.created_at DESC
    """, (session["user_id"],))
    complaints = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("my_complaints.html", complaints=complaints)


# ---supervisor side complaint

@shaj_bp.route("/supervisor/complaints")
def view_complaints():
    if "user_id" not in session:
        flash("Please log in first.", "error")
        return redirect(url_for("login"))

    if session.get("role") != "supervisor":
        flash("Supervisor access required.", "error")
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT c.complaint_id, c.room_no, c.description, c.status, c.remark, c.created_at,
               u.username AS student_username
        FROM complaints c
        JOIN users u ON c.student_id = u.id
        WHERE c.supervisor_id = %s
        ORDER BY c.created_at DESC
        """,
        (session.get("supervisor_id"),)
    )

    complaints = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template(
        "supervisor_complaints.html",
        complaints=complaints,
        username=session.get("username")
    )


@shaj_bp.route("/supervisor/complaints/<int:complaint_id>/update", methods=["POST"])
def update_complaint_status(complaint_id):
    if "user_id" not in session:
        flash("Please log in first.", "error")
        return redirect(url_for("login"))

    if session.get("role") != "supervisor":
        flash("Supervisor access required.", "error")
        return redirect(url_for("login"))

    status = request.form.get("status", "").strip()
    remark = request.form.get("remark", "").strip()

    valid_statuses = [
        "Dismissed", "Will Talk in Person",
        "Warning Issued", "Filed to Proctor", "Others"
    ]

    if status not in valid_statuses:
        flash("Please select a valid status.", "error")
        return redirect(url_for("shaj.view_complaints"))

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE complaints
        SET status = %s, remark = %s
        WHERE complaint_id = %s AND supervisor_id = %s
        """,
        (status, remark, complaint_id, session.get("supervisor_id"))
    )

    conn.commit()
    cursor.close()
    conn.close()

    flash("Complaint updated.", "success")

    return redirect(url_for("shaj.view_complaints"))


# ------- student side leave

@shaj_bp.route("/leave/apply", methods=["GET", "POST"])
def apply_leave():
    if "user_id" not in session:
        flash("Please log in first.", "error")
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        supervisor_id = request.form["supervisor_id"]
        leave_days = request.form["leave_days"].strip()
        start_date = request.form["start_date"]
        return_date = request.form["return_date"]
        reason = request.form["reason"].strip()

        if not supervisor_id or not leave_days or not start_date or not return_date or not reason:
            flash("Please fill in all fields.", "error")
        else:
            cursor.execute(
                """
                INSERT INTO leaves
                (student_id, supervisor_id, leave_days, start_date, return_date, reason)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (session["user_id"], supervisor_id, leave_days, start_date, return_date, reason)
            )
            conn.commit()
            flash("Leave application submitted successfully!", "success")
            cursor.close()
            conn.close()
            return redirect(url_for("shaj.my_leaves"))

    cursor.execute("SELECT * FROM supervisors")
    supervisors = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("leave_apply.html", supervisors=supervisors)


@shaj_bp.route("/my-leaves")
def my_leaves():
    if "user_id" not in session:
        flash("Please log in first.", "error")
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT l.leave_id, l.leave_days, l.start_date, l.return_date, l.reason,
               l.status, l.created_at,
               s.supervisor_name,
               a.comments, a.approval_date
        FROM leaves l
        JOIN supervisors s ON l.supervisor_id = s.supervisor_id
        LEFT JOIN approvals a ON a.approval_id = (
            SELECT MAX(approval_id) FROM approvals WHERE leave_id = l.leave_id
        )
        WHERE l.student_id = %s
        ORDER BY l.created_at DESC
        """,
        (session["user_id"],)
    )

    leaves = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("my_leaves.html", leaves=leaves)


# ------- supervisor side leave

@shaj_bp.route("/supervisor/leaves")
def view_leaves():
    if "user_id" not in session:
        flash("Please log in first.", "error")
        return redirect(url_for("login"))

    if session.get("role") != "supervisor":
        flash("Supervisor access required.", "error")
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT l.leave_id, l.leave_days, l.start_date, l.return_date, l.reason,
               l.status, l.created_at,
               u.username AS student_username
        FROM leaves l
        JOIN users u ON l.student_id = u.id
        WHERE l.supervisor_id = %s
        ORDER BY l.created_at DESC
        """,
        (session.get("supervisor_id"),)
    )

    leaves = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template(
        "supervisor_leaves.html",
        leaves=leaves,
        username=session.get("username")
    )


@shaj_bp.route("/supervisor/leaves/<int:leave_id>/decide", methods=["POST"])
def decide_leave(leave_id):
    if "user_id" not in session:
        flash("Please log in first.", "error")
        return redirect(url_for("login"))

    if session.get("role") != "supervisor":
        flash("Supervisor access required.", "error")
        return redirect(url_for("login"))

    status = request.form.get("status", "").strip()
    comments = request.form.get("comments", "").strip()

    if status not in ["Approved", "Dismissed"]:
        flash("Please select Approved or Dismissed.", "error")
        return redirect(url_for("shaj.view_leaves"))

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO approvals (leave_id, supervisor_id, approval_status, comments)
            VALUES (%s, %s, %s, %s)
            """,
            (leave_id, session.get("supervisor_id"), status, comments)
        )

        cursor.execute(
            """
            UPDATE leaves
            SET status = %s
            WHERE leave_id = %s AND supervisor_id = %s
            """,
            (status, leave_id, session.get("supervisor_id"))
        )

        conn.commit()
        flash("Leave request updated.", "success")

    except mysql.connector.Error:
        conn.rollback()
        flash("Something went wrong. Please try again.", "error")

    finally:
        cursor.close()
        conn.close()

    return redirect(url_for("shaj.view_leaves"))


@shaj_bp.route("/supervisor/leaves/approvals")
def leave_approvals():
    if "user_id" not in session:
        flash("Please log in first.", "error")
        return redirect(url_for("login"))

    if session.get("role") != "supervisor":
        flash("Supervisor access required.", "error")
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT a.approval_id, a.approval_status, a.comments, a.approval_date,
               u.username AS student_username
        FROM approvals a
        JOIN leaves l ON a.leave_id = l.leave_id
        JOIN users u ON l.student_id = u.id
        WHERE a.supervisor_id = %s AND a.leave_id IS NOT NULL
        ORDER BY a.approval_date DESC
        """,
        (session.get("supervisor_id"),)
    )

    approvals = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template(
        "supervisor_leave_approvals.html",
        approvals=approvals,
        username=session.get("username")
    )