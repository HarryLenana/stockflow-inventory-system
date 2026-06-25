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
