
-- Create audit_log table (needed before using in trigger)
CREATE TABLE audit_log (
    log_id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    action_type VARCHAR2(10) NOT NULL,
    table_name VARCHAR2(50) NOT NULL,
    record_id NUMBER NOT NULL,
    action_timestamp TIMESTAMP DEFAULT SYSTIMESTAMP NOT NULL,
    user_id VARCHAR2(30) NOT NULL,
    details VARCHAR2(500)
);

-- Members table
CREATE TABLE members (
    member_id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username VARCHAR2(50) UNIQUE NOT NULL,
    password VARCHAR2(100) NOT NULL,
    full_name VARCHAR2(100) NOT NULL,
    email VARCHAR2(100) UNIQUE NOT NULL,
    phone VARCHAR2(20) NOT NULL,
    join_date DATE DEFAULT SYSDATE NOT NULL,
    membership_type VARCHAR2(20) NOT NULL,
    status VARCHAR2(10) DEFAULT 'Active' NOT NULL
);

-- Trainers table
CREATE TABLE trainers (
    trainer_id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    full_name VARCHAR2(100) NOT NULL,
    specialization VARCHAR2(100) NOT NULL,
    phone VARCHAR2(20) NOT NULL,
    email VARCHAR2(100) UNIQUE NOT NULL,
    hire_date DATE DEFAULT SYSDATE NOT NULL
);

-- Workout sessions table
CREATE TABLE workout_sessions (
    session_id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    member_id NUMBER NOT NULL,
    trainer_id NUMBER NOT NULL,
    session_date DATE NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    status VARCHAR2(20) DEFAULT 'Scheduled' NOT NULL,
    notes VARCHAR2(500),
    CONSTRAINT fk_member FOREIGN KEY (member_id) REFERENCES members(member_id),
    CONSTRAINT fk_trainer FOREIGN KEY (trainer_id) REFERENCES trainers(trainer_id)
);

-- Payments table
CREATE TABLE payments (
    payment_id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    member_id NUMBER NOT NULL,
    amount NUMBER(10,2) NOT NULL,
    payment_date DATE DEFAULT SYSDATE NOT NULL,
    payment_method VARCHAR2(20) NOT NULL,
    transaction_id VARCHAR2(50),
    status VARCHAR2(20) DEFAULT 'Completed' NOT NULL,
    CONSTRAINT fk_payment_member FOREIGN KEY (member_id) REFERENCES members(member_id)
);

-- Equipment table
CREATE TABLE equipment (
    equipment_id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR2(100) NOT NULL,
    purchase_date DATE NOT NULL,
    last_maintenance DATE,
    status VARCHAR2(20) NOT NULL,
    location VARCHAR2(50) NOT NULL
);

-- Procedure: register_member
CREATE OR REPLACE PROCEDURE register_member(
    p_username IN VARCHAR2,
    p_password IN VARCHAR2,
    p_full_name IN VARCHAR2,
    p_email IN VARCHAR2,
    p_phone IN VARCHAR2,
    p_membership_type IN VARCHAR2,
    p_member_id OUT NUMBER
) AS
BEGIN
    INSERT INTO members (username, password, full_name, email, phone, membership_type)
    VALUES (p_username, p_password, p_full_name, p_email, p_phone, p_membership_type)
    RETURNING member_id INTO p_member_id;
    COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        RAISE;
END register_member;
/

-- Procedure: schedule_session
CREATE OR REPLACE PROCEDURE schedule_session(
    p_member_id IN NUMBER,
    p_trainer_id IN NUMBER,
    p_session_date IN VARCHAR2,  
    p_start_time IN VARCHAR2,
    p_end_time IN VARCHAR2,
    p_session_id OUT NUMBER
) AS
    v_session_date DATE;
    v_start_time TIMESTAMP;
    v_end_time TIMESTAMP;
BEGIN
    -- Explicitly convert string inputs to proper date/time types
    v_session_date := TO_DATE(p_session_date, 'YYYY-MM-DD');
    v_start_time := TO_TIMESTAMP(p_session_date || ' ' || p_start_time, 'YYYY-MM-DD HH24:MI');
    v_end_time := TO_TIMESTAMP(p_session_date || ' ' || p_end_time, 'YYYY-MM-DD HH24:MI');
    
    INSERT INTO workout_sessions (
        member_id,
        trainer_id,
        session_date,
        start_time,
        end_time
    ) VALUES (
        p_member_id,
        p_trainer_id,
        v_session_date,
        v_start_time,
        v_end_time
    )
    RETURNING session_id INTO p_session_id;
    
    COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        RAISE;
