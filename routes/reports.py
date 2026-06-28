from flask import (
    Blueprint,
    render_template
)

from database.models import get_connection
from utils.decorators import (
    login_required,
    roles_required
)

reports_bp = Blueprint("reports", __name__)


@reports_bp.route("/reports")
@login_required
def reports():

    conn = get_connection()
    cursor = conn.cursor()

    # Total Products
    cursor.execute("SELECT COUNT(*) FROM products")
    total_products = cursor.fetchone()[0]

    # Total Suppliers
    cursor.execute("SELECT COUNT(*) FROM suppliers")
    total_suppliers = cursor.fetchone()[0]

    # Total Purchases
    cursor.execute("SELECT COUNT(*) FROM purchases")
    total_purchases = cursor.fetchone()[0]

    # Total Sales
    cursor.execute("SELECT COUNT(*) FROM sales")
    total_sales = cursor.fetchone()[0]

    # Revenue
    cursor.execute("""
        SELECT IFNULL(
            SUM(quantity * selling_price),
            0
        )
        FROM sales
    """)

    total_revenue = cursor.fetchone()[0]

    # Inventory Value
    cursor.execute("""
        SELECT IFNULL(
            SUM(stock * price),
            0
        )
        FROM products
    """)

    inventory_value = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "reports.html",
        total_products=total_products,
        total_suppliers=total_suppliers,
        total_purchases=total_purchases,
        total_sales=total_sales,
        total_revenue=total_revenue,
        inventory_value=inventory_value
    )
