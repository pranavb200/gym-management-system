from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime
import psycopg2
import os

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "default_secret_key")

# -------------------------------------------------
# Database connection helper (Supabase PostgreSQL)
# -------------------------------------------------
def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=os.getenv("PG_HOST"),
            port=os.getenv("PG_PORT"),
            user=os.getenv("PG_USER"),
            password=os.getenv("PG_PASSWORD"),
            dbname=os.getenv("PG_DB"),
            sslmode="require"  # ✅ Required for Supabase
        )
        return conn
    except psycopg2.Error as e:
        print("❌ Database connection error:", e)
        return None

# -------------------------------------------------
# Routes
# -------------------------------------------------
@app.route('/')
def home():
    return render_template('index.html')

# ------------------ Register ---------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username        = request.form['username']
        password        = request.form['password']
        full_name       = request.form['full_name']
        email           = request.form['email']
        phone           = request.form['phone']
        membership_type = request.form['membership_type']

        conn = get_db_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO members (username, password, full_name, email, phone, membership_type)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING member_id
                """, (username, password, full_name, email, phone, membership_type))
                conn.commit()
                flash('✅ Registration successful! Please login.', 'success')
                return redirect(url_for('login'))
            except psycopg2.Error as e:
                flash(f'Registration failed: {e.pgerror}', 'danger')
            finally:
                cur.close()
                conn.close()
        else:
            flash('Database connection error', 'danger')
    return render_template('register.html')

# ------------------- Login -----------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("""
                    SELECT member_id, username, full_name
                    FROM members
                    WHERE username = %s AND password = %s
                """, (username, password))
                member = cur.fetchone()

                if member:
                    session['member_id'] = member[0]
                    session['username']  = member[1]
                    session['full_name'] = member[2]
                    flash('✅ Login successful!', 'success')
                    return redirect(url_for('dashboard'))
                else:
                    flash('Invalid username or password', 'danger')
            except psycopg2.Error:
                flash('Database error during login', 'danger')
            finally:
                cur.close()
                conn.close()
        else:
            flash('Database connection error', 'danger')

    return render_template('login.html')

# ------------------ Dashboard --------------------
@app.route('/dashboard')
def dashboard():
    if 'member_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()

            # Member details
            cur.execute("""
                SELECT full_name, email, phone, membership_type, status
                FROM members WHERE member_id = %s
            """, (session['member_id'],))
            member_details = cur.fetchone()

            # Upcoming sessions
            cur.execute("""
                SELECT w.session_id, t.full_name, w.session_date, w.start_time, w.end_time
                FROM workout_sessions w
                JOIN trainers t ON w.trainer_id = t.trainer_id
                WHERE w.member_id = %s AND w.session_date >= CURRENT_DATE
                ORDER BY w.session_date, w.start_time
            """, (session['member_id'],))
            upcoming_sessions = cur.fetchall()

            # Payment history
            cur.execute("""
                SELECT payment_date, amount, payment_method, status
                FROM payments WHERE member_id = %s
                ORDER BY payment_date DESC
            """, (session['member_id'],))
            payment_history = cur.fetchall()

            return render_template(
                'dashboard.html',
                member_details=member_details,
                upcoming_sessions=upcoming_sessions,
                payment_history=payment_history
            )
        except psycopg2.Error:
            flash('Database error', 'danger')
            return redirect(url_for('home'))
        finally:
            cur.close()
            conn.close()
    else:
        flash('Database connection error', 'danger')
        return redirect(url_for('home'))

# ------------------ Schedule ---------------------
@app.route('/schedule', methods=['GET', 'POST'])
def schedule():
    if 'member_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    if not conn:
        flash('Database connection error', 'danger')
        return redirect(url_for('dashboard'))

    try:
        cur = conn.cursor()
        cur.execute("SELECT trainer_id, full_name FROM trainers ORDER BY full_name")
        trainers = cur.fetchall()

        if request.method == 'POST':
            trainer_id  = request.form['trainer_id']
            session_date = request.form['session_date']
            start_time   = request.form['start_time']
            end_time     = request.form['end_time']

            start_ts = f"{session_date} {start_time}:00"
            end_ts   = f"{session_date} {end_time}:00"

            cur.execute("""
                INSERT INTO workout_sessions (member_id, trainer_id, session_date, start_time, end_time)
                VALUES (%s, %s, %s, %s, %s)
            """, (session['member_id'], trainer_id, session_date, start_ts, end_ts))
            conn.commit()
            flash('✅ Session scheduled successfully!', 'success')
            return redirect(url_for('dashboard'))

        return render_template('schedule.html', trainers=trainers, min_date=datetime.now().strftime('%Y-%m-%d'))
    except psycopg2.Error as e:
        flash(f'Scheduling failed: {e.pgerror}', 'danger')
        return redirect(url_for('dashboard'))
    finally:
        cur.close()
        conn.close()

# ------------------ Payments ---------------------
@app.route('/make_payment', methods=['GET', 'POST'])
def make_payment():
    if 'member_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        amount          = request.form['amount']
        payment_method  = request.form['payment_method']
        transaction_id  = request.form.get('transaction_id', '')

        conn = get_db_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO payments (member_id, amount, payment_method, transaction_id)
                    VALUES (%s, %s, %s, %s)
                """, (session['member_id'], amount, payment_method, transaction_id))
                conn.commit()
                flash('💳 Payment processed successfully!', 'success')
                return redirect(url_for('dashboard'))
            except psycopg2.Error as e:
                flash(f'Payment failed: {e.pgerror}', 'danger')
            finally:
                cur.close()
                conn.close()
        else:
            flash('Database connection error', 'danger')

    return render_template('payments.html')

# ------------------- Logout ----------------------
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('home'))

# -------------------------------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv("PORT", 5000)), debug=True)
