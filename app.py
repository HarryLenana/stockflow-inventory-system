import os

from flask import (
    Flask,
    render_template
)

from database.models import (
    get_connection,
    create_tables,
    create_settings_table
)

from routes import register_routes

# ============================================
# FLASK APP
# ============================================

app = Flask(__name__)
app.secret_key = "stockflow_secret_key"

# ============================================
# UPLOADS
# ============================================

UPLOAD_FOLDER = "static/uploads/users"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ============================================
# REGISTER ROUTES
# ============================================

register_routes(app)

# ============================================
# CREATE DATABASE TABLES
# ============================================

create_tables()


# ============================================
# CREATE SETTINGS TABLE
# ============================================

create_tables()
create_settings_table()

# ============================================
# GLOBAL SETTINGS
# ============================================


@app.context_processor
def inject_settings():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT currency
        FROM settings
        LIMIT 1
    """)

    row = cursor.fetchone()

    conn.close()

    currency = "KES"

    if row and row[0]:
        currency = row[0]

    return dict(currency=currency)


# ============================================
# TEMPLATE FILTERS
# ============================================

@app.template_filter("currency")
def currency(value):

    try:
        return "{:,.2f}".format(float(value))
    except (ValueError, TypeError):
        return "0.00"


# ============================================
# ABOUT
# ============================================

@app.route("/about")
def about():

    conn = get_connection()
    cursor = conn.cursor()

    # --------------------------------
    # Products
    # --------------------------------
    cursor.execute("SELECT COUNT(*) FROM products")
    total_products = cursor.fetchone()[0]

    # --------------------------------
    # Suppliers
    # --------------------------------
    cursor.execute("SELECT COUNT(*) FROM suppliers")
    total_suppliers = cursor.fetchone()[0]

    # --------------------------------
    # Users
    # --------------------------------
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    # --------------------------------
    # Purchases
    # --------------------------------
    cursor.execute("SELECT COUNT(*) FROM purchases")
    total_purchases = cursor.fetchone()[0]

    # --------------------------------
    # Sales
    # --------------------------------
    cursor.execute("SELECT COUNT(*) FROM sales")
    total_sales = cursor.fetchone()[0]

    # --------------------------------
    # Revenue
    # --------------------------------
    cursor.execute("""
        SELECT COALESCE(
            SUM(quantity * selling_price),
            0
        )
        FROM sales
    """)

    total_revenue = cursor.fetchone()[0]

    # --------------------------------
    # Inventory Value
    # --------------------------------
    cursor.execute("""
        SELECT COALESCE(
            SUM(stock * price),
            0
        )
        FROM products
    """)

    inventory_value = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "about.html",
        total_products=total_products,
        total_suppliers=total_suppliers,
        total_users=total_users,
        total_purchases=total_purchases,
        total_sales=total_sales,
        total_revenue=total_revenue,
        inventory_value=inventory_value,
        version="2.0 Professional"
    )

# ============================================
# START APP
# ============================================


if __name__ == "__main__":
    app.run(debug=True)
