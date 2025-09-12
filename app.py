from flask import Flask, render_template, request, redirect, url_for, session, flash
import psycopg2
from psycopg2.extras import RealDictCursor
from config import Config
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=app.config['PG_HOST'],
            port=app.config['PG_PORT'],
            user=app.config['PG_USER'],
            password=app.config['PG_PASSWORD'],
            dbname=app.config['PG_DB']
        )
        return conn
    except Exception as e:
        print("Database connection error:", e)
        return None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = (
            request.form['username'],
            request.form['password'],
            request.form['full_name'],
            request.form['email'],
            request.form['phone'],
            request.form['membership_type']
        )
        conn = get_db_connection()
        if conn:
            try:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO members
                        (username,password,full_name,email,phone,membership_type,status)
                        VALUES (%s,%s,%s,%s,%s,%s,'ACTIVE')
                    """, data)
                    conn.commit()
                flash('Registration successful! Please login.', 'success')
                return redirect(url_for('login'))
            except Exception as e:
                flash(f'Registration failed: {e}', 'danger')
            finally:
                conn.close()
        else:
            flash('Database connection error', 'danger')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        if conn:
            try:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT member_id, username, full_name
                        FROM members
                        WHERE username=%s AND password=%s
                    """, (username, password))
                    member = cur.fetchone()
                    if member:
                        session['member_id'] = member[0]
                        session['username'] = member[1]
                        session['full_name'] = member[2]
                        flash('Login successful!', 'success')
                        return redirect(url_for('dashboard'))
                    else:
                        flash('Invalid username or password', 'danger')
            except Exception:
                flash('Database error during login', 'danger')
            finally:
                conn.close()
        else:
            flash('Database connection error', 'danger')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'member_id' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT full_name,email,phone,membership_type,status
                    FROM members WHERE member_id=%s
                """, (session['member_id'],))
                member_details = cur.fetchone()

                cur.execute("""
                    SELECT w.session_id, t.full_name, w.session_date,
                           w.start_time, w.end_time
                    FROM workout_sessions w
                    JOIN trainers t ON w.trainer_id = t.trainer_id
                    WHERE w.member_id = %s AND w.session_date >= CURRENT_DATE
                    ORDER BY w.session_date, w.start_time
                """, (session['member_id'],))
                upcoming_sessions = cur.fetchall()

                cur.execute("""
                    SELECT payment_date, amount, payment_method, status
                    FROM payments
                    WHERE member_id = %s
                    ORDER BY payment_date DESC
                """, (session['member_id'],))
                payment_history = cur.fetchall()

            return render_template(
                'dashboard.html',
                member_details=member_details,
                upcoming_sessions=upcoming_sessions,
                payment_history=payment_history
            )
        except Exception:
            flash('Database error', 'danger')
            return redirect(url_for('home'))
        finally:
            conn.close()
    else:
        flash('Database connection error', 'danger')
        return redirect(url_for('home'))

@app.route('/schedule', methods=['GET', 'POST'])
def schedule():
    if 'member_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    if not conn:
        flash('Database connection error', 'danger')
        return redirect(url_for('dashboard'))

    try:
        with conn.cursor() as cur:
            cur.execute("SELECT trainer_id, full_name FROM trainers ORDER BY full_name")
            trainers = cur.fetchall()

        if request.method == 'POST':
            trainer_id = request.form['trainer_id']
            session_date = request.form['session_date']
            start_time = request.form['start_time']
            end_time = request.form['end_time']
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO workout_sessions
                    (member_id, trainer_id, session_date, start_time, end_time)
                    VALUES (%s,%s,%s,%s,%s)
                """, (session['member_id'], trainer_id, session_date, start_time, end_time))
                conn.commit()
            flash('Session scheduled successfully!', 'success')
            return redirect(url_for('dashboard'))

        return render_template(
            'schedule.html',
            trainers=trainers,
            min_date=datetime.now().strftime('%Y-%m-%d')
        )
    except Exception as e:
        flash(f'Scheduling failed: {e}', 'danger')
        return redirect(url_for('dashboard'))
    finally:
        conn.close()

@app.route('/make_payment', methods=['GET', 'POST'])
def make_payment():
    if 'member_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        amount = request.form['amount']
        payment_method = request.form['payment_method']
        transaction_id = request.form.get('transaction_id', '')
        conn = get_db_connection()
        if conn:
            try:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO payments
                        (member_id, amount, payment_method, transaction_id, status, payment_date)
                        VALUES (%s,%s,%s,%s,'SUCCESS', CURRENT_TIMESTAMP)
                    """, (session['member_id'], amount, payment_method, transaction_id))
                    conn.commit()
                flash('Payment processed successfully!', 'success')
                return redirect(url_for('dashboard'))
            except Exception as e:
                flash(f'Payment failed: {e}', 'danger')
            finally:
                conn.close()
        else:
            flash('Database connection error', 'danger')
    return render_template('payments.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
