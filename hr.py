from flask import Flask, request, jsonify, render_template
import sqlite3
import random

app = Flask(__name__)

def getDBConnection():
    con = sqlite3.connect("EmploymentManagement.db")
    return con

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/search")
def search_page():
    return render_template("search.html")

@app.route("/apply")
def apply_page():
    return render_template("apply.html")

# -------------------------------------------------
# 1. Search job listings
# To test, add: /jobs/search?keyword=HR to the URL
# -------------------------------------------------
@app.route("/jobs/search", methods=["GET"])
def searchJobListings():
    keyword = request.args.get("keyword", "")

    con = getDBConnection()
    cursor = con.cursor()
    cursor.execute("""
                    SELECT * FROM JOB
                    WHERE JOB_TITLE LIKE ? OR JOB_DESCRIPTION LIKE ?""", ('%' + keyword + '%', '%' + keyword + '%'))
    rows = cursor.fetchall()
    con.close()

    headers = []
    for col in cursor.description:
        headers.append(col[0])

    jobs = []
    for row in rows:
        jobs.append(dict(zip(headers, row)))

    return jsonify({
        "count": len(jobs),
        "jobs": jobs
    })


# -------------------------------------------------
# 2. Submit an application
# -------------------------------------------------
@app.route("/applications/submit", methods=["POST"])
def submitApplication():
    data = request.get_json()

    job_id = data.get("job_id")

    con = getDBConnection()
    cursor = con.cursor()

    # Verify job exists
    cursor.execute("SELECT * FROM JOB WHERE JOB_ID = ?", (job_id,))
    job = cursor.fetchone()

    if job:
        app_id = random.randint(1000, 9999)

        cursor.execute(
            """
            INSERT INTO APPLICATION (
                APP_ID,
                JOB_ID,
                APP_FNAME,
                APP_LNAME,
                APP_EMAIL,
                APP_PHONE,
                APP_ADDRESS,
                APP_EDUCATION,
                APP_EXPERIENCE
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                app_id,
                job_id,
                data.get("first_name"),
                data.get("last_name"),
                data.get("email"),
                data.get("phone"),
                data.get("address"),
                data.get("education"),
                data.get("experience")
            )
        )

        con.commit()
        con.close()

        return jsonify({
            "message": "Application submitted successfully",
            "application_id": app_id
        }), 201
    else:
        con.close()
        return jsonify({
            "message": "Job not found"
        }), 404

if __name__ == "__main__":
    app.run(debug=True)