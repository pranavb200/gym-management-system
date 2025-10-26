
# 🏋️‍♂️ Gym Management System

## 📘 Project Description
The **Gym Management System** is a database-driven web application designed to help gym administrators and members manage registrations, trainers, workout sessions, payments, and attendance.  
Built using **Flask (Python)** and **Supabase PostgreSQL**, it provides a seamless experience for managing gym operations both locally and online.

---

## 🌐 Live Deployment
🚀 **Live App:** [https://gym-management-system-v9ws.onrender.com](https://gym-management-system-v9ws.onrender.com)

Hosted on **Render** (Flask web service) with a **Supabase PostgreSQL** backend for persistent, secure, and free cloud-based database storage.

---

## 🧠 Skills Used
- Python (Flask Framework)
- HTML, CSS, JavaScript
- PostgreSQL (Supabase Cloud Database)
- psycopg2 (Database Connector)
- Git & GitHub for Version Control
- Render for Web Deployment
- Environment Variable Configuration

---

## 🧩 Features
- Member Registration and Login
- Trainer Management
- Schedule Workout Sessions
- Track Payments
- Member Dashboard with Session and Payment History
- Persistent Cloud Database (Supabase PostgreSQL)
- Secure Authentication System (Session-based)
- Hosted Flask Web App on Render (Free Tier)

---

## ⚙️ Folder Structure
```
gym-management-system/
│
├── app.py                # Main Flask Application
├── templates/            # HTML Templates
│   ├── index.html
│   ├── register.html
│   ├── login.html
│   ├── dashboard.html
│   ├── schedule.html
│   └── payments.html
│
├── static/               # CSS / JS Files
│   ├── style.css
│
├── requirements.txt      # Python Dependencies
└── README.md             # Project Documentation
```

---

## 🧱 Database (Supabase PostgreSQL)
Supabase provides a free and permanent **PostgreSQL** instance.  
The Gym Management System uses the following schema (simplified view):

### Tables
- **members** (member_id, username, password, full_name, email, phone, membership_type, status)
- **trainers** (trainer_id, full_name, specialization)
- **workout_sessions** (session_id, member_id, trainer_id, session_date, start_time, end_time)
- **payments** (payment_id, member_id, amount, payment_method, payment_date, transaction_id, status)

### Stored Procedures / Triggers
- Automatic status updates on member registration
- Session scheduling validation
- Payment transaction logging

---

## 🔑 Environment Variables (Render + Supabase)
Set these in **Render → Environment Tab**:

| Key | Description | Example |
|-----|--------------|----------|
| `PG_HOST` | Supabase Hostname | db.dithtrecrdlsgcwowqny.supabase.co |
| `PG_PORT` | PostgreSQL Port | 5432 |
| `PG_USER` | PostgreSQL Username | postgres |
| `PG_PASSWORD` | Supabase Database Password | your_db_password |
| `PG_DB` | Database Name | postgres |
| `SECRET_KEY` | Flask Session Key | mysecret123 |

---

## 🚀 Deployment Guide
### 1️⃣ Push to GitHub
```bash
git add .
git commit -m "Final Supabase integration"
git push origin main
```

### 2️⃣ Deploy on Render
1. Go to [Render](https://render.com)
2. Click **New → Web Service**
3. Connect your GitHub repository
4. Set build command:
   ```bash
   pip install -r requirements.txt
   ```
5. Set start command:
   ```bash
   python app.py
   ```
6. Add Supabase environment variables (as above)
7. Deploy 🎉

---

## 💻 Run Locally
```bash
python -m venv venv
venv\Scripts\activate  # (Windows)
source venv/bin/activate # (Mac/Linux)

pip install -r requirements.txt
python app.py
```
Then open → [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 👨‍💻 Author
**Pranav B**  
GitHub: [https://github.com/pranavb200](https://github.com/pranavb200)  
Live App: [https://gym-management-system-v9ws.onrender.com](https://gym-management-system-v9ws.onrender.com)

---

## 🏁 Conclusion
This project demonstrates how to build a modern, full-stack **Gym Management System** using Flask and Supabase.  
It integrates authentication, scheduling, and payment management with a cloud database backend, deployed permanently for free on Render.
