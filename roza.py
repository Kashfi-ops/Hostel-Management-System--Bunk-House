from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import mysql.connector

roza_bp = Blueprint("roza", __name__)


db_config = {
    "host": "localhost",
    "user": "root",
    "password": "abc", # need to put sql password if using mac device.
    "database": "bunk_house"
}

def get_db_connection():
    return mysql.connector.connect(**db_config)




#Students get notified when a seat is available


@roza_bp.route("/seat-notification")
def seat_notification():

    if "user_id" not in session:
        flash("Please log in first.", "error")
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT COUNT(*) AS available_seats
        FROM seats
        WHERE status = 'Available'
        """
    )

    result = cursor.fetchone()

    cursor.close()
    conn.close()

    available_seats = result["available_seats"]

    if available_seats > 0:
        message = f"{available_seats} seat(s) are currently available."
        notification_type = "success"
    else:
        message = "No seats are currently available."
        notification_type = "error"

    flash(message, notification_type)

    return redirect(url_for("roza.book_seat"))




# Book a seat page
@roza_bp.route("/book-seat")
def book_seat():
    if "user_id" not in session:
        flash("Please log in to book a seat.", "error")
        return redirect(url_for("login"))

    return render_template("book_seat.html")




#  Technical Issue Feature 
# Apply for a service or report a technical issue

@roza_bp.route("/service-request", methods=["GET", "POST"])
def service_request():
    if "user_id" not in session:
        flash("Please log in first.", "error")
        return redirect(url_for("login"))

    if request.method == "POST":
        service_type = request.form["service_type"].strip()
        description = request.form["description"].strip()

        if not service_type or not description:
            flash("Please fill in all fields.", "error")
            return redirect(url_for("roza.service_request"))

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO service_requests
                (student_id, service_type, description)
                VALUES (%s, %s, %s)
                """,
                (session["user_id"], service_type, description)
            )

            conn.commit()
            flash("Your service request has been submitted successfully.", "success")

        except mysql.connector.Error:
            conn.rollback()
            flash("Something went wrong. Please try again.", "error")

        finally:
            cursor.close()
            conn.close()

        return redirect(url_for("roza.my_service_requests"))

    return render_template("service_request.html")


# View student's submitted service requests

@roza_bp.route("/my-service-requests")
def my_service_requests():
    if "user_id" not in session:
        flash("Please log in first.", "error")
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT request_id, service_type, description,
               status, created_at
        FROM service_requests
        WHERE student_id = %s
        ORDER BY created_at DESC
        """,
        (session["user_id"],)
    )

    requests = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "my_service_requests.html",
        requests=requests
    )
