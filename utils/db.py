import pymysql
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

LOG_FILE = "db_log.txt"
SQL_ROLE_MAP = {
    'admin': 'admin_role',
    'shelter_worker': 'shelter_worker_role',
    'adopter': 'adopter_role',
    'general': 'general_role'
}

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

def get_sql_role(app_role):
    """Map application role to SQL role name."""
    return SQL_ROLE_MAP.get(app_role)

def _set_sql_role(cursor, sql_role):
    """Apply SQL role for current connection if provided."""
    if sql_role:
        cursor.execute(f"SET ROLE '{sql_role}'")

def run_query(query, params=None, fetch=False, sql_role=None):
    """Execute SQL query. Return fetched data if fetch=True."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            _set_sql_role(cursor, sql_role)
            cursor.execute(query, params or ())
            data = cursor.fetchall() if fetch else None
        conn.commit()
        return data
    finally:
        conn.close()

def run_procedure(proc_name, params=None, fetch=True, sql_role=None):
    """Call a stored procedure. Raises exceptions for caller to handle."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            _set_sql_role(cursor, sql_role)
            cursor.callproc(proc_name, params or ())
            data = cursor.fetchall() if fetch else None
        conn.commit()
        return data
    except Exception as e:
        conn.rollback()
        raise  # Re-raise the exception for caller to handle
    finally:
        conn.close()
