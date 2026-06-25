import csv
from flask import Response
from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import session

import sqlite3

from database.models import create_tables

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

    # Total Products

    cursor.execute(
        "SELECT COUNT(*) FROM products"
    )
    total_products = cursor.fetchone()[0]

    # Low Stock Products

    cursor.execute(
        "SELECT COUNT(*) FROM products WHERE stock < 10"
    )
    low_stock = cursor.fetchone()[0]

    # Recent Products

    cursor.execute("""
        SELECT *
        FROM products
        ORDER BY id DESC
        LIMIT 5
    """)
    recent_products = cursor.fetchall()

    # Total Revenue

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

    # Recent Sales

    cursor.execute("""
    SELECT products.name,
           sales.quantity,
           sales.sale_date
    FROM sales
    JOIN products
    ON sales.product_id = products.id
    ORDER BY sales.id DESC
    LIMIT 5
    """)
    recent_sales = cursor.fetchall()

    # Recent Purchases

    cursor.execute("""
    SELECT products.name,
           purchases.quantity,
           purchases.purchase_date
    FROM purchases
    JOIN products
    ON purchases.product_id = products.id
    ORDER BY purchases.id DESC
    LIMIT 5
    """)
    recent_purchases = cursor.fetchall()

    conn.close()

    return render_template(
        "dashboard.html",
        total_products=total_products,
        low_stock=low_stock,
        recent_products=recent_products,
        recent_sales=recent_sales,
        recent_purchases=recent_purchases,
        total_revenue=total_revenue,
        inventory_value=inventory_value
    )


@app.route("/products")
def products():

    if "user" not in session:
        return redirect("/")

    search = request.args.get("search", "")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    if search:

        cursor.execute(
            "SELECT * FROM products WHERE name LIKE ?",
            ('%' + search + '%',)
        )

    else:

        cursor.execute(
            "SELECT * FROM products"
        )

    products = cursor.fetchall()

    conn.close()

    return render_template(
        "products.html",
        products=products
    )


@app.route("/add-product", methods=["GET", "POST"])
def add_product():

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


if __name__ == "__main__":
    app.run(debug=True)
