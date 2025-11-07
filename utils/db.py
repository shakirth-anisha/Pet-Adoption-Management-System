import pymysql
from datetime import datetime
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

LOG_FILE = "db_log.txt"

def log_message(message):
    """Append timestamped messages to the log file."""
    with open(LOG_FILE, "a") as log:
        log.write(f"[{datetime.now()}] {message}\n")

def get_connection():
    """Return a pymysql connection using environment variables."""
    return pymysql.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        database=os.getenv("DB_NAME"),
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
