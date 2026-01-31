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
def list_people():
    with db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, first_name, last_name, created_at FROM people ORDER BY id")
            rows = cur.fetchall()

    items = ""
    for (pid, first, last, created) in rows:
        items += f"""
        <li>
          <b>{pid}</b> {first} {last} ({created})
          <form method="POST" action="/delete" style="display:inline">
            <input type="hidden" name="id" value="{pid}">
            <button type="submit">x</button>
          </form>
        </li>
        """

    return f"<h2>Service C - List</h2><ul>{items}</ul>"

@app.post("/delete")
def delete_one():
    pid = int(request.form["id"])
    with db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM people WHERE id=%s", (pid,))
            cur.execute("SELECT COUNT(*) FROM people")
            remaining = cur.fetchone()[0]

    return f"""
    <p>Remaining records: {remaining}</p>
    <a href="/">Back to list</a>
    """
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
