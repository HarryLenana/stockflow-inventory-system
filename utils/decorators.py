from functools import wraps
from flask import session, redirect, flash

from database.models import get_connection

# ==========================
# LOGIN REQUIRED
# ==========================


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        if "user" not in session:
            return redirect("/")

        return f(*args, **kwargs)

    return decorated_function


# ==========================
# ROLE REQUIRED
# ==========================

def roles_required(*roles):
    def decorator(f):

        @wraps(f)
        def decorated_function(*args, **kwargs):

            if "user" not in session:
                return redirect("/")

            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT role
                FROM users
                WHERE username=?
            """, (session["user"],))

            user = cursor.fetchone()

            conn.close()

            if not user:
                session.clear()
                return redirect("/")

            if user[0] not in roles:

                flash(
                    "You do not have permission to access this page.",
                    "danger"
                )

                return redirect("/dashboard")

            return f(*args, **kwargs)

        return decorated_function

    return decorator
