from flask import flash

import os
import shutil
import sqlite3
import platform
import flask
from datetime import datetime
from flask import send_file

import csv
from flask import Response
from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import session

import sqlite3

from database.models import create_tables


def create_settings_table():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS settings(

        id INTEGER PRIMARY KEY,

        company_name TEXT,

        company_email TEXT,

        company_phone TEXT,

        company_address TEXT,

        company_website TEXT,

        currency TEXT,

        tax_rate REAL,

        low_stock INTEGER,

        dark_mode INTEGER,

        email_alerts INTEGER,

        sales_alerts INTEGER,

        purchase_alerts INTEGER,

        stock_alerts INTEGER

    )
    """)

    cursor.execute("SELECT COUNT(*) FROM settings")

    if cursor.fetchone()[0] == 0:

        cursor.execute("""
        INSERT INTO settings(

            company_name,
            company_email,
            company_phone,
            company_address,
            company_website,
            currency,
            tax_rate,
            low_stock,
            dark_mode,
            email_alerts,
            sales_alerts,
            purchase_alerts,
            stock_alerts

        )

        VALUES(

            'StockFlow Ltd',
            '',
            '',
            '',
            '',
            'KES',
            16,
            10,
            0,
            1,
            1,
            1,
            1

        )
        """)

    conn.commit()
    conn.close()


create_settings_table()

app = Flask(__name__)
app.secret_key = "stockflow_secret_key"

create_tables()


@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("""
        SELECT * FROM users
        WHERE username=? AND password=?
        """, (username, password))

        user = cursor.fetchone()

        conn.close()

        if user:

            session["user"] = username

            return redirect("/dashboard")

        return render_template(
            "login.html",
            error="Invalid username or password"
        )

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # ==========================
    # Total Products
    # ==========================

    cursor.execute("SELECT COUNT(*) FROM products")
    total_products = cursor.fetchone()[0]

    # ==========================
    # Low Stock
    # ==========================

    cursor.execute(
        "SELECT COUNT(*) FROM products WHERE stock < 10"
    )
    low_stock = cursor.fetchone()[0]

    # ==========================
    # Low Stock Products
    # ==========================

    cursor.execute("""
        SELECT name, stock
        FROM products
        WHERE stock < 10
        ORDER BY stock ASC
    """)
    low_stock_products = cursor.fetchall()

    # ==========================
    # Recent Products
    # ==========================

    cursor.execute("""
        SELECT *
        FROM products
        ORDER BY id DESC
        LIMIT 5
    """)
    recent_products = cursor.fetchall()

    # ==========================
    # Total Revenue
    # ==========================

    cursor.execute("""
        SELECT IFNULL(
            SUM(quantity * selling_price),
            0
        )
        FROM sales
    """)
    total_revenue = cursor.fetchone()[0]

    # ==========================
    # Inventory Value
    # ==========================

    cursor.execute("""
        SELECT IFNULL(
            SUM(stock * price),
            0
        )
        FROM products
    """)
    inventory_value = cursor.fetchone()[0]

    # ==========================
    # Recent Sales
    # ==========================

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

    # ==========================
    # Recent Purchases
    # ==========================

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

    # ==========================
    # Today's Revenue
    # ==========================

    from datetime import date

    today = date.today().strftime("%Y-%m-%d")

    cursor.execute("""
        SELECT IFNULL(
            SUM(quantity * selling_price),
            0
        )
        FROM sales
        WHERE sale_date = ?
    """, (today,))

    today_sales = cursor.fetchone()[0]

    # ==========================
    # Total Orders
    # ==========================

    cursor.execute("SELECT COUNT(*) FROM sales")
    total_orders = cursor.fetchone()[0]

    # ==========================
    # Today's Orders
    # ==========================

    cursor.execute("""
        SELECT COUNT(*)
        FROM sales
        WHERE sale_date = ?
    """, (today,))

    today_orders = cursor.fetchone()[0]

    # ==========================
    # Top Selling Product
    # ==========================

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

    conn.close()

    return render_template(
        "dashboard.html",
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
        top_product=top_product,
    )


@app.route("/settings", methods=["GET", "POST"])
def settings():

    if "user" not in session:
        return redirect("/")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    if request.method == "POST":

        # ==========================
        # SAVE SETTINGS
        # ==========================

        cursor.execute("""
            UPDATE settings
            SET
                company_name=?,
                company_email=?,
                company_phone=?,
                company_address=?,
                company_website=?,
                currency=?,
                tax_rate=?,
                low_stock=?,
                dark_mode=?,
                email_alerts=?,
                sales_alerts=?,
                purchase_alerts=?,
                stock_alerts=?
            WHERE id=1
        """, (

            request.form["company_name"],
            request.form["company_email"],
            request.form["company_phone"],
            request.form["company_address"],
            request.form["company_website"],
            request.form["currency"],
            request.form["tax_rate"],
            request.form["low_stock"],

            1 if request.form.get("dark_mode") else 0,
            1 if request.form.get("email_alerts") else 0,
            1 if request.form.get("sales_alerts") else 0,
            1 if request.form.get("purchase_alerts") else 0,
            1 if request.form.get("stock_alerts") else 0

        ))

        conn.commit()

        # ==========================
        # CHANGE PASSWORD
        # ==========================

        current_password = request.form.get("current_password")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        if current_password and new_password and confirm_password:

            cursor.execute("""
                SELECT password
                FROM users
                WHERE username=?
            """, (session["user"],))

            user = cursor.fetchone()

            if user:

                if user[0] != current_password:

                    flash(
                        "Current password is incorrect.",
                        "danger"
                    )

                elif new_password != confirm_password:

                    flash(
                        "New passwords do not match.",
                        "danger"
                    )

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

        else:

            flash(
                "Settings saved successfully!",
                "success"
            )

    # ==========================
    # LOAD SETTINGS
    # ==========================

    cursor.execute("SELECT * FROM settings")
    settings = cursor.fetchone()

    system_info = {

        "python": platform.python_version(),
        "flask": flask.__version__,
        "database": "SQLite",
        "os": platform.system(),
        "time": datetime.now().strftime("%d %B %Y %H:%M")

    }

    conn.close()

    return render_template(

        "settings.html",

        settings=settings,

        system_info=system_info

    )


@app.route("/backup")
def backup_database():

    if "user" not in session:
        return redirect("/")

    backup_folder = "backups"

    os.makedirs(backup_folder, exist_ok=True)

    filename = datetime.now().strftime(
        "backup_%Y%m%d_%H%M%S.db"
    )

    destination = os.path.join(
        backup_folder,
        filename
    )

    shutil.copy(
        "database.db",
        destination
    )

    return send_file(
        destination,
        as_attachment=True
    )


@app.route("/restore")
def restore_database():

    if "user" not in session:
        return redirect("/")

    return """
    <h2>
    Restore Database Feature Coming Soon
    </h2>

    <a href="/settings">
    Back
    </a>
    """


@app.route("/system-info")
def system_info():

    if "user" not in session:
        return redirect("/")

    return {

        "Python": platform.python_version(),

        "Flask": flask.__version__,

        "Database": "SQLite",

        "Operating System": platform.system()

    }


@app.route("/profile", methods=["GET", "POST"])
def profile():

    if "user" not in session:
        return redirect("/")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # ==========================
    # SAVE PROFILE
    # ==========================
    if request.method == "POST":

        full_name = request.form["full_name"]
        email = request.form["email"]
        phone = request.form["phone"]

        cursor.execute("""
            UPDATE users
            SET
                full_name = ?,
                email = ?,
                phone = ?
            WHERE username = ?
        """, (
            full_name,
            email,
            phone,
            session["user"]
        ))

        conn.commit()

    # ==========================
    # LOAD USER
    # ==========================
    cursor.execute("""
        SELECT *
        FROM users
        WHERE username = ?
    """, (session["user"],))

    user = cursor.fetchone()

    conn.close()

    return render_template(
        "profile.html",
        user=user
    )


@app.route("/add-product", methods=["GET", "POST"])
def add_product(id):

    if request.method == "POST":

        name = request.form["name"]
        category = request.form["category"]
        stock = request.form["stock"]
        price = request.form["price"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO products
        (name, category, stock, price)
        VALUES (?, ?, ?, ?)
        """, (name, category, stock, price))

        conn.commit()
        conn.close()

        return redirect("/products")

    return render_template("add_product.html")


