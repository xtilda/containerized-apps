import os
import psycopg2
from flask import Flask, request

app = Flask(__name__)

def db_conn():
    return psycopg2.connect(
        host=os.environ["DB_HOST"],
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
    )

@app.get("/")
def form():
    return """
    <h2>Service B - Add Name</h2>
    <form method="POST" action="/submit">
      First name: <input name="first_name" required>
      Last name: <input name="last_name" required>
      <button type="submit">Submit</button>
    </form>
    """

@app.post("/submit")
def submit():
    first = request.form["first_name"].strip()
    last = request.form["last_name"].strip()

    with db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id FROM people WHERE first_name=%s AND last_name=%s",
                (first, last),
            )
            exists = cur.fetchone()
            if exists:
                return """
                <p>name already exists</p>
                <a href="/">Enter a new record</a>
                """

            cur.execute(
                "INSERT INTO people (first_name, last_name) VALUES (%s, %s)",
                (first, last),
            )
            cur.execute("SELECT COUNT(*) FROM people")
            total = cur.fetchone()[0]

    return f"""
    <p>Total records in DB: {total}</p>
    <a href="/">Enter a new record</a>
    """
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
