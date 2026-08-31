from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import mysql.connector

lisan_bp = Blueprint("lisan", __name__)

# Same DB connection settings as app.py
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "bunk_house"
}

def get_db_connection():
    return mysql.connector.connect(**db_config)


@lisan_bp.route("/feedback", methods=["GET", "POST"])
def feedback_page():
    if "user_id" not in session:
        flash("Please log in to give feedback.", "error")
        return redirect(url_for("login"))

    if request.method == "POST":
        rating = request.form["rating"]
        comments = request.form["comments"].strip()

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO feedback (student_id, rating, comments) VALUES (%s, %s, %s)",
            (session["user_id"], rating, comments)
        )
        conn.commit()
        cursor.close()
        conn.close()

        flash("Thank you! Your feedback has been submitted.", "success")
        return redirect(url_for("lisan.feedback_page"))

    return render_template("feedback.html")


@lisan_bp.route("/meal")
def meal_page():
    if "user_id" not in session:
        flash("Please log in to view the meal routine.", "error")
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM meal_schedule")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    # Group rows into { day_name: {Breakfast: ..., Lunch: ..., Snack: ..., Dinner: ...} }
    days_order = ["Saturday", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    schedule = {day: {} for day in days_order}
    for row in rows:
        schedule[row["day_name"]][row["meal_type"]] = row["item_description"]

    return render_template("meal.html", schedule=schedule, days_order=days_order)


# room booking

@lisan_bp.route("/rooms")
def view_rooms():
    if "user_id" not in session:
        flash("Please log in to view rooms.", "error")
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM rooms ORDER BY room_no")
    rooms = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("rooms.html", rooms=rooms)


@lisan_bp.route("/book-room/<int:room_no>", methods=["GET", "POST"])
def book_room(room_no):
    if "user_id" not in session:
        flash("Please log in to book a room.", "error")
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM rooms WHERE room_no = %s", (room_no,))
    room = cursor.fetchone()

    if not room:
        flash("Room not found.", "error")
        cursor.close()
        conn.close()
        return redirect(url_for("lisan.view_rooms"))


    if request.method == "POST":
        cursor.execute(
            "SELECT * FROM bookings WHERE student_id = %s",
            (session["user_id"],)
        )
        existing = cursor.fetchone()

        if existing:
            flash("You already have an active booking. Cancel it first to book another room.", "error")
        elif room["occupancy"] >= room["capacity"]:
            flash("Sorry, this room just became full.", "error")
        else:
            write_cursor = conn.cursor()
            write_cursor.execute(
                "INSERT INTO bookings (student_id, room_no) VALUES (%s, %s)",
                (session["user_id"], room_no)
            )
            write_cursor.execute(
                "UPDATE rooms SET occupancy = occupancy + 1 WHERE room_no = %s",
                (room_no,)
            )
            conn.commit()
            write_cursor.close()
            flash(f"Room {room_no} booked successfully!", "success")
            cursor.close()
            conn.close()
            return redirect(url_for("lisan.my_bookings"))

        cursor.close()
        conn.close()
        return redirect(url_for("lisan.view_rooms"))


    cursor.close()
    conn.close()
    return render_template("booking_confirm.html", room=room)


@lisan_bp.route("/my-bookings")
def my_bookings():
    if "user_id" not in session:
        flash("Please log in to view your bookings.", "error")
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM bookings WHERE student_id = %s ORDER BY booking_date DESC",
        (session["user_id"],)
    )
    bookings = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("my_bookings.html", bookings=bookings)


@lisan_bp.route("/cancel-booking/<int:booking_id>", methods=["POST"])
def cancel_booking(booking_id):
    if "user_id" not in session:
        flash("Please log in first.", "error")
        return redirect(url_for("login"))

    conn = get_db_connection()

    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM bookings WHERE booking_id = %s AND student_id = %s",
        (booking_id, session["user_id"])
    )
    booking = cursor.fetchone()

    if booking:
        write_cursor = conn.cursor()
        write_cursor.execute("DELETE FROM bookings WHERE booking_id = %s", (booking_id,))
        write_cursor.execute(
            "UPDATE rooms SET occupancy = occupancy - 1 WHERE room_no = %s",
            (booking["room_no"],)
        )
        conn.commit()
        write_cursor.close()
        flash("Booking cancelled successfully.", "success")
    else:
        flash("Booking not found.", "error")

    cursor.close()
    conn.close()
    return redirect(url_for("lisan.my_bookings"))