from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import mysql.connector


supervisor_bp = Blueprint("supervisor", __name__)


# =========================================================
# DATABASE CONFIGURATION
# =========================================================

db_config = {
    "host": "localhost",
    "user": "root",
    "password": "", # use pass if macos.
    "database": "bunk_house"
}


def get_db_connection():
    return mysql.connector.connect(**db_config)


# =========================================================
# SUPERVISOR ACCESS CHECK
# =========================================================

def supervisor_required():

    if "user_id" not in session:

        flash(
            "Please log in first.",
            "error"
        )

        return False

    if session.get("role") != "supervisor":

        flash(
            "Supervisor access required.",
            "error"
        )

        return False

    return True


# =========================================================
# SUPERVISOR DASHBOARD
# =========================================================

@supervisor_bp.route("/supervisor/dashboard")
def dashboard():

    if not supervisor_required():

        return redirect(
            url_for("login")
        )

    return render_template(
        "supervisor_dashboard.html",
        username=session.get("username")
    )


# =========================================================
# REQUESTS
# =========================================================
# Shows technical issues submitted by students.
# Supervisor can assign a staff member.
# =========================================================

@supervisor_bp.route("/supervisor/service-requests")
def service_requests():

    if not supervisor_required():

        return redirect(
            url_for("login")
        )


    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)


    try:

        # -------------------------------------------------
        # Get technical issue requests
        # -------------------------------------------------

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

                u.username AS student_username,

                s.staff_id,
                s.staff_name AS assigned_staff

            FROM service_requests sr

            JOIN users u
                ON sr.student_id = u.id

            LEFT JOIN staff s
                ON sr.staff_id = s.staff_id

            ORDER BY sr.created_at DESC
            """
        )

        requests = cursor.fetchall()

        cursor.execute(
            """
            SELECT

                staff_id,
                staff_name,
                phone_no,
                email,
                service_type,
                status

            FROM staff

            ORDER BY service_type, staff_name
            """
        )

        staff = cursor.fetchall()


    finally:

        cursor.close()
        conn.close()


    return render_template(
        "supervisor_service_requests.html",

        requests=requests,

        staff=staff
    )


# =========================================================
# ASSIGN STAFF
# =========================================================

@supervisor_bp.route(
    "/supervisor/service-requests/<int:request_id>/assign",
    methods=["POST"]
)
def assign_service_request(request_id):

    if not supervisor_required():

        return redirect(
            url_for("login")
        )


    staff_id = request.form.get("staff_id")


    if not staff_id:

        flash(
            "Please select a staff member.",
            "error"
        )

        return redirect(
            url_for("supervisor.service_requests")
        )


    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)


    try:

        # -------------------------------------------------
        # Check request
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT

                request_id,
                service_type,
                status

            FROM service_requests

            WHERE request_id = %s
            """,
            (request_id,)
        )

        service_request = cursor.fetchone()


        if not service_request:

            flash(
                "Service request not found.",
                "error"
            )

            return redirect(
                url_for("supervisor.service_requests")
            )


        # -------------------------------------------------
        # Check staff
        #
        # We DO NOT require Available.
        #
        # This allows the supervisor to see and select
        # any staff member.
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT

                staff_id,
                staff_name,
                service_type,
                status

            FROM staff

            WHERE staff_id = %s
            """,
            (staff_id,)
        )

        staff = cursor.fetchone()


        if not staff:

            flash(
                "Staff member not found.",
                "error"
            )

            return redirect(
                url_for("supervisor.service_requests")
            )


        # -------------------------------------------------
        # Assign staff to request
        # -------------------------------------------------

        cursor.execute(
            """
            UPDATE service_requests

            SET

                supervisor_id = %s,
                staff_id = %s,
                status = 'Assigned',
                approved_at = CURRENT_TIMESTAMP,
                assigned_at = CURRENT_TIMESTAMP

            WHERE request_id = %s
            """,
            (
                session.get("supervisor_id"),
                staff_id,
                request_id
            )
        )


        # -------------------------------------------------
        # Mark staff as Busy
        #
        # Staff still remains visible in the list.
        # -------------------------------------------------

        cursor.execute(
            """
            UPDATE staff

            SET status = 'Busy'

            WHERE staff_id = %s
            """,
            (staff_id,)
        )


        conn.commit()


        flash(
            f"Request assigned to {staff['staff_name']}.",
            "success"
        )


    except mysql.connector.Error:

        conn.rollback()

        flash(
            "Something went wrong while assigning the request.",
            "error"
        )


    finally:

        cursor.close()
        conn.close()


    return redirect(
        url_for("supervisor.service_requests")
    )


# =========================================================
# STAFF
# =========================================================
# Shows ALL staff and whether they are Available or Busy.
# =========================================================

@supervisor_bp.route("/supervisor/staff")
def staff():

    if not supervisor_required():

        return redirect(
            url_for("login")
        )


    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)


    try:

        cursor.execute(
            """
            SELECT

                staff_id,
                staff_name,
                phone_no,
                email,
                service_type,
                status

            FROM staff

            ORDER BY service_type, staff_name
            """
        )

        staff_members = cursor.fetchall()


    finally:

        cursor.close()
        conn.close()


    return render_template(
        "supervisor_staff.html",

        username=session.get("username"),

        staff=staff_members
    )
