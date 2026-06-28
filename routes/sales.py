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

sales_bp = Blueprint("sales", __name__)

# ============================================
# SALE
# ============================================


@sales_bp.route("/sales")
@login_required
@roles_required(
    "Administrator",
    "Manager",
    "Cashier"
    "Store Keeper"
)
def sales():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            sales.id,
            products.name,
            sales.quantity,
            sales.selling_price,
            sales.customer_name,
            sales.sale_date
        FROM sales
        JOIN products
        ON sales.product_id = products.id
        ORDER BY sales.id DESC
    """)

    sales = cursor.fetchall()

    conn.close()

    return render_template(
        "sales.html",
        sales=sales
    )


@sales_bp.route("/export-sales")
def export_sales():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            sales.id,
            products.name,
            sales.quantity,
            sales.selling_price,
            sales.customer_name,
            sales.sale_date
        FROM sales
        JOIN products
            ON sales.product_id = products.id
        ORDER BY sales.sale_date DESC
    """)

    sales = cursor.fetchall()

    conn.close()

    def generate():

        yield "ID,Product,Quantity,Price,Customer,Date\n"

        for sale in sales:

            yield f"{sale[0]},{sale[1]},{sale[2]},{sale[3]},{sale[4]},{sale[5]}\n"

    return Response(
        generate(),
        mimetype="text/csv",
        headers={
            "Content-Disposition":
            "attachment; filename=sales.csv"
        }
    )


@sales_bp.route("/add-sale", methods=["GET", "POST"])
def add_sale():

    conn = get_connection()
    cursor = conn.cursor()

    if request.method == "POST":

        product_id = request.form["product_id"]
        quantity = int(request.form["quantity"])
        selling_price = request.form["selling_price"]
        customer_name = request.form["customer_name"]
        sale_date = request.form["sale_date"]

        cursor.execute(
            "SELECT stock FROM products WHERE id=?",
            (product_id,)
        )

        current_stock = cursor.fetchone()[0]

        if quantity > current_stock:

            conn.close()

            flash("Not enough stock available.", "danger")

            return redirect("/add-sale")

        cursor.execute("""
            INSERT INTO sales
            (
                product_id,
                quantity,
                selling_price,
                customer_name,
                sale_date
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            product_id,
            quantity,
            selling_price,
            customer_name,
            sale_date
        ))

        cursor.execute("""
            UPDATE products
            SET stock = stock - ?
            WHERE id = ?
        """, (
            quantity,
            product_id
        ))

        conn.commit()

        conn.close()

        flash("Sale recorded successfully!", "success")

        return redirect("/sales")

    cursor.execute("SELECT * FROM products")

    products = cursor.fetchall()

    conn.close()

    return render_template(
        "add_sale.html",
        products=products
    )

# ============================================
# DELETE SALE
# ============================================


@sales_bp.route("/delete-sale/<int:id>")
@login_required
@roles_required(
    "Administrator",
    "Manager"
)
def delete_sale(id):

    conn = get_connection()
    cursor = conn.cursor()

    # Get sale information
    cursor.execute("""
        SELECT product_id, quantity
        FROM sales
        WHERE id=?
    """, (id,))

    sale = cursor.fetchone()

    if not sale:

        conn.close()

        flash(
            "Sale not found.",
            "danger"
        )

        return redirect("/sales")

    product_id, quantity = sale

    # Restore stock
    cursor.execute("""
        UPDATE products
        SET stock = stock + ?
        WHERE id=?
    """, (
        quantity,
        product_id
    ))

    # Delete sale
    cursor.execute("""
        DELETE FROM sales
        WHERE id=?
    """, (id,))

    conn.commit()
    conn.close()

    flash(
        "Sale deleted successfully!",
        "success"
    )

    return redirect("/sales")
