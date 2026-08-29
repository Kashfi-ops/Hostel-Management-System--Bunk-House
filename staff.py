from flask import Blueprint, render_template, session, redirect, url_for, flash, request
import mysql.connector


staff_bp = Blueprint("staff", __name__)


# =========================================================
# DATABASE CONFIGURATION
# =========================================================

db_config = {
    "host": "localhost",
    "user": "root",
    "password": "Ksjzja1867@#",
    "database": "bunk_house"
}


def get_db_connection():
    return mysql.connector.connect(**db_config)


# =========================================================
# STAFF ACCESS CHECK
# =========================================================

def staff_required():

    if "user_id" not in session:

        flash(
            "Please log in first.",
            "error"
        )

        return False

    if session.get("role") != "staff":

        flash(
            "Staff access required.",
            "error"
        )

        return False

    return True


# =========================================================
# STAFF DASHBOARD
# =========================================================

@staff_bp.route("/staff/dashboard")
def dashboard():

    if not staff_required():
        return redirect(url_for("login"))

    current_filter = request.args.get(
        "filter",
        "all"
    )

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:

        # -------------------------------------------------
        # Find the staff member connected to this login
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                s.staff_id,
                s.staff_name,
                s.service_type,
                s.status

            FROM staff s

            JOIN users u
                ON s.email = u.email

            WHERE u.id = %s
            """,
            (session["user_id"],)
        )

        staff_member = cursor.fetchone()


        # -------------------------------------------------
        # Staff profile not found
        # -------------------------------------------------

        if not staff_member:

            flash(
                "Your staff account is not connected to a staff profile.",
                "error"
            )

            return render_template(
                "staff_dashboard.html",
                username=session.get("username"),
                staff_member=None,
                tasks=[],
                current_filter=current_filter
            )


        # -------------------------------------------------
        # MY TASKS
        # Show all tasks assigned to this staff member
        # -------------------------------------------------

        if current_filter == "all":

            cursor.execute(
                """
                SELECT
                    sr.request_id,
                    sr.service_type,
                    sr.description,
                    sr.status,
                    sr.created_at,
                    sr.approved_at,
                    sr.assigned_at,

                    u.username AS student_username

                FROM service_requests sr

                JOIN users u
                    ON sr.student_id = u.id

                WHERE sr.staff_id = %s

                ORDER BY sr.assigned_at DESC
                """,
                (staff_member["staff_id"],)
            )


        # -------------------------------------------------
        # IN PROGRESS
        # -------------------------------------------------

        elif current_filter == "progress":

            cursor.execute(
                """
                SELECT
                    sr.request_id,
                    sr.service_type,
                    sr.description,
                    sr.status,
                    sr.created_at,
                    sr.approved_at,
                    sr.assigned_at,

                    u.username AS student_username

                FROM service_requests sr

                JOIN users u
                    ON sr.student_id = u.id

                WHERE sr.staff_id = %s

                AND sr.status = 'In Progress'

                ORDER BY sr.assigned_at DESC
                """,
                (staff_member["staff_id"],)
            )


        # -------------------------------------------------
        # COMPLETED
        # -------------------------------------------------

        elif current_filter == "completed":

            cursor.execute(
                """
                SELECT
                    sr.request_id,
                    sr.service_type,
                    sr.description,
                    sr.status,
                    sr.created_at,
                    sr.approved_at,
                    sr.assigned_at,

                    u.username AS student_username

                FROM service_requests sr

                JOIN users u
                    ON sr.student_id = u.id

                WHERE sr.staff_id = %s

                AND sr.status = 'Completed'

                ORDER BY sr.assigned_at DESC
                """,
                (staff_member["staff_id"],)
            )


        # -------------------------------------------------
        # Unknown filter
        # -------------------------------------------------

        else:

            return redirect(
                url_for(
                    "staff.dashboard",
                    filter="all"
                )
            )


        tasks = cursor.fetchall()


    finally:

        cursor.close()
        conn.close()


    return render_template(
        "staff_dashboard.html",
        username=session.get("username"),
        staff_member=staff_member,
        tasks=tasks,
        current_filter=current_filter
    )


# =========================================================
# START SERVICE REQUEST
# =========================================================

@staff_bp.route(
    "/staff/service-request/<int:request_id>/start",
    methods=["POST"]
)
def start_service_request(request_id):

    if not staff_required():
        return redirect(url_for("login"))


    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:

        # -------------------------------------------------
        # Find logged-in staff member
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                s.staff_id

            FROM staff s

            JOIN users u
                ON s.email = u.email

            WHERE u.id = %s
            """,
            (session["user_id"],)
        )

        staff_member = cursor.fetchone()


        if not staff_member:

            flash(
                "Staff profile not found.",
                "error"
            )

            return redirect(
                url_for("staff.dashboard")
            )


        # -------------------------------------------------
        # Start the task
        # Only the assigned staff member can start it
        # -------------------------------------------------

        cursor.execute(
            """
            UPDATE service_requests

            SET status = 'In Progress'

            WHERE request_id = %s

            AND staff_id = %s

            AND status = 'Assigned'
            """,
            (
                request_id,
                staff_member["staff_id"]
            )
        )

        conn.commit()


        if cursor.rowcount == 0:

            flash(
                "Task could not be started.",
                "error"
            )

        else:

            flash(
                "Task started successfully.",
                "success"
            )


    except mysql.connector.Error:

        conn.rollback()

        flash(
            "Something went wrong. Please try again.",
            "error"
        )


    finally:

        cursor.close()
        conn.close()


    return redirect(
        url_for(
            "staff.dashboard",
            filter="all"
        )
    )


# =========================================================
# COMPLETE SERVICE REQUEST
# =========================================================

@staff_bp.route(
    "/staff/service-request/<int:request_id>/complete",
    methods=["POST"]
)
def complete_service_request(request_id):

    if not staff_required():
        return redirect(url_for("login"))


    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:

        # -------------------------------------------------
        # Find logged-in staff member
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                s.staff_id

            FROM staff s

            JOIN users u
                ON s.email = u.email

            WHERE u.id = %s
            """,
            (session["user_id"],)
        )

        staff_member = cursor.fetchone()


        if not staff_member:

            flash(
                "Staff profile not found.",
                "error"
            )

            return redirect(
                url_for("staff.dashboard")
            )


        # -------------------------------------------------
        # Complete the task
        # -------------------------------------------------

        cursor.execute(
            """
            UPDATE service_requests

            SET status = 'Completed'

            WHERE request_id = %s

            AND staff_id = %s

            AND status = 'In Progress'
            """,
            (
                request_id,
                staff_member["staff_id"]
            )
        )

        conn.commit()


        if cursor.rowcount == 0:

            flash(
                "Task could not be completed.",
                "error"
            )

        else:

            flash(
                "Task marked as completed.",
                "success"
            )


    except mysql.connector.Error:

        conn.rollback()

        flash(
            "Something went wrong. Please try again.",
            "error"
        )


    finally:

        cursor.close()
        conn.close()


    return redirect(
        url_for(
            "staff.dashboard",
            filter="all"
        )
    )
