from datetime import datetime
import os

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    session,
    flash,
    current_app
)

from werkzeug.utils import secure_filename

from database.models import get_connection
from utils.decorators import (
    login_required,
    roles_required
)

users_bp = Blueprint("users", __name__)


# ============================================
# USER MANAGEMENT
# ============================================


@users_bp.route("/users")
@login_required
@roles_required("Administrator")
def users():

    if "user" not in session:
        return redirect("/")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            full_name,
            username,
            email,
            phone,
            role,
            profile_picture,
            created_at
        FROM users
        ORDER BY full_name
    """)

    users = cursor.fetchall()

    conn.close()

    return render_template(
        "users.html",
        users=users
    )


# ============================================
# ADD USER
# ============================================

@users_bp.route("/add-user", methods=["GET", "POST"])
@login_required
@roles_required("Administrator")
def add_user():

    if "user" not in session:
        return redirect("/")

    conn = get_connection()
    cursor = conn.cursor()

    if request.method == "POST":

        full_name = request.form["full_name"]
        username = request.form["username"]
        password = request.form["password"]
        email = request.form["email"]
        phone = request.form["phone"]
        role = request.form["role"]

        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:?")

        cursor.execute("""
            SELECT id
            FROM users
            WHERE username=?
        """, (username,))

        existing = cursor.fetchone()

        if existing:

            flash(
                "Username already exists.",
                "danger"
            )

        else:

            cursor.execute("""
                INSERT INTO users
                (
                    username,
                    password,
                    full_name,
                    email,
                    phone,
                    role,
                    created_at
                )

                VALUES
                (
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?
                )
            """, (

                username,
                password,
                full_name,
                email,
                phone,
                role,
                created_at

            ))

            conn.commit()

            flash(
                "User created successfully!",
                "success"
            )

            conn.close()

            return redirect("/users")

    conn.close()

    return render_template("add_user.html")


# ============================================
# EDIT USER
# ============================================

@users_bp.route("/edit-user/<int:user_id>", methods=["GET", "POST"])
@login_required
@roles_required("Administrator")
def edit_user(user_id):

    if "user" not in session:
        return redirect("/")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM users
        WHERE id=?
    """, (user_id,))

    user = cursor.fetchone()

    if not user:

        conn.close()

        flash(
            "User not found.",
            "danger"
        )

        return redirect("/users")

    if request.method == "POST":

        full_name = request.form["full_name"]
        username = request.form["username"]
        email = request.form["email"]
        phone = request.form["phone"]
        role = request.form["role"]

        filename = user[6]

        picture = request.files.get("profile_picture")

        if picture and picture.filename != "":

            filename = secure_filename(
                picture.filename
            )

            picture.save(
                os.path.join(
                    current_app.config["UPLOAD_FOLDER"],
                    filename
                )
            )

        cursor.execute("""
            UPDATE users
            SET
                full_name=?,
                username=?,
                email=?,
                phone=?,
                role=?,
                profile_picture=?
            WHERE id=?
        """, (

            full_name,
            username,
            email,
            phone,
            role,
            filename,
            user_id

        ))

        conn.commit()

        conn.close()

        flash(
            "User updated successfully.",
            "success"
        )

        return redirect("/users")

    conn.close()

    return render_template(
        "edit_user.html",
        user=user
    )


# ============================================
# DELETE USER
# ============================================

@users_bp.route("/delete-user/<int:user_id>")
@login_required
@roles_required("Administrator")
def delete_user(user_id):

    if "user" not in session:
        return redirect("/")

    if user_id == 1:

        flash(
            "The main administrator cannot be deleted.",
            "danger"
        )

        return redirect("/users")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM users
        WHERE id=?
    """, (user_id,))

    conn.commit()

    conn.close()

    flash(
        "User deleted successfully.",
        "success"
    )

    return redirect("/users")
