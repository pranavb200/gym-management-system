
# 🏋️‍♂️ Gym Management System

## 📘 Project Description
The **Gym Management System** is a database-driven web application that allows gym administrators to manage members, trainers, workout plans, attendance, and payments efficiently.  
It is built using **Postgre SQL** as the backend and **Flask (Python)** for the web interface. The system demonstrates database concepts such as **Views**, **Stored Procedures**, **Triggers**, **Transactions**, and **Normalization (up to 3NF)**.

---

## 🧠 Skills Used
- SQL (Postgres)
- Database Design (ER Model, Normalization till 3NF)
- Flask (Python Web Framework)
- HTML, CSS, JavaScript (Frontend)
- SQLAlchemy (Database connection)
- Render / GitHub Deployment
- Environment Variables Configuration

---

## ⚙️ Project Modules
1. **Member Management**
   - Add, Update, Delete, and View Members
   - Attendance Tracking

2. **Trainer Management**
   - Assign trainers to members
   - Manage trainer schedules

3. **Workout & Plans**
   - Maintain workout plans and schedules

4. **Payments**
   - Record payments and generate reports

5. **Reports & Dashboard**
   - Views for member details, payment history, and attendance summary

---

## 🧩 Database Components (Oracle)
- **3 Views**  
  Example: Member Attendance, Payment History, Active Trainers

- **3 Stored Procedures**  
  Example: Add Member, Update Payment, Assign Trainer

- **3 Triggers**  
  Example: Auto-update member status, log payment insertions, attendance tracking

- **Transactions**  
  Used for consistent operations like new member registration with payment

---

## 🗂️ Folder Structure
```
Gym_Management_System/
│
├── app.py
├── templates/
│   ├── index.html
│   ├── add_member.html
│   ├── trainer.html
│   └── payments.html
│
├── static/
│   ├── style.css
│   └── script.js
│
├── requirements.txt
└── README.md
```

---

## 🚀 How to Run Locally

### 1️⃣ Setup Virtual Environment
```bash
python -m venv venv
venv\Scriptsctivate   # For Windows
source venv/bin/activate  # For Mac/Linux
```

### 2️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 3️⃣ Configure Environment Variables
Create a `.env` file in the project root:
```
DB_USER=your_oracle_username
DB_PASSWORD=your_oracle_password
DB_DSN=your_oracle_dsn
```
If you are not using `.env`, update `app.py` with your credentials directly.

### 4️⃣ Run Flask App
```bash
python app.py
```

Then open in browser:  
👉 (https://gym-management-system-vagf.onrender.com)

---

## ☁️ Deployment Guide (Render / GitHub)

1. Push project to **GitHub Repository**
2. Connect repository to **Render.com**
3. Add Environment Variables under “Environment” section in Render
4. Deploy the web service — your project will be live with a public link!

---

## 👨‍💻 Author
**Pranav B**  
GitHub: [https://github.com/pranavb200](https://github.com/pranavb200)

---

## 🏁 Conclusion
This project demonstrates database-driven web development integrating **Postgres SQL**, **Flask**, and **HTML/CSS** to create a real-world **Gym Management System** that fulfills academic DBMS requirements and can be deployed publicly.
