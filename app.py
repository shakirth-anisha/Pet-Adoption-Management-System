from flask import Flask, render_template
from utils.db import get_connection

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('base.html')

@app.route("/test_db")
def test_db():
    conn = get_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute("SELECT NOW() AS time;")
            result = cur.fetchone()
        conn.close()
        return f"Database connected successfully! Server time: {result['time']}"
    return "Database connection failed."

if __name__ == '__main__':
    app.run(debug=True)