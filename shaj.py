from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import mysql.connector

shaj_bp = Blueprint("shaj", __name__)

# Same DB connection settings as app.py
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
        description = request.form["description"].strip()
        supervisor_id = request.form["supervisor_id"]

        if not description or not supervisor_id:
            flash("Please fill in all fields.", "error")
        else:
            cursor.execute(
                "INSERT INTO complaints (description, student_id, supervisor_id) VALUES (%s, %s, %s)",
                (description, session["user_id"], supervisor_id)
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
        SELECT c.complaint_id, c.description, c.status, c.created_at,
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