import os

from werkzeug.utils import secure_filename
from database.models import get_connection
from utils.decorators import login_required
from flask import (
    render_template,
    request,
    redirect,
    session,
    flash
)
from flask import Blueprint

from flask import current_app

auth = Blueprint("auth", __name__)


# ============================================
# LOGIN
# ============================================

@auth.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM users
            WHERE username=?
            AND password=?
        """, (username, password))

        user = cursor.fetchone()

        conn.close()

        if user:

            session["user"] = user[1]
            session["role"] = user[7]

            return redirect("/dashboard")

        return render_template(
            "login.html",
            error="Invalid username or password."
        )

    return render_template("login.html")

# ============================================
# LOGOUT
# ============================================


@auth.route("/logout")
@login_required
def logout():

    session.clear()

    flash("You have been logged out successfully.", "success")

    return redirect("/")


# ============================================
# PROFILE
# ============================================


@auth.route("/profile", methods=["GET", "POST"])
@login_required
def profile():

    if "user" not in session:
        return redirect("/")

    conn = get_connection()
    cursor = conn.cursor()

    if request.method == "POST":

        full_name = request.form["full_name"]
        email = request.form["email"]
        phone = request.form["phone"]

        cursor.execute("""
            UPDATE users
            SET
                full_name=?,
                email=?,
                phone=?
            WHERE username=?
        """, (

            full_name,
            email,
            phone,
            session["user"]

        ))

        conn.commit()

        flash(
            "Profile updated successfully.",
            "success"
        )

    cursor.execute("""
        SELECT *
        FROM users
        WHERE username=?
    """, (session["user"],))

    user = cursor.fetchone()

    conn.close()

    return render_template(
        "profile.html",
        user=user
    )

# ============================================
# CHANGE PASSWORD
# ============================================


@auth.route("/change-password", methods=["GET", "POST"])
def change_password():

    if "user" not in session:
        return redirect("/")

    conn = get_connection()
    cursor = conn.cursor()

    if request.method == "POST":

        current_password = request.form["current_password"]
        new_password = request.form["new_password"]
        confirm_password = request.form["confirm_password"]

        cursor.execute("""
            SELECT password
            FROM users
            WHERE username=?
        """, (session["user"],))

        user = cursor.fetchone()

        if not user:

            flash("User not found.", "danger")

        elif user[0] != current_password:

            flash("Current password is incorrect.", "danger")

        elif new_password != confirm_password:

            flash("New passwords do not match.", "danger")

        else:

            cursor.execute("""
                UPDATE users
                SET password=?
                WHERE username=?
            """, (
                new_password,
                session["user"]
            ))

            conn.commit()

            flash(
                "Password changed successfully!",
                "success"
            )

            conn.close()

            return redirect("/profile")

    conn.close()

    return render_template("change_password.html")


# ============================================
# UPLOAD PROFILE PICTURE
# ============================================

@auth.route("/upload-profile-picture", methods=["GET", "POST"])
def upload_profile_picture():

    if "user" not in session:
        return redirect("/")

    conn = get_connection()
    cursor = conn.cursor()

    if request.method == "POST":

        picture = request.files.get("profile_picture")

        if picture is None:

            flash(
                "No file selected.",
                "danger"
            )

            conn.close()
            return redirect("/upload-profile-picture")

        if picture.filename == "":

            flash(
                "Please choose an image.",
                "danger"
            )

            conn.close()
            return redirect("/upload-profile-picture")

        filename = secure_filename(picture.filename)

        picture.save(
            os.path.join(
                current_app.config["UPLOAD_FOLDER"],
                filename
            )
        )

        cursor.execute("""
            UPDATE users
            SET profile_picture=?
            WHERE username=?
        """, (
            filename,
            session["user"]
        ))

        conn.commit()

        conn.close()

        flash(
            "Profile picture updated successfully!",
            "success"
        )

        return redirect("/profile")

    conn.close()

    return render_template("upload_profile_picture.html")
