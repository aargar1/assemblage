# Copyright (C) 2026-present Aarav Garg
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the Server Side Public License, version 1,
# as published by MongoDB, Inc.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# Server Side Public License for more details.
#
# You should have received a copy of the Server Side Public License
# along with this program. If not, see
# <http://www.mongodb.com/licensing/server-side-public-license>.

import os
import sqlite3
import secrets
import string
import subprocess
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template
import smtplib
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


# ---------------- CONFIG ----------------
DB_FILE = "/srv/asm/accounts.db"

from config import SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASS
from config import DOMAIN

# ---------------- INIT ------------------
app = Flask(__name__)

# Create database if it doesn't exist
with sqlite3.connect(DB_FILE) as conn:
    conn.execute("""
    CREATE TABLE IF NOT EXISTS pending_accounts (
        token TEXT PRIMARY KEY,
        first_name TEXT,
        last_name TEXT,
        student_email TEXT,
        student_no TEXT,
        created_at TEXT
    )
    """)
    conn.commit()

# --------------- HELPERS ----------------
def username_exists(username):
    """Check if Linux user already exists"""
    try:
        subprocess.run(["id", username], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False

def create_linux_user(username, password):
    """Create Linux user with password"""
    subprocess.run(["sudo", "/srv/asm/crtusr.sh", username, password], check=True)

def send_verification_email(email, code):
    """Send verification code via email"""
    subject = "Your Assemblage Code"
    body = f"""Hello,

Your verification code is:

{code}

It will expire in 15 minutes.

Thank you.
"""
    msg = f"Subject: {subject}\nFrom: {SMTP_USER}\nTo: {email}\n\n{body}"
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10) as server:
        server.ehlo()
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SMTP_USER, email, msg)

# ---------------- ROUTES ----------------
@app.route("/create_account", methods=["POST"])
def create_account():
    try:
        data = request.get_json(force=True)
        logger.debug(f"Incoming data: {data}")

        first_name = data.get("firstName", "").strip()
        last_name = data.get("lastName", "").strip()
        student_email = data.get("studentEmail", "").strip()
        student_no = data.get("studentNo", "").strip()
        logger.debug(f"Parsed fields: {first_name}, {last_name}, {student_email}, {student_no}")

        if not (first_name and last_name and student_email and student_no):
            return jsonify({"error": "Missing required fields"}), 400
        if DOMAIN not in student_email.lower():
            return jsonify({"error": "Invalid email"}), 400

        username = student_email.split("@")[0]
        logger.debug(f"Username will be: {username}")

        verification_code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        created_at = datetime.utcnow().isoformat()
        logger.debug(f"Generated verification code: {verification_code}")

        with sqlite3.connect(DB_FILE) as conn:
            conn.execute("""
            INSERT INTO pending_accounts (token, first_name, last_name, student_email, student_no, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (verification_code, first_name, last_name, student_email, student_no, created_at))
            conn.commit()
        logger.debug("Saved verification request to DB")

        try:
            send_verification_email(student_email, verification_code)
            logger.debug("Verification email sent")
        except Exception as e:
            logger.error(f"Email send failed: {e}")
            return jsonify({"error": f"Failed to send email: {e}"}), 500

        return jsonify({"message": "Verification code sent. Check your email."})

    except Exception as e:
        logger.exception("Unhandled exception in /create_account")
        return jsonify({"error": str(e)}), 500


@app.route("/verify_code", methods=["POST"])
def verify_code():
    data = request.get_json()
    code = data.get("code", "").strip()

    with sqlite3.connect(DB_FILE) as conn:
        row = conn.execute("""
        SELECT first_name, last_name, student_email, student_no, created_at
        FROM pending_accounts
        WHERE token = ?
        """, (code,)).fetchone()

        if not row:
            return jsonify({"error": "Invalid or expired code"}), 400

        first_name, last_name, student_email, student_no, created_at_str = row
        created_at = datetime.fromisoformat(created_at_str)

        if datetime.utcnow() > created_at + timedelta(minutes=15):
            conn.execute("DELETE FROM pending_accounts WHERE token = ?", (code,))
            conn.commit()
            return jsonify({"error": "This verification code has expired"}), 400

        username = student_email.split("@")[0]

        password_chars = string.ascii_letters + string.digits
        password = ''.join(secrets.choice(password_chars) for _ in range(12))

        try:
            create_linux_user(username, password)
        except subprocess.CalledProcessError as e:
            return jsonify({"error": f"System error: {e}"}), 500

        conn.execute("DELETE FROM pending_accounts WHERE token = ?", (code,))
        conn.commit()

    return jsonify({"message": "Account created successfully!", "username": username, "password": password})


@app.route("/")
def index():
    return render_template("index.html")

# ----------------- MAIN -----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
