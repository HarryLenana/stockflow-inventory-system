import os
import sqlite3
import psycopg2

DATABASE_URL = os.environ.get("DATABASE_URL")


def get_connection():

    if DATABASE_URL:
        return psycopg2.connect(DATABASE_URL)

    return sqlite3.connect("database.db")