@app.route("/edit-product/<int:id>", methods=["GET", "POST"])
def edit_product(id):

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    if request.method == "POST":

        name = request.form["name"]
        category = request.form["category"]
        stock = request.form["stock"]
        price = request.form["price"]

        cursor.execute("""
        UPDATE products
        SET name=?, category=?, stock=?, price=?
        WHERE id=?
        """, (name, category, stock, price, id))

        conn.commit()
        conn.close()

        return redirect("/products")

    cursor.execute(
        "SELECT * FROM products WHERE id=?",
        (id,)
    )

    product = cursor.fetchone()

    conn.close()

    return render_template(
        "edit_product.html",
        product=product
    )


@app.route("/delete-product/<int:id>")
def delete_product(id):

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM products WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/products")

# ==========================
# SUPPLIERS
# ==========================


@app.route("/suppliers")
def suppliers():

    if "user" not in session:
        return redirect("/")

    search = request.args.get("search", "")

    conn = sqlite3.connect("database.db")
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


@app.route("/add-supplier", methods=["GET", "POST"])
def add_supplier():

    if request.method == "POST":

        name = request.form["name"]
        phone = request.form["phone"]
        email = request.form["email"]
        address = request.form["address"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO suppliers
        (name, phone, email, address)
        VALUES (?, ?, ?, ?)
        """, (name, phone, email, address))

        conn.commit()
        conn.close()

        return redirect("/suppliers")

    return render_template("add_supplier.html")


@app.route("/edit-supplier/<int:id>", methods=["GET", "POST"])
def edit_supplier(id):

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    if request.method == "POST":

        name = request.form["name"]
        phone = request.form["phone"]
        email = request.form["email"]
        address = request.form["address"]

        cursor.execute("""
        UPDATE suppliers
        SET name=?, phone=?, email=?, address=?
        WHERE id=?
        """, (name, phone, email, address, id))

        conn.commit()
        conn.close()

        return redirect("/suppliers")

    cursor.execute(
        "SELECT * FROM suppliers WHERE id=?",
        (id,)
    )

    supplier = cursor.fetchone()

    conn.close()

    return render_template(
        "edit_supplier.html",
        supplier=supplier
    )


@app.route("/delete-supplier/<int:id>")
def delete_supplier(id):

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM suppliers WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/suppliers")

# ==========================
# PURCHASES
# ==========================


@app.route("/purchases")
def purchases():

    if "user" not in session:
        return redirect("/")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT purchases.id,
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


@app.route("/add-purchase", methods=["GET", "POST"])
def add_purchase():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    if request.method == "POST":

        product_id = request.form["product_id"]
        supplier_id = request.form["supplier_id"]
        quantity = int(request.form["quantity"])
        cost = request.form["cost"]
        purchase_date = request.form["purchase_date"]

        cursor.execute("""
        INSERT INTO purchases
        (product_id, supplier_id, quantity, cost, purchase_date)
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
        conn.close()

        return redirect("/purchases")

    cursor.execute(
        "SELECT * FROM products"
    )
    products = cursor.fetchall()

    cursor.execute(
        "SELECT * FROM suppliers"
    )
    suppliers = cursor.fetchall()

    conn.close()

    return render_template(
        "add_purchase.html",
        products=products,
        suppliers=suppliers
    )
# ==========================
# SALES
# ==========================


@app.route("/sales")
def sales():

    if "user" not in session:
        return redirect("/")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT sales.id,
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


@app.route("/add-sale", methods=["GET", "POST"])
def add_sale():

    conn = sqlite3.connect("database.db")
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

            return """
            <h2>Not enough stock available.</h2>
            <a href='/add-sale'>Go Back</a>
            """

        cursor.execute("""
        INSERT INTO sales
        (product_id, quantity, selling_price,
         customer_name, sale_date)
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

        return redirect("/sales")

    cursor.execute(
        "SELECT * FROM products"
    )

    products = cursor.fetchall()

    conn.close()

    return render_template(
        "add_sale.html",
        products=products
    )
# ==========================
# REPORTS
# ==========================


@app.route("/reports")
def reports():

    if "user" not in session:
        return redirect("/")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # Total Products

    cursor.execute(
        "SELECT COUNT(*) FROM products"
    )
    total_products = cursor.fetchone()[0]

    # Total Suppliers

    cursor.execute(
        "SELECT COUNT(*) FROM suppliers"
    )
    total_suppliers = cursor.fetchone()[0]

    # Total Purchases

    cursor.execute(
        "SELECT COUNT(*) FROM purchases"
    )
    total_purchases = cursor.fetchone()[0]

    # Total Sales

    cursor.execute(
        "SELECT COUNT(*) FROM sales"
    )
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


@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")

# ==========================
# EXPORT PRODUCTS CSV
# ==========================


@app.route("/export-products")
def export_products():

    if "user" not in session:
        return redirect("/")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM products"
    )

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


@app.route("/export-suppliers")
def export_suppliers():

    if "user" not in session:
        return redirect("/")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM suppliers"
    )

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


@app.route("/export-purchases")
def export_purchases():

    if "user" not in session:
        return redirect("/")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT purchases.id,
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


@app.route("/export-sales")
def export_sales():

    if "user" not in session:
        return redirect("/")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT sales.id,
           products.name,
           sales.quantity,
           sales.selling_price,
           sales.customer_name,
           sales.sale_date
    FROM sales
    JOIN products
    ON sales.product_id = products.id
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


@app.route("/about")
def about():
    return render_template("about.html")


if __name__ == "__main__":
    app.run(debug=True)
