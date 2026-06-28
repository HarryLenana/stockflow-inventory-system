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

purchases_bp = Blueprint("purchases", __name__)


# ============================================
# PURCHASES
# ============================================


@purchases_bp.route("/purchases")
@login_required
@roles_required("Administrator", "Manager", "Store Keeper")
def purchases():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            purchases.id,
            products.name,
            suppliers.name,
            purchases.quantity,
            purchases.cost,
            purchases.purchase_date
        FROM purchases
        JOIN products
        ON purchases.product_id = products.id
        JOIN suppliers
        ON purchases.supplier_id = suppliers.id
        ORDER BY purchases.id DESC
    """)

    purchases = cursor.fetchall()

    conn.close()

    return render_template(
        "purchases.html",
        purchases=purchases
    )


@purchases_bp.route("/export-purchases")
def export_purchases():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            purchases.id,
            products.name,
            suppliers.name,
            purchases.quantity,
            purchases.cost,
            purchases.purchase_date
        FROM purchases
        JOIN products
            ON purchases.product_id = products.id
        JOIN suppliers
            ON purchases.supplier_id = suppliers.id
        ORDER BY purchases.purchase_date DESC
    """)

    purchases = cursor.fetchall()

    conn.close()

    def generate():

        yield "ID,Product,Supplier,Quantity,Cost,Date\n"

        for purchase in purchases:

            yield f"{purchase[0]},{purchase[1]},{purchase[2]},{purchase[3]},{purchase[4]},{purchase[5]}\n"

    return Response(
        generate(),
        mimetype="text/csv",
        headers={
            "Content-Disposition":
            "attachment; filename=purchases.csv"
        }
    )


@purchases_bp.route("/add-purchase", methods=["GET", "POST"])
def add_purchase():

    conn = get_connection()
    cursor = conn.cursor()

    if request.method == "POST":

        product_id = request.form["product_id"]
        supplier_id = request.form["supplier_id"]
        quantity = int(request.form["quantity"])
        cost = request.form["cost"]
        purchase_date = request.form["purchase_date"]

        cursor.execute("""
            INSERT INTO purchases
            (
                product_id,
                supplier_id,
                quantity,
                cost,
                purchase_date
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            product_id,
            supplier_id,
            quantity,
            cost,
            purchase_date
        ))

        cursor.execute("""
            UPDATE products
            SET stock = stock + ?
            WHERE id = ?
        """, (
            quantity,
            product_id
        ))

        conn.commit()

        flash(
            "Purchase added successfully!",
            "success"
        )

        conn.close()

        return redirect("/purchases")

    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()

    cursor.execute("SELECT * FROM suppliers")
    suppliers = cursor.fetchall()

    conn.close()

    return render_template(
        "add_purchase.html",
        products=products,
        suppliers=suppliers
    )

# ============================================
# DELETE PURCHASE
# ============================================


@purchases_bp.route("/delete-purchase/<int:id>")
@login_required
@roles_required("Administrator", "Manager")
def delete_purchase(id):

    conn = get_connection()
    cursor = conn.cursor()

    # Get purchase quantity and product
    cursor.execute("""
        SELECT product_id, quantity
        FROM purchases
        WHERE id=?
    """, (id,))

    purchase = cursor.fetchone()

    if not purchase:

        conn.close()

        flash(
            "Purchase not found.",
            "danger"
        )

        return redirect("/purchases")

    product_id, quantity = purchase

    # Reduce stock
    cursor.execute("""
        UPDATE products
        SET stock = stock - ?
        WHERE id=?
    """, (
        quantity,
        product_id
    ))

    # Delete purchase
    cursor.execute("""
        DELETE FROM purchases
        WHERE id=?
    """, (id,))

    conn.commit()
    conn.close()

    flash(
        "Purchase deleted successfully!",
        "success"
    )

    return redirect("/purchases")
