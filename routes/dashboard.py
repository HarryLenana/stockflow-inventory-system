from datetime import datetime

from flask import (
    Blueprint,
    render_template,
    session,
    redirect
)

from database.models import get_connection
from utils.decorators import login_required

dashboard_bp = Blueprint("dashboard", __name__)

# ============================================
# DASHBOARD
# ============================================


@dashboard_bp.route("/dashboard")
@login_required
def dashboard():

    if "user" not in session:
        return redirect("/")

    conn = get_connection()
    cursor = conn.cursor()

    # -----------------------
    # Total Products
    # -----------------------

    cursor.execute("SELECT COUNT(*) FROM products")
    total_products = cursor.fetchone()[0]

    # -----------------------
    # Low Stock
    # -----------------------

    cursor.execute("""
        SELECT COUNT(*)
        FROM products
        WHERE stock < 10
    """)

    low_stock = cursor.fetchone()[0]

    # -----------------------
    # Low Stock Products
    # -----------------------

    cursor.execute("""
        SELECT name, stock
        FROM products
        WHERE stock < 10
        ORDER BY stock ASC
    """)

    low_stock_products = cursor.fetchall()

    # -----------------------
    # Recent Products
    # -----------------------

    cursor.execute("""
        SELECT *
        FROM products
        ORDER BY id DESC
        LIMIT 5
    """)

    recent_products = cursor.fetchall()

    # -----------------------
    # Total Revenue
    # -----------------------

    cursor.execute("""
        SELECT COALESCE(
            SUM(quantity * selling_price),
            0
        )
        FROM sales
    """)

    total_revenue = cursor.fetchone()[0]

    # -----------------------
    # Inventory Value
    # -----------------------

    cursor.execute("""
        SELECT COALESCE(
            SUM(stock * price),
            0
        )
        FROM products
    """)

    inventory_value = cursor.fetchone()[0]

    # -----------------------
    # Recent Sales
    # -----------------------

    cursor.execute("""
        SELECT
            products.name,
            sales.quantity,
            sales.sale_date
        FROM sales
        JOIN products
        ON sales.product_id = products.id
        ORDER BY sales.id DESC
        LIMIT 5
    """)

    recent_sales = cursor.fetchall()

    # -----------------------
    # Recent Purchases
    # -----------------------

    cursor.execute("""
        SELECT
            products.name,
            purchases.quantity,
            purchases.purchase_date
        FROM purchases
        JOIN products
        ON purchases.product_id = products.id
        ORDER BY purchases.id DESC
        LIMIT 5
    """)

    recent_purchases = cursor.fetchall()

    # -----------------------
    # Today's Revenue
    # -----------------------

    today = datetime.now().strftime("%Y-%m-%d")

    cursor.execute("""
        SELECT COALESCE(
            SUM(quantity * selling_price),
            0
        )
        FROM sales
        WHERE sale_date=?
    """, (today,))

    today_sales = cursor.fetchone()[0]

    # -----------------------
    # Total Orders
    # -----------------------

    cursor.execute("SELECT COUNT(*) FROM sales")
    total_orders = cursor.fetchone()[0]

    # -----------------------
    # Today's Orders
    # -----------------------

    cursor.execute("""
        SELECT COUNT(*)
        FROM sales
        WHERE sale_date=?
    """, (today,))

    today_orders = cursor.fetchone()[0]

    # -----------------------
    # Top Selling Product
    # -----------------------

    cursor.execute("""
        SELECT
            products.name,
            SUM(sales.quantity) AS sold
        FROM sales
        JOIN products
        ON sales.product_id = products.id
        GROUP BY products.name
        ORDER BY sold DESC
        LIMIT 1
    """)

    top_product = cursor.fetchone()

    cursor.execute("""
        SELECT *
        FROM users
        WHERE username=?
    """, (session["user"],))

    user = cursor.fetchone()

    conn.close()

    return render_template(
        "dashboard.html",
        user=user,
        total_products=total_products,
        low_stock=low_stock,
        low_stock_products=low_stock_products,
        recent_products=recent_products,
        recent_sales=recent_sales,
        recent_purchases=recent_purchases,
        total_revenue=total_revenue,
        inventory_value=inventory_value,
        today_sales=today_sales,
        total_orders=total_orders,
        today_orders=today_orders,
        top_product=top_product
    )
