from flask import Flask, flash, request, jsonify, render_template, redirect, url_for
import sqlite3
import random
import os

app = Flask(__name__)
# Secret key is required for sessions and flash messages to work
# It signs data sent to the browser so Flask can trust it
app.secret_key = os.urandom(24)

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
                    SELECT JOB_ID, JOB_TITLE, JOB_DESCRIPTION, JOB_SALARY, JOB_DATEPOSTED, DEPT_NAME FROM JOB
                    JOIN DEPARTMENT ON JOB.DEPT_ID = DEPARTMENT.DEPT_ID
                    WHERE JOB_TITLE LIKE ? OR JOB_DESCRIPTION LIKE ?""", ('%' + keyword + '%', '%' + keyword + '%'))
    rows = cursor.fetchall()
    con.close()

    jobs = []
    for row in rows:
        jobs.append(row)

    print("testing")
    print(jobs)
    return render_template("search.html", jobs=jobs)


# -------------------------------------------------
# 2. Submit an application
# -------------------------------------------------
@app.route("/applications/submit", methods=["POST"])
def submitApplication():
    job_id = request.form.get("job_id")
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    address = request.form.get("address")
    education = request.form.get("education")
    experience = request.form.get("experience")

    # Verify job exists
    con = getDBConnection()
    cursor = con.cursor()
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
                first_name,
                last_name,
                email,
                phone,
                address,
                education,
                experience
            )
        )

        con.commit()
        con.close()

        flash("Application submitted successfully!")
        return redirect(url_for("apply_page"))
    else:
        con.close()
        flash("Job not found.")
        return redirect(url_for("apply_page"))

if __name__ == "__main__":
    app.run(debug=True)