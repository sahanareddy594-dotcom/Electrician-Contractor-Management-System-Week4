from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

# CREATE TABLES
conn = get_db()
c = conn.cursor()

c.execute("CREATE TABLE IF NOT EXISTS electricians(id INTEGER PRIMARY KEY, name TEXT, phone TEXT, experience TEXT)")
c.execute("CREATE TABLE IF NOT EXISTS jobs(id INTEGER PRIMARY KEY, title TEXT, location TEXT, deadline TEXT, electrician_id INTEGER)")
c.execute("CREATE TABLE IF NOT EXISTS tasks(id INTEGER PRIMARY KEY, name TEXT, job_id INTEGER, electrician_id INTEGER, status TEXT)")
c.execute("CREATE TABLE IF NOT EXISTS materials(id INTEGER PRIMARY KEY, name TEXT, quantity INTEGER, used INTEGER)")

conn.commit()
conn.close()

# DASHBOARD
@app.route("/")
def dashboard():
    conn = get_db()
    e = conn.execute("SELECT COUNT(*) FROM electricians").fetchone()[0]
    j = conn.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
    t = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
    conn.close()
    return render_template("dashboard.html", e=e, j=j, t=t)

# ELECTRICIANS
@app.route("/electricians", methods=["GET","POST"])
def electricians():
    conn = get_db()
    if request.method == "POST":
        conn.execute("INSERT INTO electricians(name,phone,experience) VALUES(?,?,?)",
                     (request.form["name"], request.form["phone"], request.form["experience"]))
        conn.commit()

    data = conn.execute("SELECT * FROM electricians").fetchall()
    conn.close()
    return render_template("electricians.html", data=data)

# JOBS
@app.route("/jobs", methods=["GET","POST"])
def jobs():
    conn = get_db()

    if request.method == "POST":
        conn.execute("INSERT INTO jobs(title,location,deadline,electrician_id) VALUES(?,?,?,?)",
                     (request.form["title"], request.form["location"],
                      request.form["deadline"], request.form["electrician"]))
        conn.commit()

    search = request.args.get("search")

    if search:
        data = conn.execute("""
        SELECT jobs.*, electricians.name as ename
        FROM jobs
        LEFT JOIN electricians ON jobs.electrician_id = electricians.id
        WHERE jobs.title LIKE ?
        """, ('%' + search + '%',)).fetchall()
    else:
        data = conn.execute("""
        SELECT jobs.*, electricians.name as ename
        FROM jobs
        LEFT JOIN electricians ON jobs.electrician_id = electricians.id
        """).fetchall()

    electricians = conn.execute("SELECT * FROM electricians").fetchall()
    conn.close()

    return render_template("jobs.html", data=data, electricians=electricians)

# TASKS
@app.route("/tasks", methods=["GET","POST"])
def tasks():
    conn = get_db()

    if request.method == "POST":
        conn.execute("INSERT INTO tasks(name,job_id,electrician_id,status) VALUES(?,?,?,?)",
                     (request.form["name"], request.form["job"],
                      request.form["electrician"], request.form["status"]))
        conn.commit()

    status = request.args.get("status")

    if status:
        data = conn.execute("""
        SELECT tasks.*, jobs.title as jobname, electricians.name as ename
        FROM tasks
        LEFT JOIN jobs ON tasks.job_id = jobs.id
        LEFT JOIN electricians ON tasks.electrician_id = electricians.id
        WHERE tasks.status=?
        """, (status,)).fetchall()
    else:
        data = conn.execute("""
        SELECT tasks.*, jobs.title as jobname, electricians.name as ename
        FROM tasks
        LEFT JOIN jobs ON tasks.job_id = jobs.id
        LEFT JOIN electricians ON tasks.electrician_id = electricians.id
        """).fetchall()

    jobs = conn.execute("SELECT * FROM jobs").fetchall()
    electricians = conn.execute("SELECT * FROM electricians").fetchall()

    conn.close()
    return render_template("tasks.html", data=data, jobs=jobs, electricians=electricians)

# MATERIALS
@app.route("/materials", methods=["GET","POST"])
def materials():
    conn = get_db()

    if request.method == "POST":
        conn.execute("INSERT INTO materials(name,quantity,used) VALUES(?,?,?)",
                     (request.form["name"], request.form["quantity"], request.form["used"]))
        conn.commit()

    data = conn.execute("SELECT * FROM materials").fetchall()
    conn.close()
    return render_template("materials.html", data=data)

# REPORTS
@app.route("/reports")
def reports():
    conn = get_db()
    tasks = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
    completed = conn.execute("SELECT COUNT(*) FROM tasks WHERE status='Completed'").fetchone()[0]
    electricians = conn.execute("SELECT COUNT(*) FROM electricians").fetchone()[0]
    conn.close()
    return render_template("reports.html", tasks=tasks, completed=completed, electricians=electricians)

if __name__ == "__main__":
    app.run(debug=True)