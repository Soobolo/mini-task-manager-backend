from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)

DB = "tasks.db"

# Initialize database
def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT NOT NULL,
            completed INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Helper function to convert rows to dict
def row_to_dict(row):
    return {"id": row[0], "task": row[1], "completed": bool(row[2])}

# Get all tasks
@app.route("/tasks", methods=["GET"])
def get_tasks():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT * FROM tasks")
    tasks = [row_to_dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify(tasks)

# Add new task
@app.route("/tasks", methods=["POST"])
def add_task():
    data = request.get_json()
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("INSERT INTO tasks (task) VALUES (?)", (data["task"],))
    conn.commit()
    task_id = c.lastrowid
    conn.close()
    return jsonify({"id": task_id, "task": data["task"], "completed": False}), 201

# Delete task
@app.route("/tasks/<int:id>", methods=["DELETE"])
def delete_task(id):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("DELETE FROM tasks WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Deleted"}), 200

# Toggle completed
@app.route("/tasks/<int:id>/toggle", methods=["POST"])
def toggle_task(id):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT completed FROM tasks WHERE id=?", (id,))
    row = c.fetchone()
    if not row:
        conn.close()
        return jsonify({"error": "Task not found"}), 404
    new_status = 0 if row[0] else 1
    c.execute("UPDATE tasks SET completed=? WHERE id=?", (new_status, id))
    conn.commit()
    conn.close()
    return jsonify({"id": id, "completed": bool(new_status)}), 200

if __name__ == "__main__":
    app.run(debug=True)
