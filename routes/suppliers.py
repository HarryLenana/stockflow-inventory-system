from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    session,
    flash,
    Response
)

from database.models import get_connection
from utils.decorators import (
    login_required,
    roles_required
)

suppliers_bp = Blueprint("suppliers", __name__)

# ============================================
# SUPPLIERS
# ============================================


@suppliers_bp.route("/suppliers")
@login_required
@roles_required("Administrator", "Manager")
def suppliers():

    if "user" not in session:
        return redirect("/")

    search = request.args.get("search", "")

    conn = get_connection()
    cursor = conn.cursor()

    if search:

        cursor.execute(
            "SELECT * FROM suppliers WHERE name LIKE ?",
            ('%' + search + '%',)
        )

    else:

        cursor.execute(
            "SELECT * FROM suppliers"
        )

    suppliers = cursor.fetchall()

    conn.close()

    return render_template(
        "suppliers.html",
        suppliers=suppliers
    )

# ============================================
# EXPORT SUPPLIERS
# ============================================


@suppliers_bp.route("/export-suppliers")
def export_suppliers():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            name,
            phone,
            email,
            address
        FROM suppliers
        ORDER BY name
    """)

    suppliers = cursor.fetchall()

    conn.close()

    def generate():

        yield "ID,Name,Phone,Email,Address\n"

        for supplier in suppliers:

            yield f"{supplier[0]},{supplier[1]},{supplier[2]},{supplier[3]},{supplier[4]}\n"

    return Response(
        generate(),
        mimetype="text/csv",
        headers={
            "Content-Disposition":
            "attachment; filename=suppliers.csv"
        }
    )

# ============================================
# ADD SUPPLIER
# ============================================


@suppliers_bp.route("/add-supplier", methods=["GET", "POST"])
@login_required
@roles_required("Administrator", "Manager")
def add_supplier():

    if "user" not in session:
        return redirect("/")

    conn = get_connection()
    cursor = conn.cursor()

    if request.method == "POST":

        name = request.form["name"]
        phone = request.form["phone"]
        email = request.form["email"]
        address = request.form["address"]

        cursor.execute("""
            INSERT INTO suppliers
            (
                name,
                phone,
                email,
                address
            )
            VALUES
            (
                ?, ?, ?, ?
            )
        """, (
            name,
            phone,
            email,
            address
        ))

        conn.commit()
        conn.close()

        flash(
            "Supplier added successfully!",
            "success"
        )

        return redirect("/suppliers")

    conn.close()

    return render_template("add_supplier.html")

# ============================================
# EDIT SUPPLIER
# ============================================


@suppliers_bp.route("/edit-supplier/<int:id>", methods=["GET", "POST"])
@login_required
@roles_required("Administrator", "Manager")
def edit_supplier(id):

    if "user" not in session:
        return redirect("/")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM suppliers
        WHERE id=?
    """, (id,))

    supplier = cursor.fetchone()

    if not supplier:

        conn.close()

        flash(
            "Supplier not found.",
            "danger"
        )

        return redirect("/suppliers")

    if request.method == "POST":

        name = request.form["name"]
        phone = request.form["phone"]
        email = request.form["email"]
        address = request.form["address"]

        cursor.execute("""
            UPDATE suppliers
            SET
                name=?,
                phone=?,
                email=?,
                address=?
            WHERE id=?
        """, (
            name,
            phone,
            email,
            address,
            id
        ))

        conn.commit()
        conn.close()

        flash(
            "Supplier updated successfully!",
            "success"
        )

        return redirect("/suppliers")

    conn.close()

    return render_template(
        "edit_supplier.html",
        supplier=supplier
    )

# ============================================
# DELETE SUPPLIER
# ============================================


@suppliers_bp.route("/delete-supplier/<int:id>")
@login_required
@roles_required("Administrator", "Manager")
def delete_supplier(id):

    if "user" not in session:
        return redirect("/")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM suppliers
        WHERE id=?
    """, (id,))

    conn.commit()
    conn.close()

    flash(
        "Supplier deleted successfully!",
        "success"
    )

    return redirect("/suppliers")
