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

products_bp = Blueprint("products", __name__)


# ============================================
# PRODUCTS
# ============================================


@products_bp.route("/products")
@login_required
@roles_required("Administrator", "Manager", "Store Keeper")
def products():
    if "user" not in session:
        return redirect("/")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM products
        ORDER BY name
    """)

    products = cursor.fetchall()

    conn.close()

    return render_template(
        "products.html",
        products=products
    )


@products_bp.route("/export-products")
def export_products():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            name,
            category,
            stock,
            price
        FROM products
        ORDER BY name
    """)

    products = cursor.fetchall()

    conn.close()

    def generate():

        yield "ID,Name,Category,Stock,Price\n"

        for product in products:

            yield f"{product[0]},{product[1]},{product[2]},{product[3]},{product[4]}\n"

    return Response(
        generate(),
        mimetype="text/csv",
        headers={
            "Content-Disposition":
            "attachment; filename=products.csv"
        }
    )


# ============================================
# ADD PRODUCT
# ============================================

@products_bp.route("/add-product", methods=["GET", "POST"])
@login_required
def add_product():

    if "user" not in session:
        return redirect("/")

    if request.method == "POST":

        name = request.form["name"]
        category = request.form["category"]
        stock = request.form["stock"]
        price = request.form["price"]

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO products
            (
                name,
                category,
                stock,
                price
            )
            VALUES
            (
                ?,
                ?,
                ?,
                ?
            )
        """, (
            name,
            category,
            stock,
            price
        ))

        conn.commit()
        conn.close()

        flash(
            "Product added successfully!",
            "success"
        )

        return redirect("/products")

    return render_template("add_product.html")


# ============================================
# EDIT PRODUCT
# ============================================

@products_bp.route("/edit-product/<int:id>", methods=["GET", "POST"])
def edit_product(id):

    if "user" not in session:
        return redirect("/")

    conn = get_connection()
    cursor = conn.cursor()

    if request.method == "POST":

        name = request.form["name"]
        category = request.form["category"]
        stock = request.form["stock"]
        price = request.form["price"]

        cursor.execute("""
            UPDATE products
            SET
                name=?,
                category=?,
                stock=?,
                price=?
            WHERE id=?
        """, (
            name,
            category,
            stock,
            price,
            id
        ))

        conn.commit()
        conn.close()

        flash(
            "Product updated successfully!",
            "success"
        )

        return redirect("/products")

    cursor.execute("""
        SELECT *
        FROM products
        WHERE id=?
    """, (id,))

    product = cursor.fetchone()

    conn.close()

    if not product:

        flash(
            "Product not found.",
            "danger"
        )

        return redirect("/products")

    return render_template(
        "edit_product.html",
        product=product
    )


# ============================================
# DELETE PRODUCT
# ============================================

@products_bp.route("/delete-product/<int:id>")
def delete_product(id):

    if "user" not in session:
        return redirect("/")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM products
        WHERE id=?
    """, (id,))

    conn.commit()
    conn.close()

    flash(
        "Product deleted successfully!",
        "success"
    )

    return redirect("/products")
