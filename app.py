from flask import Flask, render_template, request, redirect, url_for, session, flash
import cx_Oracle
from config import Config
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)

# ✅ Let cx_Oracle use default client or environment configuration
# Remove any hard-coded local path to instant client.

def get_db_connection():
    try:
        connection = cx_Oracle.connect(
            user=app.config['ORACLE_USER'],
            password=app.config['ORACLE_PASSWORD'],
            dsn=app.config['ORACLE_DSN']
        )
        return connection
    except cx_Oracle.DatabaseError as e:
        print("Database connection error:", e)
        return None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        full_name = request.form['full_name']
        email = request.form['email']
        phone = request.form['phone']
        membership_type = request.form['membership_type']
        
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                member_id = cursor.var(cx_Oracle.NUMBER)
                cursor.callproc('register_member', [
                    username, password, full_name, email, phone,
                    membership_type, member_id
                ])
                conn.commit()
                flash('Registration successful! Please login.', 'success')
                return redirect(url_for('login'))
            except cx_Oracle.DatabaseError as e:
                error, = e.args
                flash(f'Registration failed: {error.message}', 'danger')
            finally:
                cursor.close()
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
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT member_id, username, full_name FROM members "
                    "WHERE username = :username AND password = :password",
                    {'username': username, 'password': password}
                )
                member = cursor.fetchone()
                if member:
                    session['member_id'] = member[0]
                    session['username'] = member[1]
                    session['full_name'] = member[2]
                    flash('Login successful!', 'success')
                    return redirect(url_for('dashboard'))
                else:
                    flash('Invalid username or password', 'danger')
            except cx_Oracle.DatabaseError:
                flash('Database error during login', 'danger')
            finally:
                cursor.close()
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
            cursor = conn.cursor()
            cursor.execute(
                "SELECT full_name, email, phone, membership_type, status "
                "FROM members WHERE member_id = :member_id",
                {'member_id': session['member_id']}
            )
            member_details = cursor.fetchone()

            cursor.execute(
                """SELECT w.session_id, t.full_name, w.session_date,
                          w.start_time, w.end_time
                   FROM workout_sessions w
                   JOIN trainers t ON w.trainer_id = t.trainer_id
                   WHERE w.member_id = :member_id AND w.session_date >= TRUNC(SYSDATE)
                   ORDER BY w.session_date, w.start_time""",
                {'member_id': session['member_id']}
            )
            upcoming_sessions = cursor.fetchall()

            cursor.execute(
                "SELECT payment_date, amount, payment_method, status "
                "FROM payments WHERE member_id = :member_id "
                "ORDER BY payment_date DESC",
                {'member_id': session['member_id']}
            )
            payment_history = cursor.fetchall()

            return render_template(
                'dashboard.html',
                member_details=member_details,
                upcoming_sessions=upcoming_sessions,
                payment_history=payment_history
            )
        except cx_Oracle.DatabaseError:
            flash('Database error', 'danger')
            return redirect(url_for('home'))
        finally:
            cursor.close()
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
        cursor = conn.cursor()
        cursor.execute("SELECT trainer_id, full_name FROM trainers ORDER BY full_name")
        trainers = cursor.fetchall()

        if request.method == 'POST':
            trainer_id = request.form['trainer_id']
            session_date = request.form['session_date']
            start_time = request.form['start_time']
            end_time = request.form['end_time']

            session_id = cursor.var(cx_Oracle.NUMBER)
            cursor.callproc('schedule_session', [
                session['member_id'], trainer_id,
                session_date, start_time, end_time, session_id
            ])
            conn.commit()
            flash('Session scheduled successfully!', 'success')
            return redirect(url_for('dashboard'))

        return render_template(
            'schedule.html',
            trainers=trainers,
            min_date=datetime.now().strftime('%Y-%m-%d')
        )
    except cx_Oracle.DatabaseError as e:
        error, = e.args
        flash(f'Scheduling failed: {error.message}', 'danger')
        return redirect(url_for('dashboard'))
    finally:
        cursor.close()
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
                cursor = conn.cursor()
                payment_id = cursor.var(cx_Oracle.NUMBER)
                cursor.callproc('process_payment', [
                    session['member_id'],
                    amount,
                    payment_method,
                    transaction_id,
                    payment_id
                ])
                conn.commit()
                flash('Payment processed successfully!', 'success')
                return redirect(url_for('dashboard'))
            except cx_Oracle.DatabaseError as e:
                error, = e.args
                flash(f'Payment failed: {error.message}', 'danger')
            finally:
                cursor.close()
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
