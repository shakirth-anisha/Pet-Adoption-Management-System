import pymysql
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

LOG_FILE = "db_log.txt"

def log_message(message):
    with open(LOG_FILE, "a") as log:
        log.write(f"[{datetime.now()}] {message}\n")

def get_connection():
    """Return a pymysql connection."""
    return pymysql.connect(
        host="localhost",
        user="dbms_927",
        password="pes2ug23cs927",
        database="pet_adoption_db",
        cursorclass=pymysql.cursors.DictCursor
    )

def run_query(query, params=None, fetch=False):
    """Execute SQL query. Return fetched data if fetch=True."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params or ())
            data = cursor.fetchall() if fetch else None
        conn.commit()
        return data
    finally:
        conn.close()

def run_procedure(proc_name, params=None, fetch=True):
    """Call a stored procedure."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.callproc(proc_name, params or ())
            data = cursor.fetchall() if fetch else None
        conn.commit()
        return data
    finally:
        conn.close()
