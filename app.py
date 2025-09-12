from flask import Flask, render_template, request, redirect, url_for
import cx_Oracle
import os
from dotenv import load_dotenv

# Load environment variables from .env (local use only)
load_dotenv()

app = Flask(__name__)

# Oracle DB connection
def get_db_connection():
    dsn_tns = cx_Oracle.makedsn(
        os.getenv("DB_HOST", "localhost"),
        os.getenv("DB_PORT", "1521"),
        service_name=os.getenv("DB_SERVICE", "XE")
    )
    conn = cx_Oracle.connect(
        user=os.getenv("DB_USER", "system"),
        password=os.getenv("DB_PASSWORD", "mypassword"),
        dsn=dsn_tns
    )
    return conn

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/members")
def members():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT member_id, name, age, membership_type FROM Members")
    members_data = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("members.html", members=members_data)

@app.route("/add_member", methods=["GET", "POST"])
def add_member():
    if request.method == "POST":
        name = request.form["name"]
        age = request.form["age"]
        membership_type = request.form["membership_type"]

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Members (member_id, name, age, membership_type) VALUES (member_seq.NEXTVAL, :1, :2, :3)",
            (name, age, membership_type)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for("members"))

    return render_template("add_member.html")

if __name__ == "__main__":
    app.run(debug=True)
