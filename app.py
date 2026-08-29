from flask import Flask, render_template, request, redirect, url_for, session, flash

import mysql.connector

from werkzeug.security import generate_password_hash, check_password_hash

from shaj import shaj_bp
from lisan import lisan_bp
from roza import roza_bp
from supervisor import supervisor_bp
from staff import staff_bp


app = Flask(__name__)

# Secret key
app.secret_key = "your_secret_key"


app.register_blueprint(shaj_bp)
app.register_blueprint(lisan_bp)
app.register_blueprint(roza_bp)
app.register_blueprint(supervisor_bp)
app.register_blueprint(staff_bp)


db_config = {
    "host": "localhost",
    "user": "root",
    "password": "", # use pass if using macos.
    "database": "bunk_house"
}


def get_db_connection():
    return mysql.connector.connect(**db_config)


@app.route("/")
def index():

    return render_template("index.html")

#sign up

@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        username = request.form["username"].strip()
        email = request.form["email"].strip()
        password = request.form["password"]

        if not username or not email or not password:

            flash(
                "All fields are required.",
                "error"
            )

            return redirect(url_for("signup"))

        conn = get_db_connection()
        cursor = conn.cursor()

        try:

            cursor.execute(
                """
                INSERT INTO users
                (username, email, password, role)
                VALUES (%s, %s, %s, %s)
                """,
                (
                    username,
                    email,
                    password,
                    "student"
                )
            )

            conn.commit()

            flash(
                "Account created successfully! Please log in.",
                "success"
            )

            return redirect(url_for("login"))

        except mysql.connector.IntegrityError:

            flash(
                "Username or email already exists.",
                "error"
            )

            return redirect(url_for("signup"))

        finally:

            cursor.close()
            conn.close()

    return render_template("signup.html")

## login

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"].strip()
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT
                id,
                username,
                password,
                role,
                supervisor_id
            FROM users
            WHERE username = %s
            """,
            (username,)
        )

        user = cursor.fetchone()

        cursor.close()
        conn.close()

     
        
        if user and user["password"] == password:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]

            # which supervisor? 

            if user["role"] == "supervisor":

                session["supervisor_id"] = user["supervisor_id"]

            else:

                # Remove ex supervisor information
            
                session.pop("supervisor_id", None)

            flash(
                f"Welcome back, {user['username']}!",
                "success"
            )

            # Send user to the correct dashboard
          

            if user["role"] == "supervisor":

                return redirect(
                    url_for("supervisor.dashboard")
                )

            elif user["role"] == "staff":

                return redirect(
                    url_for("staff.dashboard")
                )

            else:

                return redirect(
                    url_for("dashboard")
                )

        else:

            flash(
                "Invalid username or password.",
                "error"
            )

            return redirect(url_for("login"))

    return render_template("login.html")


# =========================================================
# STUDENT DASHBOARD
# =========================================================

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:

        flash(
            "Please log in to view that page.",
            "error"
        )

        return redirect(url_for("login"))

    # Do not allow supervisors or staff to use
    # the student dashboard.

    if session.get("role") == "supervisor":

        return redirect(
            url_for("supervisor.dashboard")
        )

    if session.get("role") == "staff":

        return redirect(
            url_for("staff.dashboard")
        )

    return render_template(
        "dashboard.html",
        username=session["username"]
    )

@app.route("/logout")
def logout():

    session.clear()

    flash(
        "You have been logged out.",
        "success"
    )

    return redirect(url_for("login"))

if __name__ == "__main__":

    app.run(debug=True)