END;
/
-- Procedure: process_payment
CREATE OR REPLACE PROCEDURE process_payment(
    p_member_id IN NUMBER,
    p_amount IN NUMBER,
    p_payment_method IN VARCHAR2,
    p_transaction_id IN VARCHAR2,
    p_payment_id OUT NUMBER
) AS
BEGIN
    INSERT INTO payments (member_id, amount, payment_method, transaction_id)
    VALUES (p_member_id, p_amount, p_payment_method, p_transaction_id)
    RETURNING payment_id INTO p_payment_id;
    COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        RAISE;
END process_payment;
/

-- Trigger: log_member_registration
CREATE OR REPLACE TRIGGER log_member_registration
AFTER INSERT ON members
FOR EACH ROW
BEGIN
    INSERT INTO audit_log (action_type, table_name, record_id, action_timestamp, user_id)
    VALUES ('INSERT', 'MEMBERS', :NEW.member_id, SYSTIMESTAMP, USER);
END;
/

-- Trigger: validate_session_time
CREATE OR REPLACE TRIGGER validate_session_time
BEFORE INSERT OR UPDATE ON workout_sessions
FOR EACH ROW
BEGIN
    IF :NEW.start_time >= :NEW.end_time THEN
        RAISE_APPLICATION_ERROR(-20001, 'End time must be after start time');
    END IF;
    
    IF :NEW.session_date < TRUNC(SYSDATE) THEN
        RAISE_APPLICATION_ERROR(-20002, 'Cannot schedule sessions in the past');
    END IF;
END;
/


-- Trigger: update_membership_status
CREATE OR REPLACE TRIGGER update_membership_status
AFTER UPDATE OF status ON payments
FOR EACH ROW
WHEN (NEW.status = 'Overdue')
BEGIN
    UPDATE members
    SET status = 'Suspended'
    WHERE member_id = :NEW.member_id;
END;
/

INSERT INTO trainers (full_name, specialization, phone, email) VALUES 
('Alex Johnson', 'Weight Training', '555-0101', 'alex@example.com');
INSERT INTO trainers (full_name, specialization, phone, email) VALUES 
('Maria Garcia', 'Yoga', '555-0102', 'maria@example.com');
INSERT INTO trainers (full_name, specialization, phone, email) VALUES 
('James Smith', 'CrossFit', '555-0103', 'james@example.com');
INSERT INTO trainers (full_name, specialization, phone, email) VALUES 
('Sarah Lee', 'Pilates', '555-0104', 'sarah@example.com');
INSERT INTO trainers (full_name, specialization, phone, email) VALUES 
('David Kim', 'Boxing', '555-0105', 'david@example.com');

COMMIT;

select *from trainers;

select *from members;



--  Member Dashboard View
CREATE OR REPLACE VIEW member_dashboard_view AS
SELECT 
    m.member_id,
    m.username,
    m.full_name,
    m.email,
    m.membership_type,
    m.status,
    (SELECT COUNT(*) FROM workout_sessions ws 
     WHERE ws.member_id = m.member_id 
     AND ws.session_date >= TRUNC(SYSDATE)) AS upcoming_sessions_count,
    (SELECT SUM(amount) FROM payments p 
     WHERE p.member_id = m.member_id) AS total_payments
FROM members m;
select *from member_dashboard_view;


--  Trainer Schedule View
CREATE OR REPLACE VIEW trainer_schedule_view AS
SELECT 
    t.trainer_id,
    t.full_name AS trainer_name,
    t.specialization,
    ws.session_date,
    TO_CHAR(ws.start_time, 'HH24:MI') AS start_time,
    TO_CHAR(ws.end_time, 'HH24:MI') AS end_time,
    m.full_name AS member_name,
    ws.status
FROM trainers t
LEFT JOIN workout_sessions ws ON t.trainer_id = ws.trainer_id
LEFT JOIN members m ON ws.member_id = m.member_id
WHERE ws.session_date >= TRUNC(SYSDATE)
ORDER BY t.full_name, ws.session_date;

select *from trainer_schedule_view;

