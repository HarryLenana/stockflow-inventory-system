import sqlite3

DB_NAME = "database.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def create_tables():

    conn = get_connection()
    cursor = conn.cursor()

    # PRODUCTS

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        stock INTEGER NOT NULL,
        price REAL NOT NULL
    )
    """)

    # SUPPLIERS

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS suppliers(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT NOT NULL,
        email TEXT NOT NULL,
        address TEXT NOT NULL
    )
    """)

    # PURCHASES

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS purchases(
       id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        supplier_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        cost REAL NOT NULL,
        purchase_date TEXT NOT NULL
    )
    """)

    # SALES

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sales(
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       product_id INTEGER NOT NULL,
       quantity INTEGER NOT NULL,
       selling_price REAL NOT NULL,
       customer_name TEXT NOT NULL,
       sale_date TEXT NOT NULL
    )
    """)

    # USERS

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      username TEXT UNIQUE NOT NULL,
      password TEXT NOT NULL
    )
    """)

    # Create default admin account

    cursor.execute("""
    INSERT OR IGNORE INTO users
   (username, password)
    VALUES ('admin', 'admin123')
    """)

    conn.commit()
    conn.close()

# ============================================
# CREATE SETTINGS TABLE
# ============================================


def create_settings_table():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

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
            INSERT INTO settings (

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

            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (

            "StockFlow Ltd",
            "",
            "",
            "",
            "",
            "KES",
            16,
            10,
            0,
            1,
            1,
            1,
            1

        ))

    conn.commit()
    conn.close()
